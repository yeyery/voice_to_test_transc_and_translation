import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from Vosk_to_text import continuous_transcription

def update_translation(generator, text_widget: ScrolledText, root: tk.Tk) -> None:
    transcriptions = next(generator)
    text_widget.insert(tk.END, f"{transcriptions}\n")
    # text_widget.insert(tk.END, f"Fn: {transcriptions['french']}\n")
    text_widget.see("end")

    root.after(1000, update_translation, generator, text_widget, root)

def main() -> None:

    # initialize tkinter object
    root = tk.Tk()

    # destroy the app when the escape button is hit
    root.bind("<Escape>", lambda _: root.destroy())

    # full screen the app
    root.attributes("-fullscreen", True)

    # make the demensions of your app the same as the demensions of your screen
    root.geometry('%dx%d+0+0' % (1480,320))

    # make background black
    root.configure(background='#111827')

    text_widget = ScrolledText(root, 
                               height=320, 
                               width=1480,
                               font=("Helvetica", 45),
                               bg='#111827',
                               fg="#F3F4F6",
                               wrap="word")

    text_widget.pack(expand=True, fill="both")

    # get rid of the scroll bar
    text_widget.vbar.pack_forget()

    generator = continuous_transcription()

    root.after(1000, update_translation, generator, text_widget, root)

    # run the app
    root.mainloop()

if __name__ == "__main__":
    main()