package com.ononymuos.focussentinel.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.ononymuos.focussentinel.core.SentinelConfig
import com.ononymuos.focussentinel.ui.theme.*
import java.io.File

@Composable
fun SettingsDialog(
    config: SentinelConfig,
    onDismiss: () -> Unit,
    onSave: (SentinelConfig) -> Unit,
    onPickAudio: (alarmType: String) -> Unit,
    onTestAudio: (customPath: String?, defaultKey: String) -> Unit
) {
    var eyeRatio by remember { mutableFloatStateOf(config.eyeRatioThreshold) }
    var readingPitch by remember { mutableFloatStateOf(config.readingPitchThreshold) }
    var sleepFrames by remember { mutableFloatStateOf(config.sleepThresholdFrames.toFloat()) }
    var absenceFrames by remember { mutableFloatStateOf(config.faceCoverThresholdFrames.toFloat()) }
    var phoneConfidence by remember { mutableFloatStateOf(config.phoneConfidenceThreshold) }
    var phoneFrames by remember { mutableFloatStateOf(config.phoneThresholdFrames.toFloat()) }
    var volume by remember { mutableFloatStateOf(config.audioVolume) }
    var haptics by remember { mutableStateOf(config.hapticsEnabled) }
    var backgroundMonitor by remember { mutableStateOf(config.runInBackground) }

    var sleepPath by remember { mutableStateOf(config.customSleepSoundPath) }
    var absencePath by remember { mutableStateOf(config.customAbsenceSoundPath) }
    var phonePath by remember { mutableStateOf(config.customPhoneSoundPath) }

    LaunchedEffect(config.customSleepSoundPath, config.customAbsenceSoundPath, config.customPhoneSoundPath) {
        sleepPath = config.customSleepSoundPath
        absencePath = config.customAbsenceSoundPath
        phonePath = config.customPhoneSoundPath
    }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(0.95f)
                .fillMaxHeight(0.90f)
                .clip(RoundedCornerShape(16.dp))
                .background(SurfaceDark)
                .padding(20.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
            ) {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Icon(Icons.Default.Tune, contentDescription = null, tint = AccentCyan)
                        Text(
                            text = "SENTINEL CONFIG",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimary
                        )
                    }
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close", tint = TextSecondary)
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // SECTION 1: Custom Audio Pickers
                Text("CUSTOM ALERTS & AUDIO", color = AccentCyan, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                AudioPickerItem(
                    title = "Micro-Sleep / Drowsiness Alarm",
                    filePath = sleepPath,
                    defaultName = "Default (sleep_alarm.mp3)",
                    onPick = { onPickAudio("sleep") },
                    onReset = {
                        sleepPath = null
                        config.customSleepSoundPath = null
                    },
                    onTest = { onTestAudio(sleepPath, "sleep") }
                )

                Spacer(modifier = Modifier.height(8.dp))

                AudioPickerItem(
                    title = "Absence / Face Hidden Alarm",
                    filePath = absencePath,
                    defaultName = "Default (face_hidden.mp3)",
                    onPick = { onPickAudio("absence") },
                    onReset = {
                        absencePath = null
                        config.customAbsenceSoundPath = null
                    },
                    onTest = { onTestAudio(absencePath, "face_hidden") }
                )

                Spacer(modifier = Modifier.height(8.dp))

                AudioPickerItem(
                    title = "Phone Distraction Alarm",
                    filePath = phonePath,
                    defaultName = "Default (phone_alert.mp3)",
                    onPick = { onPickAudio("phone") },
                    onReset = {
                        phonePath = null
                        config.customPhoneSoundPath = null
                    },
                    onTest = { onTestAudio(phonePath, "phone") }
                )

                Spacer(modifier = Modifier.height(16.dp))

                // SECTION 2: Volume & Haptics
                Text("VOLUME & FEEDBACK", color = AccentCyan, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                Text("Alert Volume: ${(volume * 100).toInt()}%", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                Slider(
                    value = volume,
                    onValueChange = { volume = it },
                    valueRange = 0.0f..1.0f,
                    colors = SliderDefaults.colors(thumbColor = AccentCyan, activeTrackColor = AccentCyan)
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Vibration Haptics", color = TextPrimary)
                    Switch(
                        checked = haptics,
                        onCheckedChange = { haptics = it },
                        colors = SwitchDefaults.colors(checkedThumbColor = AccentCyan, checkedTrackColor = AccentCyan.copy(alpha = 0.5f))
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("Background Foreground Monitoring", color = TextPrimary)
                    Switch(
                        checked = backgroundMonitor,
                        onCheckedChange = { backgroundMonitor = it },
                        colors = SwitchDefaults.colors(checkedThumbColor = AccentCyan, checkedTrackColor = AccentCyan.copy(alpha = 0.5f))
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // SECTION 3: Sensitivity Calibration
                Text("DETECTION SENSITIVITY", color = AccentCyan, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(8.dp))

                Text("Phone Detection Confidence: ${(phoneConfidence * 100).toInt()}%", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                Slider(
                    value = phoneConfidence,
                    onValueChange = { phoneConfidence = it },
                    valueRange = 0.20f..0.80f,
                    colors = SliderDefaults.colors(thumbColor = AccentCyan, activeTrackColor = AccentCyan)
                )

                Text("Eye Aspect Ratio (EAR) Cutoff: ${String.format("%.1f", eyeRatio)}%", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                Slider(
                    value = eyeRatio,
                    onValueChange = { eyeRatio = it },
                    valueRange = 5.0f..20.0f,
                    colors = SliderDefaults.colors(thumbColor = PrimaryEmerald, activeTrackColor = PrimaryEmerald)
                )

                Text("Reading Pitch Angle: ${readingPitch.toInt()}°", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                Slider(
                    value = readingPitch,
                    onValueChange = { readingPitch = it },
                    valueRange = -30.0f..0.0f,
                    colors = SliderDefaults.colors(thumbColor = WarningOrange, activeTrackColor = WarningOrange)
                )

                Text("Sleep Trigger Delay: ${(sleepFrames / 30.0).toString().take(3)}s", color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
                Slider(
                    value = sleepFrames,
                    onValueChange = { sleepFrames = it },
                    valueRange = 15.0f..90.0f,
                    colors = SliderDefaults.colors(thumbColor = AlertCrimson, activeTrackColor = AlertCrimson)
                )

                Spacer(modifier = Modifier.height(24.dp))

                // Action Buttons
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text("CANCEL", color = TextSecondary)
                    }
                    Button(
                        onClick = {
                            val updated = config.copy(
                                eyeRatioThreshold = eyeRatio,
                                readingPitchThreshold = readingPitch,
                                sleepThresholdFrames = sleepFrames.toInt(),
                                faceCoverThresholdFrames = absenceFrames.toInt(),
                                phoneConfidenceThreshold = phoneConfidence,
                                phoneThresholdFrames = phoneFrames.toInt(),
                                audioVolume = volume,
                                hapticsEnabled = haptics,
                                customSleepSoundPath = sleepPath,
                                customAbsenceSoundPath = absencePath,
                                customPhoneSoundPath = phonePath,
                                runInBackground = backgroundMonitor
                            )
                            onSave(updated)
                            onDismiss()
                        },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(8.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = AccentCyan)
                    ) {
                        Text("SAVE CHANGES", color = BackgroundDark, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@Composable
fun AudioPickerItem(
    title: String,
    filePath: String?,
    defaultName: String,
    onPick: () -> Unit,
    onReset: () -> Unit,
    onTest: () -> Unit
) {
    val displayName = if (filePath != null) File(filePath).name else defaultName
    val isCustom = filePath != null

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(8.dp))
            .background(CardSurface)
            .padding(12.dp)
    ) {
        Text(text = title, color = TextPrimary, fontWeight = FontWeight.SemiBold, style = MaterialTheme.typography.bodyMedium)
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = displayName,
            color = if (isCustom) PrimaryEmerald else TextMuted,
            style = MaterialTheme.typography.bodySmall,
            maxLines = 1
        )
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = onPick,
                shape = RoundedCornerShape(6.dp),
                colors = ButtonDefaults.buttonColors(containerColor = AccentCyan.copy(alpha = 0.2f)),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
            ) {
                Icon(Icons.Default.AudioFile, contentDescription = null, tint = AccentCyan, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Choose Audio", color = AccentCyan, style = MaterialTheme.typography.labelMedium)
            }
            OutlinedButton(
                onClick = onTest,
                shape = RoundedCornerShape(6.dp),
                contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null, tint = TextPrimary, modifier = Modifier.size(16.dp))
                Spacer(modifier = Modifier.width(4.dp))
                Text("Test", color = TextPrimary, style = MaterialTheme.typography.labelMedium)
            }
            if (isCustom) {
                IconButton(onClick = onReset, modifier = Modifier.size(32.dp)) {
                    Icon(Icons.Default.DeleteOutline, contentDescription = "Reset to default", tint = AlertCrimson, modifier = Modifier.size(18.dp))
                }
            }
        }
    }
}
