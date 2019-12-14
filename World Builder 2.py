import tkinter as tk
from tkinter import ttk


class CustomNotebook(ttk.Notebook):
    """A ttk Notebook with close buttons on each tab.
    https://stackoverflow.com/questions/39458337/is-there-a-way-to-add-close-buttons-to-tabs-in-tkinter-ttk-notebook"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__initialized = True

        kwargs["style"] = "CustomNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""

        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index

    def on_close_release(self, event):
        """Called when the button is released over the close button"""
        if not self.instate(['pressed']):
            return

        element = self.identify(event.x, event.y)
        index = self.index("@%d,%d" % (event.x, event.y))

        if "close" in element and self._active == index:
            self.forget(index)
            self.event_generate("<<NotebookTabClosed>>")

        self.state(["!pressed"])
        self._active = None

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAKEDAA4ODjs7O4+Pj8oAACH5BAEKAAMALAAAAAAIAAgAAAISDIYD
                Zrj3XgJCnFmv\nMlJu7wQFADs=
            '''),
            tk.PhotoImage("img_closeactive", data='''R0lGODlhCAAIAKEBAEUAAMoAAMo
            AAMoAACH5BAEKAAIALAAAAAAIAAgAAAIRDIQCZrj3XlpthqqM\nlJm7UAAAOw==
            '''),
            tk.PhotoImage("img_closepressed", data='''R0lGODlhCAAIAMIEAG4PD3wtLe
            UqKv9mZsoAAMoAAMoAAMoAACH5BAEKAAQALAAAAAAIAAgAAAMX\nKEBMoIq99UKILIwR
            GtFcU10UNmGSkAAAOw==
            ''')
        )

        style.element_create("close", "image", "img_close",
                             ("active", "pressed", "!disabled", "img_closepressed"),
                             ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("CustomNotebook", [("CustomNotebook.client", {"sticky": "nswe"})])
        style.layout("CustomNotebook.Tab", [
            ("CustomNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CustomNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CustomNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CustomNotebook.label", {"side": "left", "sticky": ''}),
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])


class TilemapEditorWindow:

    def __init__(self, parent):
        """Overarching editor window for the levels"""
        # Add editor to parent window
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, expand=1)
        parent.add(self.frame, text="Map Editor")

        # Layout setup
        # Set up level viewing section
        self.tilemap_panel = CustomNotebook(self.frame)
        self.tilemap_panel.grid(row=1, column=0, sticky=tk.NW)

        # Add button panel
        self.buttons = ttk.Frame(self.frame)
        self.buttons.grid(row=0, column=0, sticky=tk.NW)
        # self.close_view_button = ttk.Button(self.buttons, text="X", width=2, command=self.close_view)
        # self.close_view_button.grid(row=0, column=0, sticky=tk.NW)
        self.new_view_button = ttk.Button(self.buttons, text="+", width=2, command=self.new_view)
        self.new_view_button.grid(row=0, column=1, sticky=tk.NW)

        # Create initial tilemap view
        self.new_view()

    def new_view(self):
        """Create a new, blank view"""
        TilemapView(self.tilemap_panel)
        self.tilemap_panel.select(self.tilemap_panel.index("end") - 1)

    def close_view(self):
        """Close the currently open view"""
        self.tilemap_panel.forget("current")


class TilemapView:

    def __init__(self, parent):
        """Sub-window for viewing individual levels"""
        # Check if the parent is a notebook, which it SHOULD BE
        if type(parent) != CustomNotebook:
            raise TypeError("Cannot assign a {} to a {}".format(TilemapView, type(parent)))

        # Create element layout
        self.view = ttk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.canvas = tk.Canvas(self.view, width=1024, height=576, bg="WHITE", bd=0)
        self.canvas.pack()

        parent.add(self.view, text="*Untitled")


class SelectionPane:

    def __init__(self, parent):
        """Overarching class for the object selection panes"""
        pass


class TilePane(SelectionPane):

    def __init__(self, parent):
        """Overarching class for selection panes that are specifically for tiles"""
        super().__init__(parent)


class TileCollection(TilePane):

    def __init__(self, parent):
        """These are configurable groupings of tiles to make it easier to find specific tiles"""
        super().__init__(parent)


class TileAssembly(SelectionPane):

    def __init__(self, parent):
        """These are multi-tile objects that allow one to place structures quickly—like trees, for example"""
        super().__init__(parent)


class App:

    def __init__(self, parent):
        """World Builder 2"""
        # Begin editor layout setup
        self.source = ttk.Notebook(parent)

        # Create tilemap editing window
        self.tilemap_editor = TilemapEditorWindow(self.source)

        # tab1 = ttk.Frame(self.source)
        tab2 = ttk.Frame(self.source)

        # self.source.add(tab1, text="Tab 1")
        self.source.add(tab2, text="Tab 2")

        self.source.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()

    main = App(root)

    root.mainloop()
