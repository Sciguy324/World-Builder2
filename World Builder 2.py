import tkinter as tk
from tkinter import ttk


class CustomButton(ttk.Button):
    """A ttk button that has special effects"""

    __initialized = False

    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__initialized = True

        kwargs["style"] = "CustomButton"
        ttk.Button.__init__(self, *args, **kwargs)

        # self._active = None

        self.bind("<ButtonPress-1>", self.on_press, True)
        self.bind("<ButtonRelease-1>", self.on_release, True)

    def on_press(self, event):
        """Called when the button is pressed over the new map button"""
        self.state(['pressed'])
        print(self.config())

    def on_release(self, event):
        """Called when the button is released over the new map button"""
        if not self.instate(['pressed']):
            return

        self.state(["!pressed"])

    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_addnew", data='''R0lGODlhCAAIAKEDAAAAAHx8fJqamsoA
            ACH5BAEKAAMALAAAAAAIAAgAAAIU3BABZqgNXHRBiITr\nTZPHxjFHOBQAOw==
            '''),
            tk.PhotoImage("img_addnew_active", data='''R0lGODlhCAAIAKEDAAAvAACQA
            ACzAMoAACH5BAEKAAMALAAAAAAIAAgAAAIU3BABZqgNXHRBiITr\nTZPHxjFHOBQAOw=
            =
            '''),
            tk.PhotoImage("img_addnew_pressed", data='''R0lGODlhCAAIAKEDAA9NDyuj
            KyvAK8oAACH5BAEKAAMALAAAAAAIAAgAAAIU3BABZqgNXHRBiITr\nTZPHxjFHOBQAOw
            ==\n''')
        )

        style.element_create("add_new", "image", "img_addnew",
                             ("active", "pressed", "!disabled", "img_addnew_pressed"),
                             ("active", "!disabled", "img_addnew_active"), border=8, sticky='')

        style.layout('CustomButton', [
            ('CustomButton.button', {
                'sticky': 'nswe',
                'children': [(
                    'CustomButton.focus', {
                        'sticky': 'nswe',
                        'children': [(
                            'CustomButton.padding', {
                                'sticky': 'nswe',
                                'children': [
                                    ('CustomButton.label', {'sticky': 'nswe'}),
                                    ('CustomButton.add_new', {'sticky': 'nswe'}),
                                ]
                            }
                        )]
                    }
                )]
            })
        ])


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

        # print(self.configure())

        self._active = None

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)

    def on_close_press(self, event):
        """Called when the button is pressed over the close button"""
        element = self.identify(event.x, event.y)

        # Check if user pressed "closed"
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

        # Close tab if user clicked "close"
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
                                    ("CustomNotebook.close", {"side": "left", "sticky": ''})
                                ]
                            })
                        ]
                    })
                ]
            }),
        ])
        # print(style.layout("CustomNotebook.tab"))
        # print(style.element_names())
        # style.layout("CustomNotebook", [("CustomNotebook.close", {"side": "right", "sticky": "nswe"})])


class TilemapEditorWindow:

    imgs = {}
    __initialized = False

    def __init__(self, parent):
        """Overarching editor window for the levels"""
        # Check if PhotoImages are initialized before proceeding
        if not TilemapEditorWindow.__initialized:
            TilemapEditorWindow._initialize_images()

        # Add editor to parent window
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, expand=1)
        parent.add(self.frame, text="Map Editor")

        # Layout setup
        # Add tool mode tracking variable
        self.tool_mode = tk.IntVar(self.frame, 0, "tool_mode")
        # self.tool_mode.trace("w", self.tool_callback)

        # Add buttons panel
        self.buttons_bar = ttk.Frame(self.frame)
        self.buttons_bar.grid(row=0, column=1, sticky=tk.NW, pady=4)
        # Add individual buttons
        for i, j in enumerate(["draw", "move"]):
            self.tool_button = tk.Radiobutton(self.buttons_bar, indicator=0, value=i, variable=self.tool_mode,
                                              image=TilemapEditorWindow.imgs[j])
            self.tool_button.grid(row=0, column=i + 1, sticky=tk.NW)

        # Set up level viewing section
        self.tilemap_panel = CustomNotebook(self.frame)
        self.tilemap_panel.bind("<<NotebookTabClosed>>", self.close_view)
        self.tilemap_panel.grid(row=1, column=1, sticky=tk.NW)

        # Add "new map" button to viewing pane
        self.new_view_button = ttk.Button(self.frame, command=self.new_view, image=TilemapEditorWindow.imgs["add_new"])
        self.new_view_button.grid(row=1, column=0, sticky=tk.NW)

        # Add the Selection panes
        self.selection_pane = ttk.Frame(self.frame)
        self.selection_pane.grid(row=1, column=2, sticky=tk.E, ipadx=20)
        self.tile_pane_test = TilePane(self.selection_pane)

        # Create initial tilemap view
        self.new_view()

    @classmethod
    def _initialize_images(cls):
        """Initialize all of the PhotoImages"""
        addnew_data = '''R0lGODlhCgAKAMIDAAAvAACQAACzAE3bO03bO03bO03bO03bOyH5BAEKAAQ
            ALAAAAAAKAAoAAAMg\nSAoRoJAwF5cQb4F9927XMFwNKIik43UeBHSV1GTRRCcAOw==
            '''

        draw_tool_data = '''R0lGODlhIAAgAKEAAAAAAP///wAAAAAAACH5BAEKAAIALAAAAAAgACAA
            AAJalI+py+0PH5ixChAy\nsHLmsHESGIrOVJoXelCqgWlhasYfrdry234yztGRgBYhi2d0vZLECp
            N38Q2hT6T0uLwqc9pmpLrU\nYXOeH1U2Pf+8ztgYidpS49C6/VUAADs=
            '''

        move_tool_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAAAJajI+p
            y+0PAwCxmjktxFg3znkK\nCIpLaDJoOnZsm5kUPCe1eh8rEp8977L9dKSicSc5Ko3ApTN4eTp9ue
            jQ+qkmr8mHFnlJgV9jVlkM\nNR9f2xK7zUXH1e+6HVEAADs=
            '''

        cls.imgs = {"add_new": tk.PhotoImage("img_addnew_active", data=addnew_data),
                    "draw": tk.PhotoImage("img_draw_tool", data=draw_tool_data),
                    "move": tk.PhotoImage("img_move_tool", data=move_tool_data)}
        cls.__initialized = True

    def new_view(self):
        """Create a new, blank view"""
        TilemapView(self.tilemap_panel, self.tool_mode)
        self.tilemap_panel.select(self.tilemap_panel.index("end") - 1)

    def close_view(self, event):
        """Close the currently open view"""
        # self.tilemap_panel.forget("current")

    def tool_callback(self, name, index, op):
        """Set the mode of  to draw mode"""
        # TODO: Add modes to TileMapEditorWindow
        # print("Name:", name)
        # print("Index:", index)
        # print("Mode:", op)
        # print("Draw mode is now: ", self.tool_mode.get())


class TilemapView:

    def __init__(self, parent, control_var):
        """Sub-window for viewing individual levels"""
        # Check if the parent is a notebook, which it SHOULD BE
        if type(parent) != CustomNotebook:
            raise TypeError("Cannot assign a {} to a {}".format(TilemapView, type(parent)))

        # Declare some variables
        self.level_width = 16 + 5
        self.level_height = 9 + 5
        self.saved = False
        self.name = "Untitled"

        # Create element layout
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.canvas = tk.Canvas(self.frame, width=64 * 16, height=64 * 9, bg="WHITE", bd=0)
        self.canvas.grid(row=0, column=0)

        # Add the scrollbars
        self.canvas_vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas_vbar.grid(row=0, column=1, sticky=tk.N + tk.S)
        self.canvas_vbar.activate("slider")
        self.canvas_hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas_hbar.grid(row=1, column=0, sticky=tk.E + tk.W)
        self.canvas_hbar.activate("slider")
        self.canvas.config(scrollregion=(0, 0, 64 * self.level_width, 64 * self.level_height),
                           xscrollcommand=self.canvas_hbar.set,
                           yscrollcommand=self.canvas_vbar.set)
        self.canvas.xview(tk.MOVETO, 0.0)
        self.canvas.yview(tk.MOVETO, 0.0)

        # Set up some controls
        self.control_ref = control_var.trace("w", self.set_mode)
        parent.bind("<<NotebookTabClosed>>", self.close_view)
        self.canvas.bind("<B1-Motion>")

        # Add the view to the parent frame
        parent.add(self.frame)
        self.update_title()

        # Draw the grid
        self.draw_grid()

    def draw_grid(self):
        """Draw the tilemap grid"""
        for i in range(self.level_width + 1):
            self.canvas.create_line(64 * i, 0, 64 * i, 64 * self.level_height, fill="BLACK", width=2.0)
        for i in range(self.level_height + 1):
            self.canvas.create_line(0, 64 * i, 64 * self.level_width, 64 * i, fill="BLACK", width=2.0)

    def update_title(self):
        """Update the title of the view"""
        # If not saved, add an asterisk in front of the displayed name
        if self.saved:
            self.frame.master.tab(self.frame, text=self.name)
        else:
            self.frame.master.tab(self.frame, text="*" + self.name)

    def draw_tilemap(self):
        """Draw the current level"""
        # TODO: Add functionality to "draw_tilemap"
        pass

    def set_mode(self, name, index, op):
        """Set the mode of the window.  Available modes are 'draw' and 'move'"""
        # TODO: Add mode functionality to tilemap view
        print("Check")

    def draw(self, event):
        """Event callback for drawing on the grid"""
        pass

    def move(self, event):
        """Event callback for moving the grid around"""
        pass


class SelectionPane:

    def __init__(self, parent):
        """Overarching class for the object selection panes"""
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(anchor="ne")
        self.selection_canvas = tk.Canvas(self.frame, width=64 * 3, height=576, bg="WHITE", bd=0)
        self.selection_canvas.pack()
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


class WorldEditorWindow:

    def __init__(self, parent):
        # Create the source frame
        self.frame = tk.Frame(borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Create the canvas viewport
        self.canvas = tk.Canvas(self.frame, bg="BLACK", bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Add to parent frame
        parent.add(self.frame, text="World Editor")


class NotesEditorWindow:

    def __init__(self, parent):
        # Create the source frame
        self.frame = tk.Frame(borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Create the text entry
        self.textbox = tk.Text(self.frame, borderwidth=1, padx=10, pady=10, maxundo=10)
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.textbox.bind("<Control-z>", self.undo_edit)
        self.textbox.bind("<Control-y>", self.redo_edit)
        self.textbox.bind("<Control-BackSpace>", self.delete_word)

        # Add to parent frame
        parent.add(self.frame, text="Notes")

    def undo_edit(self, event=None):
        """Undo an edit"""
        try:
            self.textbox.config(undo=True)
            self.textbox.edit_undo()
        except tk.TclError:
            pass

    def redo_edit(self, event=None):
        """Redo an edit"""
        try:
            self.textbox.config(undo=True)
            self.textbox.edit_redo()
        except tk.TclError:
            pass

    def delete_word(self, event):
        """Backspace text until encountering a special character/whitespace"""
        tol = 100
        acc = 0
        if self.textbox.get("insert-1c") in [" ", "/", "\\", "{", "}", ".", "[", "]", ","]:
            self.textbox.delete("insert-1c")
        while self.textbox.get("insert-1c") not in [" ", "/", "\\", "{", "}", ".", "[", "]", ","]:
            acc += 1
            self.textbox.delete("insert-1c")
            if acc > tol:
                break


class App:

    def __init__(self, parent):
        """World Builder 2"""
        # Begin editor layout setup
        self.source = ttk.Notebook(parent)

        # Create the various editing windows
        self.tilemap_editor = TilemapEditorWindow(self.source)
        self.world_editor = WorldEditorWindow(self.source)
        self.notepad = NotesEditorWindow(self.source)

        self.source.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("World Builder 2")
    icon = tk.PhotoImage("""R0lGODlhEAAQAKU7ABIaVhIbVxckXhgkXh0rZR0sZSEybCU3ciU4cik9eCxBfS5Fgy9Fgy9GgzFJ
                            iDRNjTZQkjhUljlUljlUlztXmz1anz1aoJGRkZaWlZaWlpeXl5qbm5ubm5ycnJ+enp+foKCgoKGh
                            oaKioqOjo6SkpKWlpaampqenp6mpqamqqqqqqqurq6ysrK2tra6urq+vr7Cvr7CxsbKysrS0tLW1
                            tbq6us/Pz9nZ2dra2uTk5P///1J711J711J711J711J71yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5
                            BAEKAD8ALAAAAAAQABAAAAZtwJ9wKPSMiEiiphMyJZEXDAdEWj2Hl8y0lHJdhZnNh6SCzb4/pkn1
                            mtmuhYToxIrRbrokIeGYoFoyNTl5RAQIDBAWP202hEMDCA0QFUM1OEgCCAuTaAMHDA8UaAEGCqFo
                            AKWnaKoRaEMOEq9CQQA7
                            """)

    main = App(root)

    root.mainloop()
