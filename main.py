from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import os
import requests
import webbrowser
import json
import shutil
from kivy.utils import platform
from urllib.parse import urlparse

if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission
    from android.storage import app_storage_path
    from jnius import autoclass, cast

# -------------------------
# Sound Cache Class
# -------------------------
class SoundCache:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def get_sound(self, path):
        if path in self.cache:
            # Перемещаем в конец (самый недавний)
            if path in self.access_order:
                self.access_order.remove(path)
            self.access_order.append(path)
            print(f"Sound cache hit: {os.path.basename(path)}")
            return self.cache[path]
        print(f"Sound cache miss: {os.path.basename(path)}")
        return None
    
    def add_sound(self, path, sound):
        if len(self.cache) >= self.max_size:
            # Удаляем самый старый
            if self.access_order:
                oldest = self.access_order.pop(0)
                if oldest in self.cache:
                    print(f"Removing from cache: {os.path.basename(oldest)}")
                    if hasattr(self.cache[oldest], 'unload'):
                        self.cache[oldest].unload()
                    del self.cache[oldest]
        
        self.cache[path] = sound
        self.access_order.append(path)
        print(f"Added to cache: {os.path.basename(path)} (cache size: {len(self.cache)})")
    
    def preload_sounds(self, sound_paths):
        """Предзагружает первые несколько звуков для быстрого доступа"""
        print(f"Preloading {min(3, len(sound_paths))} sounds...")
        for path in sound_paths[:3]:  # Предзагружаем первые 3 звука
            if path not in self.cache:
                sound = SoundLoader.load(path)
                if sound:
                    self.add_sound(path, sound)
    
    def clear_cache(self):
        """Очищает кэш"""
        for sound in self.cache.values():
            if hasattr(sound, 'unload'):
                sound.unload()
        self.cache.clear()
        self.access_order.clear()
        print("Sound cache cleared")

# -------------------------
# Smart Search Input Class
# -------------------------
class SmartSearchInput(TextInput):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.suggestions_popup = None
        self.suggestions = []
    
    def on_text(self, instance, value):
        super().on_text(instance, value)
        
        # Закрываем предыдущие подсказки
        if self.suggestions_popup:
            self.suggestions_popup.dismiss()
            self.suggestions_popup = None
        
        # Показываем подсказки если введено 2+ символа
        if len(value) >= 2:
            self.show_suggestions(value)
    
    def show_suggestions(self, query):
        """Показывает подсказки для поиска"""
        # Получаем совпадения
        matching_sounds = []
        for btn in self.app.buttons:
            if query.lower() in btn.btn_text.lower():
                matching_sounds.append(btn.btn_text)
        
        if not matching_sounds:
            return
        
        # Создаем контент для попапа
        content = BoxLayout(orientation='vertical', size_hint=(1, None))
        content.bind(minimum_height=content.setter('height'))
        
        # Добавляем до 5 подсказок
        for suggestion in matching_sounds[:5]:
            suggestion_btn = Button(
                text=suggestion,
                size_hint_y=None,
                height=40,
                background_color=(0.9, 0.9, 0.95, 1),
                background_normal='',
                color=(0.2, 0.2, 0.2, 1),
                font_size='14sp'
            )
            suggestion_btn.bind(on_release=lambda x, s=suggestion: self.select_suggestion(s))
            content.add_widget(suggestion_btn)
        
        # Создаем и показываем попап
        self.suggestions_popup = Popup(
            content=content,
            size_hint=(0.9, None),
            height=min(len(matching_sounds) * 40, 200),
            pos_hint={'center_x': 0.5, 'top': 0.1},
            background='',
            separator_color=(0.7, 0.7, 0.8, 1)
        )
        self.suggestions_popup.open()
    
    def select_suggestion(self, suggestion):
        """Выбирает подсказку и применяет её"""
        self.text = suggestion
        if self.suggestions_popup:
            self.suggestions_popup.dismiss()
            self.suggestions_popup = None
        
        # Применяем фильтр
        self.app.filter_buttons()

# -------------------------
# URL Download Popup Class
# -------------------------
class URLDownloadPopup(Popup):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "Download from URL"
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = False
        self.background = ''

        # Основной контейнер
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)

        # Заголовок
        title_label = Label(
            text="Enter audio file URL",
            size_hint_y=None,
            height=40,
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        content.add_widget(title_label)

        # Поле ввода URL
        self.url_input = TextInput(
            hint_text="https://example.com/audio.mp3",
            multiline=False,
            size_hint_y=None,
            height=60,
            background_color=(0.9, 0.9, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 0.7),
            padding=[15, 10]
        )
        content.add_widget(self.url_input)

        # Поле для имени файла
        filename_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        filename_layout.add_widget(Label(
            text="Filename:", 
            size_hint_x=0.4,
            color=(1, 1, 1, 1)
        ))
        
        self.filename_input = TextInput(
            hint_text="custom_name.mp3",
            multiline=False,
            size_hint_x=0.6,
            background_color=(0.9, 0.9, 0.95, 1),
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 0.7),
            padding=[10, 10]
        )
        filename_layout.add_widget(self.filename_input)
        content.add_widget(filename_layout)

        # Статус загрузки
        self.status_label = Label(
            text="",
            size_hint_y=None,
            height=40,
            font_size='14sp',
            color=(1, 1, 1, 0.8)
        )
        content.add_widget(self.status_label)

        # Кнопки
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)
        
        download_btn = Button(
            text="DOWNLOAD",
            background_color=(0.3, 0.6, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        download_btn.bind(on_press=self.start_download)
        
        cancel_btn = Button(
            text="CANCEL",
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=self.dismiss)

        btn_layout.add_widget(download_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        self.content = content
        
        # Привязываем события
        self.url_input.bind(text=self.on_url_change)

    def on_url_change(self, instance, value):
        """Автоматически извлекаем имя файла из URL"""
        if value and not self.filename_input.text:
            try:
                # Пытаемся извлечь имя файла из URL
                parsed = urlparse(value)
                filename = os.path.basename(parsed.path)
                if filename and '.' in filename:
                    self.filename_input.text = filename
            except:
                pass

    def start_download(self, instance):
        """Начинает загрузку файла"""
        url = self.url_input.text.strip()
        filename = self.filename_input.text.strip()

        if not url:
            self.status_label.text = "Please enter URL"
            self.status_label.color = (1, 0.5, 0.5, 1)
            return

        if not filename:
            self.status_label.text = "Please enter filename"
            self.status_label.color = (1, 0.5, 0.5, 1)
            return

        # Проверяем расширение файла
        valid_extensions = ('.mp3', '.wav', '.ogg')
        if not filename.lower().endswith(valid_extensions):
            self.status_label.text = "File must be .mp3, .wav or .ogg"
            self.status_label.color = (1, 0.5, 0.5, 1)
            return

        # Меняем состояние кнопки
        instance.text = "DOWNLOADING..."
        instance.background_color = (0.5, 0.5, 0.5, 1)
        instance.disabled = True

        self.status_label.text = "Starting download..."
        self.status_label.color = (1, 1, 0.8, 1)

        # Запускаем загрузку в отдельном потоке
        Clock.schedule_once(lambda dt: self.download_file(url, filename, instance), 0.1)

    def download_file(self, url, filename, button):
        """Загружает файл по URL"""
        try:
            self.status_label.text = "Connecting..."
            
            # Создаем полный путь для сохранения
            filepath = os.path.join(self.app.save_dir, filename)
            
            # Если файл существует, добавляем номер
            if os.path.exists(filepath):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filepath = os.path.join(self.app.save_dir, f"{base}_{counter}{ext}")
                    counter += 1
                filename = os.path.basename(filepath)

            # Загружаем файл
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            self.status_label.text = f"Downloading: 0%"
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded_size / total_size) * 100
                            self.status_label.text = f"Downloading: {percent:.1f}%"
                        else:
                            self.status_label.text = f"Downloaded: {downloaded_size // 1024}KB"
            
            self.status_label.text = "Download completed!"
            self.status_label.color = (0.6, 1, 0.6, 1)
            
            # Добавляем звук в приложение
            success = self.app.add_sound_button(filepath)
            
            if success:
                self.status_label.text = "File added successfully!"
                
                # Закрываем попап через 1 секунду
                Clock.schedule_once(lambda dt: self.dismiss(), 1.0)
            else:
                self.status_label.text = "Error adding file"
                self.status_label.color = (1, 0.5, 0.5, 1)
                # Удаляем файл если не удалось добавить
                try:
                    os.remove(filepath)
                except:
                    pass
                
                # Восстанавливаем кнопку
                button.text = "DOWNLOAD"
                button.background_color = (0.3, 0.6, 0.3, 1)
                button.disabled = False

        except requests.exceptions.Timeout:
            self.status_label.text = "Download timeout"
            self.status_label.color = (1, 0.5, 0.5, 1)
        except requests.exceptions.ConnectionError:
            self.status_label.text = "Connection error"
            self.status_label.color = (1, 0.5, 0.5, 1)
        except requests.exceptions.RequestException as e:
            self.status_label.text = f"Download error: {str(e)}"
            self.status_label.color = (1, 0.5, 0.5, 1)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            self.status_label.color = (1, 0.5, 0.5, 1)
        
        # Восстанавливаем кнопку в случае ошибки
        if self.status_label.color == (1, 0.5, 0.5, 1):
            button.text = "DOWNLOAD"
            button.background_color = (0.3, 0.6, 0.3, 1)
            button.disabled = False

# -------------------------
# SoundButton Class
# -------------------------
class SoundButton(BoxLayout):
    current_button = None

    def __init__(self, text, sound, icon_path=None, app=None, sound_id=None, sound_path=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.sound_id = sound_id or text
        self.sound_path = sound_path  # Сохраняем путь к файлу для кэширования
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 150
        self.spacing = 10
        self.padding = [10, 10, 10, 10]
        self.sound = sound
        self.btn_text = text
        self.is_expanded = False
        self.pinned = False
        self.volume = 1.0
        self.original_icon_path = icon_path
        self.highlight_anim = None
        self.sound_check_event = None
        self.expanded_view = None  # Ссылка на расширенное представление

        with self.canvas.before:
            Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(pos=(self.x - 2, self.y - 2),
                                           size=(self.width + 4, self.height + 4),
                                           radius=[20])
            self.bg_color = Color(0.25, 0.25, 0.35, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

        self.original_widgets = []
        
        if icon_path and os.path.exists(icon_path):
            self.icon_widget = Image(source=icon_path, size_hint=(None, 1), width=50)
            self.original_widgets.append(self.icon_widget)
            self.add_widget(self.icon_widget)

        self.button = Button(
            text=text,
            size_hint=(1, 1),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle"
        )
        self.button.text_size = (None, None)
        self.button.bind(on_press=self.play_sound)
        self.button.bind(on_touch_down=self.start_long_press, on_touch_up=self.end_long_press)
        self.original_widgets.append(self.button)
        self.add_widget(self.button)

        self.bind(pos=self.update_rect, size=self.update_rect)
        self._long_press_trigger = Clock.create_trigger(self.expand, 0.8)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.shadow.pos = (self.x - 2, self.y - 2)
        self.shadow.size = (self.width + 4, self.height + 4)

    def play_sound(self, instance=None):
        if SoundButton.current_button and SoundButton.current_button != self:
            SoundButton.current_button.stop_sound_and_collapse()
        SoundButton.current_button = self

        if self.sound:
            self.sound.volume = self.volume
            self.sound.stop()
            self.sound.play()
            self.start_highlight()
            # Отменяем предыдущую проверку и запускаем новую
            if self.sound_check_event:
                self.sound_check_event.cancel()
            self.sound_check_event = Clock.schedule_interval(self.check_sound, 0.1)

    def start_highlight(self):
        self.stop_highlight()
        # Более плавная анимация подсветки
        anim = Animation(rgba=(0.4, 0.4, 0.6, 1), duration=0.3) + \
               Animation(rgba=(0.25, 0.25, 0.35, 1), duration=0.4)
        anim.repeat = True
        anim.start(self.bg_color)
        self.highlight_anim = anim

    def stop_highlight(self):
        if self.highlight_anim:
            self.highlight_anim.cancel(self.bg_color)
            self.highlight_anim = None
        # Плавное возвращение к исходному цвету
        Animation(rgba=(0.25, 0.25, 0.35, 1), duration=0.2).start(self.bg_color)

    def check_sound(self, dt):
        if self.sound and self.sound.state != 'play':
            # Звук закончил воспроизведение
            self.stop_highlight()
            # Отменяем проверку
            if self.sound_check_event:
                self.sound_check_event.cancel()
                self.sound_check_event = None
            
            # Сворачиваем если развернуто и не закреплено
            if self.is_expanded and not getattr(App.get_running_app(), "pin_active", False):
                self.collapse()
            return False  # Останавливаем проверку
        return True  # Продолжаем проверку

    def start_long_press(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Визуальный feedback при начале long press
            Animation(background_color=(0.3, 0.3, 0.5, 0.3), duration=0.1).start(self.button)
            self._long_press_trigger()
        return False

    def end_long_press(self, instance, touch):
        if self._long_press_trigger.is_triggered:
            self._long_press_trigger.cancel()
            # Возвращаем цвет кнопки
            Animation(background_color=(0, 0, 0, 0), duration=0.2).start(self.button)
        return False

    def expand(self, *args):
        if self.is_expanded:
            return
        
        # Сворачиваем другие развернутые кнопки
        if self.app:
            for btn in self.app.buttons:
                if btn != self and btn.is_expanded and not getattr(self.app, "pin_active", False):
                    btn.collapse()
        
        self.is_expanded = True
        
        # Сохраняем оригинальную позицию и размер для возврата
        self.original_pos = self.pos[:]
        self.original_size = self.size[:]
        
        # Создаем расширенное представление
        self.create_expanded_view()
        
        # Рассчитываем высоту для расширенного состояния (под верхней панелью)
        top_bar_height = 75  # Высота верхней панели
        expanded_height = Window.height - top_bar_height - 20  # -20 для отступов
        
        # Плавная анимация расширения
        anim = Animation(
            height=expanded_height, 
            duration=0.5, 
            t='out_quad'
        )
        anim.bind(on_complete=self.on_expand_complete)
        anim.start(self)

    def on_expand_complete(self, *args):
        """Вызывается после завершения анимации расширения"""
        # Воспроизводим звук после завершения анимации
        self.play_sound()

    def create_expanded_view(self):
        self.clear_widgets()
        
        # Основной контейнер расширенного вида
        self.expanded_view = BoxLayout(orientation='vertical', spacing=20, padding=30)
        
        # Заголовок с возможностью проигрывания по клику
        title_label = Label(
            text=self.btn_text,
            size_hint_y=None,
            height=150,
            font_size='28sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        title_label.bind(on_touch_down=self.on_title_touch)
        self.expanded_view.add_widget(title_label)
        
        # Контейнер для кнопок управления
        controls_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=250)
        
        # Кнопка проигрывания
        play_btn = Button(
            text='PLAY SOUND',
            size_hint_y=None,
            height=100,
            background_color=(0.3, 0.4, 0.6, 1),  # Темно-голубовато-синий
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='22sp',
            bold=True
        )
        play_btn.bind(on_press=self.on_play_button_press)
        play_btn.bind(on_release=self.on_play_button_release)
        controls_layout.add_widget(play_btn)
        
        # Кнопки управления
        btn_layout = BoxLayout(size_hint_y=None, height=100, spacing=15)
        
        delete_btn = Button(
            text='DELETE',
            size_hint_x=0.6,
            background_color=(0.3, 0.4, 0.6, 1),  # Темно-голубовато-синий
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        delete_btn.bind(on_press=self.on_delete_button_press)
        delete_btn.bind(on_release=self.on_delete_button_release)
        btn_layout.add_widget(delete_btn)
        
        close_btn = Button(
            text='CLOSE',
            size_hint_x=0.4,
            background_color=(0.3, 0.4, 0.6, 1),  # Темно-голубовато-синий
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        close_btn.bind(on_press=self.on_close_button_press)
        close_btn.bind(on_release=self.on_close_button_release)
        btn_layout.add_widget(close_btn)
        
        controls_layout.add_widget(btn_layout)
        self.expanded_view.add_widget(controls_layout)
        self.add_widget(self.expanded_view)

    def on_play_button_press(self, instance):
        """Анимация при нажатии кнопки play"""
        Animation(background_color=(0.4, 0.5, 0.7, 1), duration=0.1).start(instance)

    def on_play_button_release(self, instance):
        """Анимация при отпускании кнопки play"""
        Animation(background_color=(0.3, 0.4, 0.6, 1), duration=0.3).start(instance)
        self.play_sound()

    def on_delete_button_press(self, instance):
        """Анимация при нажатии кнопки delete"""
        Animation(background_color=(0.4, 0.5, 0.7, 1), duration=0.1).start(instance)

    def on_delete_button_release(self, instance):
        """Анимация при отпускании кнопки delete"""
        Animation(background_color=(0.3, 0.4, 0.6, 1), duration=0.3).start(instance)
        self.delete_sound(instance)

    def on_close_button_press(self, instance):
        """Анимация при нажатии кнопки close"""
        Animation(background_color=(0.4, 0.5, 0.7, 1), duration=0.1).start(instance)

    def on_close_button_release(self, instance):
        """Анимация при отпускании кнопки close"""
        Animation(background_color=(0.3, 0.4, 0.6, 1), duration=0.3).start(instance)
        self.collapse()

    def on_title_touch(self, instance, touch):
        """Обработка клика по заголовку для проигрывания звука"""
        if self.is_expanded and instance.collide_point(*touch.pos):
            if touch.is_double_tap:
                # Анимация при двойном клике
                anim = Animation(color=(0.8, 0.8, 1, 1), duration=0.1)
                anim += Animation(color=(1, 1, 1, 1), duration=0.3)
                anim.start(instance)
                self.play_sound()
                return True
        return False

    def on_volume_change(self, instance, value):
        self.volume = value
        if self.sound:
            self.sound.volume = value
        if self.app:
            self.app.save_sound_settings()

    def delete_sound(self, instance):
        def confirm_delete(instance):
            if self.app:
                self.app.delete_sound(self)
            popup.dismiss()
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        # Анимированный заголовок
        question_label = Label(
            text=f'Delete "{self.btn_text}"?',
            font_size='20sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=60
        )
        content.add_widget(question_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=15)
        
        yes_btn = Button(
            text='YES', 
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        no_btn = Button(
            text='NO',
            background_color=(0.4, 0.4, 0.6, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirm Delete',
            content=content, 
            size_hint=(0.7, 0.4),
            background='',
            separator_color=(0.3, 0.3, 0.4, 1)
        )
        
        # Анимация появления popup
        popup.content.opacity = 0
        popup.open()
        Animation(opacity=1, duration=0.3).start(popup.content)
        
        yes_btn.bind(on_release=confirm_delete)
        no_btn.bind(on_release=popup.dismiss)

    def collapse(self):
        if not self.is_expanded:
            return
        
        self.is_expanded = False
        
        # Сначала анимируем исчезновение внутреннего содержимого
        if self.expanded_view:
            anim_opacity = Animation(opacity=0, duration=0.2)
            anim_opacity.bind(on_complete=self._start_collapse_animation)
            anim_opacity.start(self.expanded_view)
        else:
            self._start_collapse_animation()

    def _start_collapse_animation(self, *args):
        """Начинает анимацию сворачивания после исчезновения содержимого"""
        self.stop_sound_and_collapse()
        
        # Плавная анимация сворачивания
        anim = Animation(
            height=150, 
            duration=0.4, 
            t='out_quad'
        )
        anim.bind(on_complete=self.on_collapse_complete)
        anim.start(self)

    def on_collapse_complete(self, *args):
        """Вызывается после завершения анимации сворачивания"""
        # Восстанавливаем оригинальное представление
        self.restore_original_view()

    def restore_original_view(self):
        self.clear_widgets()
        for widget in self.original_widgets:
            self.add_widget(widget)
        # Сбрасываем прозрачность на случай следующего расширения
        self.opacity = 1
        self.expanded_view = None

    def stop_sound_and_collapse(self):
        if self.sound:
            self.sound.stop()
        self.stop_highlight()
        if self.sound_check_event:
            self.sound_check_event.cancel()
            self.sound_check_event = None

class MyApp(App):
    CURRENT_VERSION = "1.3.1"
    UPDATE_URL = "https://raw.githubusercontent.com/mortualer/MemeCloud/main/update.json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Упрощенная логика путей
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                base_dir = app_storage_path()
                self.save_dir = os.path.join(base_dir, "saved_sounds")
                print(f"Using app storage: {base_dir}")
            except Exception as e:
                print(f"Error getting app storage: {e}")
                self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_sounds")
        else:
            self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_sounds")

        self.settings_file = os.path.join(self.save_dir, "app_settings.json")
        print(f"Save directory: {self.save_dir}")

        # ВАЖНО: Создаем директорию ДО загрузки настроек
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.buttons = []
        self.pin_active = False
        self.sound_settings = {}
        self.permissions_granted = False
        
        # Инициализируем кэш звуков
        self.sound_cache = SoundCache(max_size=15)
        
        self.load_settings()

    def build(self):
        try:
            print("Starting app build...")
            
            # Сначала создаем простой интерфейс
            Window.clearcolor = (0.95, 0.95, 0.98, 1)
            self.root = BoxLayout(orientation='vertical', spacing=10, padding=10)
            
            # Сразу создаем основной интерфейс
            self.create_main_interface()
            
            # Загружаем звуки
            Clock.schedule_once(self.delayed_load_sounds, 0.5)
            
            # Запрашиваем разрешения на Android
            if platform == 'android':
                Clock.schedule_once(self.request_android_permissions, 1)
                
            # Проверяем обновления
            Clock.schedule_once(self.delayed_check_update, 3)
            
            return self.root
            
        except Exception as e:
            print(f"Error in build: {e}")
            # Фолбэк интерфейс
            error_label = Label(text=f"Error: {str(e)}", font_size='20sp')
            return error_label

    def delayed_load_sounds(self, dt):
        """Отложенная загрузка звуков"""
        try:
            self.load_existing_sounds()
        except Exception as e:
            print(f"Error in delayed_load_sounds: {e}")

    def delayed_check_update(self, dt):
        """Отложенная проверка обновлений"""
        try:
            self.check_for_update()
        except Exception as e:
            print(f"Error in delayed_check_update: {e}")

    def create_main_interface(self):
        """Создает основной интерфейс приложения"""
        # Верхняя панель
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=75, spacing=15)

        # Используем умный поиск вместо обычного TextInput
        self.search_input = SmartSearchInput(
            app=self,
            size_hint=(1, 1), 
            hint_text="Search...", 
            multiline=False,
            background_color=(0.9, 0.9, 0.95, 1), 
            foreground_color=(0, 0, 0, 1),
            hint_text_color=(0.5, 0.5, 0.5, 0.7),
            padding=[15, 10]
        )
        # Биндим текстовые изменения для фильтрации
        self.search_input.bind(text=self.on_search_text_change)
        top_bar.add_widget(self.search_input)

        # Кнопка Pin - пурпурного цвета как у звуковых кнопок
        self.pin_button = Button(
            text="Pin", 
            size_hint=(None, 1), 
            width=100,
            background_color=(0.25, 0.25, 0.35, 1),  # Пурпурный как у кнопок
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        self.pin_button.bind(on_release=self.toggle_pin)
        top_bar.add_widget(self.pin_button)

        # Кнопка Upload - пурпурного цвета
        self.upload_button = Button(
            text="Upload", 
            size_hint=(None, 1), 
            width=175,
            background_color=(0.25, 0.25, 0.35, 1),  # Пурпурный как у кнопок
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        self.upload_button.bind(on_release=self.show_upload_options)
        top_bar.add_widget(self.upload_button)

        # Кнопка Info - пурпурного цвета
        self.settings_button = Button(
            text="i", 
            size_hint=(None, 1), 
            width=100,
            background_color=(0.25, 0.25, 0.35, 1),  # Пурпурный как у кнопок
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='14sp'
        )
        self.settings_button.bind(on_release=self.open_settings)
        top_bar.add_widget(self.settings_button)

        self.root.add_widget(top_bar)

        # Область прокрутки для звуков
        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        self.root.add_widget(self.scroll)

    def on_search_text_change(self, instance, value):
        """Обработчик изменения текста в умном поиске"""
        self.filter_buttons()

    def on_start(self):
        print("App started successfully")
        # Копируем встроенные звуки
        self.copy_builtin_sounds()

    def copy_builtin_sounds(self):
        """Копирует встроенные звуки в рабочую директорию"""
        try:
            print("Copying built-in sounds...")
            
            # Ищем папку со звуками в разных возможных местах
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_sounds"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "saved_sounds"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "saved_sounds"),  # Для GitHub структуры
            ]
            
            source_dir = None
            for path in possible_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    source_dir = path
                    print(f"Found built-in sounds at: {source_dir}")
                    break
            
            if not source_dir:
                print("No built-in sounds directory found")
                return
            
            # Собираем все файлы для копирования
            files_to_copy = []
            for filename in os.listdir(source_dir):
                if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                    src_path = os.path.join(source_dir, filename)
                    dst_path = os.path.join(self.save_dir, filename)
                    
                    # Копируем только если файл еще не существует
                    if not os.path.exists(dst_path):
                        files_to_copy.append((src_path, dst_path, filename))
            
            if files_to_copy:
                print(f"Found {len(files_to_copy)} new sounds to copy")
                
                # Копируем все файлы сразу
                copied_count = 0
                for src_path, dst_path, filename in files_to_copy:
                    try:
                        shutil.copy2(src_path, dst_path)
                        copied_count += 1
                        print(f"Copied: {filename}")
                    except Exception as e:
                        print(f"Error copying {filename}: {e}")
                
                print(f"Successfully copied {copied_count} built-in sounds")
                
                # ОДИН раз обновляем интерфейс после копирования всех файлов
                Clock.schedule_once(self.delayed_load_sounds, 0.5)
            else:
                print("No new sounds to copy")
                
        except Exception as e:
            print(f"Error copying built-in sounds: {e}")

    def request_android_permissions(self, dt=None):
        """Запрашивает разрешения на Android"""
        if platform == 'android':
            try:
                print("Requesting Android permissions...")
                
                # Базовые разрешения
                permissions = [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ]
                
                # Для Android 13+
                if hasattr(Permission, 'READ_MEDIA_AUDIO'):
                    permissions = [
                        Permission.READ_MEDIA_AUDIO,
                        Permission.INTERNET
                    ]
                
                print(f"Requesting permissions: {permissions}")
                request_permissions(permissions, self.permission_callback)
                
            except Exception as e:
                print(f"Permission request error: {e}")

    def permission_callback(self, permissions, grant_results):
        """Обратный вызов после запроса разрешений"""
        print(f"Permission callback: {permissions}, {grant_results}")
        
        if all(grant_results):
            print("All permissions granted")
            self.permissions_granted = True
            self.show_info_popup("Success", "All permissions granted")
        else:
            print("Some permissions denied")
            self.permissions_granted = False
            self.show_info_popup("Warning", "Some permissions were denied")

    def on_activity_result(self, request_code, result_code, intent):
        """Обрабатывает результат выбора файлов на Android"""
        print(f"Activity result: request_code={request_code}, result_code={result_code}")
        
        if request_code != 123:
            return
            
        try:
            if result_code == -1:  # RESULT_OK
                from jnius import autoclass
                
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                ClipData = autoclass('android.content.ClipData')
                
                clip_data = intent.getClipData()
                processed_files = []
                
                if clip_data is not None:
                    # Множественный выбор
                    count = clip_data.getItemCount()
                    print(f"Multiple files selected: {count}")
                    for i in range(count):
                        uri = clip_data.getItemAt(i).getUri()
                        print(f"Processing URI {i+1}: {uri}")
                        result = self.process_android_uri(uri)
                        if result:
                            processed_files.append(result)
                else:
                    # Одиночный выбор
                    uri = intent.getData()
                    if uri is not None:
                        print(f"Single file selected: {uri}")
                        result = self.process_android_uri(uri)
                        if result:
                            processed_files.append(result)
                
                print(f"File processing completed. Processed {len(processed_files)} files")
                
                # ВАЖНО: Двойное обновление для гарантии
                if processed_files:
                    # Сначала немедленно обновляем
                    Clock.schedule_once(lambda dt: self.delayed_load_sounds(), 0.1)
                    # Затем еще раз через 1 секунду для надежности
                    Clock.schedule_once(lambda dt: self.force_reload_sounds(), 1.0)
                    self.show_info_popup("Success", f"Added {len(processed_files)} audio files")
                
            else:
                print("User cancelled file selection")
                
        except Exception as e:
            print(f"Error processing activity result: {e}")
            self.show_error_popup(f"Error processing selected files: {str(e)}")

    def process_android_uri(self, uri):
        """Обрабатывает URI файла на Android и возвращает имя файла если успешно"""
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            ContentResolver = autoclass('android.content.ContentResolver')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            
            content_resolver = context.getContentResolver()
            
            # Получаем имя файла
            cursor = content_resolver.query(uri, None, None, None, None)
            filename = "audio_file"
            if cursor:
                try:
                    display_name_index = cursor.getColumnIndex("_display_name")
                    if display_name_index != -1 and cursor.moveToFirst():
                        filename = cursor.getString(display_name_index)
                finally:
                    cursor.close()
            
            # Проверяем расширение файла
            if not filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                print(f"Skipping non-audio file: {filename}")
                return None
            
            print(f"Processing audio file: {filename}")
            
            # Создаем путь для сохранения
            new_path = os.path.join(self.save_dir, filename)
            
            # Если файл с таким именем уже существует, добавляем номер
            if os.path.exists(new_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(self.save_dir, f"{base}_{counter}{ext}")
                    counter += 1
            
            # Копируем содержимое файла
            input_stream = content_resolver.openInputStream(uri)
            with open(new_path, 'wb') as out_file:
                # Читаем и записываем файл по частям
                buffer_size = 8192
                buffer = bytearray(buffer_size)
                bytes_read = input_stream.read(buffer)
                while bytes_read != -1:
                    out_file.write(buffer[:bytes_read])
                    bytes_read = input_stream.read(buffer)
            
            input_stream.close()
            
            print(f"Successfully copied to: {new_path}")
            return filename
                
        except Exception as e:
            print(f"Error processing Android URI: {e}")
            self.show_error_popup(f"Error processing file: {str(e)}")
            return None

    def load_settings(self):
        """Загружает настройки приложения"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sound_settings = data.get('sound_settings', {})
                print("Settings loaded successfully")
            else:
                self.sound_settings = {}
                print("No settings file found")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.sound_settings = {}

    def save_sound_settings(self):
        """Сохраняет настройки звуков"""
        try:
            for btn in self.buttons:
                if btn.sound_id:
                    self.sound_settings[btn.sound_id] = {
                        'volume': btn.volume,
                        'name': btn.btn_text
                    }
            
            data = {
                'sound_settings': self.sound_settings,
                'app_version': self.CURRENT_VERSION
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def clean_sound_name(self, filename):
        """Очищает имя файла для отображения"""
        name = os.path.splitext(filename)[0]
        
        unwanted_phrases = [
            "Sound Button", "sound button", "SoundButton", "soundbutton",
            "Sound", "sound", "Button", "button", "MP3", "mp3", "WAV", "wav", "OGG", "ogg"
        ]
        
        for phrase in unwanted_phrases:
            name = name.replace(phrase, "")
        
        name = name.replace("_", " ").replace("-", " ").strip()
        name = " ".join(name.split())
        
        if not name:
            name = os.path.splitext(filename)[0]
            
        return name

    def load_existing_sounds(self):
        """Загружает существующие звуки"""
        print(f"Loading sounds from: {self.save_dir}")
        print(f"Directory exists: {os.path.exists(self.save_dir)}")
        
        if not os.path.exists(self.save_dir):
            print(f"Creating directory: {self.save_dir}")
            os.makedirs(self.save_dir, exist_ok=True)
        
        # Очищаем текущие кнопки
        self.layout.clear_widgets()
        self.buttons.clear()
        
        print("Scanning for audio files...")
        audio_extensions = ('.mp3', '.wav', '.ogg')
        found_files = False
        
        # Собираем все файлы сначала
        sound_files = []
        for filename in sorted(os.listdir(self.save_dir)):
            if filename.lower().endswith(audio_extensions):
                sound_path = os.path.join(self.save_dir, filename)
                sound_files.append((sound_path, filename))
                found_files = True
        
        # Предзагружаем звуки в кэш
        if sound_files:
            self.sound_cache.preload_sounds([path for path, name in sound_files])
        
        # Затем добавляем все кнопки сразу
        for sound_path, filename in sound_files:
            print(f"Found audio file: {filename}")
            self.add_sound_button(sound_path)
        
        print(f"Total sounds loaded: {len(self.buttons)}")
        
        # Если файлов не найдено, показываем сообщение
        if not found_files and len(self.buttons) == 0:
            no_sounds_label = Label(
                text="No sounds found\n\nUse the Upload button to add audio files",
                size_hint_y=None,
                height=200,
                font_size='18sp',
                halign='center'
            )
            no_sounds_label.bind(size=no_sounds_label.setter('text_size'))
            self.layout.add_widget(no_sounds_label)

    def add_sound_button(self, path):
        """Добавляет кнопку звука с использованием кэша"""
        try:
            # Проверяем, не добавлен ли уже этот звук
            filename = os.path.basename(path)
            sound_id = os.path.splitext(filename)[0]
            
            for btn in self.buttons:
                if btn.sound_id == sound_id:
                    print(f"Sound already exists: {filename}")
                    return False
            
            btn_text = self.clean_sound_name(filename)
            
            print(f"Loading sound: {filename}")
            
            # Ищем иконку
            icon_file = None
            icon_extensions = ['.png', '.jpg', '.jpeg']
            for ext in icon_extensions:
                potential_icon = os.path.join(self.save_dir, sound_id + ext)
                if os.path.exists(potential_icon):
                    icon_file = potential_icon
                    break
            
            # Пытаемся получить звук из кэша
            sound = self.sound_cache.get_sound(path)
            if sound is None:
                # Если нет в кэше, загружаем
                sound = SoundLoader.load(path)
                if sound:
                    self.sound_cache.add_sound(path, sound)
            
            if sound:
                print(f"Sound loaded successfully: {filename}")
                btn_widget = SoundButton(
                    btn_text, sound, icon_file, app=self, 
                    sound_id=sound_id, sound_path=path  # Сохраняем путь для кэширования
                )
                
                if sound_id in self.sound_settings:
                    btn_widget.volume = self.sound_settings[sound_id].get('volume', 1.0)
                
                self.layout.add_widget(btn_widget)
                self.buttons.append(btn_widget)
                return True
            else:
                print(f"Failed to load sound: {filename}")
                return False
                
        except Exception as e:
            print(f"Error adding sound button: {e}")
            return False

    def delete_sound(self, sound_button):
        """Удаляет звук и очищает его из кэша"""
        try:
            for btn in self.buttons[:]:
                if btn == sound_button:
                    if btn.sound:
                        btn.sound.stop()
                    
                    # Удаляем звук из кэша
                    if hasattr(btn, 'sound_path') and btn.sound_path:
                        if btn.sound_path in self.sound_cache.cache:
                            del self.sound_cache.cache[btn.sound_path]
                            if btn.sound_path in self.sound_cache.access_order:
                                self.sound_cache.access_order.remove(btn.sound_path)
                            print(f"Removed from cache: {os.path.basename(btn.sound_path)}")
                    
                    self.layout.remove_widget(btn)
                    self.buttons.remove(btn)
                    
                    sound_id = btn.sound_id
                    # Удаляем связанные файлы
                    for filename in os.listdir(self.save_dir):
                        file_base = os.path.splitext(filename)[0]
                        if file_base == sound_id:
                            file_path = os.path.join(self.save_dir, filename)
                            try:
                                os.remove(file_path)
                                print(f"Removed: {file_path}")
                            except Exception as e:
                                print(f"Error removing file: {e}")
                    
                    # Удаляем настройки
                    if sound_id in self.sound_settings:
                        del self.sound_settings[sound_id]
                        self.save_sound_settings()
                    
                    # Перезагружаем список звуков
                    Clock.schedule_once(self.delayed_load_sounds, 0.1)
                    break
                    
        except Exception as e:
            print(f"Error deleting sound: {e}")
            self.show_error_popup("Error deleting sound")

    def show_upload_options(self, instance):
        """Показывает опции загрузки"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        title_label = Label(
            text="How do you want to add sounds?",
            size_hint_y=None,
            height=50,
            font_size='18sp',
            color=(1, 1, 1, 1)
        )
        content.add_widget(title_label)
        
        # Вертикальный layout для кнопок с фиксированной высотой
        btn_layout = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, height=240)
        
        # Кнопка выбора файлов
        file_btn = Button(
            text="Select Audio Files",
            size_hint_y=None,
            height=70,
            background_color=(0.3, 0.6, 0.9, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        file_btn.bind(on_release=lambda x: self._file_picker_selected(popup))
        
        # Кнопка выбора папки (только для desktop)
        folder_btn = Button(
            text="Select Folder",
            size_hint_y=None,
            height=70,
            background_color=(0.4, 0.7, 0.4, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        folder_btn.bind(on_release=lambda x: self._folder_picker_selected(popup))
        
        # Кнопка Download from URL
        url_btn = Button(
            text="Download from URL",
            size_hint_y=None,
            height=70,
            background_color=(0.8, 0.5, 0.2, 1),  # Оранжевый цвет для различия
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='16sp'
        )
        url_btn.bind(on_release=lambda x: self._url_download_selected(popup))
        
        btn_layout.add_widget(file_btn)
        
        # Для Android не показываем кнопку выбора папки
        if platform != 'android':
            btn_layout.add_widget(folder_btn)
        
        btn_layout.add_widget(url_btn)  # Добавляем новую кнопку
        content.add_widget(btn_layout)
        
        cancel_btn = Button(
            text="Cancel",
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        content.add_widget(cancel_btn)
        
        popup = Popup(
            title="Add Sounds",
            content=content,
            size_hint=(0.85, 0.7),
            auto_dismiss=False,
            background=''
        )
        
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def _file_picker_selected(self, popup):
        """Обработчик выбора файлового пикера"""
        popup.dismiss()
        self.open_file_picker()

    def _folder_picker_selected(self, popup):
        """Обработчик выбора папки"""
        popup.dismiss()
        self.open_folder_picker()

    def _url_download_selected(self, popup):
        """Обработчик выбора загрузки по URL"""
        popup.dismiss()
        self.show_url_download_popup()

    def show_url_download_popup(self):
        """Показывает попап для загрузки по URL"""
        popup = URLDownloadPopup(self)
        popup.open()

    def open_file_picker(self):
        """Открывает выбор файлов"""
        if platform == 'android':
            self.open_android_file_picker()
        else:
            self.open_desktop_file_picker()

    def open_folder_picker(self):
        """Открывает выбор папки"""
        if platform == 'android':
            # На Android используем множественный выбор файлов вместо папки
            self.show_info_popup("Info", "On Android, please use 'Select Audio Files' for multiple file selection")
        else:
            self.open_desktop_folder_picker()

    def open_android_file_picker(self):
        """Открывает файловый пикер на Android"""
        try:
            from jnius import autoclass
            from android import activity
            
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            
            # Создаем Intent для выбора файла с поддержкой множественного выбора
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("audio/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, True)  # Множественный выбор
            
            # Регистрируем обработчик результата
            def on_activity_result(request_code, result_code, intent):
                print(f"File picker result: {request_code}, {result_code}")
                if request_code == 123:
                    self.on_activity_result(request_code, result_code, intent)
            
            # Устанавливаем обработчик
            activity.bind(on_activity_result=on_activity_result)
            
            # Запускаем активность
            context.startActivityForResult(intent, 123)
            print("Android file picker started")
            
        except Exception as e:
            print(f"Error opening Android file picker: {e}")
            self.show_error_popup(f"Cannot open file picker: {str(e)}")

    def open_desktop_file_picker(self):
        """Файловый пикер для desktop"""
        try:
            from tkinter import Tk, filedialog
            
            root = Tk()
            root.withdraw()
            
            file_paths = filedialog.askopenfilenames(
                title="Select Audio Files",
                filetypes=[("Audio files", "*.mp3 *.wav *.ogg"), ("All files", "*.*")]
            )
            
            root.destroy()
            
            if file_paths:
                processed_count = 0
                for file_path in file_paths:
                    if self.copy_audio_file(file_path):
                        processed_count += 1
                
                if processed_count > 0:
                    self.show_info_popup("Success", f"Added {processed_count} audio files")
                    Clock.schedule_once(self.delayed_load_sounds, 0.5)
                    
        except Exception as e:
            print(f"Error in file picker: {e}")
            self.show_error_popup(f"Error selecting files: {str(e)}")

    def open_desktop_folder_picker(self):
        """Выбор папки для desktop"""
        try:
            from tkinter import Tk, filedialog
            
            root = Tk()
            root.withdraw()
            
            folder_path = filedialog.askdirectory(title="Select Folder with Audio Files")
            
            root.destroy()
            
            if folder_path:
                self.copy_audio_from_folder(folder_path)
                
        except Exception as e:
            print(f"Error in folder picker: {e}")
            self.show_error_popup(f"Error selecting folder: {str(e)}")

    def copy_audio_file(self, file_path):
        """Копирует аудио файл"""
        try:
            filename = os.path.basename(file_path)
            
            if not filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                return False
            
            new_path = os.path.join(self.save_dir, filename)
            
            # Добавляем номер если файл существует
            if os.path.exists(new_path):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(new_path):
                    new_path = os.path.join(self.save_dir, f"{base}_{counter}{ext}")
                    counter += 1
            
            shutil.copy2(file_path, new_path)
            print(f"Copied to: {new_path}")
            
            # Добавляем кнопку
            return self.add_sound_button(new_path)
                
        except Exception as e:
            print(f"Error copying file: {e}")
            return False

    def copy_audio_from_folder(self, folder_path):
        """Копирует все аудио файлы из папки"""
        try:
            audio_files = []
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                    audio_files.append(filename)
            
            if not audio_files:
                self.show_info_popup("No Audio Files", "No audio files found in selected folder")
                return
            
            copied_count = 0
            for filename in audio_files:
                src_path = os.path.join(folder_path, filename)
                if self.copy_audio_file(src_path):
                    copied_count += 1
            
            if copied_count > 0:
                self.show_info_popup("Complete", f"Added {copied_count} audio files")
                Clock.schedule_once(self.delayed_load_sounds, 0.5)
            else:
                self.show_info_popup("Error", "No files were added")
            
        except Exception as e:
            print(f"Error copying from folder: {e}")
            self.show_error_popup(f"Error copying files: {str(e)}")

    def force_reload_sounds(self):
        """Принудительно перезагружает все звуки из папки saved_sounds"""
        print("Force reloading sounds...")
        self.load_existing_sounds()

    def open_settings(self, instance):
        """Открывает настройки с информацией о кэше"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        permissions_status = "Granted" if self.permissions_granted else "Not granted"
        cache_info = f"""MemeCloud v{self.CURRENT_VERSION}

Debug Info:
• Sounds loaded: {len(self.buttons)}
• Cache size: {len(self.sound_cache.cache)}/{self.sound_cache.max_size}
• Save dir: {self.save_dir}
• Permissions: {permissions_status}
• Platform: {platform}"""

        info_label = Label(
            text=cache_info,
            size_hint_y=None,
            height=200,
            text_size=(Window.width * 0.8 - 40, None),
            halign='left',
            valign='top'
        )
        info_label.bind(size=info_label.setter('text_size'))
        content.add_widget(info_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        if platform == 'android':
            # Кнопка Permissions с уменьшенным шрифтом
            perm_btn = Button(
                text="Permissions", 
                background_color=(0.4, 0.4, 0.6, 1),
                font_size='12sp'  # Уменьшаем шрифт чтобы поместилось
            )
            perm_btn.bind(on_release=lambda x: self.request_android_permissions())
            btn_layout.add_widget(perm_btn)
        
        # Кнопка очистки кэша
        cache_btn = Button(
            text="Clear Cache", 
            background_color=(0.5, 0.3, 0.3, 1),
            font_size='12sp'
        )
        cache_btn.bind(on_release=lambda x: self.clear_sound_cache())
        btn_layout.add_widget(cache_btn)
        
        github_btn = Button(
            text="GitHub", 
            background_color=(0.3, 0.3, 0.5, 1)
        )
        github_btn.bind(on_release=lambda x: webbrowser.open("https://github.com/mortualer/MemeCloud"))
        
        close_btn = Button(
            text="Close", 
            background_color=(0.5, 0.5, 0.7, 1)
        )
        
        btn_layout.add_widget(github_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Settings & Info", 
            content=content, 
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def clear_sound_cache(self):
        """Очищает кэш звуков"""
        self.sound_cache.clear_cache()
        self.show_info_popup("Cache Cleared", "Sound cache has been cleared")

    def toggle_pin(self, instance):
        """Переключает режим закрепления"""
        self.pin_active = not self.pin_active
        if self.pin_active:
            instance.background_color = (0.15, 0.15, 0.25, 1)  # Темнее при активности
            instance.text = "Pin"  # Оставляем текст "Pin" всегда
        else:
            instance.background_color = (0.25, 0.25, 0.35, 1)  # Обычный цвет
            instance.text = "Pin"

        for btn in self.buttons:
            if hasattr(btn, 'is_expanded') and btn.is_expanded:
                if self.pin_active:
                    btn.pinned = True
                else:
                    btn.pinned = False
                    btn.collapse()

    def filter_buttons(self, *args):
        """Фильтрует кнопки по поисковому запросу"""
        value = self.search_input.text.lower()
        for btn_widget in self.buttons:
            visible = value in btn_widget.btn_text.lower()
            btn_widget.opacity = 1 if visible else 0
            btn_widget.disabled = not visible
            btn_widget.height = 150 if visible else 0

    def show_error_popup(self, message):
        """Показывает popup с ошибкой"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint_y=None, height=50)
        content.add_widget(close_btn)
        
        popup = Popup(title="Error", content=content, size_hint=(0.6, 0.3))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_info_popup(self, title, message):
        """Показывает информационный popup"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint_y=None, height=50)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.3))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def check_for_update(self):
        """Проверяет обновления"""
        try:
            print("Checking for updates...")
            response = requests.get(self.UPDATE_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('version', '')
                
                if latest_version and latest_version != self.CURRENT_VERSION:
                    print(f"Update available: {latest_version}")
                    download_url = data.get('download_url', '')
                    changelog = data.get('changelog', '')
                    self.show_update_popup(latest_version, download_url, changelog)
                else:
                    print("No updates available")
            else:
                print(f"Update check failed: {response.status_code}")
        except Exception as e:
            print(f"Update check error: {e}")

    def show_update_popup(self, latest_version, download_url, changelog):
        """Показывает popup с информацией об обновлении"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        update_text = f"New version available: {latest_version}\n\nWhat's new:\n{changelog}"
        text_label = Label(
            text=update_text,
            size_hint_y=0.7,
            text_size=(Window.width * 0.7 - 20, None),
            halign='left',
            valign='top'
        )
        text_label.bind(size=text_label.setter('text_size'))
        
        scroll_text = ScrollView(size_hint_y=0.7)
        scroll_text.add_widget(text_label)
        content.add_widget(scroll_text)
        
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        update_btn = Button(text="Download Update", background_color=(0.2, 0.7, 0.3, 1))
        cancel_btn = Button(text="Later", background_color=(0.8, 0.3, 0.3, 1))
        btn_box.add_widget(update_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(
            title="Update Available!",
            content=content,
            size_hint=(0.8, 0.7),
            auto_dismiss=False
        )
        
        def download_update(instance):
            webbrowser.open("https://github.com/mortualer/MemeCloud/releases/latest")
            popup.dismiss()
        
        update_btn.bind(on_release=download_update)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    MyApp().run()
