[app]

# (str) Title of your application
title = MemeCloud

# (str) Package name
package.name = memecloud

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mortualer

# (str) Source code where the main.py live
source.dir = .

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.jpg

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,mp3,json,txt,ttf,otf

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,requests,openssl,android

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) Android architecture to compile for
# USE THIS INSTEAD OF android.arch
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
