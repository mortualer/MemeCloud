[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,mp3,wav,ogg,xml
source.exclude_dirs = tests, bin, ios, web

# ИСПРАВЛЕНО: убрали запятую в конце и добавили xml
source.include_patterns = saved_sounds/*,android/res/*

version = 1.3.1
android.version_code = 10300
requirements = python3,kivy,requests,openssl,android,androidstorage4kivy
orientation = portrait
fullscreen = 0


icon.filename = ic_launcher.png

android.adaptive_icon = android/res/mipmap-anydpi-v26/ic_launcher.xml
android.adaptive_icon_foreground = android/res/mipmap-anydpi-v26/ic_launcher_foreground.png
android.adaptive_icon_background = android/res/mipmap-anydpi-v26/ic_launcher_background.png
android.adaptive_icon_monochrome = android/res/mipmap-anydpi-v26/ic_launcher_monochrome.png

# Splash - ИСПРАВЛЕНО (xxxhdpi вместо xxxdpi)
presplash.filename = android/res/mipmap-xxxhdpi/ic_launcher.png

[buildozer]
log_level = 2
# ИСПРАВЛЕНО: правильный формат
android.add_resources = saved_sounds, android/res

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO
# УБРАТЬ READ_MEDIA_IMAGES если не работаете с изображениями

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

# ИСПРАВЛЕНО: убрали дублирование из intent_filters
#android.manifest_application_arguments = --icon @mipmap/ic_launcher --roundIcon @mipmap/ic_launcher_round


android.gradle_dependencies = com.android.tools.build:gradle:8.5.0
