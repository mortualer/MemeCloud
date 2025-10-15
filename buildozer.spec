[app]
title = MemeCloud
package.name = memecloud
package.domain = org.memecloud
source.dir = .
version = 1.0
requirements = python3,kivy,kivymd,pillow
orientation = portrait
fullscreen = 0
log_level = 2

[buildozer]
android.archs = arm64-v8a, armeabi-v7a
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 27b
android.ndk_api = 21
android.bootstrap = sdl2
