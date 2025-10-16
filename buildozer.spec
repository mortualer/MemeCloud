[app]

# (str) Title of your application
title = MemeCloud

# (str) Package name
package.name = memecloud

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mortualer

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,txt,ttf,otf

icon.filename = %(source.dir)s/icon.jpg

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# ОСНОВНЫЕ ДЛЯ РАБОТЫ ПРИЛОЖЕНИЯ:
requirements = python3,kivy,requests,openssl,android,pyjnius

# (str) Presplash of the application (экран загрузки)
# presplash.filename = %(source.dir)s/presplash.png

# (str) Icon of the application (иконка)
# icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions (РАЗРЕШЕНИЯ - ОБЯЗАТЕЛЬНЫЕ)
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) Android architecture to compile for
android.archs = arm64-v8a, armeabi-v7a

# (str) Android gradle plugin version
android.gradle_plugin_version = 7.0.0

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

#
# Buildozer settings
#

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
