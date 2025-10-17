[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
version = 1.0.0
requirements = python3,kivy,requests,openssl,android
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]
log_level = 2
