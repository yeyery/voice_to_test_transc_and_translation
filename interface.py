import tkinter as tk
from PIL import Image, ImageTk
from Vosk_to_text import continuous_transcription

def update_translation(generator, text_widget: tk.Label, root: tk.Tk) -> None:
    transcriptions = next(generator)
    current_text = text_widget["text"]
    update_text = f"{transcriptions}. "+current_text
    update_text = update_text[:1000]
    text_widget.config(text=update_text)

    root.after(1000, update_translation, generator, text_widget, root)

def main() -> None:

    # initialize tkinter object
    root = tk.Tk()

    # destroy the app when the escape button is hit
    root.bind("<Escape>", lambda _: root.destroy())

    # remove the cursor
    root.config(cursor="none")

    # full screen the app
    root.attributes("-fullscreen", False)

    # make the demensions of your app the same as the demensions of your screen
    root.geometry('%dx%d' % (1480,320))

    # make background black
    root.configure(background='#111827')

    main_frame = tk.Frame(root, bg='#111827')
    main_frame.pack(fill=tk.BOTH, expand=True)

    text_widget = tk.Label(
        main_frame,
        text="",
        height=320,
        wraplength=1250,
        justify=tk.LEFT,
        font=("Helvetica", 40),
        bg='#111827',
        fg="#F3F4F6",
        anchor="nw"
    )

    text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

    image_frame = tk.Frame(main_frame, bg='#111827', width=200)
    image_frame.pack(side=tk.RIGHT, anchor="se", padx=10, pady=10)

    logo = Image.open("./pictures/NSCC_logo_backgroundless.png")
    logo = logo.resize((200, 60))
    logo_tk = ImageTk.PhotoImage(logo)
    image_label = tk.Label(image_frame, image=logo_tk, bg='#111827')
    image_label.pack()

    generator = continuous_transcription()

    root.after(1000, update_translation, generator, text_widget, root)

    # run the app
    root.mainloop()

if __name__ == "__main__":
    main()