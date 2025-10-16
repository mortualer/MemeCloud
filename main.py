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
import os
import requests
import webbrowser
from kivy.utils import platform

# -------------------------
# Класс SoundButton
# -------------------------
class SoundButton(BoxLayout):
    current_button = None  # Текущая воспроизводимая кнопка

    def __init__(self, text, sound, icon_path=None, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 150
        self.spacing = 10
        self.padding = [10, 10, 10, 10]
        self.sound = sound
        self.btn_text = text
        self.is_expanded = False
        self.pinned = False

        # Фон и тень
        with self.canvas.before:
            Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(pos=(self.x - 2, self.y - 2),
                                           size=(self.width + 4, self.height + 4),
                                           radius=[20])
            self.bg_color = Color(0.25, 0.25, 0.35, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])

        if icon_path and os.path.exists(icon_path):
            icon = Image(source=icon_path, size_hint=(None, 1), width=50)
            self.add_widget(icon)

        # Кнопка
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
            self.sound.stop()
            self.sound.play()
            self.start_highlight()
            Clock.schedule_interval(self.check_sound, 0.1)

    def start_highlight(self):
        anim = Animation(rgba=(0.5, 0.5, 0.7, 1), duration=0.2) + \
               Animation(rgba=(0.25, 0.25, 0.35, 1), duration=0.2)
        anim.repeat = True
        anim.start(self.bg_color)
        self.highlight_anim = anim

    def stop_highlight(self):
        if hasattr(self, "highlight_anim"):
            self.highlight_anim.cancel(self.bg_color)
            self.bg_color.rgba = (0.25, 0.25, 0.35, 1)

    def check_sound(self, dt):
        if self.sound.state != 'play':
            self.stop_highlight()
            if self.is_expanded and not getattr(App.get_running_app(), "pin_active", False):
                self.collapse()
            return False
        return True

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
        anim = Animation(pos=(0, 0), size=(Window.width, Window.height), duration=0.3, t='out_quad')
        anim.start(self)

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        anim = Animation(size=(self.width, 150), pos=self.pos, duration=0.3, t='out_quad')
        anim.start(self)

    def stop_sound_and_collapse(self):
        if self.sound:
            self.sound.stop()
        self.stop_highlight()
        if not getattr(App.get_running_app(), "pin_active", False):
            self.collapse()


# -------------------------
# Класс DraggableBox
# -------------------------
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


# -------------------------
# Основное приложение
# -------------------------
class MyApp(App):
    CURRENT_VERSION = "1.0.0"
    GITHUB_REPO = "mortualer/SoundCloud"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_sounds")
        self.save_file = os.path.join(self.save_dir, "saved_paths.txt")
        os.makedirs(self.save_dir, exist_ok=True)
        self.buttons = []
        self.pin_active = False

    def build(self):
        # ------------------------------
        # Запрос разрешений на Android
        # ------------------------------
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
                # Manage External Storage (Android 11+)
                try:
                    from jnius import autoclass
                    Intent = autoclass('android.content.Intent')
                    Uri = autoclass('android.net.Uri')
                    Settings = autoclass('android.provider.Settings')
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    currentActivity = PythonActivity.mActivity
                    if not Settings.canManageExternalStorage(currentActivity):
                        intent = Intent(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        uri = Uri.parse('package:' + currentActivity.getPackageName())
                        intent.setData(uri)
                        currentActivity.startActivity(intent)
                except Exception as e:
                    print("Manage External Storage request failed:", e)
            except Exception as e:
                print("Permission request failed:", e)

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

        root.add_widget(top_bar)

        self.scroll = ScrollView(size_hint=(1, 1))
        self.layout = DraggableBox(orientation='vertical', spacing=15, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)
        root.add_widget(self.scroll)

        self.load_existing_sounds()
        Clock.schedule_once(lambda dt: self.check_for_update(), 1)
        return root

    # Загрузка сохранённых звуков
    def load_existing_sounds(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", encoding="utf-8") as f:
                for line in f:
                    path = line.strip()
                    if os.path.exists(path):
                        self.add_sound_button(path)
        if not self.buttons and os.path.exists(self.save_dir):
            for filename in sorted(os.listdir(self.save_dir)):
                if filename.lower().endswith(".mp3"):
                    self.add_sound_button(os.path.join(self.save_dir, filename))

    def add_sound_button(self, path):
        btn_text = os.path.splitext(os.path.basename(path))[0]
        icon_file = os.path.join(os.path.dirname(path), btn_text + ".png")
        sound = SoundLoader.load(path)
        btn_widget = SoundButton(btn_text, sound, icon_file, app=self)
        self.layout.add_widget(btn_widget)
        self.buttons.append(btn_widget)

    def open_filechooser(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10)
        filechooser = FileChooserListView(filters=['*.mp3'], path="/storage/emulated/0/")
        content.add_widget(filechooser)

        btn_box = BoxLayout(size_hint_y=None, height=80, spacing=10)
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(select_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(title="Select MP3 file", content=content, size_hint=(0.9, 0.9))

        def select_file(instance):
            if filechooser.selection:
                for path in filechooser.selection:
                    try:
                        filename = os.path.basename(path)
                        new_path = os.path.join(self.save_dir, filename)
                        if os.path.exists(new_path):
                            base, ext = os.path.splitext(filename)
                            new_path = os.path.join(self.save_dir, f"{base}_1{ext}")
                        os.rename(path, new_path)
                        self.add_sound_button(new_path)
                        with open(self.save_file, "a", encoding="utf-8") as f:
                            f.write(new_path + "\n")
                    except Exception as e:
                        print("File move error:", e)
                popup.dismiss()

        select_btn.bind(on_release=select_file)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        popup.open()

    # --- Pin кнопка ---
    def toggle_pin(self, instance):
        self.pin_active = not self.pin_active
        if self.pin_active:
            instance.background_color = (0.15, 0.25, 0.45, 1)  # тёмный
        else:
            instance.background_color = (0.3, 0.8, 0.3, 1)  # зелёный

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

    def check_for_update(self):
        try:
           url = "https://api.github.com/repos/mortualer/SoundCloud/releases/latest"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data['tag_name']
                if latest_version != self.CURRENT_VERSION:
                    self.show_update_popup(latest_version, data['html_url'])
        except Exception as e:
            print("Update check failed:", e)

    def show_update_popup(self, latest_version, url):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Button(text=f"New version available: {latest_version}",
                                  background_color=(0, 0, 0, 0), color=(0, 0, 0, 1)))
        btn_box = BoxLayout(size_hint_y=None, height=50, spacing=10)
        update_btn = Button(text="Update")
        cancel_btn = Button(text="Cancel")
        btn_box.add_widget(update_btn)
        btn_box.add_widget(cancel_btn)
        content.add_widget(btn_box)

        popup = Popup(title="Update Available", content=content, size_hint=(0.8, 0.4))
        update_btn.bind(on_release=lambda x: webbrowser.open(url))
        update_btn.bind(on_release=popup.dismiss)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()


if __name__ == "__main__":
    MyApp().run()