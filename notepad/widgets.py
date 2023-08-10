from tkinter import Button, Event, Frame, Misc, Text
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from tkinter.ttk import Label, Scrollbar, Separator

from darkdetect import isDark


class AutoHideScrollbar(Scrollbar):
    def set(self, upper: str, lower: str) -> None:
        if float(upper) <= 0.0 and float(lower) >= 1.0:
            self.pack_forget()
        else:
            self.pack(side="right", fill="y")

        Scrollbar.set(self, upper, lower)


class EditMenubar(Frame):
    def __init__(
        self,
        master: Misc | None = None,
        background: str = ...,
    ) -> None:
        super().__init__(master, background=background)

        self.filebutton = Button(self, text="File")
        self.editbutton = Button(self, text="Edit")
        self.viewbutton = Button(self, text="View")

        for target_button in (self.filebutton, self.editbutton, self.viewbutton):
            target_button.pack(fill="x", side="left", padx=5, pady=2)
            target_button.config(background=self.master.backgroundcolor, relief="flat")


class Editor(Frame):
    def __init__(self, master: Misc | None = None) -> None:
        super().__init__(master=master)

        # Some variable
        self.ln: str = 0
        self.col: str = 1
        self.encoding = "utf-8"  # TODO: move it to the settings later
        self.changed = False
        self.filepath = ""

        self.backgroundcolor = "#020202" if isDark() else "#F8F8F8"
        self.foregroundcolor = "#CCCCCC" if isDark() else "#595959"

        # Create the widgets
        self.editmenu = EditMenubar(self, background=self.backgroundcolor)
        self.editmenu.pack(side="top", fill="x")

        self.edit = Frame(self)
        self.text = Text(
            self.edit,
            relief="flat",
            font=("Consolas", 11, "normal"),
            wrap="char",
            background="#272727" if isDark() else "white",
        )
        self.yscrollbar = AutoHideScrollbar(self.edit)

        self.statusbar = Frame(self, height=30, background=self.backgroundcolor)
        self.insertindex = Label(self.statusbar)
        self.separator = Separator(self.statusbar, orient="vertical")
        self.separator2 = Separator(self.statusbar, orient="vertical")
        self.encode = Label(self.statusbar)
        self.lineend = Label(self.statusbar)

        # Config the widgets
        self.insertindex.config(
            foreground=self.foregroundcolor,
            font=("Segoe UI", 9),
            background=self.backgroundcolor,
        )
        self.encode.config(
            foreground=self.foregroundcolor,
            font=("Segoe UI", 8),
            background=self.backgroundcolor,
            text=self.encoding.upper(),
        )
        self.lineend.config(
            foreground=self.foregroundcolor,
            font=("Segoe UI", 8),
            background=self.backgroundcolor,
            text="Windows (CRLF)",
        )
        self.text.config(yscrollcommand=self.yscrollbar.set)
        self.yscrollbar.config(command=self.text.yview, orient="vertical")

        # Pack the widgets
        self.text.pack(fill="both", side="left", expand=True)
        self.yscrollbar.pack(side="right", fill="y")

        self.edit.pack(fill="both", expand=True)

        self.insertindex.pack(fill="x", side="left", padx=25, pady=2)
        self.encode.pack(side="right", fill="x", padx=25)
        self.separator.pack(side="right", fill="y", pady=5)
        self.lineend.pack(side="right", fill="x", padx=25)
        self.separator2.pack(side="right", fill="y", pady=5)

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

    def openfile(self, event: Event | None = None) -> None:
        """Open file from the filepath"""
        self.filepath = askopenfilename(
            filetypes=(("Text file", "*.txt"), ("Any file", "*.*"))
        )
        try:
            with open(self.filepath, mode="r", encoding=self.encoding) as f:
                self.text.insert("insert", f.read())
        except UnicodeDecodeError:
            showerror("Notepad", "Error, can not decode %s" % self.filepath)
        except FileNotFoundError:
            showerror("Notepad", "Error, no such file or directory %s" % self.filepath)
        else:
            self.changed = False

        if self.text.get(0.0, 2.0).find("\n") != -1:
            self.lineend.config(text="Windows (CRLF)")
        elif self.text.get(0.0, 2.0).find("\r\n") != -1:
            self.lineend.config(text="Unix (LF)")
        else:
            self.lineend.config(text="??? (CR)")
