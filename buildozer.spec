[app]
# (str) Title of your application
title = MemeCloud

# (str) Package name
package.name = memecloud

# (str) Package domain (unique)
package.domain = org.example

# (str) Source code where the main.py is located
source.dir = .

# (str) Application version
version = 1.0

# (list) Application requirements
# Добавил hostpython3 для корректной сборки в CI
requirements = python3,kivy,hostpython3

# (str) Supported orientations
orientation = portrait

# (list) Permissions required by the app
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (str) Icon for the app
icon.filename = %(source.dir)s/icon.png

# (str) Supported Android architectures
android.archs = arm64-v8a, armeabi-v7a

# (int) Minimum Android API your app requires
android.minapi = 21

# (int) Target Android API
android.api = 33

# (int) Android SDK Build Tools version
android.build_tools_version = 33.0.2

# (str) NDK version — стабильная версия r25b
android.ndk = 25.1.8937393

# (int) NDK API level
android.ndk_api = 21

# (str) Bootstrap to use for packaging
android.bootstrap = sdl2

# (bool) Copy libraries instead of using shared
android.copy_libs = 1

# (bool) Include source in the APK
android.include_src = 1

# (bool) Enable debug mode
log_level = 2

# (bool) Warn if running as root
warn_on_root = 1

# (str) Disable local p4a recipes
p4a.local_recipes =

# (str) Presplash image
presplash.filename = %(source.dir)s/presplash.png

# (str) Application icon for Android
android.icon = %(source.dir)s/icon.png

# (str) Additional arguments for p4a
# ускоряет сборку и фиксит проблемы с hostpython
p4a.extra_args = --storage-dir=~/.buildozer/android/platform/build
