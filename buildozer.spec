[app]

# Название приложения
title = MemeCloud

# Пакет приложения
package.name = memecloud
package.domain = org.example

# Версия приложения
version = 0.1

# Папка с исходниками
source.dir = .

# Расширения исходников
source.include_exts = py,png,jpg,kv,atlas

# Основной файл
source.main = main.py

# Значок приложения (если есть)
icon.filename = %(source.dir)s/icon.png

# Требуемые Python-библиотеки
requirements = python3,kivy==2.3.1,kivymd,pillow

# Архитектуры Android
android.archs = arm64-v8a,armeabi-v7a

# Минимальная версия Android
android.minapi = 21

# Целевая версия Android
android.api = 33

# Версия NDK
android.ndk = 27b

# Bootstrap (новый ключ для Buildozer 2.x)
p4a.bootstrap = sdl2

# Копировать библиотеки в APK
android.copy_libs = 1

# NDK API
android.ndk_api = 21

# Debug сборка
android.debug = 1

# Разрешения
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Включить логирование
log_level = 2
