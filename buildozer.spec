[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

requirements = python3,kivy
orientation = portrait
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.ndk = 27b
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 0
