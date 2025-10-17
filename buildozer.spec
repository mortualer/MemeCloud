[app]
title = MemeCloud
package.name = memecloud
package.domain = org.mortualer
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.2.0
requirements = python3,kivy,requests,openssl,android
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.3.0
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.jpg

# (str) Presplash of the application
presplash.filename = %(source.dir)s/presplash.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the project.properties automatically.)
#android.library_references =

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (str) python-for-android branch to use, defaults to stable
p4a.branch = stable

# (str) OUYA Console category. For example: GAME or APP
# If you leave this blank, OUYA support will not be enabled
#android.ouya.category = GAME

# (str) Filename of the keystore for signing the release apk
# android.keystore.path =

# (str) Keystore password
# android.keystore.password =

# (str) Key alias
# android.keystore.alias =

# (str) Key password
# android.keystore.alias_password =

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (list) Application initialization
# (list) Garden requirements
#garden_requirements =

# (str) A extra include dir for e.g. olefile
# extra_include_dirs =

# (list) Extra java classes to add as to the main Activity
# android.extra_java_classes =

# (list) Extra jar files to add to the libs so that pyjnius can access them
# android.extra_jars =

# (bool) If true, then skip trying to update the Android sdk
# This can be useful to avoid an Internet connection for unsupported sdk versions
# android.skip_update = False

# (bool) If true, then automatically accept SDK license
# agreements. This is intended for automation only. If set to false,
# the default, you will be shown the license when first running
# buildozer.
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based apps
# android.entrypoint = org.renpy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based apps
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access them
# android.add_jars = foo.jar,bar.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
# android.add_src =

# (list) Android AAR archives to add
# android.add_aars =

# (list) Gradle dependencies to add
# android.gradle_dependencies =

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package.
# android.enable_androidx requires android.api >= 28
android.enable_androidx = True

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# please enclose in double quotes 
# e.g. android.gradle_repositories = "maven { url 'https://kotlin.bintray.com/ktor' }"
#android.add_gradle_repositories =

# (list) packaging options to add 
# see https://google.github.io/android-gradle-dsl/current/com.android.build.gradle.internal.dsl.PackagingOptions.html
# can be necessary to solve conflicts in gradle_dependencies
# please enclose in double quotes 
# e.g. android.add_packaging_options = "exclude 'META-INF/common.kotlin_module'", "exclude 'META-INF/*.kotlin_module'"
#android.add_packaging_options =

# (list) Java classes to add as activities to the manifest.
#android.add_activities = com.example.ExampleActivity

# (str) SMali debug features to enable
# See https://developer.android.com/studio/debug/smali#smali-debugging-features
# Can be necessary to solve conflicts in gradle_dependencies
# "deprecated-ids", "not-forwarded", "normal-virtual", "static-fields", "instance-fields", "normal-virtual"
#android.smali_debug_features = deprecated-ids

# (str) launchMode to set for the main activity
#android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
#android.add_libs_armeabi = libs/android/*.so
#android.add_libs_armeabi_v7a = libs/android-v7/*.so
#android.add_libs_arm64_v8a = libs/android-v8/*.so
#android.add_libs_x86 = libs/android-x86/*.so
#android.add_libs_x86_64 = libs/android-x86_64/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
#android.wakelock = False

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the project.properties automatically.)
#android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library =

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (int) overrides automatic versionCode computation (used in build.gradle)
# this is not the same as app version and should only be edited if you know what you're doing
# android.numeric_version = 1

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for custom backup rules (see official auto backup documentation)
# android.backup_rules =

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do so with the manifestPlaceholders property.
# This property takes a map of key-value pairs. (via a string)
# Usage example : android.manifest_placeholders = [myCustomUrl:\"org.kivy.customurl\"]
# android.manifest_placeholders = [:]

# (bool) Skip byte compile for .py files
# android.no-byte-compile-python = false

[buildozer]
log_level = 2
