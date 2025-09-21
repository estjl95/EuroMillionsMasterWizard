[app]
title = EuroMillions Master Wizard
package.name = euromillionswizard
package.domain = org.joseedu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 1
icon.filename = icon.png
presplash.filename = presplash.png
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = False
android.manifest.intent_filters = \
    <intent-filter> \
        <action android:name="android.intent.action.MAIN" /> \
        <category android:name="android.intent.category.LAUNCHER" /> \
    </intent-filter>

[buildozer]
log_level = 2
warn_on_root = 1