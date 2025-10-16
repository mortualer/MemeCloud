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

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,kivymd,requests,openssl,pillow,android

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
# android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
# android.sdk = 23

# (str) Android NDK version to use
# android.ndk = 23b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
# android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
# android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
# android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
# android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (str) Android logcat filters (by default ok for Kivy-based app)
# android.logcat_filters = *:S python:D

# (str) Android additional adb arguments
# android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (list) Android Android architecture to compile for
# In the past, we had `android.arch = armeabi-v7a arm64-v8a x86 x86_64`
# We now recommend to only keep the one you need and remove the others
android.arch = arm64-v8a

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# android.arch = arm64-v8a

# (str) Android gradle plugin version (default: '4.2.2')
android.gradle_plugin_version = 7.0.0

# (int) Override Android manifest minSdkVersion
# android.minapi = 21

# (int) Override Android manifest targetSdkVersion
# android.api = 30

# (int) Override Android manifest compileSdkVersion
# android.compile_sdk_version = 30

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
# p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
# p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes =

# (str) Filename to the hook for p4a
# p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
# p4a.port =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
# ios.kivy_ios_dir = ../kivy-ios
# Alternately, use the following option if you don't want to clone the kivy-ios repository
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"
# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = %(ios.codesign.debug)s

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

# -----------------------------------------------------------------------------
# List of sections
# -----------------------------------------------------------------------------

# You can define sections to override default [app] sections
# For example, [app:@test] will override [app] for the test section

# -----------------------------------------------------------------------------
# Profiles
# -----------------------------------------------------------------------------

# You can define sections to override default [app] sections for specific profiles
# For example, [app:@debug] will override [app] for the debug profile

# The source directory can be overridden for a specific profile like this:
# source.dir.debug = ./src_debug

# Then, you can specify the application requirements for this profile:
# requirements.debug = kivy, debug_requirement

# The title, package.name and package.domain can also be overridden:
# title.debug = My Application (Debug)
# package.name.debug = myapp
# package.domain.debug = org.test

#
# Run buildozer with a specific profile:
# buildozer --profile debug android debug
