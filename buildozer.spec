[app]

# (str) Название приложения
title = MemeCloud

# (str) Пакет приложения
package.name = memecloud
package.domain = org.example

# (str) Версия приложения
version = 1.0

# (list) Основные исходники
source.include_exts = py,png,jpg,kv,atlas

# (str) Основной файл
source.main = main.py

# (str) Папка с исходниками (ВАЖНО!)
source.dir = .

# (str) Значок приложения (если есть)
icon.filename = %(source.dir)s/icon.png

# (str) Требуемый Python
requirements = python3,kivy==2.3.1,kivymd,pillow

# (list) Архитектуры Android
android.archs = arm64-v8a,armeabi-v7a

# (int) Минимальная версия Android
android.minapi = 21

# (int) Целевая версия Android
android.api = 33

# (str) Версия NDK
android.ndk = 27b

# (str) Bootstrap для приложения (sdl2 для Kivy)
p4a.bootstrap = sdl2

# (bool) Копировать библиотеки в APK
android.copy_libs = 1

# (str) Настройка NDK API
android.ndk_api = 21

# (bool) Использовать debug сборку
android.debug = 1

# (str) Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (bool) Включить логирование
log_level = 2
