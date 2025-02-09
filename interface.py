import tkinter as tk
from tkinter.scrolledtext import ScrolledText

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

    while True:
        user_input = input("enter m: ")
        if user_input == "m":
            text_widget.insert(tk.END, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\n")
            text_widget.see("end")
        else:
            break
        
    # run the app
    root.mainloop()

if __name__ == "__main__":
    main()