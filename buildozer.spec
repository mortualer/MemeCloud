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
requirements = python3,kivy

# (str) Entry point for your app
entrypoint = main.py

# (str) Supported orientations: landscape, portrait, all
orientation = portrait

# (list) Permissions required by the app
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (str) Icon for the app (optional)
icon.filename = %(source.dir)s/icon.png

# (str) Supported Android architectures
android.archs = arm64-v8a, armeabi-v7a

# (int) Minimum Android API your app requires
android.minapi = 21

# (int) Target Android API
android.api = 33

# (int) Android SDK Build Tools version
android.build_tools_version = 33.0.2

# (str) NDK version
android.ndk = 27b

# (int) NDK API level
android.ndk_api = 21

# (str) Bootstrap to use for packaging
android.bootstrap = sdl2

# (bool) Copy libraries instead of using shared
android.copy_libs = 1

# (str) Presplash image
presplash.filename = %(source.dir)s/presplash.png

# (str) Application icon for Android
android.icon = %(source.dir)s/icon.png

# (bool) Include source in the APK
android.include_src = 1

# (bool) Enable debug mode
log_level = 2
