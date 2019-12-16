import tkinter as tk
import tkinter.filedialog as filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import json


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
            # self.forget(index)
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
    tile_dict = {}
    deco_dict = {}
    __initialized = False

    def __init__(self, parent):
        """Overarching editor window for the levels"""
        # Check if PhotoImages are initialized before proceeding
        if not TilemapEditorWindow.__initialized:
            TilemapEditorWindow._initialize_images()

        # Create a lookup dictionary of the available views
        self.view_list = []

        # Add editor to parent window
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill=tk.X, expand=1)
        parent.add(self.frame, text="Map Editor")

        # Layout setup
        # Add the tool mode tracking variable
        self.tool_mode = tk.IntVar(self.frame, 0, "tool_mode")
        self.tool_mode.trace("w", self.tool_callback)

        # Add the grid mode tracking variable
        self.grid_mode = tk.IntVar(self.frame, 0, "grid_mode")
        self.grid_mode.trace("w", self.grid_mode_callback)

        # Add the border mode tracking variable
        self.border_mode = tk.IntVar(self.frame, 0, "border_mode")
        self.border_mode.trace("w", self.border_mode_callback)

        # Add buttons panel
        self.buttons_bar = ttk.Frame(self.frame)
        self.buttons_bar.grid(row=0, column=1, sticky=tk.NW, pady=4)

        # Add tool-mode buttons
        for i, j in enumerate(["draw", "move"]):
            self.tool_button = tk.Radiobutton(self.buttons_bar, indicator=0, value=i, variable=self.tool_mode,
                                              image=TilemapEditorWindow.imgs[j])
            self.tool_button.grid(row=0, column=i + 1, sticky=tk.NW)

        # Add grid toggling buttons
        self.grid_button = tk.Checkbutton(self.buttons_bar, variable=self.grid_mode, indicator=0,
                                          image=TilemapEditorWindow.imgs["grid"])
        self.grid_button.grid(row=0, column=3, sticky=tk.NW)

        # Add border toggling buttons
        self.grid_button = tk.Checkbutton(self.buttons_bar, variable=self.border_mode, indicator=0,
                                          image=TilemapEditorWindow.imgs["border"])
        self.grid_button.grid(row=0, column=4, sticky=tk.NW)

        # Set up keybindings
        # TODO: Either move these keybindings somewhere else, or limit their scope
        parent.master.bind("<Key-1>", self.keybind_draw_mode)
        parent.master.bind("<Key-2>", self.keybind_move_mode)
        parent.master.bind("<Key-3>", self.keybind_grid_mode)
        parent.master.bind("<Key-4>", self.keybind_border_mode)

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

        # Build the editor window's toolbar
        self.menubar = tk.Menu(self.frame.master.master.master)

        # Create the file menubar
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Map (Ctrl-O)", command=self._open_map)
        self.filemenu.add_command(label="Save Map (Ctrl-S)", command=None)
        self.filemenu.add_command(label="Save Map As (Ctrl-Shift-S)", command=None)
        self.filemenu.add_command(label="New Map (Ctrl-N)", command=self.new_view)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Create initial tilemap view
        self.new_view()

    def _open_map(self, event=None):
        """Event callback for opening a level"""
        file = filedialog.askopenfilename(filetypes=[("Json", "*.json")], defaultextension=[("Json", "*.json")])
        self.open_map(file)

    def open_map(self, file):
        """Open a level in a new view"""
        self.new_view()
        self.view_list[self.tilemap_panel.index("current")].load_from_file(file)

    def new_view(self, event=None):
        """Create a new, blank view"""
        # Create new view instance
        self.view_list.append(TilemapView(self.tilemap_panel,
                                          self.tool_mode.get(),
                                          self.grid_mode.get(),
                                          self.border_mode.get()))
        self.tilemap_panel.select(self.tilemap_panel.index("end") - 1)

        # Redraw all open views
        for i in self.view_list:
            i.frame.event_generate("<<TilemapEditorForceRedraw>>")

    def close_view(self, event):
        """Close the currently open view"""
        index = self.tilemap_panel.index("@%d,%d" % (event.x, event.y))

        # Check with the view if it wants to close
        if self.view_list[index].close():
            self.tilemap_panel.forget(index)
            del self.view_list[index]

    def tool_callback(self, name=None, index=None, op=None):
        """Set the mode of views to draw mode"""
        for i in self.view_list:
            i.frame.event_generate("<<TilemapEditorUpdateMode>>", x=self.tool_mode.get())

    def grid_mode_callback(self, name=None, index=None, op=None):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.frame.event_generate("<<TilemapEditorGridToggle>>", x=self.grid_mode.get())

    def border_mode_callback(self, name=None, index=None, op=None):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.frame.event_generate("<<TilemapEditorBorderToggle>>", x=self.border_mode.get())

    def keybind_draw_mode(self, event):
        """Callback for setting the editor to draw mode"""
        self.tool_mode.set(0)

    def keybind_move_mode(self, event):
        """Callback for setting the editor to move mode"""
        self.tool_mode.set(1)

    def keybind_grid_mode(self, event):
        """Callback for setting the editor to draw mode"""
        if self.grid_mode.get() == 0:
            self.grid_mode.set(1)
        else:
            self.grid_mode.set(0)

    def keybind_border_mode(self, event):
        """Callback for setting the editor to draw mode"""
        if self.border_mode.get() == 0:
            self.border_mode.set(1)
        else:
            self.border_mode.set(0)

    @classmethod
    def _initialize_images(cls):
        """Initialize all of the PhotoImages"""
        # Declare embedded image data
        addnew_data = '''R0lGODlhCgAKAMIDAAAvAACQAACzAE3bO03bO03bO03bO03bOyH5BA
            EKAAQALAAAAAAKAAoAAAMg\nSAoRoJAwF5cQb4F9927XMFwNKIik43UeBHSV1GTRRCc
            AOw==
            '''

        draw_tool_data = '''R0lGODlhIAAgAKEBAAAAAP///////////yH5BAEKAAIALAAAAAAg
            ACAAAAJdlI+py+0PH5ixChAy\nsHLmsHHLRIKhiJAqhR6r2rrfGhvYZ57tPbMxr/HtcL
            nahUgyAou1ZbKJFKKcUhFVN41irVplF4p7\n/oDinSe45dw85SE6bV1XzTCjq27P6y0F
            ADs=
            '''

        move_tool_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAAAJa
            jI+py+0PAwCxmjktxFg3znkK\nCIpLaDJoOnZsm5kUPCe1eh8rEp8977L9dKSicSc5Ko
            3ApTN4eTp9uejQ+qkmr8mHFnlJgV9jVlkM\nNR9f2xK7zUXH1e+6HVEAADs=
            '''

        grid_mode_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAAAJV
            hI+py+0foolhSkBtxVd7vmXg\n94nmdW7PyrbuCKdlF6N2eCNyjffvD/zthrkD0cfTFY
            +koPOZYCZhM6S0ip1Ct0/pdeqlha00rtk1\nzmbTxqUbeY4/CgA7
            '''

        border_mode_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAAA
            JChI+py+0Po5y0woCz3jy4DnZf\nSGJjGZ6o2Kxp67JMLC80p94erJt8n7sFacNY0XVc
            JVHLUpP0fM16Pov1is1qt5QCADs=
            '''

        # Add embedded images to the image dictionary
        cls.imgs = {"add_new": tk.PhotoImage("img_addnew_active", data=addnew_data),
                    "draw": tk.PhotoImage("img_draw_tool", data=draw_tool_data),
                    "move": tk.PhotoImage("img_move_tool", data=move_tool_data),
                    "grid": tk.PhotoImage("img_grid_mode", data=grid_mode_data),
                    "border": tk.PhotoImage("img_border_mode", data=border_mode_data)}

        # Open the ids.json file to start loading the tiles/decos
        try:
            # Attempt to read data from file
            with open("assets/ids.json", mode="r") as f:
                file_data = json.load(f)
                # Load the tiles
                for i in file_data["tile_ids"]:
                    img = Image.open("tiles/" + i["tex"])
                    img = img.crop([0, 0, 16, 16])
                    img = img.resize((64, 64))
                    cls.tile_dict[int(i["id"])] = ImageTk.PhotoImage(img)

                # Load the decos
                for i in file_data["deco_ids"]:
                    img = Image.open("tiles/" + i["tex"])
                    img = img.crop([0, 0, 16, 16])
                    img = img.resize((64, 64))
                    cls.deco_dict[int(i["id"])] = ImageTk.PhotoImage(img)

        except FileNotFoundError:
            # If the file does not exist, create a new one
            with open("assets/ids.json", mode="w") as f:
                pass

        cls.__initialized = True


class TilemapView:
    # TODO: Tkinterify TilemapView, and make it the responsibility of a subclass of CustomNotebook

    __initialized = False
    imgs = {}

    def __init__(self, parent, control_scheme, grid_scheme, border_scheme):
        """Sub-window for viewing individual levels"""
        # Check if the parent is a notebook, which it SHOULD BE
        if type(parent) != CustomNotebook:
            raise TypeError("Cannot assign a {} to a {}".format(TilemapView, type(parent)))

        # Ensure that the images have been initialized
        if not TilemapView.__initialized:
            TilemapView._initialize()

        # Declare some variables for view settings
        self.start_x = 0
        self.start_y = 0
        self.saved = False
        self.grid = grid_scheme
        self.border = border_scheme

        # Declare some variables related to the tilemap itself
        self.name = "Untitled"
        self.level_width = 16 + 2
        self.level_height = 9 + 2
        self.tilemap = [[0] * self.level_width for i in range(self.level_height)]
        self.decomap = [[0] * self.level_width for i in range(self.level_height)]
        self.file_path = ""

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

        # Set up some event handlers
        self.frame.bind("<<TilemapEditorUpdateMode>>", self._set_mode)
        self.frame.bind("<<TilemapEditorGridToggle>>", self._set_grid)
        self.frame.bind("<<TilemapEditorBorderToggle>>", self._set_border)
        self.frame.bind("<<TilemapEditorForceRedraw>>", self.redraw_view)

        # Add the view to the parent frame
        parent.add(self.frame)
        self.update_title()

        # Ensure settings are set
        self.set_mode(control_scheme)
        self.set_grid(grid_scheme)
        self.set_border(border_scheme)

        # Draw the entire view
        self.redraw_view()

    def close(self):
        """Tells the view to close"""
        # TODO: Add save request dialogue
        if not self.saved:
            print("WARNING: NOT SAVED")
        self.frame.unbind_all(["<<TilemapEditorUpdateMode>>",
                               "<<TilemapEditorGridToggle>>",
                               "<<TilemapEditorBorderToggle>>",
                               "<<TilemapEditorForceRedraw>>"])
        self.frame.forget()
        return True

    def draw_grid(self):
        """Draw the tilemap grid"""
        for i in range(self.level_width + 1):
            self.canvas.create_line(64 * i, 0, 64 * i, 64 * self.level_height, fill="BLACK", width=2.0)
        for i in range(self.level_height + 1):
            self.canvas.create_line(0, 64 * i, 64 * self.level_width, 64 * i, fill="BLACK", width=2.0)

    def draw_tilemap(self):
        """Draw the current level"""
        for i, j in enumerate(self.tilemap):
            for k, m in enumerate(j):
                if m != 0:
                    self.canvas.create_image((k * 64 + 32, i * 64 + 32), image=TilemapEditorWindow.tile_dict[m])

    def draw_decomap(self):
        """Draw the current level"""
        for i, j in enumerate(self.decomap):
            for k, m in enumerate(j):
                if m != 0:
                    self.canvas.create_image((k * 64 + 32, i * 64 + 32), image=TilemapEditorWindow.deco_dict[m])

    def draw_border(self):
        """Draw the border"""
        for i in range(self.level_width):
            self.canvas.create_image((i * 64 + 32, 32), image=TilemapView.imgs["border"])
            self.canvas.create_image((i * 64 + 32, self.level_height * 64 - 32), image=TilemapView.imgs["border"])
        for i in range(1, self.level_height - 1):
            self.canvas.create_image((32, i * 64 + 32), image=TilemapView.imgs["border"])
            self.canvas.create_image((self.level_width * 64 - 32, i * 64 + 32), image=TilemapView.imgs["border"])

    def redraw_view(self, event=None):
        """Redraw the entire view"""
        # First redraw the grid if enabled (self.grid=1)
        self.canvas.delete("all")
        if self.grid:
            self.draw_grid()
        self.draw_tilemap()
        self.draw_decomap()
        if self.border:
            self.draw_border()

    def update_title(self):
        """Update the title of the view"""
        # If not saved, add an asterisk in front of the displayed name
        if self.saved:
            self.frame.master.tab(self.frame, text=self.name)
        else:
            self.frame.master.tab(self.frame, text="*" + self.name)

    def _set_mode(self, event):
        """Event callback for setting the mode/control-scheme of the window."""
        self.set_mode(event.x)

    def set_mode(self, value):
        """Does the actual work of setting the window's mode"""
        if value == 0:
            # Drawing controls
            self.canvas.unbind_all(["<ButtonPress-1>", "<B1-Motion>"])
            self.canvas.bind("<B1-Motion>", self.draw)
            self.canvas.config(cursor="pencil")
        elif value == 1:
            # Movement controls
            self.canvas.unbind_all(["<ButtonPress-1>", "<B1-Motion>"])
            self.canvas.bind("<ButtonPress-1>", self.set_start)
            self.canvas.bind("<B1-Motion>", self.move)
            self.canvas.config(cursor="fleur")

    def _set_grid(self, event):
        self.set_grid(event.x)

    def set_grid(self, value):
        """Toggle the grid overlay"""
        self.grid = value
        self.redraw_view()

    def _set_border(self, event):
        """Event callback for setting the border"""
        self.set_border(event.x)

    def set_border(self, value):
        """Toggle the border overlay"""
        self.border = value
        if self.border:
            # Show border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0, 0, 64 * self.level_width, 64 * self.level_height))
        else:
            # Disable border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(64, 64, 64 * (self.level_width - 1), 64 * (self.level_height - 1)))
        self.redraw_view()

    def draw(self, event):
        """Event callback for drawing on the grid"""
        # TODO: Add drawing capability
        pass

    def set_start(self, event):
        """Set the starting position for dragging the canvas around"""
        self.start_x = event.x
        self.start_y = event.y

    def move(self, event):
        """Event callback for moving the grid around"""
        if self.start_x is not None and self.start_y is not None:
            self.canvas.scan_mark(self.start_x, self.start_y)
            self.start_x = None
            self.start_y = None
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def load_from_file(self, file):
        with open(file, mode="r") as f:
            level_data = json.load(f)
            self.tilemap = level_data["tilemap"]
            self.decomap = level_data["decomap"]
            self.level_height = len(self.tilemap)
            self.level_width = len(self.tilemap[0])
            self.name = level_data["name"]
            self.saved = True
        self.set_border(self.border)
        self.update_title()
        self.redraw_view()

    @classmethod
    def _initialize(cls):
        """Initialize the embedded images"""
        border_tile_data = tk.PhotoImage("img_border_tile", data='''R0lGODlhEAAQ
            AIABAP/0ANXLACH5BAEKAAEALAAAAAAQABAAAAImhINokMq9WjiQJuvexbHqiYFf\nt4
            0hKUooqJ5fWrUvutKuOXN3UwAAOw==
            ''').zoom(64).subsample(16)

        cls.imgs = {"border": border_tile_data}


class SelectionPane:

    def __init__(self, parent):
        """Overarching class for the object selection panes"""
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(anchor="ne")
        self.selection_canvas = tk.Canvas(self.frame, width=64 * 3, height=576, bg="WHITE", bd=0)
        self.selection_canvas.pack()


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

        # Add toolbar
        self.menubar = tk.Menu(parent)

        # Add event listener to update the toolbar
        self.source.bind("<<NotebookTabChanged>>", self._update_toolbar)

    def _update_toolbar(self, event):
        """Callback event handler for updating the toolbar to match the current tab"""
        self.update_toolbar(self.source.index("current"))

    def update_toolbar(self, value):
        """Updates the toolbar to match the current tab"""
        self.menubar.forget()
        self.menubar = tk.Menu(self.source.master)
        # Tilemap editor window toolbar
        if value == 0:
            self.source.master.config(menu=self.tilemap_editor.menubar)


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
