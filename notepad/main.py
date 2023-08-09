from ctypes import byref, c_char_p, c_int, sizeof, windll
from tkinter import Event, Frame, Misc, Text, Tk
from tkinter.ttk import Label, Scrollbar

from darkdetect import isDark
from sv_ttk import set_theme

from win32mica import ApplyMica


class AutoHideScrollbar(Scrollbar):
    def set(self, upper: str, lower: str):
        if float(upper) <= 0.0 and float(lower) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side="right", fill="y")

        Scrollbar.set(self, upper, lower)


class Editor(Frame):
    def __init__(self, master: Misc | None = None, theme: str = "dark") -> None:
        super().__init__(master=master)

        self.edit = Frame(self)

        self.text = Text(
            self.edit,
            relief="flat",
            font=("Consolas", 11, "normal"),
            wrap="char",
            background="#272727",
        )

        self.yscrollbar = AutoHideScrollbar(self.edit)
        self.text.config(yscrollcommand=self.yscrollbar.set)
        self.yscrollbar.config(command=self.text.yview, orient="vertical")

        self.ln: str = 0
        self.col: str = 1

        self.backgroundcolor = "#020202" if isDark() else "#fffff2"
        self.foregroundcolor = "#CCCCCC" if isDark() else "#595959"
        self.theme = theme.lower()

        self.statusbar = Frame(self, height=30, background=self.backgroundcolor)
        self.insertindex = Label(self.statusbar)
        self.insertindex.config(
            foreground=self.foregroundcolor,
            font=("Segoe UI", 9),
            background=self.backgroundcolor,
        )

        self.text.pack(fill="both", side="left", expand=True)
        self.yscrollbar.pack(side="right", fill="y")

        self.edit.pack(fill="both", expand=True)

        self.insertindex.pack(fill="x", side="left", padx=25, pady=2)

        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(0)

        self.text.bind("<KeyPress>", self.update)
        self.text.bind("<Button-1>", self.update)

        set_theme(self.theme)

        self.update(None)

    def update(self, event: Event) -> None:
        """update the statusbar"""
        self.ln, self.col = self.text.index("insert").split(".")
        self.insertindex.config(text="Ln %s, Col %s" % (self.ln, int(self.col) + 1))


class Window(Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Notepad")
        self.geometry("1275x665")
        self.iconbitmap("")

        self.theme = "dark" if isDark else "light"

        self.dark_title_bar()
        ApplyMica(windll.user32.FindWindowW(c_char_p(None), "Notepad"), self.theme)

        self.editor = Editor(theme=self.theme)
        self.editor.pack(fill="both", expand=True)

    def dark_title_bar(self, mode: bool = True):
        value = c_int(2 if mode else 0)
        windll.dwmapi.DwmSetWindowAttribute(
            windll.user32.GetParent(self.winfo_id()), 20, byref(value), sizeof(value)
        )
        self["background"] = "black"


if __name__ == "__main__":
    notepad = Window()
    notepad.mainloop()
