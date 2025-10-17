[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
version = 1.0.0
requirements = python3,kivy,requests,openssl,android
orientation = portrait
fullscreen = 0

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.jpg

# (str) Presplash of the application (экран загрузки)

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
