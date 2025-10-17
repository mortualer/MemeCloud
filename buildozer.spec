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

# Иконки - УБЕДИТЕСЬ ЧТО ФАЙЛЫ СУЩЕСТВУЮТ
icon.filename = icon.png
presplash.filename = icon.png

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.sdk = 24
android.ndk = 25b
android.private_storage = True
android.arch = arm64-v8a

# Отключаем сложные настройки иконок
android.adaptive_icon = False

# Важные настройки для сборки
android.accept_sdk_license = True
p4a.branch = develop
android.enable_androidx = True
