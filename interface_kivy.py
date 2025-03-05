from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from Vosk_to_text import continuous_transcription

Window.size = (1480, 320)
Window.clearcolor = (17/255, 24/255, 39/255, 1)
Window.fullscreen = False

class MainApp(App):
    def build(self):

        root = BoxLayout(orientation='horizontal')

        screen_res = (1480, 320)

        text_layout = BoxLayout(orientation='horizontal', size=screen_res, size_hint=(0.7, None))

        text_layout.add_widget(Widget(size_hint_y=None, height=40))  

        self.scroll_view = ScrollView(size_hint=(None, None), size=screen_res)

        self.text_label = Label(
            text="",
            size_hint_y=None,
            width=200,
            text_size=(200, None),
            font_size=47,
            halign="left",
            valign="top"
        )

        # needed to align the text
        self.text_label.bind(texture_size=self.text_label.setter("size"))
        self.text_label.bind(size=self.update_text_size)
        self.text_label.bind(size=self.scroll_bottom)

        self.scroll_view.add_widget(self.text_label)

        text_layout.add_widget(self.scroll_view)

        image_layout = AnchorLayout(anchor_x="right", anchor_y="top", size_hint_x=0.3)

        image = Image(source="./pictures/NSCC_logo_backgroundless.png", size_hint=(None, None), size=(200,200))

        image_layout.add_widget(image)

        root.add_widget(text_layout)
        root.add_widget(image_layout)

        return root
    
    def on_start(self):
        Clock.schedule_once(self.start_transcription, 30)

    def start_transcription(self, _):
        self.generator = continuous_transcription()
        Clock.schedule_interval(self.update_transcription, 1)

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
        # make it so that the maximum string size is 5000 chracters
        self.text_label.text = self.text_label.text[-5000:]

    
if __name__ == "__main__":
    MainApp().run()