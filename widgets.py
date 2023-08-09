from tkinter import Event, Frame, Misc, Text
from tkinter.filedialog import askopenfilename
from tkinter.ttk import Label, Scrollbar
from tkinter.messagebox import showerror

from darkdetect import isDark


class AutoHideScrollbar(Scrollbar):
    def set(self, upper: str, lower: str) -> None:
        if float(upper) <= 0.0 and float(lower) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side="right", fill="y")

        Scrollbar.set(self, upper, lower)


class Editor(Frame):
    def __init__(self, master: Misc | None = None) -> None:
        super().__init__(master=master)

        self.ln: str = 0
        self.col: str = 1
        self.encoding = "utf-8"  # TODO: move it to the settings later
        self.changed = False
        self.filepath = ""

        self.backgroundcolor = "#020202" if isDark() else "#fffff2"
        self.foregroundcolor = "#CCCCCC" if isDark() else "#595959"

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
        self.text.bind("<Control-o>", self.openfile)
        self.text.bind("<Control-s>", self.savefile)

        self.update(None)

    def update(self, event: Event) -> None:
        """update the statusbar"""
        self.ln, self.col = self.text.index("insert").split(".")
        self.insertindex.config(text="Ln %s, Col %s" % (self.ln, int(self.col) + 1))
        self.changed = True

    def savefile(self, event: Event | None = None, filepath: str = "") -> None:
        """Save file to target filepath"""
        try:
            with open(
                filepath
                if filepath
                else askopenfilename(
                    filetypes=(("Text file", "*.txt"), ("Any file", "*.*"))
                ),
                mode="w",
                encoding=self.encoding,
            ) as f:
                f.write(self.text.get(0.0, "end"))
        except PermissionError:
            showerror("Notepad", "Error, perminssion deied: '%s'" % self.filepath)
        else:
            self.changed = False

    def openfile(self, event: Event) -> None:
        """Open file from the filepath"""
        self.filepath = askopenfilename(
            filetypes=(("Text file", "*.txt"), ("Any file", "*.*"))
        )
        try:
            with open(self.filepath, mode="r", encoding=self.encoding) as f:
                self.text.insert("insert", f.read())
        except UnicodeDecodeError:
            showerror("Notepad", "Error, can not decode this file.")
        else:
            self.changed = False
