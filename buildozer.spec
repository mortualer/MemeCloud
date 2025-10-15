[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,ogg,ttf,json
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.accept_sdk_license = True
log_level = 2
p4a.bootstrap = sdl2
p4a.local_recipes = 
android.release_artifact_dir = bin
android.debug_artifact_dir = bin
icon.filename = icon.png
presplash.filename = presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
