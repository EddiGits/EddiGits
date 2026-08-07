package com.eddigits.lowbattery

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Settings

/**
 * Restarts battery monitoring after a reboot, so the low-battery bar keeps
 * working without the user having to reopen the app.
 */
class BootReceiver : BroadcastReceiver() {

    companion object {
        const val PREFS = "low_battery_prefs"
        const val KEY_ENABLED = "monitoring_enabled"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return

        val enabled = context
            .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getBoolean(KEY_ENABLED, false)

        if (enabled && Settings.canDrawOverlays(context)) {
            BatteryOverlayService.start(context)
        }
    }
}
