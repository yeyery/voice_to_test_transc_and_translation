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

        # Enable horizontal scrolling and disable vertical scrolling
        self.scroll_view = ScrollView(size_hint=(1, 1), size=screen_res, do_scroll_x=True, do_scroll_y=False)

        self.text_label = Label(
            text="",
            size_hint_x=None,  # Allow the label to expand in width
            height=320,  # Fixed height
            text_size=(None, None),  # Prevent forced wrapping
            font_size=47,
            halign="left",
            valign="middle"
        )

        # Bind texture size to adjust width dynamically
        self.text_label.bind(texture_size=self.update_label_size)
        self.text_label.bind(size=self.scroll_right)

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

    def update_label_size(self, instance, value):
        """ Dynamically expand label width when new text is added """
        new_width = instance.texture_size[0]
        instance.width = max(new_width, Window.size[0] * 0.9)  # Ensure text grows, but not too much

    def scroll_right(self, instance, value):
        """ Automatically scroll to the right as text expands """
        self.scroll_view.scroll_x = 1  # Always keep scrolling at the end

    def add_text(self, text: str) -> None:
        """ Add text dynamically and limit to 5000 characters while keeping whole words intact """
        self.text_label.text = (self.text_label.text + f" {text}")[-5000:].lstrip()

if __name__ == "__main__":
    MainApp().run()
