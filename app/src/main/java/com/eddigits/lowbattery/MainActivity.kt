package com.eddigits.lowbattery

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var permissionButton: Button

    private val notificationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) {
            // Notification permission is only for the persistent service
            // notification; monitoring works either way.
            startMonitoringIfAllowed()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.status_text)
        permissionButton = findViewById(R.id.permission_button)

        permissionButton.setOnClickListener {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivity(intent)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            notificationPermissionLauncher.launch(android.Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    override fun onResume() {
        super.onResume()
        startMonitoringIfAllowed()
        updateUi()
    }

    private fun startMonitoringIfAllowed() {
        if (Settings.canDrawOverlays(this)) {
            getSharedPreferences(BootReceiver.PREFS, MODE_PRIVATE)
                .edit()
                .putBoolean(BootReceiver.KEY_ENABLED, true)
                .apply()
            BatteryOverlayService.start(this)
        }
    }

    private fun updateUi() {
        if (Settings.canDrawOverlays(this)) {
            statusText.text = getString(
                R.string.status_active,
                BatteryOverlayService.LOW_BATTERY_THRESHOLD
            )
            permissionButton.isEnabled = false
            permissionButton.text = getString(R.string.permission_granted)
        } else {
            statusText.text = getString(R.string.status_needs_permission)
            permissionButton.isEnabled = true
            permissionButton.text = getString(R.string.grant_permission)
        }
    }
}
