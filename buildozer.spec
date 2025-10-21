[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,mp3,wav,ogg
source.include_dirs = saved_sounds
version = 1.2.0
requirements = python3,kivy,requests,openssl,android,androidstorage4kivy
orientation = portrait
fullscreen = 0

# Иконки
icon.filename = ic_launcher.png
android.adaptive_icon.foreground = android/res/mipmap-anydpi-v26/ic_launcher_foreground.png
android.adaptive_icon.background = android/res/mipmap-anydpi-v26/ic_launcher_background.png
android.adaptive_icon.monochrome = android/res/mipmap-anydpi-v26/ic_launcher_monochrome.png

# Splash
#presplash.filename = android/res/mipmap-hdpi/ic_launcher.png

[buildozer]
log_level = 2
android.add_resource = saved_sounds, android/res

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO,READ_MEDIA_IMAGES
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.private_storage = True
android.arch = arm64-v8a
p4a.branch = stable
android.enable_androidx = True
android.allow_backup = True
android.release_artifact = True

android.manifest.intent_filters = <application android:icon="@mipmap/ic_launcher" android:roundIcon="@mipmap/ic_launcher_round" />
android.gradle_dependencies = com.android.tools.build:gradle:8.5.0
