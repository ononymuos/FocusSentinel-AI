package com.ononymuos.focussentinel.audio

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.media.SoundPool
import android.net.Uri
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.util.Log
import com.ononymuos.focussentinel.R
import com.ononymuos.focussentinel.core.FocusState
import com.ononymuos.focussentinel.core.SentinelConfig
import java.io.File

class AudioAlertManager(private val context: Context, var config: SentinelConfig) {

    private var soundPool: SoundPool?
    private val soundMap = mutableMapOf<String, Int>()
    private var currentStreamId: Int = 0
    private var customMediaPlayer: MediaPlayer? = null
    private var currentPlayingKey: String? = null

    private val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager
        vibratorManager?.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    }

    init {
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_ALARM)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()

        soundPool = SoundPool.Builder()
            .setMaxStreams(3)
            .setAudioAttributes(audioAttributes)
            .build()

        loadSounds()
    }

    fun loadSounds() {
        try {
            soundPool?.let {
                soundMap["sleep"] = it.load(context, R.raw.sleep_alarm, 1)
                soundMap["face_hidden"] = it.load(context, R.raw.face_hidden, 1)
                soundMap["phone"] = it.load(context, R.raw.phone_alert, 1)
            }
        } catch (e: Exception) {
            Log.e("AudioAlertManager", "Error loading sound alerts: ${e.message}")
        }
    }

    fun playAlertForState(state: FocusState) {
        val alertKey = when (state) {
            FocusState.MICRO_SLEEP -> "sleep"
            FocusState.FACE_ABSENT -> "face_hidden"
            FocusState.PHONE_DISTRACTION -> "phone"
            else -> {
                stopAlert()
                return
            }
        }

        if (currentPlayingKey == alertKey) return

        stopAlert()
        triggerHaptics(state)

        if (config.audioMuted) return

        val customPath = when (state) {
            FocusState.MICRO_SLEEP -> config.customSleepSoundPath
            FocusState.FACE_ABSENT -> config.customAbsenceSoundPath
            FocusState.PHONE_DISTRACTION -> config.customPhoneSoundPath
            else -> null
        }

        if (customPath != null && File(customPath).exists()) {
            playCustomAudio(customPath, alertKey)
        } else {
            val soundId = soundMap[alertKey] ?: return
            val vol = config.audioVolume
            currentStreamId = soundPool?.play(soundId, vol, vol, 1, -1, 1.0f) ?: 0
            currentPlayingKey = alertKey
        }
    }

    private fun playCustomAudio(filePath: String, alertKey: String) {
        try {
            customMediaPlayer?.release()
            customMediaPlayer = MediaPlayer().apply {
                setDataSource(context, Uri.fromFile(File(filePath)))
                setAudioAttributes(
                    AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                        .build()
                )
                setVolume(config.audioVolume, config.audioVolume)
                isLooping = true
                prepare()
                start()
            }
            currentPlayingKey = alertKey
        } catch (e: Exception) {
            Log.e("AudioAlertManager", "Failed to play custom audio file: ${e.message}")
            // Fallback to built-in sound
            val soundId = soundMap[alertKey] ?: return
            val vol = config.audioVolume
            currentStreamId = soundPool?.play(soundId, vol, vol, 1, -1, 1.0f) ?: 0
            currentPlayingKey = alertKey
        }
    }

    fun testSound(customPath: String?, defaultKey: String) {
        stopAlert()
        if (customPath != null && File(customPath).exists()) {
            try {
                customMediaPlayer?.release()
                customMediaPlayer = MediaPlayer().apply {
                    setDataSource(context, Uri.fromFile(File(customPath)))
                    setVolume(config.audioVolume, config.audioVolume)
                    isLooping = false
                    prepare()
                    start()
                }
            } catch (e: Exception) {
                Log.e("AudioAlertManager", "Error testing custom sound: ${e.message}")
            }
        } else {
            val soundId = soundMap[defaultKey] ?: return
            val vol = config.audioVolume
            soundPool?.play(soundId, vol, vol, 1, 0, 1.0f)
        }
    }

    fun stopAlert() {
        if (currentStreamId != 0) {
            soundPool?.stop(currentStreamId)
            currentStreamId = 0
        }
        customMediaPlayer?.let {
            if (it.isPlaying) {
                it.stop()
            }
            it.release()
            customMediaPlayer = null
        }
        currentPlayingKey = null
    }

    private fun triggerHaptics(state: FocusState) {
        if (!config.hapticsEnabled || vibrator == null || !vibrator.hasVibrator()) return

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val pattern = when (state) {
                    FocusState.MICRO_SLEEP -> longArrayOf(0, 400, 150, 400, 150, 600)
                    FocusState.PHONE_DISTRACTION -> longArrayOf(0, 200, 100, 200)
                    FocusState.FACE_ABSENT -> longArrayOf(0, 150, 100, 150)
                    else -> return
                }
                val effect = VibrationEffect.createWaveform(pattern, -1)
                vibrator.vibrate(effect)
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(500)
            }
        } catch (e: Exception) {
            Log.e("AudioAlertManager", "Haptic trigger error: ${e.message}")
        }
    }

    fun release() {
        stopAlert()
        soundPool?.release()
        soundPool = null
    }
}
