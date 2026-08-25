package com.ononymuos.focussentinel.core

class SessionMetrics {
    var sessionStartTimeMs: Long = 0L
    var totalFocusSeconds: Double = 0.0
    var totalReadingSeconds: Double = 0.0
    var totalDistractedSeconds: Double = 0.0

    var sleepEventsCount: Int = 0
    var absenceEventsCount: Int = 0
    var phoneEventsCount: Int = 0

    var currentState: FocusState = FocusState.FOCUSED
    var currentPitch: Float = 0.0f
    var currentYaw: Float = 0.0f
    var currentRoll: Float = 0.0f
    var currentEyeRatio: Float = 0.0f

    fun start() {
        sessionStartTimeMs = System.currentTimeMillis()
        totalFocusSeconds = 0.0
        totalReadingSeconds = 0.0
        totalDistractedSeconds = 0.0
        sleepEventsCount = 0
        absenceEventsCount = 0
        phoneEventsCount = 0
    }

    fun updateTick(state: FocusState, deltaSec: Double) {
        currentState = state
        when (state) {
            FocusState.FOCUSED -> totalFocusSeconds += deltaSec
            FocusState.READING_OR_WRITING -> totalReadingSeconds += deltaSec
            FocusState.MICRO_SLEEP -> {
                totalDistractedSeconds += deltaSec
            }
            FocusState.FACE_ABSENT -> {
                totalDistractedSeconds += deltaSec
            }
            FocusState.PHONE_DISTRACTION -> {
                totalDistractedSeconds += deltaSec
            }
        }
    }

    val elapsedSeconds: Double
        get() {
            if (sessionStartTimeMs == 0L) return 0.0
            return (System.currentTimeMillis() - sessionStartTimeMs) / 1000.0
        }

    val focusScore: Float
        get() {
            val total = elapsedSeconds
            if (total <= 0.0) return 100.0f
            val productive = totalFocusSeconds + totalReadingSeconds
            val score = (productive / total) * 100.0
            return score.coerceIn(0.0, 100.0).toFloat()
        }
}
