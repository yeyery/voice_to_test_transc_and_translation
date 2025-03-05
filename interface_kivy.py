from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from Vosk_to_text import continuous_transcription

Window.size = (1480, 320)
Window.clearcolor = (17/255, 24/255, 39/255, 1)
Window.fullscreen = True

class MainApp(App):
    def build(self):
        screen_res = (1480, 320)

        layout = BoxLayout(orientation='vertical', size=screen_res, size_hint=(1,1))

        layout.add_widget(Widget(size_hint_y=None, height=40))  

        self.scroll_view = ScrollView(size_hint=(1, 1), size=screen_res, do_scroll_x=True, do_scroll_y=False)

        self.text_label = Label(
            text="",
            size_hint_x=None,  # Allow width expansion
            height=320,
            text_size=(None, None),  # Prevent forced wrapping
            font_size=47,
            halign="left",
            valign="middle"
        )

        # Needed to align the text
        self.text_label.bind(texture_size=self.update_label_size)
        self.text_label.bind(size=self.scroll_right)

        self.scroll_view.add_widget(self.text_label)

        layout.add_widget(self.scroll_view)

        return layout
    
    def on_start(self):
        Clock.schedule_once(self.start_transcription, 10)

    def start_transcription(self, _):
        self.generator = continuous_transcription()
        Clock.schedule_interval(self.update_transcription, 1)

    def update_transcription(self, dt):
        try:
            transcription = next(self.generator)
            self.add_text(transcription)
        except StopIteration:
            pass

    def update_label_size(self, instance, value):
        instance.width = instance.texture_size[0]  # Expand width dynamically

    def scroll_right(self, instance, value):
        # Keep scrolling to the right when new text is added
        self.scroll_view.scroll_x = 1

    def add_text(self, text: str) -> None:
        self.text_label.text = (self.text_label.text + f" {text}")[-5000:]  # Remove forced newlines

if __name__ == "__main__":
    MainApp().run()
