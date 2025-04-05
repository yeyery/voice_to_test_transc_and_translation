import tkinter as tk
from PIL import Image, ImageTk
from Vosk_to_text import continuous_transcription
import word2number as w2n

def update_translation(generator, text_widget: tk.Text, root: tk.Tk) -> None:
    """
    This function retreive the last transcription from Vosk_to_text.py and
    insert it into the GUI
    """

    # generator returns and iterator so use next to get the latest transcription
    transcriptions = next(generator)
   
    # end-1c means read to the end and remove a chracter. the \n is the last character

    # TODO: This was going to be for the timeout function
    if transcriptions == "SILENCE":
        text_widget.delete("1.0", "end")
    else:
        current_text = text_widget.get("1.0", 'end-1c')
        # keep only the first 200 characters
        current_text = current_text[:200]
        text_widget.delete("1.0", "end")
        text_widget.insert("end", f"{transcriptions}. ", "bold")
        text_widget.insert("end", f"{current_text}")

    # rerun this function after 1 second
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

    # set the background color
    main_frame = tk.Frame(root, bg='#111827')
    main_frame.pack(fill=tk.BOTH, expand=True)

    text_widget = tk.Text(
        main_frame,
        height=300,
        width=1250,
        font=("Helvetica", 40),
        bg='#111827',
        fg="#F3F4F6",
        # bd and highlightthickness is to remove the borders around the widget
        bd=0,
        highlightthickness=0,
        wrap="word",
    )

    #remove cursor
    text_widget.config(cursor="none")
    # configure a bold option
    text_widget.tag_configure("bold", font="Helvetica 40 bold")
    # places the widget in the GUI
    text_widget.place(x=15, y=10, height=300, width=1250)
    # stop user input
    # text_widget.config(state="disabled")

    image_frame = tk.Frame(main_frame, bg='#111827', width=200)
    image_frame.pack(side=tk.RIGHT, anchor="se", padx=10, pady=10)

    # load the image
    logo = Image.open("./pictures/NSCC_logo_backgroundless.png")
    logo = logo.resize((200, 60))
    # make it ok for Tkinter
    logo_tk = ImageTk.PhotoImage(logo)
    image_label = tk.Label(image_frame, image=logo_tk, bg='#111827')
    image_label.pack()

    generator = continuous_transcription()

    root.after(1000, update_translation, generator, text_widget, root)

    # run the app
    root.mainloop()

if __name__ == "__main__":
    main()