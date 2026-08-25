package com.ononymuos.focussentinel.vision

import kotlin.math.atan2
import kotlin.math.sqrt

/**
 * Solves 3D Head Pose (Pitch, Yaw, Roll) using 3D facial landmarks from MediaPipe.
 * Uses anthropometric facial vectors to extract Euler rotation angles.
 *
 * Negative Pitch = Looking downward (reading/writing notes).
 * Positive Pitch = Looking upward.
 * Yaw = Turning left / right.
 * Roll = Tilting head sideways.
 */
class HeadPoseEstimator {

    data class PoseAngles(
        val pitch: Float, // Down / Up in degrees
        val yaw: Float,   // Left / Right in degrees
        val roll: Float   // Lateral tilt in degrees
    )

    /**
     * MediaPipe Landmark Indices:
     * Nose Tip: 1
     * Chin: 152
     * Left Eye Outer: 33 (or 130)
     * Right Eye Outer: 263 (or 359)
     * Left Mouth: 61
     * Right Mouth: 291
     */
    fun estimatePose(
        noseTip: FloatArray,       // [x, y, z]
        chin: FloatArray,          // [x, y, z]
        leftEyeOuter: FloatArray,  // [x, y, z]
        rightEyeOuter: FloatArray  // [x, y, z]
    ): PoseAngles {
        // Eye midpoint
        val eyeMidX = (leftEyeOuter[0] + rightEyeOuter[0]) / 2f
        val eyeMidY = (leftEyeOuter[1] + rightEyeOuter[1]) / 2f
        val eyeMidZ = (leftEyeOuter[2] + rightEyeOuter[2]) / 2f

        // Vertical face vector: Chin to Eye Midpoint
        val vY = eyeMidY - chin[1]
        val vZ = eyeMidZ - chin[2]
        val vX = eyeMidX - chin[0]

        // Horizontal eye vector: Left eye to Right eye
        val dx = rightEyeOuter[0] - leftEyeOuter[0]
        val dy = rightEyeOuter[1] - leftEyeOuter[1]
        val dz = rightEyeOuter[2] - leftEyeOuter[2]

        // 1. Roll: Angle of eye line on image plane
        val rollRad = atan2(dy.toDouble(), dx.toDouble())
        val rollDeg = Math.toDegrees(rollRad).toFloat()

        // 2. Pitch: Downward/Upward tilt using relative Y vs Z depth displacement
        // Nose projection vs eye-chin vertical vector
        val noseRelY = noseTip[1] - eyeMidY
        val noseRelZ = noseTip[2] - eyeMidZ
        val pitchRad = atan2(noseRelY.toDouble(), -noseRelZ.toDouble() * 1.5 + 0.001)
        var pitchDeg = Math.toDegrees(pitchRad).toFloat()

        // Normalization against vertical face height
        val faceHeight = sqrt((chin[1] - eyeMidY) * (chin[1] - eyeMidY) + (chin[2] - eyeMidZ) * (chin[2] - eyeMidZ))
        val normY = (noseTip[1] - (chin[1] + eyeMidY) / 2f) / (faceHeight + 0.001f)
        pitchDeg = normY * 75f // Calibrated baseline degrees

        // 3. Yaw: Left / Right rotation using nose horizontal displacement relative to eyes
        val eyeDist = sqrt(dx * dx + dy * dy + dz * dz)
        val noseToLeft = sqrt((noseTip[0] - leftEyeOuter[0]) * (noseTip[0] - leftEyeOuter[0]) + (noseTip[1] - leftEyeOuter[1]) * (noseTip[1] - leftEyeOuter[1]))
        val noseToRight = sqrt((noseTip[0] - rightEyeOuter[0]) * (noseTip[0] - rightEyeOuter[0]) + (noseTip[1] - rightEyeOuter[1]) * (noseTip[1] - rightEyeOuter[1]))
        val yawRatio = (noseToRight - noseToLeft) / (eyeDist + 0.001f)
        val yawDeg = (yawRatio * 65f).coerceIn(-90f, 90f)

        return PoseAngles(
            pitch = pitchDeg,
            yaw = yawDeg,
            roll = rollDeg
        )
    }
}
