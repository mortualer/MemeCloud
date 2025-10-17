[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.2.0
requirements = python3,kivy,requests,openssl,android
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

# Иконки
icon.filename = %(source.dir)s/icon.png
android.adaptive_icon_foreground = %(source.dir)s/icon-foreground.png
android.adaptive_icon_background = %(source.dir)s/icon-background.png

# Заставка
presplash.filename = %(source.dir)s/icon.png

# Android настройки
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
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

# ВАЖНО: Принудительно отключить AAB
android.aab = yes
