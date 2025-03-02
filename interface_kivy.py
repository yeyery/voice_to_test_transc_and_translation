from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from Vosk_to_text import continuous_transcription

Window.size = (1480, 320)
Window.clearcolor = (17/255, 24/255, 39/255, 1)
Window.fullscreen = 'auto'

class MainApp(App):
    def build(self):

        screen_res = (1480, 320)

        layout = BoxLayout(orientation='vertical', size=screen_res, size_hint=(1,1))

        self.scroll_view = ScrollView(size_hint=(1, 1), size=screen_res)

        self.text_label = Label(
            text="Hello World\n",
            size_hint_y=None,
            width=320,
            text_size=(320, None),
            font_size=47,
            halign="left",
            valign="top"
        )

        # needed to align the text
        self.text_label.bind(texture_size=self.text_label.setter("size"))
        self.text_label.bind(size=self.update_text_size)
        self.text_label.bind(size=self.scroll_bottom)

        self.scroll_view.add_widget(self.text_label)

        layout.add_widget(self.scroll_view)

        self.generator = continuous_transcription()

        Clock.schedule_interval(self.update_transcription, 1)

        return layout

    def update_transcription(self, dt):
        try:
            transcription = next(self.generator)
            self.add_text(transcription)
        except StopIteration:
            pass

    def update_text_size(self, instance, value):
        instance.text_size = (instance.width, None)

    def scroll_bottom(self, instance, value):
        if self.text_label.height > self.scroll_view.height:
            self.scroll_view.scroll_y = 0
    
    def add_text(self, text: str) -> None:
        self.text_label.text += f"{text}\n"

    
if __name__ == "__main__":
    MainApp().run()