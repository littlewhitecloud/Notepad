from ctypes import byref, c_int, sizeof, windll
from tkinter import Tk
from tkinter.messagebox import askyesnocancel

from darkdetect import isDark
from sv_ttk import set_theme

from widgets import Editor
from win32mica import ApplyMica


class Window(Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Notepad")
        self.geometry("1275x665")
        self.iconbitmap("notepad.ico")

        self.theme = (
            "dark" if isDark() else "light"
        )  # TODO: move it to the settings later

        set_theme(self.theme)
        if self.theme == "dark":
            self.applyeffect()
            ApplyMica(
                windll.user32.GetParent(self.winfo_id()), True
            )  # TODO: make light theme able to use in light mode

        self.editor = Editor()
        self.editor.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.asksave)

    def applyeffect(self) -> None:
        """Apply Mica effect to the window and also dark the titlebar"""
        value = c_int(2)
        windll.dwmapi.DwmSetWindowAttribute(
            self.frame(), 20, byref(value), sizeof(value)
        )

        self["background"] = "black"

    def asksave(self) -> None:
        """Ask if you want to save when you want to leave"""
        if self.editor.changed:
            result = askyesnocancel(
                title="Notepad",
                message="Do you want to save %s?" % self.editor.filepath,
            )

            if result is None:
                return

            if result:
                self.editor.savefile(filepath=self.editor.filepath)

        self.destroy()


if __name__ == "__main__":
    notepad = Window()
    notepad.mainloop()
