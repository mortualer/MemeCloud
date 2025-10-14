[app]
# (str) Title of your application
title = MemeCloud

# (str) Package name
package.name = memecloud

# (str) Package domain (use your domain name)
package.domain = org.memecloud

# (str) Source code where the main.py live
source.dir = .

# (str) Application version
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Name of the kivy bootstrap to use
bootstrap = sdl2

# (str) Android NDK path (set automatically by Buildozer in GitHub Actions)
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r26b

# (str) Android SDK path (set automatically by Buildozer in GitHub Actions)
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk

# (int) Minimum Android API level
android.minapi = 21

# (int) Target Android API level
android.api = 33

# (bool) Use Android studio to compile
android.use_android_studio = true

# (bool) Use the latest version of Android NDK
android.use_latest_ndk = true

# (str) Android NDK version (if not using the latest version)
android.ndk_version = r25b

# (str) Path to the Android SDK
android.sdk_version = 33

# (str) Android API level
#android.api = 33

# (list) Android permissions
# e.g. android.permissions = INTERNET
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (list) Pattern to whitelist for inclusion in the APK
# e.g. android.whitelist = lib/*, assets/*, etc.
android.whitelist = 

# (list) Pattern to blacklist for exclusion from the APK
android.blacklist = 

# (bool) Copy libraries that are used in the app (default is False)
android.copylibs = True

# (str) Android NDK API level
android.ndk_api = 21

# (bool) Build for all architectures (default is False)
android.archs = armeabi-v7a, arm64-v8a
