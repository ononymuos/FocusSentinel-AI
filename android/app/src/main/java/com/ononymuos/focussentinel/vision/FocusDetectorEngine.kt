package com.ononymuos.focussentinel.vision

import android.content.Context
import android.graphics.Bitmap
import android.os.SystemClock
import android.util.Log
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.framework.image.MPImage
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarkerResult
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarker
import com.google.mediapipe.tasks.vision.handlandmarker.HandLandmarkerResult
import com.google.mediapipe.tasks.vision.objectdetector.ObjectDetector
import com.google.mediapipe.tasks.vision.objectdetector.ObjectDetectorResult
import com.ononymuos.focussentinel.core.FocusState
import com.ononymuos.focussentinel.core.SentinelConfig
import com.ononymuos.focussentinel.core.SessionMetrics
import kotlin.math.abs
import kotlin.math.sqrt

class FocusDetectorEngine(
    private val context: Context,
    val config: SentinelConfig,
    val metrics: SessionMetrics,
    private val onStateChanged: (FocusState, SessionMetrics) -> Unit
) {
    private var faceLandmarker: FaceLandmarker? = null
    private var handLandmarker: HandLandmarker? = null
    private var objectDetector: ObjectDetector? = null
    private val poseEstimator = HeadPoseEstimator()

    private var closedFrames = 0
    private var coveredFrames = 0
    private var phoneFrames = 0
    private var lastTickMs = SystemClock.uptimeMillis()
    
    // Multi-signal state
    private var isObjectPhoneDetected = false
    private var isHandHoldingPhoneDetected = false

    // Landmark Indices from MediaPipe Face Mesh
    private val LEFT_EYE_TOP = 159
    private val LEFT_EYE_BOTTOM = 145
    private val FACE_LEFT = 130
    private val FACE_RIGHT = 243
    private val NOSE_TIP = 1
    private val CHIN = 152

    init {
        setupLandmarker()
        setupHandLandmarker()
        setupObjectDetector()
    }

    private fun setupLandmarker() {
        try {
            val baseOptions = BaseOptions.builder()
                .setModelAssetPath("models/face_landmarker.task")
                .build()

            val options = FaceLandmarker.FaceLandmarkerOptions.builder()
                .setBaseOptions(baseOptions)
                .setRunningMode(RunningMode.LIVE_STREAM)
                .setNumFaces(1)
                .setMinFaceDetectionConfidence(0.5f)
                .setMinFacePresenceConfidence(0.5f)
                .setMinTrackingConfidence(0.5f)
                .setResultListener { result: FaceLandmarkerResult, _: MPImage ->
                    processLandmarkResult(result)
                }
                .setErrorListener { error ->
                    Log.e("FocusDetectorEngine", "MediaPipe Face error: ${error.message}")
                }
                .build()

            faceLandmarker = FaceLandmarker.createFromOptions(context, options)
        } catch (e: Exception) {
            Log.e("FocusDetectorEngine", "Error initializing FaceLandmarker: ${e.message}")
        }
    }

    private fun setupHandLandmarker() {
        try {
            val baseOptions = BaseOptions.builder()
                .setModelAssetPath("models/hand_landmarker.task")
                .build()

            val options = HandLandmarker.HandLandmarkerOptions.builder()
                .setBaseOptions(baseOptions)
                .setRunningMode(RunningMode.LIVE_STREAM)
                .setNumHands(2)
                .setMinHandDetectionConfidence(0.35f)
                .setMinHandPresenceConfidence(0.35f)
                .setMinTrackingConfidence(0.35f)
                .setResultListener { result: HandLandmarkerResult, _: MPImage ->
                    processHandResult(result)
                }
                .setErrorListener { error ->
                    Log.e("FocusDetectorEngine", "MediaPipe Hand error: ${error.message}")
                }
                .build()

            handLandmarker = HandLandmarker.createFromOptions(context, options)
        } catch (e: Exception) {
            Log.e("FocusDetectorEngine", "Error initializing HandLandmarker: ${e.message}")
        }
    }

    private fun setupObjectDetector() {
        try {
            val baseOptions = BaseOptions.builder()
                .setModelAssetPath("models/efficientdet_lite0.tflite")
                .build()

            // Set lower threshold on detector so partially occluded / hand-held phones are detected
            val options = ObjectDetector.ObjectDetectorOptions.builder()
                .setBaseOptions(baseOptions)
                .setRunningMode(RunningMode.LIVE_STREAM)
                .setMaxResults(5)
                .setScoreThreshold(0.20f)
                .setResultListener { result: ObjectDetectorResult, _: MPImage ->
                    processObjectResult(result)
                }
                .setErrorListener { error ->
                    Log.e("FocusDetectorEngine", "MediaPipe ObjectDetector error: ${error.message}")
                }
                .build()

            objectDetector = ObjectDetector.createFromOptions(context, options)
        } catch (e: Exception) {
            Log.e("FocusDetectorEngine", "Error initializing ObjectDetector: ${e.message}")
        }
    }

    fun processFrame(bitmap: Bitmap, timestampMs: Long) {
        val mpImage = BitmapImageBuilder(bitmap).build()
        faceLandmarker?.detectAsync(mpImage, timestampMs)
        handLandmarker?.detectAsync(mpImage, timestampMs)
        objectDetector?.detectAsync(mpImage, timestampMs)
    }

    @Synchronized
    private fun processObjectResult(result: ObjectDetectorResult) {
        val detections = result.detections()
        var detectedPhone = false
        if (detections != null && detections.isNotEmpty()) {
            for (detection in detections) {
                for (category in detection.categories()) {
                    val name = category.categoryName().lowercase()
                    // Detect cell phones even if labeled as remote or mobile device
                    if (name.contains("phone") || name.contains("cell") || name.contains("remote")) {
                        if (category.score() >= config.phoneConfidenceThreshold.coerceAtMost(0.25f)) {
                            detectedPhone = true
                            break
                        }
                    }
                }
                if (detectedPhone) break
            }
        }
        isObjectPhoneDetected = detectedPhone
    }

    @Synchronized
    private fun processHandResult(result: HandLandmarkerResult) {
        val hands = result.landmarks()
        var phonePostureDetected = false

        if (hands != null && hands.isNotEmpty()) {
            // Case A: Two hands holding phone / texting posture
            if (hands.size >= 2) {
                val hand1 = hands[0]
                val hand2 = hands[1]
                val wrist1 = hand1[0]
                val wrist2 = hand2[0]
                val distWrists = distance(wrist1.x(), wrist1.y(), wrist2.x(), wrist2.y())
                
                // Wrists close together in front of camera (< 0.35 normalized screen width) is typical texting posture
                if (distWrists < 0.35f) {
                    phonePostureDetected = true
                }
            }

            // Case B: Hand holding object near face or chest in calling/browsing grip
            for (hand in hands) {
                val wrist = hand[0]
                val thumbTip = hand[4]
                val indexTip = hand[8]
                val pinkyTip = hand[20]

                // Grip check: thumb and pinky holding width
                val gripSpan = distance(thumbTip.x(), thumbTip.y(), pinkyTip.x(), pinkyTip.y())
                val isCurvedGrip = gripSpan in 0.08f..0.30f
                
                // Hand raised in upper/mid field of view (y < 0.85)
                if (wrist.y() < 0.85f && isCurvedGrip) {
                    if (isObjectPhoneDetected || hands.size >= 2) {
                        phonePostureDetected = true
                    }
                }
            }
        }
        isHandHoldingPhoneDetected = phonePostureDetected
    }

    @Synchronized
    private fun processLandmarkResult(result: FaceLandmarkerResult) {
        val now = SystemClock.uptimeMillis()
        val deltaSec = (now - lastTickMs) / 1000.0
        lastTickMs = now

        val faceLandmarksList = result.faceLandmarks()
        val hasFace = faceLandmarksList != null && faceLandmarksList.isNotEmpty()

        var nextState = FocusState.FOCUSED

        // 1. Phone Distraction Check (Object detected OR hand holding phone / texting posture)
        val isUsingPhone = isObjectPhoneDetected || isHandHoldingPhoneDetected

        if (isUsingPhone) {
            phoneFrames++
            if (phoneFrames >= config.phoneThresholdFrames.coerceAtMost(6)) {
                nextState = FocusState.PHONE_DISTRACTION
            }
        } else {
            phoneFrames = 0
        }

        // 2. Face Absent Check
        if (nextState == FocusState.FOCUSED) {
            if (!hasFace) {
                coveredFrames++
                if (coveredFrames >= config.faceCoverThresholdFrames) {
                    nextState = FocusState.FACE_ABSENT
                }
                metrics.currentEyeRatio = 0.0f
            } else {
                coveredFrames = 0
                val landmarks = faceLandmarksList[0]

                // Calculate EAR (Eye Aspect Ratio)
                val top = landmarks[LEFT_EYE_TOP]
                val bottom = landmarks[LEFT_EYE_BOTTOM]
                val left = landmarks[FACE_LEFT]
                val right = landmarks[FACE_RIGHT]

                val eyeH = distance(top.x(), top.y(), bottom.x(), bottom.y())
                val faceW = distance(left.x(), left.y(), right.x(), right.y())
                val earPercent = if (faceW > 0f) (eyeH / faceW) * 100f else 0f

                metrics.currentEyeRatio = earPercent

                // 3D Head Pose (Pitch/Yaw/Roll)
                val nose = landmarks[NOSE_TIP]
                val chin = landmarks[CHIN]
                val pose = poseEstimator.estimatePose(
                    floatArrayOf(nose.x(), nose.y(), nose.z()),
                    floatArrayOf(chin.x(), chin.y(), chin.z()),
                    floatArrayOf(left.x(), left.y(), left.z()),
                    floatArrayOf(right.x(), right.y(), right.z())
                )
                metrics.currentPitch = pose.pitch
                metrics.currentYaw = pose.yaw
                metrics.currentRoll = pose.roll

                // If user is looking down but hands are in texting/holding phone position
                if (isHandHoldingPhoneDetected && pose.pitch < config.readingPitchThreshold) {
                    nextState = FocusState.PHONE_DISTRACTION
                } else {
                    // Reading vs True Drowsiness Classification
                    val isReading = pose.pitch < config.readingPitchThreshold
                    val isEyesClosed = earPercent < config.eyeRatioThreshold

                    if (isEyesClosed) {
                        if (isReading) {
                            closedFrames = 0
                            nextState = FocusState.READING_OR_WRITING
                        } else {
                            closedFrames++
                            if (closedFrames >= config.sleepThresholdFrames) {
                                nextState = FocusState.MICRO_SLEEP
                            }
                        }
                    } else {
                        closedFrames = 0
                        if (isReading) {
                            nextState = FocusState.READING_OR_WRITING
                        } else {
                            nextState = FocusState.FOCUSED
                        }
                    }
                }
            }
        }

        metrics.updateTick(nextState, deltaSec)
        onStateChanged(nextState, metrics)
    }

    private fun distance(x1: Float, y1: Float, x2: Float, y2: Float): Float {
        val dx = x1 - x2
        val dy = y1 - y2
        return sqrt(dx * dx + dy * dy)
    }

    fun close() {
        faceLandmarker?.close()
        handLandmarker?.close()
        objectDetector?.close()
        faceLandmarker = null
        handLandmarker = null
        objectDetector = null
    }
}
