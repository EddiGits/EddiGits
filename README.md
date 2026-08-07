# Low Battery Indication

An Android app that shows an **always-visible red warning bar** across the top of the
screen — over any app you're using — whenever the battery drops **below 10%**, in the
spirit of the colored status-bar warnings from the Android Lollipop / Marshmallow days.

## How it behaves

- 🔴 The red bar (`⚠ LOW BATTERY — X% — PLEASE CHARGE`) appears **automatically** as soon
  as the battery level goes below 10% while not charging.
- ✅ The bar disappears **automatically** when you plug in the charger, or when the level
  rises back to 10% or above.
- 🔁 Monitoring survives reboots (starts again on boot once you've opened the app and
  granted the permission).

## How it works

- A small **foreground service** (`BatteryOverlayService`) listens to the system
  `ACTION_BATTERY_CHANGED` / power-connected / power-disconnected broadcasts.
- When the level is below the threshold and the device isn't charging, it draws a red bar
  as a **system overlay window** (`TYPE_APPLICATION_OVERLAY`) pinned to the top of the
  screen, on top of whatever app is open. The bar is non-interactive, so it never blocks
  touches.
- The service runs with a minimal-priority persistent notification so Android keeps it
  alive in the background.

## Setup on your phone

1. Install the APK (build it yourself, or grab the artifact from the GitHub Actions
   **Build APK** workflow run).
2. Open the app once and tap **Grant overlay permission** — this is the standard
   "Display over other apps" permission the bar needs.
3. Done. The service starts automatically; there's nothing else to configure.

> Tip: on some devices (Xiaomi, Samsung, etc.) you may also want to exclude the app from
> aggressive battery optimization so the system doesn't kill the monitoring service.

## Building

Requires JDK 17 and the Android SDK (compileSdk 34).

```bash
./gradlew assembleDebug
# APK lands in app/build/outputs/apk/debug/app-debug.apk
```

Or just push to GitHub — the included workflow builds the debug APK on every push and
uploads it as a downloadable artifact.

## Configuration

The threshold lives in one place: `LOW_BATTERY_THRESHOLD` in
[`BatteryOverlayService.kt`](app/src/main/java/com/eddigits/lowbattery/BatteryOverlayService.kt)
(default `10`). The bar color/height/text are in the same file and in
[`strings.xml`](app/src/main/res/values/strings.xml).
