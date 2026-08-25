package com.ononymuos.focussentinel

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.runtime.*
import androidx.core.content.ContextCompat
import com.ononymuos.focussentinel.audio.AudioAlertManager
import com.ononymuos.focussentinel.core.FocusState
import com.ononymuos.focussentinel.core.SentinelConfig
import com.ononymuos.focussentinel.core.SessionMetrics
import com.ononymuos.focussentinel.service.FocusSentinelForegroundService
import com.ononymuos.focussentinel.ui.screens.MainScreen
import com.ononymuos.focussentinel.ui.theme.FocusSentinelTheme
import com.ononymuos.focussentinel.vision.FocusDetectorEngine
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors

class MainActivity : ComponentActivity() {

    private lateinit var audioManager: AudioAlertManager
    private lateinit var engine: FocusDetectorEngine
    private val cameraExecutor = Executors.newSingleThreadExecutor()
    private val metrics = SessionMetrics()

    private var configState by mutableStateOf(SentinelConfig())
    private var currentState by mutableStateOf(FocusState.FOCUSED)
    
    private var lensFacing by mutableStateOf(CameraSelector.LENS_FACING_FRONT)
    private var previewView: PreviewView? = null
    private var currentPickingAlarmType: String? = null

    private val permissionLauncher = registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
        if (it[Manifest.permission.CAMERA] == true) {
            previewView?.let { view -> startCamera(view) }
            if (configState.runInBackground) {
                startService()
            }
        }
    }

    // Audio File Picker
    private val audioPickerLauncher = registerForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { savePickedAudio(it) }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val loadedConfig = SentinelConfig.load(this)
        configState = loadedConfig

        audioManager = AudioAlertManager(this, loadedConfig)
        
        engine = FocusDetectorEngine(
            context = this,
            config = loadedConfig,
            metrics = metrics,
            onStateChanged = { state, _ ->
                currentState = state
                runOnUiThread {
                    audioManager.playAlertForState(state)
                }
            }
        )
        metrics.start()

        permissionLauncher.launch(arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.POST_NOTIFICATIONS
        ))

        setContent {
            FocusSentinelTheme {
                val s = currentState
                val cfg = configState
                MainScreen(
                    state = s,
                    metrics = metrics,
                    config = cfg,
                    onConfigUpdated = { updated ->
                        configState = updated
                        updated.save(this@MainActivity)
                        audioManager.config = updated
                        engine.config.apply {
                            eyeRatioThreshold = updated.eyeRatioThreshold
                            readingPitchThreshold = updated.readingPitchThreshold
                            sleepThresholdFrames = updated.sleepThresholdFrames
                            faceCoverThresholdFrames = updated.faceCoverThresholdFrames
                            audioMuted = updated.audioMuted
                            audioVolume = updated.audioVolume
                            hapticsEnabled = updated.hapticsEnabled
                            customSleepSoundPath = updated.customSleepSoundPath
                            customAbsenceSoundPath = updated.customAbsenceSoundPath
                            customPhoneSoundPath = updated.customPhoneSoundPath
                            runInBackground = updated.runInBackground
                        }
                    },
                    onToggleMute = { muted ->
                        val updated = cfg.copy(audioMuted = muted)
                        configState = updated
                        updated.save(this@MainActivity)
                        audioManager.config = updated
                    },
                    onToggleCamera = {
                        lensFacing = if (lensFacing == CameraSelector.LENS_FACING_FRONT) {
                            CameraSelector.LENS_FACING_BACK
                        } else {
                            CameraSelector.LENS_FACING_FRONT
                        }
                        previewView?.let { startCamera(it) }
                    },
                    onPreviewAvailable = { view ->
                        previewView = view
                        if (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                            startCamera(view)
                        }
                    },
                    onPickAudio = { alarmType ->
                        currentPickingAlarmType = alarmType
                        audioPickerLauncher.launch("audio/*")
                    },
                    onTestAudio = { customPath, defaultKey ->
                        audioManager.testSound(customPath, defaultKey)
                    }
                )
            }
        }
    }

    private fun savePickedAudio(uri: Uri) {
        val alarmType = currentPickingAlarmType ?: return
        try {
            val dir = File(filesDir, "custom_alerts")
            if (!dir.exists()) dir.mkdirs()

            val destFile = File(dir, "custom_${alarmType}_${System.currentTimeMillis()}.mp3")
            contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(destFile).use { output ->
                    input.copyTo(output)
                }
            }

            val path = destFile.absolutePath
            val updated = when (alarmType) {
                "sleep" -> configState.copy(customSleepSoundPath = path)
                "absence" -> configState.copy(customAbsenceSoundPath = path)
                "phone" -> configState.copy(customPhoneSoundPath = path)
                else -> configState
            }
            configState = updated
            updated.save(this)
            audioManager.config = updated
        } catch (e: Exception) {
            Log.e("MainActivity", "Failed to save audio file: ${e.message}")
        }
    }

    private fun startCamera(view: PreviewView) {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            val cameraSelector = CameraSelector.Builder().requireLensFacing(lensFacing).build()
            
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(view.surfaceProvider)
            }

            val imageAnalyzer = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor) { image ->
                        processImageProxy(image)
                    }
                }

            try {
                cameraProvider.unbindAll()
                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalyzer)
            } catch (e: Exception) {
                Log.e("MainActivity", "Camera binding failed", e)
            }
        }, ContextCompat.getMainExecutor(this))
    }

    private fun processImageProxy(image: ImageProxy) {
        val bitmap = image.toBitmap()
        engine.processFrame(bitmap, image.imageInfo.timestamp)
        image.close()
    }

    private fun startService() {
        val serviceIntent = Intent(this, FocusSentinelForegroundService::class.java)
        ContextCompat.startForegroundService(this, serviceIntent)
    }

    override fun onDestroy() {
        super.onDestroy()
        engine.close()
        audioManager.release()
        cameraExecutor.shutdown()
        val serviceIntent = Intent(this, FocusSentinelForegroundService::class.java)
        serviceIntent.action = FocusSentinelForegroundService.ACTION_STOP
        startService(serviceIntent)
    }
}
