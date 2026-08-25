package com.ononymuos.focussentinel.ui.screens

import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.ononymuos.focussentinel.core.FocusState
import com.ononymuos.focussentinel.core.SentinelConfig
import com.ononymuos.focussentinel.core.SessionMetrics
import com.ononymuos.focussentinel.ui.components.SettingsDialog
import com.ononymuos.focussentinel.ui.theme.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*

@Composable
fun MainScreen(
    state: FocusState,
    metrics: SessionMetrics,
    config: SentinelConfig,
    onConfigUpdated: (SentinelConfig) -> Unit,
    onToggleMute: (Boolean) -> Unit,
    onToggleCamera: () -> Unit,
    onPreviewAvailable: (PreviewView) -> Unit,
    onPickAudio: (alarmType: String) -> Unit,
    onTestAudio: (customPath: String?, defaultKey: String) -> Unit
) {
    var showSettings by remember { mutableStateOf(false) }

    if (showSettings) {
        SettingsDialog(
            config = config,
            onDismiss = { showSettings = false },
            onSave = {
                onConfigUpdated(it)
                showSettings = false
            },
            onPickAudio = onPickAudio,
            onTestAudio = onTestAudio
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Status Banner
        val bannerColor = when (state) {
            FocusState.FOCUSED -> PrimaryEmerald
            FocusState.READING_OR_WRITING -> WarningOrange
            FocusState.MICRO_SLEEP -> AlertCrimson
            FocusState.FACE_ABSENT -> InactiveGray
            FocusState.PHONE_DISTRACTION -> AlertCrimson
        }
        val bannerText = when (state) {
            FocusState.FOCUSED -> "FOCUS: ACTIVE"
            FocusState.READING_OR_WRITING -> "MODE: READING / STUDYING"
            FocusState.MICRO_SLEEP -> "ALERT: DROWSINESS DETECTED"
            FocusState.FACE_ABSENT -> "ALERT: USER ABSENT"
            FocusState.PHONE_DISTRACTION -> "ALERT: PHONE DETECTED"
        }

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(8.dp))
                .background(bannerColor.copy(alpha = 0.2f))
                .padding(16.dp),
            contentAlignment = Alignment.Center
        ) {
            Text(text = bannerText, color = bannerColor, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleLarge)
        }

        // Live Camera Preview & Controls (takes remaining top space)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(12.dp))
                .background(CardSurface)
        ) {
            AndroidView(
                factory = { ctx ->
                    PreviewView(ctx).apply {
                        scaleType = PreviewView.ScaleType.FILL_CENTER
                        onPreviewAvailable(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
            
            // Overlay Top Controls (Settings)
            IconButton(
                onClick = { showSettings = true },
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(12.dp)
                    .background(BackgroundDark.copy(alpha=0.6f), RoundedCornerShape(50))
            ) {
                Icon(
                    imageVector = Icons.Default.Settings,
                    contentDescription = "Settings",
                    tint = AccentCyan
                )
            }

            // Overlay Bottom Controls
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .align(Alignment.BottomCenter)
                    .padding(12.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                IconButton(
                    onClick = { onToggleMute(!config.audioMuted) }, 
                    modifier = Modifier.background(BackgroundDark.copy(alpha=0.6f), RoundedCornerShape(50))
                ) {
                    Icon(
                        imageVector = if (config.audioMuted) Icons.Default.VolumeOff else Icons.Default.VolumeUp,
                        contentDescription = "Toggle Mute",
                        tint = TextPrimary
                    )
                }
                IconButton(
                    onClick = { onToggleCamera() }, 
                    modifier = Modifier.background(BackgroundDark.copy(alpha=0.6f), RoundedCornerShape(50))
                ) {
                    Icon(
                        imageVector = Icons.Default.Cameraswitch,
                        contentDescription = "Switch Camera",
                        tint = TextPrimary
                    )
                }
            }
        }

        // Metrics Grid
        Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
            MetricCard("Focus Score", "${metrics.focusScore.toInt()}%", Modifier.weight(1f))
            MetricCard("Elapsed", "${(metrics.elapsedSeconds / 60).toInt()}m", Modifier.weight(1f))
        }

        Row(horizontalArrangement = Arrangement.spacedBy(16.dp), modifier = Modifier.fillMaxWidth()) {
            MetricCard("Eye Ratio (EAR)", String.format("%.1f%%", metrics.currentEyeRatio), Modifier.weight(1f))
            MetricCard("Pitch Angle", String.format("%.1f°", metrics.currentPitch), Modifier.weight(1f))
        }
        
        Text("FocusSentinel AI • © 2026 Usama Baig", color = TextMuted, style = MaterialTheme.typography.bodySmall, modifier = Modifier.align(Alignment.CenterHorizontally))
    }
}

@Composable
fun MetricCard(title: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(CardSurface)
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = title, color = TextSecondary, style = MaterialTheme.typography.bodyMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = value, color = TextPrimary, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
    }
}
