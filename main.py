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
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
import os
import requests
import webbrowser
import json
import shutil
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, check_permission, Permission
    from android.storage import primary_external_storage_path, app_storage_path

# -------------------------
# SoundButton Class
# -------------------------
class SoundButton(BoxLayout):
    current_button = None

    def __init__(self, text, sound, icon_path=None, app=None, sound_id=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.sound_id = sound_id or text
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
        self._long_press_trigger = Clock.create_trigger(self.expand, 0.5)

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
        anim = Animation(rgba=(0.5, 0.5, 0.7, 1), duration=0.2) + \
               Animation(rgba=(0.25, 0.25, 0.35, 1), duration=0.2)
        anim.repeat = True
        anim.start(self.bg_color)
        self.highlight_anim = anim

    def stop_highlight(self):
        if self.highlight_anim:
            self.highlight_anim.cancel(self.bg_color)
            self.highlight_anim = None
        self.bg_color.rgba = (0.25, 0.25, 0.35, 1)

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
            self._long_press_trigger()
        return False

    def end_long_press(self, instance, touch):
        self._long_press_trigger.cancel()
        return False

    def expand(self, *args):
        if self.is_expanded:
            return
        if self.app:
            for btn in self.app.buttons:
                if btn != self and btn.is_expanded and not getattr(self.app, "pin_active", False):
                    btn.collapse()
        self.is_expanded = True
        
        # Воспроизводим звук при расширении
        self.play_sound()
        self.create_expanded_view()
        
        anim = Animation(pos=(0, 0), size=(Window.width, Window.height), duration=0.3, t='out_quad')
        anim.start(self)

    def create_expanded_view(self):
        self.clear_widgets()
        
        expanded_layout = BoxLayout(orientation='vertical', spacing=15, padding=25)
        expanded_layout.bind(on_touch_down=self.on_expanded_touch)
        
        title_label = Label(
            text=self.btn_text,
            size_hint_y=None,
            height=120,
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        title_label.bind(on_touch_down=self.on_title_touch)
        expanded_layout.add_widget(title_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=120, spacing=15)
        
        delete_btn = Button(
            text='DELETE',
            size_hint_x=0.6,
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        delete_btn.bind(on_press=self.delete_sound)
        btn_layout.add_widget(delete_btn)
        
        close_btn = Button(
            text='CLOSE',
            size_hint_x=0.4,
            background_color=(0.5, 0.5, 0.7, 1),
            color=(1, 1, 1, 1),
            font_size='18sp'
        )
        close_btn.bind(on_press=lambda x: self.collapse())
        btn_layout.add_widget(close_btn)
        
        expanded_layout.add_widget(btn_layout)
        self.add_widget(expanded_layout)

    def on_expanded_touch(self, instance, touch):
        if self.is_expanded and touch.is_double_tap:
            self.play_sound()
            return True
        return False

    def on_title_touch(self, instance, touch):
        if self.is_expanded and instance.collide_point(*touch.pos):
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
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f'Delete "{self.btn_text}"?'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        yes_btn = Button(text='Yes', background_color=(0.8, 0.3, 0.3, 1))
        no_btn = Button(text='No')
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.7, 0.4))
        yes_btn.bind(on_release=confirm_delete)
        no_btn.bind(on_release=popup.dismiss)
        popup.open()

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        
        self.stop_sound_and_collapse()
        self.restore_original_view()
        
        anim = Animation(size=(self.width, 150), pos=self.pos, duration=0.3, t='out_quad')
        anim.start(self)

    def restore_original_view(self):
        self.clear_widgets()
        for widget in self.original_widgets:
            self.add_widget(widget)

    def stop_sound_and_collapse(self):
        if self.sound:
            self.sound.stop()
        self.stop_highlight()
        if self.sound_check_event:
            self.sound_check_event.cancel()
            self.sound_check_event = None

class DraggableBox(BoxLayout):
    def on_touch_down(self, touch):
        for child in reversed(self.children):
            if child.collide_point(*touch.pos):
                child.drag_start_y = touch.y
                self.dragged = child
                self.drag_index = self.children.index(child)
                return super().on_touch_down(touch)
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if hasattr(self, 'dragged') and self.dragged:
            dy = touch.y - self.dragged.drag_start_y
            self.dragged.y += dy
            self.dragged.drag_start_y = touch.y
            children_sorted = sorted(self.children, key=lambda w: w.y, reverse=True)
            self.clear_widgets()
            for w in children_sorted:
                self.add_widget(w)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.dragged = None
        return super().on_touch_up(touch)

class MyApp(App):
    CURRENT_VERSION = "1.2.0"
    UPDATE_URL = "https://raw.githubusercontent.com/mortualer/MemeCloud/main/update.json"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path, app_storage_path
                self.save_dir = os.path.join(primary_external_storage_path(), "MemeCloud", "saved_sounds")
            except Exception:
                from android.storage import app_storage_path
                self.save_dir = os.path.join(app_storage_path(), "saved_sounds")
        else:
            self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_sounds")

        self.settings_file = os.path.join(self.save_dir, "app_settings.json")
        print(f"Save directory: {self.save_dir}")

        os.makedirs(self.save_dir, exist_ok=True)
        self.buttons = []
        self.pin_active = False
        self.sound_settings = {}
        self.load_settings()

    def build(self):
        if platform == 'android':
            self.request_android_permissions()
        
        Window.clearcolor = (0.95, 0.95, 0.98, 1)
        root = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, None), height=75, spacing=15)

        self.search_input = TextInput(size_hint=(1, 1), hint_text="Search...", multiline=False,
                                      background_color=(0.9, 0.9, 0.95, 1), foreground_color=(0, 0, 0, 1))
        self.search_input.bind(text=self.filter_buttons)
        top_bar.add_widget(self.search_input)

        self.pin_button = Button(text="Pin", size_hint=(None, 1), width=100,
                                 background_color=(0.3, 0.8, 0.3, 1), color=(1, 1, 1, 1))
        self.pin_button.bind(on_release=self.toggle_pin)
        top_bar.add_widget(self.pin_button)

        self.upload_button = Button(text="Upload", size_hint=(None, 1), width=175,
                                    background_color=(0.5, 0.8, 0.5, 1), color=(1, 1, 1, 1))
        self.upload_button.bind(on_release=self.open_filechooser)
        top_bar.add_widget(self.upload_button)

        self.settings_button = Button(text="i", size_hint=(None, 1), width=100,
                                     background_color=(0.4, 0.4, 0.6, 1), color=(1, 1, 1, 1),
                                     font_size='14sp')
        self.settings_button.bind(on_release=self.open_settings)
        top_bar.add_widget(self.settings_button)

        root.add_widget(top_bar)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = DraggableBox(orientation='vertical', spacing=15, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        root.add_widget(self.scroll)

        self.load_existing_sounds()
        
        Clock.schedule_once(lambda dt: self.check_for_update(), 3)
        return root

    def on_start(self):
        print("App started")
        if platform == 'android':
            Clock.schedule_once(self.check_android_permissions, 1)
        
        # Копируем встроенные mp3 при первом запуске
        try:
            app_root = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.join(app_root, "saved_sounds")
            dst_dir = self.save_dir
            if os.path.exists(src_dir):
                for file in os.listdir(src_dir):
                    if file.lower().endswith(".mp3"):
                        src = os.path.join(src_dir, file)
                        dst = os.path.join(dst_dir, file)
                        if not os.path.exists(dst):
                            shutil.copy2(src, dst)
                            print(f"Copied {file}")
                # Перезагружаем звуки после копирования
                Clock.schedule_once(lambda dt: self.load_existing_sounds(), 1)
        except Exception as e:
            print("Error copying default sounds:", e)

    def request_android_permissions(self):
        if platform == 'android':
            try:
                print("Requesting Android permissions...")
                from android.permissions import request_permissions, Permission
                
                permissions = [
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.MANAGE_EXTERNAL_STORAGE
                ]
                
                request_permissions(permissions)
                print("Permissions requested")
                
            except Exception as e:
                print(f"Permission request failed: {e}")

    def check_android_permissions(self, dt):
        if platform == 'android':
            try:
                from android.permissions import check_permission, Permission
                
                permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
                for perm in permissions:
                    if not check_permission(perm):
                        print(f"Permission {perm} not granted")
                        return
                print("All permissions granted")
                
            except Exception as e:
                print(f"Permission check error: {e}")

    def load_settings(self):
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
        name = os.path.splitext(filename)[0]
        
        unwanted_phrases = [
            "Sound Button", "sound button", "SoundButton", "soundbutton",
            "Sound", "sound", "Button", "button", "MP3", "mp3"
        ]
        
        for phrase in unwanted_phrases:
            name = name.replace(phrase, "")
        
        name = name.replace("_", " ").replace("-", " ").strip()
        name = " ".join(name.split())
        
        if not name:
            name = os.path.splitext(filename)[0]
            
        return name

    def load_existing_sounds(self):
        print(f"Loading sounds from: {self.save_dir}")
        
        if not os.path.exists(self.save_dir):
            print(f"Creating directory: {self.save_dir}")
            os.makedirs(self.save_dir, exist_ok=True)
            return
        
        # Очищаем существующие кнопки
        self.layout.clear_widgets()
        self.buttons.clear()
        
        print("Scanning for MP3 files...")
        for filename in sorted(os.listdir(self.save_dir)):
            if filename.lower().endswith('.mp3'):
                sound_path = os.path.join(self.save_dir, filename)
                print(f"Found MP3: {filename}")
                self.add_sound_button(sound_path)
        
        print(f"Total sounds loaded: {len(self.buttons)}")

    def add_sound_button(self, path):
        # Проверяем если этот звук уже существует в кнопках
        for btn in self.buttons:
            if btn.sound_id in path:
                return  # Пропускаем если уже существует
        
        filename = os.path.basename(path)
        btn_text = self.clean_sound_name(filename)
        sound_id = os.path.splitext(filename)[0]
        
        print(f"Loading sound: {filename}")
        
        # Ищем иконку
        icon_file = os.path.join(os.path.dirname(path), self.clean_sound_name(filename) + ".png")
        if not os.path.exists(icon_file):
            icon_file = os.path.join(os.path.dirname(path), os.path.splitext(filename)[0] + ".png")
        
        sound = SoundLoader.load(path)
        if sound:
            print(f"Sound loaded: {filename}")
            btn_widget = SoundButton(btn_text, sound, icon_file, app=self, sound_id=sound_id)
            
            if sound_id in self.sound_settings:
                btn_widget.volume = self.sound_settings[sound_id].get('volume', 1.0)
            
            self.layout.add_widget(btn_widget)
            self.buttons.append(btn_widget)
        else:
            print(f"Failed to load: {filename}")

    def delete_sound(self, sound_button):
        try:
            for btn in self.buttons[:]:
                if btn == sound_button:
                    if btn.sound:
                        btn.sound.stop()
                    
                    self.layout.remove_widget(btn)
                    self.buttons.remove(btn)
                    
                    sound_id = btn.sound_id
                    for filename in os.listdir(self.save_dir):
                        if filename.startswith(sound_id) or sound_id in filename:
                            file_path = os.path.join(self.save_dir, filename)
                            try:
                                os.remove(file_path)
                                print(f"Removed: {file_path}")
                            except Exception as e:
                                print(f"Error removing file: {e}")
                    
                    if sound_id in self.sound_settings:
                        del self.sound_settings[sound_id]
                        self.save_sound_settings()
                    
                    break
                    
        except Exception as e:
            print(f"Error deleting sound: {e}")
            self.show_error_popup("Error deleting sound")

    def open_filechooser(self, instance):
        print("Opening file chooser...")
        
        content = BoxLayout(orientation='vertical', spacing=10)
        
        if platform == 'android':
            initial_path = "/storage/emulated/0/"
        else:
            initial_path = "/"
            
        filechooser = FileChooserListView(
            filters=['*.mp3'], 
            path=initial_path,
            size_hint=(1, 0.8)
        )
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=80, spacing=10)
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(select_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(title="Select MP3 File", content=content, size_hint=(0.9, 0.9))

        def select_file(instance):
            if filechooser.selection:
                for path in filechooser.selection:
                    try:
                        print(f"Selected: {path}")
                        filename = os.path.basename(path)
                        new_path = os.path.join(self.save_dir, filename)
                        
                        if os.path.exists(new_path):
                            base, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(new_path):
                                new_path = os.path.join(self.save_dir, f"{base}_{counter}{ext}")
                                counter += 1
                        
                        import shutil
                        shutil.copy2(path, new_path)
                        print(f"Copied to: {new_path}")
                        
                        self.add_sound_button(new_path)
                            
                    except Exception as e:
                        print(f"Copy error: {e}")
                        self.show_error_popup(f"Upload error: {e}")
                popup.dismiss()
            else:
                print("No file selected")

        select_btn.bind(on_release=select_file)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        popup.open()

    def open_settings(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        info_label = Label(
            text=f"MemeCloud v{self.CURRENT_VERSION}\n\nDebug Info:\n• Sounds loaded: {len(self.buttons)}\n• Save dir: {self.save_dir}\n• Icons: {'Loaded' if os.path.exists('icon.png') else 'Missing'}",
            size_hint_y=None,
            height=200,
            text_size=(Window.width * 0.8 - 40, None),
            halign='center',
            valign='top'
        )
        info_label.bind(size=info_label.setter('text_size'))
        content.add_widget(info_label)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        github_btn = Button(text="GitHub", background_color=(0.3, 0.3, 0.5, 1))
        github_btn.bind(on_release=lambda x: webbrowser.open("https://github.com/mortualer/MemeCloud"))
        
        close_btn = Button(text="Close", background_color=(0.5, 0.5, 0.7, 1))
        
        btn_layout.add_widget(github_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Settings & Info", content=content, size_hint=(0.8, 0.6))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def toggle_pin(self, instance):
        self.pin_active = not self.pin_active
        if self.pin_active:
            instance.background_color = (0.15, 0.25, 0.45, 1)
        else:
            instance.background_color = (0.3, 0.8, 0.3, 1)

        for btn in self.buttons:
            if btn.is_expanded:
                if self.pin_active:
                    btn.pinned = True
                else:
                    btn.pinned = False
                    btn.collapse()

    def filter_buttons(self, *args):
        value = self.search_input.text.lower()
        for btn_widget in self.buttons:
            visible = value in btn_widget.btn_text.lower()
            btn_widget.opacity = 1 if visible else 0
            btn_widget.disabled = not visible
            btn_widget.height = 150 if visible else 0

    def show_error_popup(self, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message))
        close_btn = Button(text="OK", size_hint_y=None, height=50)
        content.add_widget(close_btn)
        
        popup = Popup(title="Error", content=content, size_hint=(0.6, 0.3))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def check_for_update(self):
        try:
            print("Checking for updates...")
            response = requests.get(self.UPDATE_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('version', '')
                download_url = data.get('download_url', '')
                changelog = data.get('changelog', '')
                
                if latest_version and latest_version != self.CURRENT_VERSION:
                    print(f"Update available: {latest_version}")
                    self.show_update_popup(latest_version, download_url, changelog)
                else:
                    print("No updates available")
            else:
                print(f"Update check failed: {response.status_code}")
        except Exception as e:
            print(f"Update check error: {e}")

    def show_update_popup(self, latest_version, download_url, changelog):
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
