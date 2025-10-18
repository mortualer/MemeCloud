[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,mp3
version = 1.2.0
requirements = python3,kivy,requests,android
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

# Адаптивные иконки
icon.filename = icon.png
#android.adaptive_icon_foreground = icon-foreground.png
#android.adaptive_icon_background = icon-background.png
presplash.filename = icon.png

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.private_storage = True
android.arch = arm64-v8a, armeabi-v7a

# Включаем адаптивные иконки
#android.adaptive_icon = True

# Дополнительные настройки
android.accept_sdk_license = True
p4a.branch = develop
android.enable_androidx = True
android.allow_backup = True

# Отключаем AAB, собираем только APK
android.aab = False

# Оптимизация сборки
android.release_artifact = .apk
