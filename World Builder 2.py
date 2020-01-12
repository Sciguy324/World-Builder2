import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from tkinter import ttk
from PIL import ImageTk, Image
from os import path
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
            self.event_generate("<<NotebookTabClosed>>", x=index)

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


class TilemapEditorWindow(tk.Frame):
    imgs = {}
    tile_dict = {}
    deco_dict = {}
    loading_dict = {}
    light_dict = {}
    __initialized = False

    def __init__(self, parent, **kw):
        """Overarching editor window for the levels"""
        # Ensure PhotoImages are initialized before proceeding
        if not TilemapEditorWindow.__initialized:
            TilemapEditorWindow._initialize_images()

        super().__init__(parent, **kw)

        # Create a lookup list of the available views
        self.view_list = []

        # Create the master lookup dictionary of the available panes, and add the subcategories
        self.panes = {"tile": {},
                      "deco": {},
                      "loading": {},
                      "light": {}}

        # Add editor to parent window
        parent.add(self, text="Map Editor")

        # Layout setup
        # Add the tool mode tracking variable
        self.tool_mode = tk.IntVar(self, 0, "tool_mode")
        self.tool_mode.trace("w", self.tool_callback)

        # Add the grid mode tracking variable
        self.grid_mode = tk.IntVar(self, 0, "grid_mode")
        self.grid_mode.trace("w", self.grid_mode_callback)

        # Add the border mode tracking variable
        self.border_mode = tk.IntVar(self, 0, "border_mode")
        self.border_mode.trace("w", self.border_mode_callback)

        # Add the tile ID tracking variable
        self.tile_id = tk.IntVar(self, 0, "selected_tile")
        self.tile_id.trace("w", self.tile_id_callback)

        # Add the deco ID tracking variable
        self.deco_id = tk.IntVar(self, 0, "selected_deco")
        self.deco_id.trace("w", self.deco_id_callback)

        # Add the deco ID tracking variable
        self.loading_id = tk.IntVar(self, 0, "selected_loading")
        self.loading_id.trace("w", self.deco_id_callback)

        # Add the deco ID tracking variable
        self.light_id = tk.IntVar(self, 0, "selected_light")
        self.light_id.trace("w", self.deco_id_callback)

        # Add the group tracking variable
        self.group = tk.StringVar(self, "", "selected_group")
        self.group.trace("w", lambda name, index, op: self.set_pane(self.group.get(), self.layer.get()))

        # Add the selected layer tracking variable
        self.layer = tk.IntVar(self, 0, "selected_layer")
        self.layer.trace("w", self._set_layer)

        # Add buttons panel
        self.buttons_bar = ttk.Frame(self)
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

        # Add spacing
        self.button_spacing1 = tk.Frame(self.buttons_bar, height=16, width=16)
        self.button_spacing1.grid(row=0, column=5, sticky=tk.NW)

        # Add layer selection buttons (tile, deco, collision, loading, light)
        for i, j in enumerate(["tile_layer", "deco_layer", "collider_layer", "loading_layer", "light_layer"]):
            self.layer_button = tk.Radiobutton(self.buttons_bar, indicator=0, value=i, variable=self.layer,
                                               image=TilemapEditorWindow.imgs[j])
            self.layer_button.grid(row=0, column=i + 6, sticky=tk.NW)

        # Add another spacing
        self.button_spacing2 = tk.Frame(self.buttons_bar, height=16, width=16)
        self.button_spacing2.grid(row=0, column=11, sticky=tk.NW)

        # Add the tile coordinate label
        self.tile_coords_text = tk.StringVar(self, "Row, Col: ¯\\_(ツ)_/¯", "tile_coords_text")
        self.tile_coords = tk.Label(self.buttons_bar, textvariable=self.tile_coords_text,
                                    borderwidth=1, relief=tk.SUNKEN, padx=5, pady=5)
        self.tile_coords.grid(row=0, column=12, sticky=tk.W)

        # Add the level coordinate label
        self.level_coords_text = tk.StringVar(self, "X, Y: ¯\\_(ツ)_/¯", "level_coords_text")
        self.level_coords = tk.Label(self.buttons_bar, textvariable=self.level_coords_text,
                                     borderwidth=1, relief=tk.SUNKEN, padx=5, pady=5)
        self.level_coords.grid(row=0, column=13, sticky=tk.W)

        # Set up keybindings
        parent.master.bind("<Key-1>", self.keybind_draw_mode)
        parent.master.bind("<Key-2>", self.keybind_move_mode)
        parent.master.bind("<Key-3>", self.keybind_grid_mode)
        parent.master.bind("<Key-4>", self.keybind_border_mode)

        # Set up the layer keybindings
        for i in range(5, 10):
            parent.master.bind("<Key-{}>".format(i), self.keybind_layer_mode)

        # Set up level viewing section
        self.tilemap_panel = CustomNotebook(self)
        self.tilemap_panel.bind("<<NotebookTabClosed>>", self.close_view)
        self.tilemap_panel.grid(row=1, column=1, sticky=tk.NW)

        # Add "new map" button to viewing pane
        self.new_view_button = ttk.Button(self, command=self.new_view, image=TilemapEditorWindow.imgs["add_new"])
        self.new_view_button.grid(row=1, column=0, sticky=tk.NW)

        # Add the Selection panes
        self.selection_frame = ttk.Frame(self)
        self.selection_frame.grid(row=1, column=2, sticky=tk.E, ipadx=20)
        self.load_groups()
        self.set_pane("All", self.layer.get())

        # Add the category dropdown box
        options = list([i for i, j in self.panes["tile"].items()])
        self.group_dropdown = tk.OptionMenu(self, self.group, *options)
        self.group_dropdown.grid(row=0, column=2, sticky=tk.E)

        # Build the editor window's toolbar
        self.menubar = tk.Menu(self.master.master.master)

        # Create the file menubar
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Map (Ctrl-O)", command=self._open_map)
        self.filemenu.add_command(label="Save Map (Ctrl-S)", command=self._save_map)
        self.filemenu.add_command(label="Save Map As (Ctrl-Shift-S)", command=self._save_map_as)
        self.filemenu.add_command(label="New Map (Ctrl-N)", command=self.new_view)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Settings", command=self.unimplemented)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Create the edit menubar
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Undo (Ctrl-Z)", command=self.unimplemented)
        self.editmenu.add_command(label="Redo (Ctrl-Y)", command=self.unimplemented)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Change Tilemap Size", command=self.unimplemented)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Set Default Spawn", command=self.unimplemented)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu, command=self.unimplemented)

        # Create the tile menubar
        self.tilemenu = tk.Menu(self.menubar, tearoff=0)
        self.tilemenu.add_command(label="Edit Tile Geometry", command=self.unimplemented)
        self.tilemenu.add_command(label="Apply Tile Geometry", command=self.unimplemented)
        self.tilemenu.add_separator()
        self.tilemenu.add_command(label="Edit Tile Groups", command=self.unimplemented)
        self.tilemenu.add_command(label="Edit Deco Groups", command=self.unimplemented)
        self.menubar.add_cascade(label="Tile", menu=self.tilemenu)

        # Create the assembly menubar
        self.assemblymenu = tk.Menu(self.menubar, tearoff=0)
        self.assemblymenu.add_command(label="Edit Tile Geometries", command=self.unimplemented)
        self.assemblymenu.add_command(label="Apply Tile Geometries", command=self.unimplemented)
        self.assemblymenu.add_separator()
        self.assemblymenu.add_command(label="Edit Assembly Groups", command=self.unimplemented)
        self.menubar.add_cascade(label="Assembly", menu=self.assemblymenu)

        # Create the help menubar
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Ok", command=self.unimplemented)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

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

    def _save_map(self, event=None):
        """Event callback for saving a level"""
        self.view_list[self.tilemap_panel.index("current")].quick_save()

    def _save_map_as(self, event=None):
        """Event callback for save a level as a new file"""
        self.view_list[self.tilemap_panel.index("current")].save_to_file(None)

    def new_view(self, event=None):
        """Create a new, blank view"""
        # Create new view instance
        self.view_list.append(TilemapView(self.tilemap_panel))
        self.tilemap_panel.select(self.tilemap_panel.index("end") - 1)

        # Redraw all open views
        for i in self.view_list:
            i.redraw_view()

    def close_view(self, event):
        """Close the currently open view"""
        # Index of view in question passed as x-coordinate of event
        # Check with the view if it wants to close
        if self.view_list[event.x].close():
            self.tilemap_panel.forget(event.x)
            del self.view_list[event.x]

    @staticmethod
    def unimplemented(self, event=None):
        """This function has not yet been implemented"""
        print("This feature has not yet been implemented")

    def tool_callback(self, name=None, index=None, op=None):
        """Set the mode of views to draw mode"""
        for i in self.view_list:
            i.set_mode(self.tool_mode.get())

    def grid_mode_callback(self, name=None, index=None, op=None):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.set_grid()

    def border_mode_callback(self, name=None, index=None, op=None):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.set_border(self.border_mode.get())

    def tile_id_callback(self, name=None, index=None, op=None):
        """Callback to set the grid visibility of the views"""
        for i in self.view_list:
            i.set_id(self.tile_id.get())

    def deco_id_callback(self, name=None, index=None, op=None):
        """Callback to set the grid visibility of the views"""
        for i in self.view_list:
            i.set_id(self.deco_id.get())

    def keybind_draw_mode(self, event):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        self.tool_mode.set(0)

    def keybind_move_mode(self, event):
        """Callback for setting the editor to move mode"""
        if self.master.index("current") != 0:
            return
        self.tool_mode.set(1)

    def keybind_grid_mode(self, event):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        if self.grid_mode.get() == 0:
            self.grid_mode.set(1)
        else:
            self.grid_mode.set(0)

    def keybind_border_mode(self, event):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        if self.border_mode.get() == 0:
            self.border_mode.set(1)
        else:
            self.border_mode.set(0)

    def keybind_layer_mode(self, event):
        """Callback for setting the layer"""
        self.layer.set(int(event.char) - 5)

    def set_pane(self, pane, layer):
        """Set the currently viewable pane"""
        # Remove current panes
        for i, j in self.panes.items():
            for k, l in j.items():
                l.pack_forget()
        self.group.set(pane)
        # Tilemap mode: select pane from the tile panes
        if layer == 0:
            self.panes["tile"][pane].pack(anchor="ne")
        # Decomap mode: select pane from the deco panes
        elif layer == 1:
            self.panes["deco"][pane].pack(anchor="ne")
        # Loading zone mode: select the loading zone pane
        elif layer == 3:
            self.panes["loading"][pane].pack(anchor="ne")
        # Lightmap mode: select the lightmap pane
        elif layer == 4:
            self.panes["light"][pane].pack(anchor="ne")

    def _set_layer(self, name=None, index=None, op=None):
        """Event callback for changing the currently editable layer"""
        self.set_layer(self.layer.get())

    def set_layer(self, layer):
        """Set the currently editable layer"""
        if layer == 0:
            self.group_dropdown.forget()
            options = list([i for i, j in self.panes["tile"].items()])
            self.group_dropdown = tk.OptionMenu(self, self.group, *options)
            self.group_dropdown.grid(row=0, column=2, sticky=tk.E)
            self.tile_id_callback()
        elif layer == 1:
            self.group_dropdown.forget()
            options = list([i for i, j in self.panes["deco"].items()])
            self.group_dropdown = tk.OptionMenu(self, self.group, *options)
            self.group_dropdown.grid(row=0, column=2, sticky=tk.E)
            self.deco_id_callback()
        else:
            self.group_dropdown.grid_forget()
            self.group_dropdown.forget()

        self.set_pane("All", layer)
        for i in self.view_list:
            i.set_layer()

    def load_groups(self):
        """Loads all groups from the project file"""
        # Add the hard-coded "all" category
        self.panes["tile"] = {"All": TileCollection(self.selection_frame,
                                                    [i for i, j in TilemapEditorWindow.tile_dict.items()],
                                                    "tile",
                                                    self.tile_id,
                                                    borderwidth=1,
                                                    relief=tk.SUNKEN)}

        self.panes["deco"] = {"All": TileCollection(self.selection_frame,
                                                    [i for i, j in TilemapEditorWindow.deco_dict.items()],
                                                    "deco",
                                                    self.deco_id,
                                                    borderwidth=1,
                                                    relief=tk.SUNKEN)}

        self.panes["loading"] = {"All": TileCollection(self.selection_frame,
                                                       [0, 1, 2, 3, 4, 5],
                                                       "loading",
                                                       self.loading_id,
                                                       borderwidth=1,
                                                       relief=tk.SUNKEN)}

        self.panes["light"] = {"All": TileCollection(self.selection_frame,
                                                     [0],
                                                     "light",
                                                     self.light_id,
                                                     borderwidth=1,
                                                     relief=tk.SUNKEN)}

        print("Loaded: ")
        with open("project.json", mode="r") as f:
            data = json.load(f)
            for i in data["groups"]:
                print(i["name"], "({})".format(i["type"]), "-", i["entries"])
                # Load tile pane if applicable
                if i["name"] not in self.panes["tile"] and i["type"] == "tile":
                    self.panes["tile"][i["name"]] = TileCollection(self.selection_frame,
                                                                   [TilemapEditorWindow.tile_dict[i] for i in
                                                                    i["entries"]],
                                                                   "tile",
                                                                   self.tile_id,
                                                                   borderwidth=1,
                                                                   relief=tk.SUNKEN)
                # Load deco pane if applicable
                elif i["name"] not in self.panes["deco"] and i["type"] == "deco":
                    self.panes["deco"][i["name"]] = TileCollection(self.selection_frame,
                                                                   [TilemapEditorWindow.deco_dict[i] for i in
                                                                    i["entries"]],
                                                                   "deco",
                                                                   self.deco_id,
                                                                   borderwidth=1,
                                                                   relief=tk.SUNKEN)
                # Handle invalid attempts to load pane
                else:
                    print("WARNING: Invalid group name '{}' detected in project file, group will not be loaded"). \
                        format(i["name"])
                    if i["type"] not in ["tile", "deco"]:
                        print("Invalid type name?")
                    else:
                        print("Possible duplicate group?")

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

        tile_layer_data = '''R0lGODlhIAAgAKECAAAAAD8/P////////yH5BAEKAAIALAAAAAA
            gACAAAAJNlI+py+0Po5y0woCz\n3jy4DnZfAJTmiaJjyrJrC5dv3M50at9nrssN1sP9S
            MHdsGhkAJE+JZHJ60V101uVdo1lYdvakQmw\niMfksvlsKQAAOw==
            '''

        deco_layer_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAAAJ
            PjI8JkO1/FoMUyllzlLrf1WUf\nFjojWJpn2pwca7gXvH20st5xfssk6+v5fp4hqmQ8A
            nk0mS4QbEZhRmpyWUUmlZXtTDNsCbnP77NG\n1JkrBQA7
            '''

        collision_layer_data = '''R0lGODlhIAAgAKECAAAAAGhoaP///////yH5BAEKAAMALA
            AAAAAgACAAAAJrnI+py20AnGQQzvuq\nxVJv3ngRSIkjmZgnmqnsoX5svJLCLWi48O4+
            3vv5WEIhqlKskEw3E4gmekI1nGn0YvVgstQJV9v5\nKh1i8KJ8TQXQlbV6zQYE3I+5HZ
            69zyNyvV7l99cXSFh4xxfnUgAAOw==
            '''

        loading_layer_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAA
            AAJrBBKGmtfrmIwU2ocZ2rz7v2ng\nSBoTiXZnynJi64kv7JoXDa44Ou+ys6vpPqaisX
            YjGpc5IG7YS9kaw9Y0VKFdldrXb1lUzcJU8HcU\nRaeDW/FzTZausVZnUGmu8vKTOdt+
            x5WRtVJIeHgxUQAAOw==
            '''

        light_layer_data = '''R0lGODlhIAAgAKEAAAAAAM7Ozv///wAAACH5BAEKAAMALAAAAA
            AgACAAAAJznI+py+0PBwCxnmkd\nvdv0LHWY94HlBabRiEzuyTIu97JzNgn6LpxWzuP5
            VoBeMTh8AI/BHhEDbO4oL6JUmIpekxpmkysj\nScGKm3bKgZS8ujU5cX6rsaryMVb3BC
            b7PBwQsCenJtjnxxGI51d1+Nf4CIlQAAA7
            '''

        delete_zone = '''R0lGODlhEAAQAKEBAAAAAP8AAP9UVP8AACH5BAEKAAMALAAAAAAQABA
            AAAI5TDaGmocP40IASGoV\nCDbu7nyQKJFk4nFn4wlCBzkP4MLX8K0yzlH9Evr5YIfVc
            GRDom4Sg4MBdRQAADs=
            '''

        new_zone = '''R0lGODlhEAAQAKEAAAAAAOzkAP//ZgAAACH5BAEKAAMALAAAAAAQABAAAA
            IsTDaGmocP44KgyuUG\nCODOuoGeZghGFzkgZ6VZOL7tSD9Z3eC2zu+84WAIHQUAOw==
            '''

        configure_zone = '''R0lGODlhEAAQAMIAAAAAAP8AAACzAAC+AAAAAAAAAAAAAAAAACH5
            BAEKAAQALAAAAAAQABAAAAM8\nKEKk7G2xSeuzDGgKKZjfJGVfQJhhlZ5g006mOXxOak
            6zSKw4n7GMnO7Xq3QAg6TPBdpgnpgRVASp\nSiAJADs=
            '''

        copy_zone = '''R0lGODlhEAAQAKEBAAAAACQ5qTBM4SQ5qSH5BAEKAAMALAAAAAAQABAAA
            AI9TDaGmocP44qgWvDY\nAKYbPG3dFYAQV56gAwiptBztCyeba9Y3LTl7XokhZiULzdc
            SKJc51cXk02UYVAejAAA7
            '''

        paste_zone = '''R0lGODlhEAAQAKEBAAAAACQ5qTBM4SQ5qSH5BAEKAAMALAAAAAAQABAA
            AAI3TDaGmocP44KgyuUG\nELXHvBkicGlC0KFPZooGiT1hB68yV5dmDrEbvwJxdELgxX
            Nh6TAOhtNRAAA7
            '''

        extend_zone = '''R0lGODlhEAAQAKECAAAAACQ5qTBM4TBM4SH5BAEKAAMALAAAAAAQABA
            AAAI3TDaGmocP44Kg2vrY\nAMJ4ADmbcGHSCJ4iejYPd0ki97UIbEUr3Gp4nHkJhsSUp
            JSb2HSMpoNRAAA7
            '''

        # Add embedded images to the image dictionary
        cls.imgs = {"add_new": tk.PhotoImage("img_addnew_active", data=addnew_data),
                    "draw": tk.PhotoImage("img_draw_tool", data=draw_tool_data),
                    "move": tk.PhotoImage("img_move_tool", data=move_tool_data),
                    "grid": tk.PhotoImage("img_grid_mode", data=grid_mode_data),
                    "border": tk.PhotoImage("img_border_mode", data=border_mode_data),
                    "tile_layer": tk.PhotoImage("img_tile_layer", data=tile_layer_data),
                    "deco_layer": tk.PhotoImage("img_deco_layer", data=deco_layer_data),
                    "collider_layer": tk.PhotoImage("img_collide_layer", data=collision_layer_data),
                    "loading_layer": tk.PhotoImage("img_load_layer", data=loading_layer_data),
                    "light_layer": tk.PhotoImage("img_light_layer", data=light_layer_data),
                    "delete_zone": tk.PhotoImage("img_del_zone", data=delete_zone).zoom(64).subsample(16),
                    "new_zone": tk.PhotoImage("img_new_zone", data=new_zone).zoom(64).subsample(16),
                    "configure_zone": tk.PhotoImage("img_edit_zone", data=configure_zone).zoom(64).subsample(16),
                    "copy_zone": tk.PhotoImage("img_copy_zone", data=copy_zone).zoom(64).subsample(16),
                    "paste_zone": tk.PhotoImage("img_paste_zone", data=paste_zone).zoom(64).subsample(16),
                    "extend_zone": tk.PhotoImage("img_paste_zone", data=extend_zone).zoom(64).subsample(16)}

        cls.loading_dict = [cls.imgs["delete_zone"],
                            cls.imgs["new_zone"],
                            cls.imgs["configure_zone"],
                            cls.imgs["copy_zone"],
                            cls.imgs["paste_zone"],
                            cls.imgs["extend_zone"]]

        # TODO: Add light images
        cls.light_dict = [cls.imgs["delete_zone"]]

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
                file_data = {"tile_ids": [],
                             "deco_ids": []}
                json.dump(file_data, f)
                print("Error: File not found")

        cls.__initialized = True


class TilemapView(tk.Frame):
    __initialized = False
    imgs = {}

    def __init__(self, parent, **kw):
        """Sub-window for viewing individual levels"""
        # Check if the parent is a notebook, which it SHOULD BE
        super().__init__(parent, **kw)
        if type(parent) != CustomNotebook:
            raise TypeError("Cannot assign a {} to a {}".format(TilemapView, type(parent)))

        # Ensure that the images have been initialized
        if not TilemapView.__initialized:
            TilemapView._initialize()

        # Declare some variables for view settings
        self.start_x = 0
        self.start_y = 0
        self.saved = False
        self.current_tile = 0

        # Declare some variables related to the tilemap itself
        self.name = "Untitled"
        self.level_width = 16 + 2
        self.level_height = 9 + 2
        self.tilemap = [[0] * self.level_width for i in range(self.level_height)]
        self.decomap = [[0] * self.level_width for i in range(self.level_height)]
        self.collider = [[0] * (self.level_width * 2) for i in range(self.level_height * 2)]
        self.default_start = [0, 0]
        self.lightmap = []
        self.loading_zones = []
        self.file_path = None

        # Create element layout
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.canvas = tk.Canvas(self.frame, width=64 * 16, height=64 * 9, bg="WHITE", bd=0)
        self.canvas.grid(row=0, column=0)

        # Add the scrollbars
        self.canvas_vbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas_vbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas_vbar.activate("slider")
        self.canvas_hbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas_hbar.grid(row=1, column=0, sticky=tk.EW)
        self.canvas_hbar.activate("slider")
        self.canvas.config(scrollregion=(0, 0, 64 * self.level_width, 64 * self.level_height),
                           xscrollcommand=self.canvas_hbar.set,
                           yscrollcommand=self.canvas_vbar.set)
        self.canvas.xview(tk.MOVETO, 0.0)
        self.canvas.yview(tk.MOVETO, 0.0)

        # Add the view to the parent frame
        parent.add(self.frame)
        self.update_title()

        # Ensure settings are set
        self.set_mode(parent.master.tool_mode.get())
        self.set_border(parent.master.border_mode.get())
        self.canvas.bind("<Motion>", self.update_coords)

        # Draw the entire view
        self.redraw_view()

    def update_coords(self, event):
        """Event callback for updating the tilemap editor's coordinates"""
        self.master.master.tile_coords_text.set("Row, Col: {}, {}".format(event.y // 64, event.x // 64))
        self.master.master.level_coords_text.set("X, Y: {}, {}".format(event.x, event.y))

    def close(self):
        """Tells the view to close"""
        if not self.saved:
            # If progress is unsaved, ask user if they want to save
            action = messagebox.askyesnocancel("World Builder 2",
                                               "Progress is unsaved.  Would you like to save first?",
                                               icon='warning')

            # User wants to save progress before closing tab
            if action:
                self.save_to_file(self.file_path)

            # User wants to cancel
            if action is None:
                return False

            # User wants to continue without saving
            if action is False:
                pass

        self.frame.unbind_all(["<<TilemapEditorUpdateMode>>",
                               "<<TilemapEditorGridToggle>>",
                               "<<TilemapEditorBorderToggle>>",
                               "<<TilemapEditorForceRedraw>>"])
        self.frame.forget()
        return True

    def draw_collision(self):
        """Draw the collision map"""
        for i in range(self.level_width * 2 + 1):
            self.canvas.create_line(32 * i, 0, 32 * i, 64 * self.level_height, fill="BLACK", width=1.0)
        for i in range(self.level_height * 2 + 1):
            self.canvas.create_line(0, 32 * i, 64 * self.level_width, 32 * i, fill="BLACK", width=1.0)
        for i, j in enumerate(self.collider):
            solid_count = 0
            last_k = 0
            # When drawing rows, combine adjacent solids into a single rectangle
            for k, m in enumerate(j):
                if m == 1:
                    solid_count += 1
                elif m == 0 and solid_count > 0:
                    self.canvas.create_rectangle((k * 32 - 32 * solid_count, i * 32, k * 32, i * 32 + 32),
                                                 fill="gray",
                                                 width=1,
                                                 stipple="gray50")
                    solid_count = 0
                last_k = k

            # Entire row was solid, and never got a chance to fill in during loop.  Do so now.
            if solid_count > 0:
                self.canvas.create_rectangle((0, i * 32, last_k * 32 + 32, i * 32 + 32),
                                             fill="gray",
                                             width=1,
                                             stipple="gray50")

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

    def redraw_view(self):
        """Redraw the entire view"""
        # Redraw basic map
        self.canvas.delete("all")
        self.draw_tilemap()
        self.draw_decomap()

        # Draw layer-specific stuff (self.master.master.layer.get())
        if self.master.master.layer.get() == 2:
            self.draw_collision()
        elif self.master.master.layer.get() == 3:
            # TODO: Add loading zone layer
            print("LOADING ZONE UNIMPLEMENTED")
        elif self.master.master.layer.get() == 4:
            # TODO: Add lightmap layer
            print("LIGHTMAP UNIMPLEMENTED")

        # Redraw the grid if enabled (self.master.master.grid_mode.get()=1)
        if self.master.master.grid_mode.get():
            self.draw_grid()

        # Redraw the border if enabled (self.master.master.border_mode.get()=1)
        if self.master.master.border_mode.get():
            self.draw_border()

    def set_id(self, tile_id):
        """Event callback to update the current tile ID"""
        self.current_tile = tile_id

    def update_title(self):
        """Update the title of the view"""
        # If not saved, add an asterisk in front of the displayed name
        if self.saved:
            self.frame.master.tab(self.frame, text=self.name)
        else:
            self.frame.master.tab(self.frame, text="*" + self.name)

    def set_mode(self, value):
        """Does the actual work of setting the window's mode"""
        if value == 0:
            # Drawing controls
            # self.canvas.unbind_all(["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"])
            for i in ["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"]:
                self.canvas.unbind(i)
            # Tilemap mode
            if self.master.master.layer.get() == 0:
                self.canvas.bind("<B1-Motion>", self.draw_tile)
                self.canvas.bind("<ButtonRelease-1>", self._draw_tile_and_grid)
            # Decomap mode
            elif self.master.master.layer.get() == 1:
                self.canvas.bind("<B1-Motion>", self.draw_deco)
                self.canvas.bind("<ButtonRelease-1>", self._draw_deco_and_grid)
            # Collision map mode
            elif self.master.master.layer.get() == 2:
                self.canvas.bind("<B1-Motion>", self.draw_collider)
                self.canvas.bind("<ButtonRelease-1>", self._draw_collider_and_grid)
            # Loading zone mode
            elif self.master.master.layer.get() == 3:
                pass
            # Lightmap mode
            elif self.master.master.layer.get() == 4:
                pass
            self.canvas.config(cursor="pencil")
        elif value == 1:
            # Movement controls
            for i in ["<ButtonRelease-1>", "<ButtonPress-1>", "<B1-Motion>"]:
                self.canvas.unbind(i)
            # self.canvas.unbind("<ButtonRelease-1>")  # Manually unbind event because I don't know
            # self.canvas.unbind_all(["<ButtonRelease-1>", "<ButtonPress-1>", "<B1-Motion>"])
            self.canvas.bind("<ButtonPress-1>", self.set_start)
            self.canvas.bind("<B1-Motion>", self.move)
            self.canvas.config(cursor="fleur")

    def _draw_tile_and_grid(self, event):
        self.canvas.delete("all")
        self.draw_tile(event)
        self.redraw_view()

    def _draw_deco_and_grid(self, event):
        self.canvas.delete("all")
        self.draw_deco(event)
        self.redraw_view()

    def _draw_collider_and_grid(self, event):
        self.canvas.delete("all")
        self.draw_collider(event)
        self.redraw_view()

    def set_grid(self):
        """Update the grid overlay"""
        self.redraw_view()

    def set_border(self, value):
        """Toggle the border overlay"""
        if value:
            # Show border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0, 0, 64 * self.level_width, 64 * self.level_height))
        else:
            # Disable border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(64, 64, 64 * (self.level_width - 1), 64 * (self.level_height - 1)))
        self.redraw_view()

    def set_layer(self):
        """Update the layer visibility status"""
        self.set_mode(self.master.master.tool_mode.get())
        self.redraw_view()

    def draw_tile(self, event):
        """Event callback for drawing a tile on the grid"""
        # Determine the position at which to to draw the tile
        tile_x = int(self.canvas.xview()[0] * len(self.tilemap[0]) + event.x / 64)
        tile_y = int(self.canvas.yview()[0] * len(self.tilemap) + event.y / 64)

        border_mode = self.master.master.border_mode.get()

        if not border_mode:
            tile_x += 1
            tile_y += 1

        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        if event.y / 64 < int(self.canvas.yview()[0] * len(self.tilemap)):
            return
        if event.y / 64 + 0.1 > int(self.canvas.yview()[1] * len(self.tilemap) - 1 - int(not border_mode)):
            return
        if event.x / 64 < int(self.canvas.xview()[0] * len(self.tilemap[0])):
            return
        if event.x / 64 + 0.1 > int(self.canvas.xview()[1] * len(self.tilemap[0]) - 1 - int(not border_mode)):
            return

        # Draw the tile
        self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                 image=TilemapEditorWindow.tile_dict[self.current_tile])
        # Add the tile to the tilemap matrix
        try:
            self.tilemap[tile_y][tile_x] = int(self.current_tile)
        except IndexError:
            pass

    def draw_deco(self, event):
        """Draw either a tile or a deco on the grid, depending on the arguments"""
        # Determine the position at which to to draw the tile
        tile_x = int(self.canvas.xview()[0] * len(self.decomap[0]) + event.x / 64)
        tile_y = int(self.canvas.yview()[0] * len(self.decomap) + event.y / 64)

        border_mode = self.master.master.border_mode.get()

        if not border_mode:
            tile_x += 1
            tile_y += 1

        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        if event.y / 64 < int(self.canvas.yview()[0] * len(self.decomap)):
            return
        if event.y / 64 + 0.1 > int(self.canvas.yview()[1] * len(self.decomap) - 1 - int(not border_mode)):
            return
        if event.x / 64 < int(self.canvas.xview()[0] * len(self.decomap[0])):
            return
        if event.x / 64 + 0.1 > int(self.canvas.xview()[1] * len(self.decomap[0]) - 1 - int(not border_mode)):
            return

        # Draw the tile
        self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                 image=TilemapEditorWindow.deco_dict[self.current_tile])
        # Add the tile to the tilemap matrix
        try:
            self.decomap[tile_y][tile_x] = int(self.current_tile)
        except IndexError:
            pass

    def draw_collider(self, event):
        """Event callback for drawing a tile on the grid"""
        border = self.master.master.border_mode.get()

        if not border:
            event.x += 32
            event.y += 32

        # Determine the position at which to to draw the tile
        tile_x = int(self.canvas.xview()[0] * len(self.collider[0]) + event.x / 32)
        tile_y = int(self.canvas.yview()[0] * len(self.collider) + event.y / 32)

        if not border:
            tile_x += 1
            tile_y += 1

        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        # Top side catch
        if event.y / 32 < int(self.canvas.yview()[0] * len(self.collider)):
            return
        # Bottom side catch
        if event.y / 32 + 0.2 > int(self.canvas.yview()[1] * len(self.collider) - 1 - 2 * int(not border)):
            return
        # Left size catch
        if event.x / 32 < int(self.canvas.xview()[0] * len(self.collider[0])):
            return
        # Right side catch
        if event.x / 32 + 0.2 > int(self.canvas.xview()[1] * len(self.collider[0]) - 1 - 2 * int(not border)):
            return

        # Draw the tile
        self.canvas.create_rectangle((tile_x * 32, tile_y * 32, tile_x * 32 + 32, tile_y * 32 + 32),
                                     fill="gray",
                                     width=1,
                                     stipple="gray50")

        # Add the tile to the tilemap matrix
        try:
            self.collider[tile_y][tile_x] = 1
        except IndexError:
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
        """Loads level data from a .json file"""
        with open(file, mode="r") as f:
            level_data = json.load(f)
            self.tilemap = level_data["tilemap"]
            self.decomap = level_data["decomap"]
            self.level_height = len(self.tilemap)
            self.level_width = len(self.tilemap[0])
            self.name = level_data["name"]
            self.default_start = level_data["spawn"]
            self.lightmap = level_data["lightmap"]
            self.loading_zones = level_data["loading_zones"]
            self.saved = True
        self.set_border(self.master.master.border_mode.get())
        self.update_title()
        self.redraw_view()

    def quick_save(self):
        """Saves the level data to the file defined by self.file_path"""
        self.save_to_file(self.file_path)

    def save_to_file(self, file):
        """Saves the level data to a .json file"""
        # TODO: Test if saved files are actually loadable in engine.
        # No file path has been set
        if file is None:
            file = filedialog.asksaveasfilename(filetypes=[('JSON File', '*.json')],
                                                defaultextension=[('JSON File', '*.json')])
            # User canceled saving, exit function
            print("File: ", file)
            if file == "":
                return

            # Record path
            file = path.split(file)[1]
            self.name = path.splitext(file)[0]
            file = path.join("maps", file)
            self.file_path = file

        # Write json tag to file
        with open(file, mode="w") as f:
            level_data = {"tilemap": self.tilemap,
                          "decomap": self.decomap,
                          "colliders": self.collider,
                          "loading_zones": self.loading_zones,
                          "lightmap": self.lightmap,
                          "spawn": self.default_start,
                          "name": self.name}
            json.dump(level_data, f)
        self.saved = True
        self.update_title()

    @classmethod
    def _initialize(cls):
        """Initialize the embedded images"""
        border_tile_data = tk.PhotoImage("img_border_tile", data='''R0lGODlhEAAQ
            AIABAP/0ANXLACH5BAEKAAEALAAAAAAQABAAAAImhINokMq9WjiQJuvexbHqiYFf\nt4
            0hKUooqJ5fWrUvutKuOXN3UwAAOw==
            ''').zoom(64).subsample(16)

        inactive_zone = tk.PhotoImage("img_border_tile", data='''R0lGODlhEAAQAKE
            CAAAAAMMAAACPAACPACH5BAEKAAIALAAAAAAQABAAAAI2TCSGmocP44qgWshE\nNabiB
            wRWCEgIeYqPc5YaurAg6U6UWJtpnpgXJtOtfMIbLwiScGLMBqIAADs=
            ''').zoom(64).subsample(16)

        active_zone = tk.PhotoImage("img_border_tile", data='''R0lGODlhEAAQAKEBA
            AAAAACPAACkIQCPACH5BAEKAAMALAAAAAAQABAAAAI0lDaGmocP45J0uQjo\nhSBXHHg
            T0pVAED7Mibao6ADGPIuP2RlwJdsMZhthPkRVETKzKBuIAgA7
            ''').zoom(64).subsample(16)

        cls.imgs = {"border": border_tile_data,
                    "active_zone": active_zone,
                    "inactive_zone": inactive_zone}


class SelectionPane(tk.Frame):

    def __init__(self, parent, **kw):
        """Overarching class for the object selection panes"""
        super().__init__(parent, **kw)
        # Add the tile canvas
        self.canvas = tk.Canvas(self, width=72 * 3, height=72 * 8, bg="WHITE", bd=0)
        self.canvas.grid_propagate(False)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)

        # Add the scrollbars
        self.canvas_vbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas_vbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas_vbar.activate("slider")
        # self.canvas_hbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        # self.canvas_hbar.grid(row=1, column=0, sticky=tk.E + tk.W)
        # self.canvas_hbar.activate("slider")
        self.canvas.config(scrollregion=(0, 0, 64 * 3, 64 * 16),
                           # xscrollcommand=self.canvas_hbar.set,
                           yscrollcommand=self.canvas_vbar.set)
        self.canvas.xview(tk.MOVETO, 0.0)
        self.canvas.yview(tk.MOVETO, 0.0)

        # Declare positional variables
        self.current_x = 0
        self.current_y = 0

    def add_option(self, *args):
        """Base function to add a new entry to the selection pane.  Override in subclass"""
        pass


class TilePane(SelectionPane):

    def __init__(self, parent, **kw):
        """Overarching class for selection panes that are specifically for tiles"""
        self.var_ref = None
        super().__init__(parent, **kw)

    def add_option(self, value, mode):
        """Base function to add a new tile to the selection pane"""
        # Correct next position
        if self.current_x == 3:
            self.current_y += 1
            self.current_x = 0

        # If mode = "tile" load from tileset.  If mode = "deco" load from decoset
        if mode == "tile":
            radiobutton = tk.Radiobutton(self.canvas,
                                         indicator=0,
                                         value=value,
                                         variable=self.var_ref,
                                         image=TilemapEditorWindow.tile_dict[value])
        elif mode == "deco":
            radiobutton = tk.Radiobutton(self.canvas,
                                         indicator=0,
                                         value=value,
                                         variable=self.var_ref,
                                         image=TilemapEditorWindow.deco_dict[value])
        else:
            raise ValueError("Cannot initialize TileCollection with unknown mode '{}'."
                             "  Options are 'tile' and 'deco'".format(mode))

        # Configure new radiobutton
        self.canvas.create_window(self.current_x * 72 + 36, self.current_y * 72 + 36, window=radiobutton)
        self.current_x += 1


class TileCollection(TilePane):

    def __init__(self, parent, group, mode, var, **kw):
        """These are configurable groupings of tiles to make it easier to find specific tiles"""
        super().__init__(parent, **kw)

        # Save a reference to the tracker variable
        self.var_ref = var

        # TODO: Add a configuration option for changing the width of the pane
        # Iterate through group to declare tile images in a HEIGHT x 3 grid
        for i in group:
            if self.current_x == 3:
                self.current_y += 1
                self.current_x = 0
            # If mode = "tile" load from tileset.  If mode = "deco" load from decoset
            if mode == "tile":
                radiobutton = tk.Radiobutton(self.canvas,
                                             indicator=0,
                                             value=i,
                                             variable=var,
                                             image=TilemapEditorWindow.tile_dict[i])
            elif mode == "deco":
                radiobutton = tk.Radiobutton(self.canvas,
                                             indicator=0,
                                             value=i,
                                             variable=var,
                                             image=TilemapEditorWindow.deco_dict[i])
            elif mode == "loading":
                radiobutton = tk.Radiobutton(self.canvas,
                                             indicator=0,
                                             value=i,
                                             variable=var,
                                             image=TilemapEditorWindow.loading_dict[i])
            elif mode == "light":
                radiobutton = tk.Radiobutton(self.canvas,
                                             indicator=0,
                                             value=i,
                                             variable=var,
                                             image=TilemapEditorWindow.light_dict[i])
            else:
                raise ValueError("Cannot initialize TileCollection with unknown mode '{}'."
                                 "  Options are 'tile' and 'deco'".format(mode))

            # Configure new radiobutton
            self.canvas.create_window(self.current_x * 72 + 36, self.current_y * 72 + 36, window=radiobutton)
            self.current_x += 1

        # Configure scroll-region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


class TileAssembly(SelectionPane):

    def __init__(self, parent, **kw):
        """These are multi-tile objects that allow one to place structures quickly—like trees, for example"""
        super().__init__(parent, **kw)


class WorldEditorWindow:

    def __init__(self, parent):
        # Create the source frame
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Create the canvas viewport
        self.canvas = tk.Canvas(self.frame, bg="BLACK", bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Add to parent frame
        parent.add(self.frame, text="World Editor")


class NotesEditorWindow:

    def __init__(self, parent):
        # Create the source frame
        self.frame = tk.Frame(parent, borderwidth=1, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.BOTH, expand=1)

        # Create the text entry
        self.textbox = tk.Text(self.frame, borderwidth=1, padx=10, pady=10, maxundo=10)
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.textbox.bind("<Control-z>", lambda event: self.undo_edit())
        self.textbox.bind("<Control-y>", lambda event: self.redo_edit())
        self.textbox.bind("<Control-BackSpace>", lambda event: self.delete_word())

        # Add to parent frame
        parent.add(self.frame, text="Notes")

    def undo_edit(self):
        """Undo an edit"""
        try:
            self.textbox.config(undo=True)
            self.textbox.edit_undo()
        except tk.TclError:
            pass

    def redo_edit(self):
        """Redo an edit"""
        try:
            self.textbox.config(undo=True)
            self.textbox.edit_redo()
        except tk.TclError:
            pass

    def delete_word(self):
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
        self.source.bind("<<NotebookTabChanged>>",
                         lambda event: self.update_toolbar(self.source.index("current")))

    def update_toolbar(self, value):
        """Updates the toolbar to match the current tab"""
        self.menubar.forget()
        self.menubar = tk.Menu(self.source.master)
        # Tilemap editor window toolbar
        if value == 0:
            # self.menubar = self.tilemap_editor.menubar
            self.source.master.config(menu=self.tilemap_editor.menubar)
        else:
            self.source.master.config(menu=self.menubar)


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
