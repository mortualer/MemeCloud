[app]
# Имя приложения
title = MemeCloud
# Пакет приложения (только латиница и точки)
package.name = memecloud
package.domain = org.example

# Главный скрипт
source.dir = .
source.include_exts = py,png,jpg,kv,mp3,wav
# Точка входа
entrypoint = main.py

# Зависимости Python
requirements = python3,kivy

# Платформа Android
orientation = portrait
fullscreen = 0

# Icon (можно оставить дефолтный)
icon.filename = %(source.dir)s/icon.png

# Версия приложения
version = 1.0.0

# Разрешения Android (если нужны)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE

# Кэш Buildozer
log_level = 2
warn_on_root = 1

# Target Android SDK
android.api = 33
android.minapi = 21
android.ndk = 26b
android.sdk = 33
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r26b
