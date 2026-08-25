package com.ononymuos.focussentinel.core

import android.content.Context
import android.content.SharedPreferences

data class SentinelConfig(
    var eyeRatioThreshold: Float = 11.0f,         // EAR Cutoff (%)
    var readingPitchThreshold: Float = -10.0f,    // Pitch in degrees (< -10 = looking down into notebook)
    var sleepThresholdFrames: Int = 30,          // ~1.0-1.5s at 30 FPS
    var faceCoverThresholdFrames: Int = 60,      // ~2.0-3.0s at 30 FPS
    var phoneConfidenceThreshold: Float = 0.35f, // Object detector confidence threshold for phone
    var phoneThresholdFrames: Int = 8,           // Consecutive/accumulated frames to trigger phone alert

    // Audio & Haptics
    var audioMuted: Boolean = false,
    var audioVolume: Float = 0.85f,
    var hapticsEnabled: Boolean = true,

    // Custom Audio File Paths (null = default built-in sounds)
    var customSleepSoundPath: String? = null,
    var customAbsenceSoundPath: String? = null,
    var customPhoneSoundPath: String? = null,

    // Visual HUD & Overlay
    var showHud: Boolean = true,
    var showMeshWireframe: Boolean = true,
    var showFaceBoundingBox: Boolean = true,
    var runInBackground: Boolean = true
) {
    companion object {
        private const val PREFS_NAME = "focus_sentinel_prefs"

        fun load(context: Context): SentinelConfig {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            return SentinelConfig(
                eyeRatioThreshold = prefs.getFloat("eyeRatioThreshold", 11.0f),
                readingPitchThreshold = prefs.getFloat("readingPitchThreshold", -10.0f),
                sleepThresholdFrames = prefs.getInt("sleepThresholdFrames", 30),
                faceCoverThresholdFrames = prefs.getInt("faceCoverThresholdFrames", 60),
                phoneConfidenceThreshold = prefs.getFloat("phoneConfidenceThreshold", 0.35f),
                phoneThresholdFrames = prefs.getInt("phoneThresholdFrames", 8),
                audioMuted = prefs.getBoolean("audioMuted", false),
                audioVolume = prefs.getFloat("audioVolume", 0.85f),
                hapticsEnabled = prefs.getBoolean("hapticsEnabled", true),
                customSleepSoundPath = prefs.getString("customSleepSoundPath", null),
                customAbsenceSoundPath = prefs.getString("customAbsenceSoundPath", null),
                customPhoneSoundPath = prefs.getString("customPhoneSoundPath", null),
                runInBackground = prefs.getBoolean("runInBackground", true)
            )
        }
    }

    fun save(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit()
            .putFloat("eyeRatioThreshold", eyeRatioThreshold)
            .putFloat("readingPitchThreshold", readingPitchThreshold)
            .putInt("sleepThresholdFrames", sleepThresholdFrames)
            .putInt("faceCoverThresholdFrames", faceCoverThresholdFrames)
            .putFloat("phoneConfidenceThreshold", phoneConfidenceThreshold)
            .putInt("phoneThresholdFrames", phoneThresholdFrames)
            .putBoolean("audioMuted", audioMuted)
            .putFloat("audioVolume", audioVolume)
            .putBoolean("hapticsEnabled", hapticsEnabled)
            .putString("customSleepSoundPath", customSleepSoundPath)
            .putString("customAbsenceSoundPath", customAbsenceSoundPath)
            .putString("customPhoneSoundPath", customPhoneSoundPath)
            .putBoolean("runInBackground", runInBackground)
            .apply()
    }
}
