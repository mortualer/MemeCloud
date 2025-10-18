[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,mp3
version = 1.2.0
requirements = python3,kivy,requests,android,openssl
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

# Простая иконка
icon.filename = icon.png
presplash.filename = icon.png

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.private_storage = True
android.arch = arm64-v8a

# Отключаем адаптивные иконки для простоты
android.adaptive_icon = False

# Дополнительные настройки
android.accept_sdk_license = True
p4a.branch = develop
android.enable_androidx = True
android.allow_backup = True

# Отключаем AAB, собираем только APK
android.aab = False
