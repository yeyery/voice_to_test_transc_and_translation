import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
from Vosk_to_text import continuous_transcription

def update_translation(text_widget: ScrolledText, root: tk.Tk) -> None:
    transcriptions = next(continuous_transcription())
    text_widget.insert(tk.END, f"En: {transcriptions['english']}\n")
    text_widget.insert(tk.END, f"Fn: {transcriptions['french']}\n")
    text_widget.see("end")

    root.after(1500, update_translation, text_widget, root)

def main() -> None:

    # initialize tkinter object
    root = tk.Tk()

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

    text_widget.pack()

    threading.Thread(target=update_translation, args=(text_widget, root)).start()

    # run the app
    root.mainloop()

if __name__ == "__main__":
    main()