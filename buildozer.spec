[app]

# (str) Название приложения
title = MemeCloud

# (str) Пакет приложения
package.name = memecloud
package.domain = org.example

# (str) Версия приложения
version = 0.1

# (list) Папка с исходниками
source.include_exts = py,png,jpg,kv,atlas

# (list) Основной файл
source.main = main.py

# (str) Значок приложения (если есть)
icon.filename = %(source.dir)s/icon.png

# (str) Требуемый Python
# Здесь используем системный Python, Buildozer сам создаст виртуальное окружение
# python3 значит Python 3.10+
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
android.bootstrap = sdl2

# (bool) Копировать библиотеки в APK
android.copy_libs = 1

# (str) Настройка NDK API
android.ndk_api = 21

# (bool) Использовать debug сборку (пока для тестов)
android.debug = 1

# (str) Разрешения Android
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (bool) Включить логирование
log_level = 2
