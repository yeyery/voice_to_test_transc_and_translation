import dearpygui.dearpygui as dpg
from Vosk_to_text import continuous_transcription
import threading
import time

# Global Variables
generator = None
transcription_text = ""

def update_text():
    global transcription_text
    try:
        transcription = next(generator)
        transcription_text += f"{transcription}. "
        transcription_text = transcription_text[-300:]
        dpg.set_value("transcription_label", transcription_text)
    except StopIteration:
        pass


def start_transcription():
    """
    This function gets the transcriptions
    """

    global generator
    generator = continuous_transcription()

    while True:
        update_text()
        time.sleep(1)


def main():
    
    dpg.create_context()

    # get image data
    width, height, channels, data = dpg.load_image("./pictures/NSCC_logo_backgroundless.png")

    # close the app when the esc key is pressed
    with dpg.handler_registry():
        dpg.add_key_press_handler(dpg.mvKey_Escape, callback=lambda: dpg.stop_dearpygui())

    # get the image
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag="NSCC Logo")

    with dpg.font_registry():
        font = dpg.add_font("./fonts/OpenSans-Regular.ttf", 60)

    with dpg.window(tag="Primary Window") as main_window:
        dpg.bind_font(font)
        with dpg.group(horizontal=True):
            with dpg.child_window(height=260, width=1250, border=False,tag="text"):
                dpg.add_text("", tag="transcription_label", wrap=1250)

            with dpg.child_window(height=260, width=200, border=False, tag="logo"):
                image = dpg.add_image("NSCC Logo", width=200, height=60)
                dpg.set_item_pos(image, (-20, 200))
    
    dpg.create_viewport(title="Speech To Text Chatbot", width=1480, height=320)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    threading.Thread(target=start_transcription, daemon=True).start()

    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()