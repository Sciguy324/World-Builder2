import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from tkinter import ttk
from PIL import ImageTk, Image
from os import path
from os import getcwd
import json
import re
from dataclasses import dataclass, field
from typing import List


class ScrollbarEntry(tk.Frame):
    """Class for entries that follow the format Label, Scrollbar, Entry"""

    def __init__(self, parent, text=None, value=None, max_value=1024.0, **kwargs):
        super().__init__(parent, **kwargs)
        # Convert to list format
        if type(text) != list:
            # If the text was not given, create a list of 'None' based on commands
            if text is None:
                if type(value) == list:
                    # If command is a list, use its length for self.texts
                    self.texts = [None] * len(value)
                else:
                    # Command was not a list, so just assume its length is '1'
                    self.texts = [None]
            else:
                # If text was not a list and not 'None' assume it must be converted to a list
                self.texts = [text]
        else:
            # text was already a list
            self.texts = text

        if type(value) != list:
            if value is None:
                if type(text) == list:
                    # If text is a list, use its length for self.commands
                    self.values = [None] * len(text)
                else:
                    # text was not a list, so just assume its length is '1'
                    self.values = [None]
            else:
                # If command was not a list and not 'None' assume it must be converted to a list
                self.values = [value]
        else:
            # command was already a list
            self.values = value

        # Check for dimension mismatch
        if len(self.texts) != len(self.values):
            raise ValueError("Length mismatch between text and commands")

        self.variables = []
        self.text_variables = []
        # noinspection PyUnusedLocal
        for i, j in enumerate(self.values):
            self.variables.append(tk.DoubleVar(self, j))
            self.text_variables.append(tk.StringVar(self, str(j)))
            self.text_variables[i].trace_variable('w', lambda name, index, op, bound_i=i: self.set_variable(bound_i))

        self.labels = []
        self.scrollbars = []
        self.entries = []

        # Add the widgets
        for i, (j, k, m, n) in enumerate(zip(self.texts, self.variables, self.values, self.text_variables)):
            self.labels.append(tk.Label(self, text=j))
            self.labels[i].grid(row=i, column=0, sticky=tk.NW)
            self.scrollbars.append(tk.Scale(self, from_=0, to=max_value, showvalue=0, orient=tk.HORIZONTAL, variable=k,
                                            command=self.raise_event))
            self.scrollbars[i].grid(row=i, column=1, sticky=tk.NW)
            self.entries.append(tk.Entry(self, width=6, textvariable=n))
            self.entries[i].grid(row=i, column=2, sticky=tk.NW)

    def set_variable(self, index):
        """Event callback for text variables so that the actual variables are up to date"""
        try:
            self.variables[index].set(float(self.text_variables[index].get()))
            self.event_generate("<<ScrollbarMoved>>")
        except ValueError:
            pass

    def raise_event(self, event=None):
        """Raise an event telling the parent widget that the scrollbars have been used"""
        for i, j in zip(self.entries, self.variables):
            i.delete(0, tk.END)
            i.insert(0, str(j.get()))

        self.event_generate("<<ScrollbarMoved>>")


class Dialog(tk.Toplevel):
    """General class for dialogs"""

    def __init__(self, parent, *args, title=None, **kwargs):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        # Initialize class variables
        self.parent = parent
        self.result = None

        # Set up basic window geometry
        if title:
            self.title(title)
        self.frame = tk.Frame(self)
        self.initial_focus = self.body()
        self.frame.pack(padx=5, pady=5)
        self.buttons()

        # Adjust some configurations
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.initial_focus.focus_set()

        self.wait_window(self)

    def body(self):
        """Create the dialog body.  Override in subclass."""
        pass

    def buttons(self):
        """Add OK and CANCEL buttons.  Override in subclass if unneeded."""
        # This frame acts independently of self.frame
        frame = tk.Frame(self)

        # Create the OK button
        ok_button = tk.Button(frame, text="Ok", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Create the CANCEL button
        cancel_button = tk.Button(frame, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Bind some shortcuts
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        frame.pack()

    def ok(self, event=None):
        """Event callback for pressing the OK button."""

        # Check if fields are valid
        if not self.check():
            return

        # Remove the window from the screen and update
        self.withdraw()
        self.update_idletasks()

        # Apply the data entered in the fields and finally destroy the dialog window
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        """Function to handle closing the window.  Override in subclass."""
        self.parent.focus_set()
        self.destroy()

    def check(self):
        """Verify the output.  Override in subclass."""
        return 1

    def apply(self):
        """Return the output.  Override in subclass."""
        pass


class DataSetDialog(Dialog):

    def __init__(self, parent, fields, title=None, **kwargs):
        # Check 'fields' validity before proceeding
        # Check if fields is a dictionary
        if type(fields) == dict:
            fields = [fields]
        # Check if fields is a list of either length zero or of dictionaries
        if type(fields) == list and (len(fields) == 0 or all([type(i) == dict for i in fields])):
            pass
        else:
            raise ValueError("Unsupported type '{},' fields must be a dictionary or a list of dictionaries".
                             format(type(fields)))
        self.fields = fields
        self.button_set = []
        super().__init__(parent, title=title, **kwargs)

    def body(self):
        """Create the body of the dialog"""
        for i, j in enumerate(self.fields):
            c = 0
            self.button_set.append({})
            for k, m in j.items():
                label = tk.Label(self.frame, text=str(k))
                label.grid(row=i, column=c)
                c += 1
                self.button_set[i][k] = tk.Entry(self.frame)
                self.button_set[i][k].insert(0, str(m))
                self.button_set[i][k].grid(row=i, column=c)
                c += 1

    def check(self):
        """Check if the fields are valid"""
        return True

    def apply(self):
        """Update self.result with the data entered in the fields"""
        self.result = []
        for i, j in enumerate(self.fields):
            self.result.append({})
            for k, m in j.items():
                self.result[i][k] = self.button_set[i][k].get()


class NumberSetDialog(DataSetDialog):

    def __init__(self, parent, fields, title=None, **kwargs):
        super().__init__(parent, fields, title, **kwargs)

    def check(self):
        """Check if all fields are a number"""
        for i in self.button_set:
            for j, k in i.items():
                try:
                    int(k.get())
                    float(k.get())
                except ValueError:
                    return False
        return True


class LightEditorDialog(Dialog):
    """Dialog for editing lights"""

    def __init__(self, parent, light_data, **kwargs):
        self.light_data = light_data.copy()
        self.canvas = None
        self.blacklight_state = None
        self.diameter_slider = None
        self.red_slider = None
        self.green_slider = None
        self.blue_slider = None
        self.shade_color = (100, 100, 100)

        super().__init__(parent, title="Edit Light", **kwargs)

    def body(self):
        """Generate the body of the window"""
        # Create the canvas
        self.canvas = tk.Canvas(self.frame, width=256, height=256)
        self.canvas.pack(padx=5, pady=5)

        # Color the canvas
        self.canvas.create_rectangle((0, 0, 256, 256), fill="black", width=1)

        # Basic properties editing section
        # Blacklight tracking variable
        self.blacklight_state = tk.BooleanVar(self, False)
        self.blacklight_state.trace_variable('w', lambda name, index, op: self.event_generate("<<ScrollbarMoved>>"))

        # Blacklight box
        blacklight_frame = tk.Frame(self.frame)
        blacklight_frame.pack(padx=5, pady=5)
        tk.Label(blacklight_frame, text="Blacklight?").grid(row=0, column=0, sticky=tk.W)
        blacklight_box = tk.Checkbutton(blacklight_frame, variable=self.blacklight_state)
        blacklight_box.grid(row=0, column=1, sticky=tk.W)

        # Create the maximum diameter scrollbar entry
        self.diameter_slider = ScrollbarEntry(self.frame, text="Maximum Diameter", value=self.light_data.diameter,
                                              max_value=8)
        self.diameter_slider.pack(padx=5, pady=5)

        # Add the color fade editing sections
        # Editing section header
        tk.Label(self.frame, text="Red Effect").pack(padx=5, pady=5)
        # Add the amplitude, inner diameter, and outer diameter sliders/entries
        self.red_slider = ScrollbarEntry(self.frame,
                                         text=["Amplitude", "Inner Diameter", "Outer Diameter"],
                                         value=[self.light_data.red.amplitude,
                                                self.light_data.red.inner_diameter,
                                                self.light_data.red.outer_diameter],
                                         max_value=512.0)
        self.red_slider.pack()

        # Editing section header
        tk.Label(self.frame, text="Green Effect").pack(padx=5, pady=5)
        # Add the amplitude, inner diameter, and outer diameter sliders/entries
        self.green_slider = ScrollbarEntry(self.frame,
                                           text=["Amplitude", "Inner Diameter", "Outer Diameter"],
                                           value=[self.light_data.green.amplitude,
                                                  self.light_data.green.inner_diameter,
                                                  self.light_data.green.outer_diameter],
                                           max_value=512.0)
        self.green_slider.pack()

        # Editing section header
        tk.Label(self.frame, text="Blue Effect").pack(padx=5, pady=5)
        # Add the amplitude, inner diameter, and outer diameter sliders/entries
        self.blue_slider = ScrollbarEntry(self.frame,
                                          text=["Amplitude", "Inner Diameter", "Outer Diameter"],
                                          value=[self.light_data.blue.amplitude,
                                                 self.light_data.blue.inner_diameter,
                                                 self.light_data.blue.outer_diameter],
                                          max_value=512.0)
        self.blue_slider.pack()

        # Add the draw_light callback for the scrollbars
        self.bind("<<ScrollbarMoved>>", lambda event: self.draw_light())
        self.draw_light()

    @staticmethod
    def calc_intensity(color, value, blacklight=False):
        # Note: assumes background is black
        try:
            n = int(max(min(color.amplitude /
                            (color.inner_diameter - color.outer_diameter) * (value - color.outer_diameter),
                            255.0), 0.0))
            if blacklight:
                return max(min(155 - n, 255), 0)
            else:
                return max(min(n - 100, 255), 0)
        except ZeroDivisionError:
            return 255

    def draw_light(self):
        """Draw a preview of the light in the display canvas"""
        # Update the light data
        # TODO: Add zoom feature for lights larger than the window
        self.light_data.blacklight = self.blacklight_state.get()
        self.light_data.diameter = self.diameter_slider.variables[0].get()

        self.light_data.red.amplitude = self.red_slider.variables[0].get()
        self.light_data.red.inner_diameter = self.red_slider.variables[1].get()
        self.light_data.red.outer_diameter = self.red_slider.variables[2].get()

        self.light_data.green.amplitude = self.green_slider.variables[0].get()
        self.light_data.green.inner_diameter = self.green_slider.variables[1].get()
        self.light_data.green.outer_diameter = self.green_slider.variables[2].get()

        self.light_data.blue.amplitude = self.blue_slider.variables[0].get()
        self.light_data.blue.inner_diameter = self.blue_slider.variables[1].get()
        self.light_data.blue.outer_diameter = self.blue_slider.variables[2].get()

        # Clear the canvas
        self.canvas.delete("all")
        if self.light_data.blacklight:
            self.canvas.create_rectangle((0, 0, 256, 256), fill='#%02x%02x%02x' % (155, 155, 155), width=0)
        else:
            self.canvas.create_rectangle((0, 0, 256, 256), fill="black", width=1)

        # Construct the light
        i = 64 * self.light_data.diameter
        blacklight = self.light_data.blacklight
        # i = 64
        red = self.light_data.red
        greem = self.light_data.green
        blue = self.light_data.blue
        while i >= 0.0:
            red_intensity = self.calc_intensity(red, i, blacklight)
            greem_intensity = self.calc_intensity(greem, i, blacklight)
            blue_intensity = self.calc_intensity(blue, i, blacklight)
            # print("RGB: {}, {}, {}".format(red_intensity, greem_intensity, blue_intensity))
            # print('\t#%02x%02x%02x' % (red_intensity, greem_intensity, blue_intensity))
            # c = self.light_data.diameter * 64 - i
            c = 64 - i
            self.canvas.create_oval((c * 2, c * 2, 256 - c * 2, 256 - c * 2),
                                    fill='#%02x%02x%02x' % (red_intensity, greem_intensity, blue_intensity),
                                    width=0)
            i -= 1

    def cancel(self, event=None):
        """Function to handle closing the window"""
        self.parent.focus_set()
        self.destroy()

    def check(self):
        """Verify the output.  Note: already checked during editing process."""
        return 1

    def apply(self):
        """Return the output by placing it in self.result"""
        self.result = self.light_data


class GroupEditorDialog(Dialog):

    def __init__(self, parent, id_list, groups: dict, **kwargs):
        # Declare variables related to body
        self.button_frame = None
        self.selected_group = None
        self.group_option_menu = None
        self.new_group_button = None
        self.delete_group_button = None
        self.content_frame = None
        self.preview_frame = None
        self.preview_canvas = None
        self.preview_scrollbar = None
        self.selection_frame = None
        self.selection_canvas = None
        self.selection_scrollbar = None
        self.selected_tile = None
        self.selection_translator = []
        self.selection_height = 0

        # Save data to variables
        self.groups = dict((i, j.copy()) for i, j in groups.items())
        self.group_panes = {}
        self.id_list = id_list

        super().__init__(parent, title="Edit Groups", **kwargs)

        # Button to add a new group
        # Button to remove an existing group
        # Selection pane to select what tiles should be in the group
        # Modification pane to modify the order of the tiles
        # Returns a GroupModifierObject

    def body(self):
        """Create the dialog body"""
        # Create a frame to house the buttons
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(anchor="nw")

        # Set up string variable
        self.selected_group = tk.StringVar(self)
        self.selected_group.set("Select Group")
        self.selected_group.trace_add('write', self.group_callback)

        # Group dropdown list that excludes any group named "All"
        group_names = [i for i, j in self.groups.items()]
        self.group_option_menu = tk.OptionMenu(self.button_frame, self.selected_group, *group_names)
        self.group_option_menu.grid(row=0, column=0, sticky=tk.W, padx=4)

        # Add new group button
        self.new_group_button = tk.Button(self.button_frame, text="New Group", command=self.add_group)
        self.new_group_button.grid(row=0, column=1, sticky=tk.W, padx=4)

        # Add delete group button
        self.new_group_button = tk.Button(self.button_frame, text="Delete Group", command=self.delete_group)
        self.new_group_button.grid(row=0, column=2, sticky=tk.W, padx=4)

        self.content_frame = tk.Frame(self.frame)
        self.content_frame.pack(anchor="nw")

        # Add preview canvas
        self.preview_frame = tk.Frame(self.content_frame)
        self.preview_frame.grid(row=0, column=1, sticky=tk.NW, padx=4)

        # Add all already defined groups
        for i, j in self.groups.items():
            self.group_panes[i] = GroupEditorGroup(self.preview_frame, j.copy())

        # Add selection canvas
        self.selection_frame = tk.Frame(self.content_frame)
        self.selection_frame.grid(row=0, column=0, sticky=tk.NW, padx=4)

        self.selection_canvas = tk.Canvas(self.selection_frame, width=16 * 64, height=5 * 64, bg="WHITE", bd=0)
        self.selection_canvas.grid(row=0, column=0, sticky=tk.NW, padx=4)
        self.selection_canvas.bind("<Button-1>", func=self.select_tile)
        self.selected_tile = tk.IntVar(self, 0, "group_editor_selected_tile")

        self.selection_scrollbar = tk.Scrollbar(self.selection_frame, orient=tk.VERTICAL,
                                                command=self.selection_canvas.yview)
        self.selection_scrollbar.grid(row=0, column=1, sticky=tk.NS, padx=4)
        self.selection_scrollbar.activate("slider")

        # Add content to selection canvas
        self.selection_translator = []
        x = 0
        self.selection_height = 0
        for i, j in self.id_list.items():
            self.selection_canvas.create_image((64 * x + 32, 64 * self.selection_height + 32), image=j)
            self.selection_translator.append(i)
            x += 1
            if x >= 16:
                self.selection_height += 1
                x = 0

        self.selection_height += 1

        # Activate the canvas scrollbars
        self.selection_canvas.config(scrollregion=(0, 0, 64 * 16, 64 * self.selection_height),
                                     yscrollcommand=self.selection_scrollbar.set)

    def reload_dropdown_menu(self):
        """Reload the dropdown menu"""
        self.group_option_menu['menu'].delete(0, 'end')
        for i, j in self.groups.items():
            self.group_option_menu['menu'].add_command(label=i, command=tk._setit(self.selected_group, i))

    def add_group(self, event=None):
        """Add a new group to the selection"""
        # Launch text dialogue to get the name of the new group
        result = DataSetDialog(self, [{"Group Name": ""}], "New Group").result
        if result is not None:
            new_group_name = str(result[0]['Group Name'])
            # Add the group to the list and create a new pane
            self.groups[new_group_name] = [-1, -1, -1]
            self.group_panes[new_group_name] = GroupEditorGroup(self.preview_frame)

            # Update the dropdown menu
            self.reload_dropdown_menu()

            # Set the current group
            self.selected_group.set(new_group_name)

    def delete_group(self, event=None):
        """Delete the currently open group"""
        # Hide the currently visible group
        for i, j in self.group_panes.items():
            j.pack_forget()

        # Remove the groups
        group_name = self.selected_group.get()
        self.group_panes[group_name].forget()
        del self.group_panes[group_name]
        del self.groups[group_name]

        # Reload the dropdown menu
        self.selected_group.set("Select Group")
        self.reload_dropdown_menu()

    def group_callback(self, name=None, index=None, op=None):
        """Callback function for when the group changes"""
        # Hide the currently visible group
        for i, j in self.group_panes.items():
            j.pack_forget()

        # Show the current group
        try:
            self.group_panes[self.selected_group.get()].pack(anchor="nw")
        except KeyError:
            pass

    def select_tile(self, event):
        """Select the tile at the given event coordinates"""
        # Obtain coordinates of the selected tile
        tile_x = int(event.x / 64)
        tile_y = int(self.selection_canvas.yview()[0] * self.selection_height + event.y / 64)

        # Ensure selection is within bounds
        if tile_x < 0 or tile_y < 0:
            return
        elif tile_x > 16 or tile_y > self.selection_height:
            return

        # Ensure selection is a valid tile
        if tile_y * 16 + tile_x >= len(self.selection_translator):
            self.selected_tile.set(-1)
        else:
            # Obtain the selected tile
            self.selected_tile.set(self.selection_translator[tile_y * 16 + tile_x])

        # Redraw the selection box
        self.selection_canvas.delete("selection_box")
        self.selection_canvas.create_rectangle((tile_x * 64, tile_y * 64, tile_x * 64 + 64, tile_y * 64 + 64),
                                               fill="orange",
                                               outline="orange",
                                               width=2,
                                               stipple="gray50",
                                               tag="selection_box")

        # Update the currently open group pane
        if self.selected_group.get() != "Select Group":
            self.group_panes[self.selected_group.get()].set_tile(self.selected_tile.get())

    def apply(self):
        """Apply the result, if applicable"""
        result = {}
        for group_name, pane in self.group_panes.items():
            tile_set = pane.tiles.copy()
            while len(tile_set) > 0 and tile_set[-1] == -1:
                tile_set.pop(-1)
            result[group_name] = tile_set
        self.result = result

    def cancel(self, event=None):
        """Function to handle closing the window."""
        # Clear the group panes from memory
        names = [i for i, j in self.group_panes.items()]
        for name in names:
            self.group_panes[name].destroy()
            del self.group_panes[name]

        # Return to the parent window and destroy this one
        self.parent.focus_set()
        self.destroy()


class GroupEditorGroup(tk.Frame):
    """A class for group panes specifically for the GroupEditorDialog class"""

    def __init__(self, parent, tiles=None, **kwargs):
        super().__init__(parent, **kwargs)

        # Initialize the tile list
        if tiles is None:
            self.tiles = [-1] * (16 * 9)
        else:
            self.tiles = tiles

        # Add the selected tile tracker variable
        self.selected_index = tk.IntVar(self, -1)

        # Construct the canvas
        self.canvas = tk.Canvas(self, width=3 * 64, height=9 * 64, bg="WHITE", bd=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NW, padx=4)

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky=tk.NS, padx=4)
        self.scrollbar.activate("slider")

        # Activate the canvas scrollbars
        self.canvas.config(scrollregion=(0, 0, 64 * 16, 64 * 9),
                           yscrollcommand=self.scrollbar.set)

        # Add the selection binding
        self.canvas.bind("<Button-1>", func=self.select_tile)

        self.auto_size()
        self.redraw()

    def auto_size(self):
        """Automatically resize the group list"""
        # If the tile list is deemed to short, extend it.
        if len(self.tiles) <= 3:
            self.tiles += [-1] * 9
        # If a tile is present near the end of the tile list, extend said list.
        elif self.tiles[:-4:-1] != [-1, -1, -1]:
            self.tiles += [-1] * 9
            self.canvas.config(scrollregion=(0, 0, 64 * 16, 64 * (len(self.tiles) // 3)))

    def redraw(self):
        """Redraws the panel"""
        self.canvas.delete("all")

        # Draw the tiles
        x = 0
        y = 0
        for i in self.tiles:
            if i != -1:
                self.canvas.create_image((64 * x + 32, 64 * y + 32), image=self.master.master.master.master.id_list[i])
            x += 1
            if x >= 3:
                y += 1
                x = 0

        # Highlight the selected tile, if applicable
        selected = self.selected_index.get()
        if selected != -1:
            tile_x = selected % 3
            tile_y = selected // 3
            self.canvas.create_rectangle((tile_x * 64, tile_y * 64, tile_x * 64 + 64, tile_y * 64 + 64),
                                         fill="blue",
                                         outline="blue",
                                         width=2,
                                         stipple="gray50",
                                         tag="selection_box")

    def set_tile(self, tile_id):
        """Set the currently selected tile to the given tile id"""
        if self.selected_index.get() != -1:
            self.tiles[self.selected_index.get()] = tile_id
            self.auto_size()
            self.redraw()
        else:
            self.auto_size()

    def select_tile(self, event):
        """Highlights the tile the user just clicked on"""
        height = len(self.tiles) // 3
        # Obtain coordinates of the selected tile
        tile_x = int(event.x / 64)
        tile_y = int(self.canvas.yview()[0] * height + event.y / 64)

        # Ensure selection is within bounds
        if tile_x < 0 or tile_y < 0:
            return
        elif tile_x > 3 or tile_y > height:
            return

        # Ensure selection is a valid tile
        if tile_y * 3 + tile_x >= len(self.tiles):
            return

        # Obtain the selected tile
        self.selected_index.set(tile_y * 3 + tile_x)

        # Redraw the selection box
        self.canvas.delete("selection_box")
        self.canvas.create_rectangle((tile_x * 64, tile_y * 64, tile_x * 64 + 64, tile_y * 64 + 64),
                                     fill="blue",
                                     outline="blue",
                                     width=2,
                                     stipple="gray50",
                                     tag="selection_box")


# TODO: Refactor ids list

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

        self.bind("<ButtonPress-1>", lambda event: self.on_press(), True)
        self.bind("<ButtonRelease-1>", lambda event: self.on_release(), True)

    def on_press(self):
        """Called when the button is pressed over the new map button"""
        self.state(['pressed'])
        print(self.config())

    def on_release(self):
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
        if not CustomNotebook.__initialized:
            CustomNotebook.__initialize_custom_style()
            CustomNotebook.__initialized = True

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

        # Raise an event to inform the relevant classes that the given tab is being closed
        if "close" in element and self._active == index:
            # self.forget(index)
            self.event_generate("<<NotebookTabClosed>>", x=index)

        self.state(["!pressed"])
        self._active = None

    @classmethod
    def __initialize_custom_style(cls):
        style = ttk.Style()
        cls.images = (
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


class TilemapEditorWindow(tk.Frame):
    imgs = {}
    tile_dict = {}
    deco_dict = {}
    mini_tile_dict = {}
    mini_deco_dict = {}
    collider_dict = {}
    height_dict = {}
    loading_dict = {}
    light_dict = {}
    ids_data = {}
    __initialized = False

    class Decorators(object):
        @classmethod
        def apply_to_current_view(cls, function):
            """Apply a function to the currently open view, if one is open.  The index of the current view is passed as
             the x-coordinate of event"""

            def inner(self, event=None):
                if self.master.index("current") != 0:
                    return
                function(self, self.tilemap_panel.index("current"))

            return inner

        @classmethod
        def hidden_event(cls, function):
            """For functions that should not be run if no views are currently open.
            An unused event argument is expected"""

            def inner(self, event=None):
                function(self)

            return inner

        @classmethod
        def callback(cls, function):
            """Reduces the unneeded 'name=None, index=None, op=None' arguments in callback functions"""

            def inner(self, name=None, index=None, op=None):
                function(self)

            return inner

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
                      "collision": {},
                      "height": {},
                      "loading": {},
                      "light": {}}

        self.visible_pane = None

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

        # Add the group tracking variable
        self.group = tk.StringVar(self, "", "selected_group")
        # TODO: Should this line exist?
        self.group.trace("w", lambda name, index, op: self.set_pane(self.group.get(), self.layer.get()))

        # Add the selected layer tracking variable
        self.layer = tk.IntVar(self, 0, "selected_layer")
        self.layer.trace("w", lambda name, index, op: self.set_layer(self.layer.get()))

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

        # Add layer selection buttons (tile, deco, collision, height, loading, light)
        for i, j in enumerate(["tile_layer", "deco_layer", "collider_layer", "height_layer", "loading_layer",
                               "light_layer"]):
            self.layer_button = tk.Radiobutton(self.buttons_bar, indicator=0, value=i, variable=self.layer,
                                               image=TilemapEditorWindow.imgs[j])
            self.layer_button.grid(row=0, column=i + 6, sticky=tk.NW)

        # Add another spacing
        self.button_spacing2 = tk.Frame(self.buttons_bar, height=16, width=16)
        self.button_spacing2.grid(row=0, column=12, sticky=tk.NW)

        # Add the tile coordinate label
        self.tile_coords_text = tk.StringVar(self, "Row, Col: ¯\\_(ツ)_/¯", "tile_coords_text")
        self.tile_coords = tk.Label(self.buttons_bar, textvariable=self.tile_coords_text,
                                    borderwidth=1, relief=tk.SUNKEN, padx=5, pady=5)
        self.tile_coords.grid(row=0, column=13, sticky=tk.W)

        # Add the level coordinate label
        self.level_coords_text = tk.StringVar(self, "X, Y: ¯\\_(ツ)_/¯", "level_coords_text")
        self.level_coords = tk.Label(self.buttons_bar, textvariable=self.level_coords_text,
                                     borderwidth=1, relief=tk.SUNKEN, padx=5, pady=5)
        self.level_coords.grid(row=0, column=14, sticky=tk.W)

        # TODO: Find a more efficient way of limiting the scope of these keybindings
        # Set up tool keybindings
        parent.master.bind("<Key-1>", self.keybind_draw_mode)
        parent.master.bind("<Key-2>", self.keybind_move_mode)
        parent.master.bind("<Key-3>", self.keybind_grid_mode)
        parent.master.bind("<Key-4>", self.keybind_border_mode)

        # Set up the layer keybindings
        for i in range(5, 10):
            parent.master.bind("<Key-{}>".format(i), self.keybind_layer_mode)
        parent.master.bind("<Key-0>", self.keybind_layer_mode)

        # Set up menubar keybindings
        parent.master.bind("<Control-o>", self._open_map)
        parent.master.bind("<Control-s>", self._save_map)
        parent.master.bind("<Control-S>", self._save_map_as)
        parent.master.bind("<Control-n>", self.new_view)
        parent.master.bind("<Control-w>", self._close_view)
        parent.master.bind("<Control-z>", self.undo)
        parent.master.bind("<Control-y>", self.redo)

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
        self.filemenu.add_command(label="Close Map (Ctrl-W)", command=self._close_view)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Settings", command=self.unimplemented)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Create the edit menubar
        self.editmenu = tk.Menu(self.menubar, tearoff=0)
        self.editmenu.add_command(label="Undo (Ctrl-Z)", command=self.undo)
        self.editmenu.add_command(label="Redo (Ctrl-Y)", command=self.redo)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Change Tilemap Size", command=self.change_tilemap_size)
        self.editmenu.add_separator()
        self.editmenu.add_command(label="Set Default Spawn", command=self._edit_default_spawn)
        self.menubar.add_cascade(label="Edit", menu=self.editmenu)

        # Create the tile menubar
        self.tilemenu = tk.Menu(self.menubar, tearoff=0)
        self.tilemenu.add_command(label="Edit Tile Groups", command=self.edit_tile_groups)
        self.tilemenu.add_command(label="Edit Deco Groups", command=self.edit_deco_groups)
        self.tilemenu.add_separator()
        self.tilemenu.add_command(label="Import Tile", command=lambda: self.import_tile('tile'))
        self.tilemenu.add_command(label="Import Deco", command=lambda: self.import_tile('deco'))
        self.menubar.add_cascade(label="Tile", menu=self.tilemenu)

        # Create the assembly menubar
        # self.assemblymenu = tk.Menu(self.menubar, tearoff=0)
        # self.assemblymenu.add_command(label="Edit Assembly Groups", command=self.unimplemented)
        # self.menubar.add_cascade(label="Assembly", menu=self.assemblymenu)

        self.project_menu = tk.Menu(self.menubar, tearoff=0)
        self.project_menu.add_command(label="Add Current Level to Project", command=self.include_level)
        self.project_menu.add_command(label="Remove Current Level from Project", command=self.exclude_level)
        self.menubar.add_cascade(label="Project", menu=self.project_menu)

        # Create the help menubar
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="This menubar cannot help you", command=self.unimplemented)
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)

        # Create initial tilemap view
        self.new_view()

    @Decorators.hidden_event
    def _open_map(self):
        """Event callback for opening a level"""
        # Make sure the tilemap editor is actually open
        if self.master.index("current") != 0:
            return
        file = filedialog.askopenfilename(filetypes=[("Json", "*.json")], defaultextension=[("Json", "*.json")])
        if file == "" or file is None:
            return
        self.open_map(file)

    def open_map(self, file):
        """Open a level in a new view"""
        self.new_view()
        self.view_list[self.tilemap_panel.index("current")].load_from_file(file)

    @Decorators.hidden_event
    def _save_map(self):
        """Event callback for saving a level"""
        if self.master.index("current") != 0:
            return
        self.view_list[self.tilemap_panel.index("current")].quick_save()

    @Decorators.hidden_event
    def _save_map_as(self):
        """Event callback for save a level as a new file"""
        if self.master.index("current") != 0:
            return
        self.view_list[self.tilemap_panel.index("current")].save_to_file(None)

    @Decorators.hidden_event
    def _edit_default_spawn(self):
        """Event callback for setting the default spawn of the currently open level"""
        input_data = self.view_list[self.tilemap_panel.index("current")].level.default_start
        data = NumberSetDialog(self.master.master, [{"Col": input_data[0], "Row": input_data[1]}]).result
        if data is not None:
            self.view_list[self.tilemap_panel.index("current")].level.default_start = [data[0]["Col"], data[0]["Row"]]

    @Decorators.hidden_event
    def new_view(self):
        """Create a new, blank view"""
        if self.master.index("current") != 0:
            return
        # Create new view instance
        self.view_list.append(TilemapView(self.tilemap_panel))
        self.tilemap_panel.select(self.tilemap_panel.index("end") - 1)

        # Redraw all open views
        for i in self.view_list:
            i.redraw_view()

    @Decorators.hidden_event
    def _close_view(self):
        # TODO: Make the close_view process a bit more sane
        """Event callback for closing the currently open view"""
        if self.master.index("current") != 0:
            return
        self.close_view(self.tilemap_panel.index("current"))

    def close_view(self, event):
        """Close the currently open view"""
        # Check with the view if it wants to close
        if type(event) == int:
            # Index of the view in question passed in directly
            if self.view_list[event].close():
                # Attempt to close view was not interrupted by user (such as by clicking "cancel" in an unsaved view)
                self.tilemap_panel.forget(event)
                self.view_list[event].destroy()
                del self.view_list[event]
        else:
            # Index of the view in question passed in as x-coordinate of event
            if self.view_list[event.x].close():
                # Attempt to close view was not interrupted by user
                self.tilemap_panel.forget(event.x)
                self.view_list[event.x].destroy()
                del self.view_list[event.x]

    def reload_view_size(self, index):
        """Reloads the viewport size in the given view"""
        if self.master.index("current") != 0:
            return
        self.view_list[index].set_border(not self.border_mode.get())
        self.view_list[index].set_border(self.border_mode.get())

    @Decorators.apply_to_current_view
    def undo(self, index):
        """Tell the tilemap at the given index to undo"""
        self.view_list[index].undo()
        self.reload_view_size(index)

    @Decorators.apply_to_current_view
    def redo(self, index):
        """Tell the tilemap at the given index to redo"""
        self.view_list[index].redo()
        self.reload_view_size(index)

    @Decorators.apply_to_current_view
    def change_tilemap_size(self, index):
        """Open a dialog to change the size of the currently open tilemap"""
        # Open the dialog
        size_change = NumberSetDialog(self.master.master, [{"Left": 0}, {"Right": 0}, {"Up": 0}, {"Down": 0}]).result
        if size_change is None:
            return
        try:
            self.view_list[index].level.change_size(left=int(size_change[0]["Left"]),
                                                    right=int(size_change[1]["Right"]),
                                                    up=int(size_change[2]["Up"]),
                                                    down=int(size_change[3]["Down"]))
        except ValueError:
            messagebox.showerror("Invalid Input", "Invalid Tilemap Size")

        # Reload the view area
        self.reload_view_size(index)
        self.view_list[index].backup_state()

    @Decorators.hidden_event
    def edit_tile_groups(self):
        """Open a dialog to edit the tile groups"""
        # Open the dialog
        result = GroupEditorDialog(self, TilemapEditorWindow.tile_dict,
                                   App.project_data["groups"]["tile"]).result
        if result is not None:
            App.project_data["groups"]["tile"] = result
            self.reload_groups()

    @Decorators.hidden_event
    def edit_deco_groups(self):
        """Open a dialog to edit the deco groups"""
        # Open the dialog
        result = GroupEditorDialog(self, TilemapEditorWindow.deco_dict,
                                   App.project_data["groups"]["deco"]).result
        if result is not None:
            App.project_data["groups"]["deco"] = result
            self.reload_groups()

    def import_tile(self, mode):
        """Import a tile"""
        # Verify mode
        if mode not in ["tile", "deco"]:
            raise ValueError(f'\'{mode}\' is not a valid mode.  Valid modes are \'tile\' and \'deco\'')

        # Open import dialog
        file = filedialog.askopenfile(filetypes=[('PNG File', '*.png')],
                                      defaultextension=[('PNG File', '*.png')])

        # User did, in fact, import a tile
        if file is not None:
            current_directory = getcwd().replace('\\', '/')
            file_path, tile_name = path.split(file.name)
            file.close()
            # If the tile is NOT already in the tile folder, save it there
            if current_directory + '/tiles' != file_path:
                print("Saving file to tile folder")
                with open(f'{file_path}/{tile_name}', mode='rb') as rf:
                    with open(f'tiles/{tile_name}', mode='wb') as wf:
                        wf.write(rf.read())
            else:
                print("Tile was already in tile folder")

            # Open the image
            img = Image.open(path.join(file_path, tile_name))
            img = img.crop([0, 0, 16, 16])
            img = img.resize((64, 64), Image.NORMAL)
            # Update the image registries
            next_id = max(TilemapEditorWindow.tile_dict.keys()) + 1
            TilemapEditorWindow.tile_dict[next_id] = ImageTk.PhotoImage(img)
            TilemapEditorWindow.ids_data[f'{mode}_ids'].append({"id": next_id, "tex": tile_name, "geo": [0, 0, 0, 0]})
            # Update the default pane
            self.panes[mode]["All"].add_option(next_id, mode)

            print(f'Imported {tile_name} from {file_path}')

    @Decorators.apply_to_current_view
    def include_level(self, index):
        """Include the currently open level in the project.json file"""
        # Level is not already in project.json
        level = self.view_list[index].level
        if level.name not in App.project_data["levels"]:
            # Level must be saved in order to proceed
            if self.view_list[index].saved and self.view_list[index].file_path is not None:
                relative_path = self.view_list[index].file_path.replace((getcwd() + '/').replace('\\', '/'), '')
                App.project_data["levels"][level.name] = {"path": relative_path, "world_pos": level.world_pos}
                level.ignore_from_project = False
                messagebox.showinfo("World Builder 2", "Level added to project.")
            else:
                messagebox.showerror("Unsaved Level", "Please save your level first before adding it to the project.")
        else:
            messagebox.showinfo("World Builder 2", "This level is already included in the project.")

    @Decorators.apply_to_current_view
    def exclude_level(self, index):
        """Exclude the currently open level from the project.json file"""
        level = self.view_list[index].level
        if level.name in App.project_data["levels"]:
            del App.project_data["levels"][level.name]
            level.ignore_from_project = True
            messagebox.showinfo("World Builder 2", "Level removed from project.")
        else:
            messagebox.showinfo("World Builder 2", "This level was not already in the project.")

    @staticmethod
    def unimplemented(event=None):
        """This function has not yet been implemented"""
        print("This feature has not yet been implemented")

    @Decorators.callback
    def tool_callback(self):
        """Set the mode of views to draw mode"""
        for i in self.view_list:
            i.set_mode(self.tool_mode.get())

    @Decorators.callback
    def grid_mode_callback(self):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.set_grid()

    @Decorators.callback
    def border_mode_callback(self):
        """Set the grid visibility of the views"""
        for i in self.view_list:
            i.set_border(self.border_mode.get())

    @Decorators.hidden_event
    def keybind_draw_mode(self):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        self.tool_mode.set(0)

    @Decorators.hidden_event
    def keybind_move_mode(self):
        """Callback for setting the editor to move mode"""
        if self.master.index("current") != 0:
            return
        self.tool_mode.set(1)

    @Decorators.hidden_event
    def keybind_grid_mode(self):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        if self.grid_mode.get() == 0:
            self.grid_mode.set(1)
        else:
            self.grid_mode.set(0)

    @Decorators.hidden_event
    def keybind_border_mode(self):
        """Callback for setting the editor to draw mode"""
        if self.master.index("current") != 0:
            return
        if self.border_mode.get() == 0:
            self.border_mode.set(1)
        else:
            self.border_mode.set(0)

    def keybind_layer_mode(self, event):
        """Generic callback for setting the layer"""
        try:
            if int(event.char) == 0:
                self.layer.set(5)
            else:
                self.layer.set(int(event.char) - 5)
        except ValueError:
            print("Caught ValueError in keybind_layer_mode")

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
            self.visible_pane = self.panes["tile"][pane]
        # Decomap mode: select pane from the deco panes
        elif layer == 1:
            self.panes["deco"][pane].pack(anchor="ne")
            self.visible_pane = self.panes["deco"][pane]
        # Collision mode: select the collision pane
        elif layer == 2:
            self.panes["collision"][pane].pack(anchor="ne")
            self.visible_pane = self.panes["collision"][pane]
        # Height mode: select the height pane
        elif layer == 3:
            self.panes["height"][pane].pack(anchor="ne")
            self.visible_pane = self.panes["height"][pane]
        # Loading zone mode: select the loading zone pane
        elif layer == 4:
            self.panes["loading"][pane].pack(anchor="ne")
            self.visible_pane = self.panes["loading"][pane]
        # Lightmap mode: select the lightmap pane
        elif layer == 5:
            self.panes["light"][pane].pack(anchor="ne")
            self.visible_pane = self.panes["light"][pane]

    def set_layer(self, layer):
        """Set the currently editable layer"""
        self.group_dropdown.grid_forget()
        self.group_dropdown.forget()
        if layer == 0:
            options = list([i for i, j in self.panes["tile"].items()])
            self.set_option_menu(options)
            self.group_dropdown.grid(row=0, column=2, sticky=tk.E)
        elif layer == 1:
            options = list([i for i, j in self.panes["deco"].items()])
            self.set_option_menu(options)
            self.group_dropdown.grid(row=0, column=2, sticky=tk.E)

        self.set_pane("All", layer)
        for i in self.view_list:
            i.set_layer()

    def add_pane(self, pane_name, pane_type, pane_entries):
        """Add a tile selection pane"""
        if pane_type not in ["tile", "deco"]:
            raise ValueError(f'\'{pane_type}\' is not a valid pane type!')

        # Only add the pane if it has not already been added to the pane list
        if pane_name not in self.panes[pane_type]:
            self.panes[pane_type][pane_name] = TileCollection(self.selection_frame,
                                                              pane_entries,
                                                              pane_type,
                                                              borderwidth=1,
                                                              relief=tk.SUNKEN)
        else:
            raise ValueError('f\'{pane_name}\' is a duplicate group name')

    def set_option_menu(self, options):
        """Set the options in the group dropdown menu"""
        self.group_dropdown["menu"].delete(0, 'end')
        for option in options:
            self.group_dropdown["menu"].add_command(label=option, command=tk._setit(self.group, option))

    def load_groups(self):
        """Loads all groups from the project file"""
        # Add the hard-coded "all" category
        self.panes["tile"] = {"All": TileCollection(self.selection_frame,
                                                    [i for i, j in TilemapEditorWindow.tile_dict.items()],
                                                    "tile",
                                                    borderwidth=1,
                                                    relief=tk.SUNKEN)}

        self.panes["deco"] = {"All": TileCollection(self.selection_frame,
                                                    [i for i, j in TilemapEditorWindow.deco_dict.items()],
                                                    "deco",
                                                    borderwidth=1,
                                                    relief=tk.SUNKEN)}

        self.panes["collision"] = {"All": TileCollection(self.selection_frame,
                                                         [0, 1],
                                                         "collision",
                                                         borderwidth=1,
                                                         relief=tk.SUNKEN)}

        self.panes["height"] = {"All": TileCollection(self.selection_frame,
                                                      [0, 1, 2, 3],
                                                      "height",
                                                      borderwidth=1,
                                                      relief=tk.SUNKEN)}

        self.panes["loading"] = {"All": TileCollection(self.selection_frame,
                                                       [0, 1, 2, 3, 4, 5],
                                                       "loading",
                                                       borderwidth=1,
                                                       relief=tk.SUNKEN)}

        self.panes["light"] = {"All": TileCollection(self.selection_frame,
                                                     [0, 1, 2, 3, 4],
                                                     "light",
                                                     borderwidth=1,
                                                     relief=tk.SUNKEN)}

        print("Loaded: ")
        self.load_custom_panes(App.project_data["groups"])

    def load_custom_panes(self, groups: dict, verbose=False):
        """Load custom panes"""
        for group_type, j in groups.items():
            for name, tiles in j.items():
                if not verbose:
                    print(f'{name}, ({group_type}) - {tiles}')
                self.add_pane(name, group_type, tiles)

    def reload_groups(self):
        """Tile panes from the App.project_data["groups"] dictionary"""
        # Unload tile panes
        for name, pane in self.panes["tile"].copy().items():
            if name != "All":
                pane.forget()
                del self.panes["tile"][name]

        # Unload deco panes
        for name, pane in self.panes["deco"].copy().items():
            if name != "All":
                pane.forget()
                del self.panes["deco"][name]

        # Load tile panes
        self.load_custom_panes(App.project_data["groups"])

        # Reload option menu
        self.set_layer(self.layer.get())

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

        height_layer_data = '''R0lGODlhIAAgAIABAAAAAP///yH5BAEKAAEALAAAAAAgACAAA
            AJRjI+pq+APo5xo2gsr3lLzDzCi\nI5ZlZqZHp5pWO15ws80Masdkrof8/fgBd8IErrg
            KIj2+peG4hPI4QgzyFY04n8ptgNgCgZhiWbJs\nPaOx3kQBADs=
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

        solidify_data = '''R0lGODlhEAAQAMIFAACJAACNAADNAAD9AAD/AP///////////yH5B
            AEKAAcALAAAAAAQABAAAAMm\nSLPcPiLKOQGkOIab6e7YB07iqHFmmaKj2rKgG8OdXBN
            Bru87kAAAOw==
            '''

        desolidify_data = '''R0lGODlhEAAQAKEDAKc+PtUyMv9DQ////yH5BAEKAAMALAAAAAA
            QABAAAAI7lC+DeuE+XohQSArf\nADbrz3kipUzXN3GY6UXDipFTOWYvHdu3lZv3m0C5f
            i/hjNiREXes4VKxAWyetwIAOw==
            '''

        elevate_data = '''R0lGODlhEAAQAKEAAADVAGPiYwDVAADVACH5BAEKAAIALAAAAAAQAB
            AAAAIglI+pu+EPFZyBGWeR\nAyCLzXXME3Ke6Rloup4i+7rpTBcAOw==
            '''

        descend_data = '''R0lGODlhEAAQAKECAKYAAMUAAADVAADVACH5BAEKAAIALAAAAAAQAB
            AAAAIhlI+pyxfR0otoUmNv\npnu9D4QNKEZBCFxCyaAuqryvSjMFADs=
            '''

        elevate_fast_data = '''R0lGODlhEAAQAKECAADVAGPiY////////yH5BAEKAAIALAAAA
            AAQABAAAAIllI+pu+EPFZyBGWeR\nAyCLzXXME3Ke6RlouoZMm7VrMgvieadHAQA7
            '''

        descend_fast_data = '''R0lGODlhEAAQAKECAKYAAMUAAP///////yH5BAEKAAIALAAAA
            AAQABAAAAImlI+pG73iTHhyVqvi\nwUnrzFFQCDYBgFImCogQ6xopxdZwYtvxLhYAOw=
            =
            '''

        height_blank_data = '''R0lGODlhEAAQAIABAP+gAP///yH5BAEKAAEALAAAAAAQABAAA
            AIeBBKGmocP45J0uRov3lVzxk3h\nCHkbGJrkuRoOAzsFADs=
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

        new_light = '''R0lGODlhEAAQAMIEAAAAAFVVVaqqquzkAADhAADhAADhAADhACH5BAEKA
            AQALAAAAAAQABAAAAM0\nOEOk7G2xSeuzCk7dqNxgd1ldNorjp35o27IsKcUxAShAxdl
            Aj1WAgCBHAhI9RRlkOZMkAAA7
            '''

        edit_light = '''R0lGODlhEAAQAMIDAAAAADw8PACzAADhAADhAADhAADhAADhACH5BAEK
            AAQALAAAAAAQABAAAAM3\nKEKk7G2xSeujANgJCRja1hCB9oViAJ6bRA4wSnVBDbaWKo
            uMPvO+hyt3uwCLvEltlJxBnhJIAgA7
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
                    "height_layer": tk.PhotoImage("img_height_layer", data=height_layer_data),
                    "loading_layer": tk.PhotoImage("img_load_layer", data=loading_layer_data),
                    "light_layer": tk.PhotoImage("img_light_layer", data=light_layer_data),
                    "delete": tk.PhotoImage("img_delete", data=delete_zone).zoom(64).subsample(16),
                    "solidify": tk.PhotoImage("img_solidify", data=solidify_data).zoom(64).subsample(16),
                    "desolidify": tk.PhotoImage("img_desolidify", data=desolidify_data).zoom(64).subsample(16),
                    "elevate": tk.PhotoImage("img_elevate", data=elevate_data).zoom(64).subsample(16),
                    "descend": tk.PhotoImage("img_descend", data=descend_data).zoom(64).subsample(16),
                    "elevate_fast": tk.PhotoImage("img_descend_fast", data=elevate_fast_data).zoom(64).subsample(16),
                    "descend_fast": tk.PhotoImage("img_descend_fast", data=descend_fast_data).zoom(64).subsample(16),
                    "height_blank": tk.PhotoImage("img_height_blank", data=height_blank_data).zoom(64).subsample(16),
                    "new_zone": tk.PhotoImage("img_new_zone", data=new_zone).zoom(64).subsample(16),
                    "configure_zone": tk.PhotoImage("img_edit_zone", data=configure_zone).zoom(64).subsample(16),
                    "copy": tk.PhotoImage("img_copy", data=copy_zone).zoom(64).subsample(16),
                    "paste": tk.PhotoImage("img_paste", data=paste_zone).zoom(64).subsample(16),
                    "extend_zone": tk.PhotoImage("img_paste_zone", data=extend_zone).zoom(64).subsample(16),
                    "new_light": tk.PhotoImage("img_new_light", data=new_light).zoom(64).subsample(16),
                    "edit_light": tk.PhotoImage("img_edit_light", data=edit_light).zoom(64).subsample(16)
                    }

        cls.collider_dict = [cls.imgs["desolidify"],
                             cls.imgs["solidify"]
                             ]

        cls.height_dict = [cls.imgs["elevate"],
                           cls.imgs["elevate_fast"],
                           cls.imgs["descend"],
                           cls.imgs["descend_fast"]
                           ]

        cls.loading_dict = [cls.imgs["delete"],
                            cls.imgs["new_zone"],
                            cls.imgs["configure_zone"],
                            cls.imgs["copy"],
                            cls.imgs["paste"],
                            cls.imgs["extend_zone"]
                            ]

        cls.light_dict = [cls.imgs["delete"],
                          cls.imgs["new_light"],
                          cls.imgs["edit_light"],
                          cls.imgs["copy"],
                          cls.imgs["paste"]
                          ]

        # Open the ids.json file to start loading the tiles/decos
        try:
            # Attempt to read data from file
            with open("assets/ids.json", mode="r") as f:
                file_data = json.load(f)
                cls.ids_data = file_data
                # Load the tiles
                for i in file_data["tile_ids"]:
                    img = Image.open("tiles/" + i["tex"])
                    img = img.crop([0, 0, 16, 16])
                    mini_img = img.resize((8, 8), Image.NORMAL)
                    img = img.resize((64, 64), Image.NORMAL)
                    cls.mini_tile_dict[int(i["id"])] = mini_img
                    cls.tile_dict[int(i["id"])] = ImageTk.PhotoImage(img)

                # Load the decos
                for i in file_data["deco_ids"]:
                    img = Image.open("tiles/" + i["tex"])
                    img = img.crop([0, 0, 16, 16])
                    mini_img = img.resize((8, 8), Image.NORMAL)
                    img = img.resize((64, 64), Image.NORMAL)
                    cls.mini_deco_dict[int(i["id"])] = mini_img
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
        self.saved = True
        self.current_tile = 0
        self.copied_zone = None
        self.copied_zone_coords = None
        self.copied_light = None

        # Declare the tilemap data
        self.level = Level()
        self.past_states = []
        self.future_states = []
        self.file_path = None

        self.backup_state()

        # Note: Past/current/future level state data follows the format:
        # past_states: [oldest -> newest], excluding current state
        # level: current state
        # future_states: [oldest -> newest], excluding current state

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
        self.canvas.config(scrollregion=(0, 0, 64 * self.level.level_width, 64 * self.level.level_height),
                           xscrollcommand=self.canvas_hbar.set,
                           yscrollcommand=self.canvas_vbar.set)
        self.canvas.xview(tk.MOVETO, 0.0)
        self.canvas.yview(tk.MOVETO, 0.0)

        self.image_view = Image.new('RGBA', (8 * 16, 8 * 9))

        # Add the view to the parent frame
        # This isn't supposed to be self.frame, but I'm worried if I change it, something will break
        # Will fix later™
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
        disp_x = (self.canvas.xview()[0] * self.level.level_width - int(self.master.master.border_mode.get()) + 1) * 64
        disp_y = (self.canvas.yview()[0] * self.level.level_height - int(self.master.master.border_mode.get()) + 1) * 64
        x = event.x + disp_x
        y = event.y + disp_y

        self.master.master.tile_coords_text.set("Col, Row: {:.0f}, {:.0f}".format(x // 64, y // 64))
        self.master.master.level_coords_text.set("X, Y: {:.0f}, {:.0f}".format(event.x, event.y))

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
        self.frame.forget()
        return True

    def draw_grid(self):
        """Draw the tilemap grid"""
        for i in range(self.level.level_width + 1):
            self.canvas.create_line(64 * i, 0, 64 * i, 64 * self.level.level_height, fill="BLACK", width=2.0)
        for i in range(self.level.level_height + 1):
            self.canvas.create_line(0, 64 * i, 64 * self.level.level_width, 64 * i, fill="BLACK", width=2.0)

    def draw_tilemap(self, update_minimap=False):
        """Draw the current level"""
        for i, j in enumerate(self.level.tilemap):
            for k, m in enumerate(j):
                if m != 0:
                    self.canvas.create_image((k * 64 + 32, i * 64 + 32), image=TilemapEditorWindow.tile_dict[m])
                    if update_minimap:
                        if TilemapEditorWindow.mini_tile_dict[m].mode == 'RGBA':
                            self.image_view.paste(TilemapEditorWindow.mini_tile_dict[m], box=(k * 8, i * 8),
                                                  mask=TilemapEditorWindow.mini_tile_dict[m])
                        else:
                            self.image_view.paste(TilemapEditorWindow.mini_tile_dict[m], box=(k * 8, i * 8))

    def draw_decomap(self, update_minimap=False):
        """Draw the current level's decomap"""
        self.level.decomap.sort()
        for deco_id, x, y in self.level.decomap:
            if deco_id != 0:
                self.canvas.create_image((x * 64 + 32, y * 64 + 32), image=TilemapEditorWindow.deco_dict[deco_id])
                if update_minimap:
                    if TilemapEditorWindow.mini_deco_dict[deco_id].mode == 'RGBA':
                        self.image_view.paste(TilemapEditorWindow.mini_deco_dict[deco_id], box=(x * 8, y * 8),
                                              mask=TilemapEditorWindow.mini_deco_dict[deco_id])
                    else:
                        self.image_view.paste(TilemapEditorWindow.mini_deco_dict[deco_id], box=(x * 8, y * 8))

    def draw_collision(self):
        """Draw the collision map"""
        self.apply_geometry()
        for i in range(self.level.level_width * 2 + 1):
            self.canvas.create_line(32 * i, 0, 32 * i, 64 * self.level.level_height, fill="BLACK", width=1.0)
        for i in range(self.level.level_height * 2 + 1):
            self.canvas.create_line(0, 32 * i, 64 * self.level.level_width, 32 * i, fill="BLACK", width=1.0)
        for i, j in enumerate(self.level.collider):
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

            # End of row was solid, and never got a chance to fill in during loop.  Do so now.
            if solid_count > 0:
                self.canvas.create_rectangle(((last_k - solid_count) * 32 + 32, i * 32, last_k * 32 + 32, i * 32 + 32),
                                             fill="gray",
                                             width=1,
                                             stipple="gray50")

    def draw_height_map(self):
        """Draw the current level's height map"""
        for deco_id, x, y in self.level.decomap:
            if deco_id != 0:
                # self.canvas.create_image((x * 64 + 32, y * 64 + 32), image=TilemapEditorWindow.imgs["height_blank"])
                self.canvas.create_rectangle((x * 64, y * 64, x * 64 + 64, y * 64 + 64),
                                             fill="orange",
                                             outline="orange",
                                             width=2,
                                             stipple="gray50")
                self.canvas.create_text((x * 64 + 32, y * 64 + 32), fill="Dark Red", font="Courier 30 bold",
                                        text=str(TilemapEditorWindow.ids_data["deco_ids"][deco_id]["height"]))

    def draw_loading_zones(self):
        """Draw the loading zones"""
        for i, j in self.level.loading_zones.items():
            if j.target_level == "":
                self.canvas.create_image((i[0] * 64 + 32, i[1] * 64 + 32),
                                         image=TilemapView.imgs["inactive_zone"])
            else:
                self.canvas.create_image((i[0] * 64 + 32, i[1] * 64 + 32),
                                         image=TilemapView.imgs["active_zone"])

    def draw_lights(self):
        """Draw the lights"""
        for i, j in self.level.lightmap.items():
            if j.active:
                self.canvas.create_image((i[0] * 64 + 32, i[1] * 64 + 32),
                                         image=TilemapView.imgs["active_light"])
            else:
                self.canvas.create_image((i[0] * 64 + 32, i[1] * 64 + 32),
                                         image=TilemapView.imgs["inactive_light"])

    def draw_border(self):
        """Draw the border"""
        for i in range(self.level.level_width):
            self.canvas.create_image((i * 64 + 32, 32), image=TilemapView.imgs["border"])
            self.canvas.create_image((i * 64 + 32, self.level.level_height * 64 - 32), image=TilemapView.imgs["border"])
        for i in range(1, self.level.level_height - 1):
            self.canvas.create_image((32, i * 64 + 32), image=TilemapView.imgs["border"])
            self.canvas.create_image((self.level.level_width * 64 - 32, i * 64 + 32), image=TilemapView.imgs["border"])

    def redraw_view(self, update_minimap=False):
        """Redraw the entire view"""
        # Redraw basic map
        self.canvas.delete("all")

        if update_minimap:
            del self.image_view
            self.image_view = Image.new('RGBA', (8 * self.level.level_width, 8 * self.level.level_height))

        self.draw_tilemap(update_minimap)
        self.draw_decomap(update_minimap)

        # Draw layer-specific stuff (self.master.master.layer.get())
        # Draw collision layer if enabled
        if self.master.master.layer.get() == 2:
            self.draw_collision()
        # Draw height layer if enabled
        elif self.master.master.layer.get() == 3:
            self.draw_height_map()
        # Draw loading zones layer if enabled
        elif self.master.master.layer.get() == 4:
            self.draw_loading_zones()
        # Draw lightmap layer if enabled
        elif self.master.master.layer.get() == 5:
            self.draw_lights()

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
            self.frame.master.tab(self.frame, text=self.level.name)
        else:
            self.frame.master.tab(self.frame, text="*" + self.level.name)

    def set_mode(self, value):
        """Does the actual work of setting the window's mode"""
        if value == 0:
            # Drawing controls
            for i in ["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"]:
                self.canvas.unbind(i)
            # Tilemap mode
            if self.master.master.layer.get() == 0:
                self.canvas.bind("<B1-Motion>", self.draw_tile)
                self.canvas.bind("<ButtonRelease-1>", lambda event: self._generic_finish_draw(event, self.draw_tile))
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_tile))
            # Decomap mode
            elif self.master.master.layer.get() == 1:
                self.canvas.bind("<B1-Motion>", self.draw_deco)
                self.canvas.bind("<ButtonRelease-1>", lambda event: self._generic_finish_draw(event, self.draw_deco))
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_deco))
            # Collision map mode
            elif self.master.master.layer.get() == 2:
                self.canvas.bind("<B1-Motion>", self.draw_collider)
                self.canvas.bind("<ButtonRelease-1>",
                                 lambda event: self._generic_finish_draw(event, self.draw_collider))
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_collider))
            # Height map mode
            elif self.master.master.layer.get() == 3:
                self.canvas.bind("<ButtonRelease-1>", lambda event: self.redraw_view())
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_height))
            # Loading zone mode
            elif self.master.master.layer.get() == 4:
                self.canvas.bind("<B1-Motion>", self.draw_zone)
                self.canvas.bind("<ButtonRelease-1>", lambda event: self._generic_finish_draw(event, self.draw_zone))
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_zone))
            # Lightmap mode
            elif self.master.master.layer.get() == 5:
                self.canvas.bind("<B1-Motion>", self.draw_light)
                self.canvas.bind("<ButtonRelease-1>", lambda event: self._generic_finish_draw(event, self.draw_light))
                self.canvas.bind("<ButtonPress-1>", lambda event: self._generic_start_draw(event, self.draw_light))
            self.canvas.config(cursor="pencil")
        elif value == 1:
            # Movement controls
            for i in ["<ButtonRelease-1>", "<ButtonPress-1>", "<B1-Motion>"]:
                self.canvas.unbind(i)
            self.canvas.bind("<ButtonPress-1>", self.set_start)
            self.canvas.bind("<B1-Motion>", self.move)
            self.canvas.config(cursor="fleur")

    def _generic_start_draw(self, event, draw_function):
        self.backup_state()
        draw_function(event)

    def _generic_finish_draw(self, event, draw_function):
        self.canvas.delete("all")
        self.backup_state()
        draw_function(event)
        self.redraw_view()

    def set_grid(self):
        """Update the grid overlay"""
        self.redraw_view()

    def set_border(self, value):
        """Toggle the border overlay"""
        if value:
            # Show border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(0, 0, 64 * self.level.level_width,
                                             64 * self.level.level_height))
        else:
            # Disable border
            self.canvas.delete("all")
            self.canvas.config(scrollregion=(64, 64, 64 * (self.level.level_width - 1),
                                             64 * (self.level.level_height - 1)))
        self.redraw_view()

    def set_layer(self):
        """Update the layer visibility status"""
        self.set_mode(self.master.master.tool_mode.get())
        self.redraw_view()

    def event_to_tile(self, event):
        """Converts mouse events to tiled coordinates"""
        if self.master.master.border_mode.get():
            tile_x = int(self.canvas.xview()[0] * self.level.level_width + event.x / 64)
            tile_y = int(self.canvas.yview()[0] * self.level.level_height + event.y / 64)
        else:
            tile_x = int(self.canvas.xview()[0] * (self.level.level_width - 2) + event.x / 64)
            tile_y = int(self.canvas.yview()[0] * (self.level.level_height - 2) + event.y / 64)
            tile_x += 1
            tile_y += 1

        return tile_x, tile_y

    @staticmethod
    def check_bounds(event):
        """Check if a mouse event was within bounds.  Does not apply for the collider layer due to double resolution"""
        if event.y / 64 < 0.1:
            return False
        if event.y / 64 > 8.9:
            return False
        if event.x / 64 < 0.1:
            return False
        if event.x / 64 > 15.9:
            return False
        return True

    def draw_tile(self, event):
        """Event callback for drawing a tile on the grid"""
        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        if not self.check_bounds(event):
            return

        # No longer saved
        self.saved = False
        self.update_title()

        # Determine the position at which to to draw the tile
        tile_x, tile_y = self.event_to_tile(event)

        # Determine the id of the selected tile
        current_tile = self.master.master.visible_pane.selected_id.get()

        # Draw the tile
        self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                 image=TilemapEditorWindow.tile_dict[current_tile])
        # Add the tile to the tilemap matrix
        try:
            self.level.tilemap[tile_y][tile_x] = int(current_tile)
        except IndexError:
            pass

    def draw_deco(self, event):
        """Draw either a tile or a deco on the grid, depending on the arguments"""
        if not self.check_bounds(event):
            return

        # No longer saved
        self.saved = False
        self.update_title()

        tile_x, tile_y = self.event_to_tile(event)

        # Determine the id of the selected tile
        current_tile = self.master.master.visible_pane.selected_id.get()

        # Draw the tile
        self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                 image=TilemapEditorWindow.deco_dict[current_tile])
        # Add the tile to the decomap
        if int(current_tile) == 0:
            self.level.decomap.remove(tile_x, tile_y)
        else:
            self.level.decomap.add(tile_x, tile_y, int(current_tile))

    def draw_collider(self, event):
        """Event callback for drawing a collider on the grid"""

        if self.master.master.border_mode.get():
            tile_x = int(self.canvas.xview()[0] * (len(self.level.collider[0])) + event.x / 32)
            tile_y = int(self.canvas.yview()[0] * (len(self.level.collider)) + event.y / 32)
        else:
            tile_x = int(self.canvas.xview()[0] * (len(self.level.collider[0]) - 4) + event.x / 32)
            tile_y = int(self.canvas.yview()[0] * (len(self.level.collider) - 4) + event.y / 32)
            tile_x += 2
            tile_y += 2

        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        # Top side catch
        if event.y / 64 < 0.05:
            return
        # Bottom side catch
        if event.y / 64 > 9.55:
            return
        # Left size catch
        if event.x / 64 < 0.05:
            return
        # Right side catch
        if event.x / 64 > 16.55:
            return

        # Determine the id of the selected tile
        solid_state = self.master.master.visible_pane.selected_id.get()

        # Draw the collider
        if solid_state:
            self.canvas.create_rectangle((tile_x * 32, tile_y * 32, tile_x * 32 + 32, tile_y * 32 + 32),
                                         fill="green",
                                         width=1,
                                         stipple="gray50")
        else:
            self.canvas.create_rectangle((tile_x * 32, tile_y * 32, tile_x * 32 + 32, tile_y * 32 + 32),
                                         fill="red",
                                         width=1,
                                         stipple="gray50")

        # Add the collider to the collider matrix
        try:
            # [ 0, 2 ] -> [0, 1, 2, 3]
            # [ 1, 3 ]
            # Determine which geometry sub-tile to modify
            sub_x = round(tile_x / 2 - tile_x // 2 + 0.1)
            sub_y = round(tile_y / 2 - tile_y // 2 + 0.1)
            # Grab tile ID and layer
            if self.level.decomap[tile_x // 2, tile_y // 2]:
                target_id = self.level.decomap[tile_x // 2, tile_y // 2][-1][0]
                target_set = "deco_ids"
            else:
                target_id = self.level.tilemap[tile_y // 2][tile_x // 2]
                target_set = "tile_ids"
            # Modify tile's geometry
            for i, j in enumerate(TilemapEditorWindow.ids_data[target_set]):
                if j["id"] == target_id:
                    if (sub_x, sub_y) == (0, 0):
                        TilemapEditorWindow.ids_data[target_set][i]["geo"][0] = solid_state
                    elif (sub_x, sub_y) == (0, 1):
                        TilemapEditorWindow.ids_data[target_set][i]["geo"][1] = solid_state
                    elif (sub_x, sub_y) == (1, 0):
                        TilemapEditorWindow.ids_data[target_set][i]["geo"][2] = solid_state
                    elif (sub_x, sub_y) == (1, 1):
                        TilemapEditorWindow.ids_data[target_set][i]["geo"][3] = solid_state
                    break
            self.level.collider[tile_y][tile_x] = solid_state
        except IndexError:
            pass

    def draw_height(self, event):
        """Event callback for drawing heights"""
        if not self.check_bounds(event):
            return

        # No longer saved
        self.saved = False
        self.update_title()

        tile_x, tile_y = self.event_to_tile(event)

        # Determine the id of the selected tile
        height_option = self.master.master.visible_pane.selected_id.get()

        # Draw the tile
        self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                 image=TilemapEditorWindow.height_dict[height_option])

        # Modify the height value in the ids list
        deco_id = self.level.decomap[tile_x, tile_y]
        # If there was actually a deco at the selected location
        if deco_id is not None:
            for i in deco_id:
                if height_option == 0:
                    TilemapEditorWindow.ids_data["deco_ids"][i[0]]["height"] += 1
                elif height_option == 1:
                    TilemapEditorWindow.ids_data["deco_ids"][i[0]]["height"] += 5
                elif height_option == 2:
                    TilemapEditorWindow.ids_data["deco_ids"][i[0]]["height"] -= 1
                elif height_option == 3:
                    TilemapEditorWindow.ids_data["deco_ids"][i[0]]["height"] -= 5

    def draw_zone(self, event):
        """Event callback for editing loading zones"""
        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        if not self.check_bounds(event):
            return

        # No longer saved
        self.saved = False
        self.update_title()

        # Determine the position at which to to draw the tile
        tile_x, tile_y = self.event_to_tile(event)

        # Determine the id of the selected tile
        mode = self.master.master.visible_pane.selected_id.get()

        if mode == 0:
            # Delete the zone
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["delete"])
            if (tile_x, tile_y) in self.level.loading_zones:
                self.level.loading_zones.pop((tile_x, tile_y))

        elif mode == 1:
            # Add a new zone
            if (tile_x, tile_y) not in self.level.loading_zones:
                self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                         image=TilemapView.imgs["inactive_zone"])
                self.level.loading_zones[tile_x, tile_y] = LoadingZone("", [0, 0])

        elif mode == 2:
            # Edit an existing zone
            if (tile_x, tile_y) in self.level.loading_zones:
                self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                         image=TilemapEditorWindow.imgs["configure_zone"])
                data = self.level.loading_zones[tile_x, tile_y]
                new_data = DataSetDialog(self, [{"Target X": data.target_pos[0], "Target Y": data.target_pos[1]},
                                                {"Target Level": data.target_level}]).result
                if new_data is not None:
                    self.level.loading_zones[tile_x, tile_y].target_pos = [int(new_data[0]["Target X"]),
                                                                           int(new_data[0]["Target Y"])]
                    self.level.loading_zones[tile_x, tile_y].target_level = new_data[1]["Target Level"]
            self.redraw_view()

        elif mode == 3:
            # Copy the existing zone
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["copy"])
            if (tile_x, tile_y) in self.level.loading_zones:
                self.copied_zone = self.level.loading_zones[tile_x, tile_y].copy()
                self.copied_zone_coords = [tile_x, tile_y]

        elif mode == 4:
            # Paste the copied zone
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["paste"])
            if self.copied_zone is not None:
                self.level.loading_zones[tile_x, tile_y] = self.copied_zone.copy()

        elif mode == 5:
            # Extend the copied zone
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["extend_zone"])
            if self.copied_zone is not None:
                new_zone = self.copied_zone.copy()
                new_zone.target_pos[0] += tile_x - self.copied_zone_coords[0]
                new_zone.target_pos[1] += tile_y - self.copied_zone_coords[1]
                self.level.loading_zones[tile_x, tile_y] = new_zone

    def draw_light(self, event):
        """Event callback for drawing a light"""
        # Check to make sure tile is actually on the screen.  If not, cancel drawing.
        if not self.check_bounds(event):
            return

        # No longer saved
        self.saved = False
        self.update_title()

        # Determine the position at which to to draw the tile
        tile_x, tile_y = self.event_to_tile(event)

        # Determine the id of the selected tile
        mode = self.master.master.visible_pane.selected_id.get()

        if mode == 0:
            # Delete light
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["delete"])
            if (tile_x, tile_y) in self.level.lightmap:
                self.level.lightmap.pop((tile_x, tile_y))

        elif mode == 1:
            # Add light
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["new_light"])
            if (tile_x, tile_y) not in self.level.lightmap:
                red = ColorFade(255, 0, 64)
                green = ColorFade(255, 0, 64)
                blue = ColorFade(255, 0, 64)
                self.level.lightmap[(tile_x, tile_y)] = Light(1, red, green, blue)

        elif mode == 2:
            # Edit light
            if (tile_x, tile_y) in self.level.lightmap:
                self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                         image=TilemapEditorWindow.imgs["edit_light"])
                new_light = LightEditorDialog(self, self.level.lightmap[tile_x, tile_y]).result
                if new_light is not None:
                    new_light.active = True
                    self.level.lightmap[tile_x, tile_y] = new_light

            self.redraw_view()

        elif mode == 3:
            # Copy light
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["copy"])
            if (tile_x, tile_y) in self.level.lightmap:
                self.copied_light = self.level.lightmap[tile_x, tile_y].copy()

        elif mode == 4:
            # Paste light
            self.canvas.create_image(tile_x * 64 + 32, tile_y * 64 + 32,
                                     image=TilemapEditorWindow.imgs["paste"])
            if self.copied_light is not None:
                self.level.lightmap[tile_x, tile_y] = self.copied_light.copy()

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

    def apply_geometry(self):
        """Applies the tile/deco geometry from ids_data"""
        # Reset map
        for i, j in enumerate(self.level.collider):
            for k, m in enumerate(j):
                self.level.collider[i][k] = 0

        # Apply tile geometry
        for y, i in enumerate(self.level.tilemap):
            for x, j in enumerate(i):
                for k in TilemapEditorWindow.ids_data["tile_ids"]:
                    if k["id"] == j:
                        self.level.collider[y * 2][x * 2] = k["geo"][0]
                        self.level.collider[y * 2 + 1][x * 2] = k["geo"][1]
                        self.level.collider[y * 2][x * 2 + 1] = k["geo"][2]
                        self.level.collider[y * 2 + 1][x * 2 + 1] = k["geo"][3]

        # Apply deco geometry
        for deco_id, x, y in self.level.decomap:
            for i in TilemapEditorWindow.ids_data["deco_ids"]:
                if i["id"] == deco_id:
                    self.level.collider[y * 2][x * 2] ^= i["geo"][0]
                    self.level.collider[y * 2 + 1][x * 2] ^= i["geo"][1]
                    self.level.collider[y * 2][x * 2 + 1] ^= i["geo"][2]
                    self.level.collider[y * 2 + 1][x * 2 + 1] ^= i["geo"][3]

    def load_from_file(self, file):
        """Loads level data from a .json file"""
        # TODO: Add function to check if data is formatted correctly
        self.backup_state()
        with open(file, mode="r") as f:
            level_data = json.load(f)
            self.level.load_from_json(level_data)
            self.saved = True
            self.file_path = file
        self.set_border(self.master.master.border_mode.get())
        self.update_title()
        self.apply_geometry()
        self.redraw_view()

    def quick_save(self):
        """Saves the level data to the file defined by self.file_path"""
        self.save_to_file(self.file_path)

    def save_to_file(self, file):
        """Saves the level data to a .json file"""
        # TODO: Test if saved files are actually loadable in engine.
        # Save the ids_data to ids.json
        with open("assets/ids.json", mode="w") as f:
            ids_data = json.dumps(TilemapEditorWindow.ids_data, indent=2)
            ids_data = re.sub(r'\[\s+(\d),\s+(\d),\s+(\d),\s+(\d)\s+\]', r'[\1, \2, \3, \4]', ids_data)
            f.write(ids_data)
        # TODO: Save excluded levels to project.json?
        # If this file is NOT part of the project and hasn't been excluded, ask whether it should be.
        print(self.level.ignore_from_project)
        if not self.level.ignore_from_project:
            if self.level.name not in App.project_data["levels"]:
                result = messagebox.askyesnocancel(title="Unregistered Level", message="This level was not found in "
                                                                                       "the project.json file.  Would "
                                                                                       "you like to save it to the "
                                                                                       "project?  (Clicking 'No' will "
                                                                                       "exclude for as long as it "
                                                                                       "remains in the editor)")
                if result is None:
                    # User canceled the saving process
                    return
                elif result:
                    # User added level to project.json
                    App.project_data["levels"][self.level.name] = {"path": "", "world_pos": self.level.world_pos}
                else:
                    # User excluded level from project.json
                    self.level.ignore_from_project = True

        # Save the project data to project.json
        App.save_project_data()

        # No file path has been set
        if file is None:
            file = filedialog.asksaveasfilename(filetypes=[('JSON File', '*.json')],
                                                defaultextension=[('JSON File', '*.json')])
            print("File: ", file)
            if file == "":
                # User canceled saving, exit function
                return

            # Obtain and save file path
            file = path.split(file)[1]
            self.level.name = path.splitext(file)[0]
            file = path.join("maps", file)
            self.file_path = file

        if self.level.name in App.project_data["levels"]:
            relative_path = file.replace((getcwd() + '/').replace('\\', '/'), '')
            App.project_data["levels"][self.level.name]["path"] = relative_path

        # Write json tag to file
        with open(file, mode="w") as f:
            f.write(self.level.jsonify())
        self.saved = True
        self.update_title()

        # Save a screenshot of the entire file
        self.redraw_view(True)
        self.image_view.save(f'mini/{self.level.name}.png')

        # Also save the screenshot to the WorldEditorWindow
        if not self.level.ignore_from_project:
            del WorldEditorWindow.mini_maps[self.level.name]
            WorldEditorWindow.mini_maps[self.level.name] = ImageTk.PhotoImage(self.image_view)

    def backup_state(self):
        """Save a backup of the current level state"""
        # Only update if something changed.
        if len(self.past_states) == 0 or self.level != self.past_states[-1]:
            self.past_states.append(self.level.copy())
            self.future_states = []

    def undo(self):
        """Return to the previous level state"""
        if len(self.past_states) > 0:
            # If the current state is identical to the previous, go back two states
            if self.level == self.past_states[-1]:
                self.future_states.insert(0, self.level.copy())
                self.level = self.past_states.pop(-1).copy()
                if len(self.past_states) <= 0:
                    return

            # Save current state to future, and load an older one
            self.future_states.insert(0, self.level.copy())
            self.level = self.past_states.pop(-1).copy()

            # Reload map and update saved status
            self.redraw_view()
            self.saved = False
            self.update_title()

    def redo(self):
        """Return to a future level state"""
        if len(self.future_states) > 0:
            # Save currents state to past, and load a future one
            self.past_states.append(self.level.copy())
            self.level = self.future_states.pop(0).copy()

            # Reload map and update saved status
            self.redraw_view()
            self.saved = False
            self.update_title()

    @classmethod
    def _initialize(cls):
        """Initialize the embedded images"""
        border_tile_data = tk.PhotoImage("img_border_tile", data='''R0lGODlhEAAQ
            AIABAP/0ANXLACH5BAEKAAEALAAAAAAQABAAAAImhINokMq9WjiQJuvexbHqiYFf\nt4
            0hKUooqJ5fWrUvutKuOXN3UwAAOw==
            ''').zoom(64).subsample(16)

        inactive_zone = tk.PhotoImage("img_inactive_zone", data='''R0lGODlhEAAQAKE
            CAAAAAMMAAACPAACPACH5BAEKAAIALAAAAAAQABAAAAI2TCSGmocP44qgWshE\nNabiB
            wRWCEgIeYqPc5YaurAg6U6UWJtpnpgXJtOtfMIbLwiScGLMBqIAADs=
            ''').zoom(64).subsample(16)

        active_zone = tk.PhotoImage("img_active_zone", data='''R0lGODlhEAAQAKEBA
            AAAAACPAACkIQCPACH5BAEKAAMALAAAAAAQABAAAAI0lDaGmocP45J0uQjo\nhSBXHHg
            T0pVAED7Mibao6ADGPIuP2RlwJdsMZhthPkRVETKzKBuIAgA7
            ''').zoom(64).subsample(16)

        active_light = tk.PhotoImage("img_active_light", data='''R0lGODlhEAAQAOM
            EAAAAAFVVVQC+AP+RAADhAKqqqgD/APG/AOzkAADhAADhAADhAADhAADhAADh\nAADhA
            CH5BAEKAA8ALAAAAAAQABAAAARIUIj3JLV10ke2353GUQZhUl3mGZ54bez4fqg8V1yXt
            jlW\nby4c6DE4CGkpwQGhSf4eAAlg6KMArtNPEBAoZGmfKy0IBmLOGkwEADs=
            ''').zoom(64).subsample(16)

        inactive_light = tk.PhotoImage("img_inactive_light", data='''R0lGODlhEAA
            QAMIEAAAAAMMAAFVVVaqqqgDhAADhAADhAADhACH5BAEKAAQALAAAAAAQABAAAAM1\nG
            EGk7G2xSeuzCk7dqNxgd1ndJ57oGHlsewlCisGmDChAxRFAn+sVgGDwI1F6GCMp85BAI
            AkAOw==
            ''').zoom(64).subsample(16)

        cls.imgs = {"border": border_tile_data,
                    "active_zone": active_zone,
                    "inactive_zone": inactive_zone,
                    "active_light": active_light,
                    "inactive_light": inactive_light}


class Level:
    """Container structure for level data"""

    def __init__(self):
        self.name = "Untitled"
        self.world_pos = [0, 0]
        self.level_width = 16 + 2
        self.level_height = 9 + 2
        self.tilemap = [[0] * self.level_width for i in range(self.level_height)]
        self.decomap = Decomap()
        self.collider = [[0] * (self.level_width * 2) for i in range(self.level_height * 2)]
        self.default_start = [0, 0]
        self.lightmap = LightmapDict()
        self.loading_zones = LoadingZoneDict()

        # Special Status data
        self.ignore_from_project = False

    def __eq__(self, other):
        if type(other) != Level:
            return False
        else:
            return str(self.jsonify()) == str(other.jsonify())

    def __ne__(self, other):
        if type(other) != Level:
            return True
        else:
            return str(self.jsonify()) != str(other.jsonify())

    def load_from_json(self, data):
        """Load level data from a JSON representation"""
        self.tilemap = data["tilemap"]
        self.level_width = len(self.tilemap[0])
        self.level_height = len(self.tilemap)
        self.decomap = Decomap()
        # Note: This is still here in case I ever need to upgrade an older map
        #        for i, j in enumerate(data["decomap"]):
        #            for k, m in enumerate(j):
        #                if m != 0:
        #                    self.decomap.add(k, i, m)
        for i, j, k in data["decomap"]:
            self.decomap.add(j, k, i)

        self.collider = [[0] * (self.level_width * 2) for i in range(self.level_height * 2)]
        self.loading_zones = LoadingZoneDict()
        for i in data["loading_zones"]:
            self.loading_zones[i["zone"][0], i["zone"][1]] = LoadingZone(i["target_level"], i["target_pos"])
        for i in data["lightmap"]:
            red = ColorFade(i["red"]["amplitude"], i["red"]["inner_diameter"], i["red"]["outer_diameter"])
            green = ColorFade(i["green"]["amplitude"], i["green"]["inner_diameter"], i["green"]["outer_diameter"])
            blue = ColorFade(i["blue"]["amplitude"], i["blue"]["inner_diameter"], i["blue"]["outer_diameter"])
            self.lightmap[i["pos"][0], i["pos"][1]] = Light(i["diameter"], red, green, blue, i["blacklight"], True)
        self.default_start = data["spawn"]
        self.name = data["name"]
        if self.name in App.project_data["levels"]:
            self.world_pos = App.project_data["levels"][self.name]["world_pos"]
        else:
            try:
                self.world_pos = data["world_pos"]
            except KeyError:
                self.world_pos = [0, 0]

    def copy(self):
        """Return a copy of the level data"""
        result = Level()
        result.name = self.name
        result.level_width = self.level_width
        result.level_height = self.level_height
        result.tilemap = []
        for i in self.tilemap:
            result.tilemap.append(i.copy())
        result.decomap = self.decomap.copy()
        result.default_start = self.default_start.copy()
        result.lightmap = self.lightmap.copy()
        result.loading_zones = self.loading_zones.copy()
        return result

    def change_size(self, left=0, right=0, up=0, down=0):
        """Changes the size of the level from the edges"""
        # Check if the size changes were valid
        if self.level_width + left + right < 18:
            raise ValueError("Size changes leave behind invalid width")

        if self.level_height + up + down < 11:
            raise ValueError("Size changes leave behind invalid width")

        if left != 0:
            if left > 0:
                for i, j in enumerate(self.tilemap):
                    for k in range(left):
                        self.tilemap[i].insert(0, 0)

                for i, j in enumerate(self.collider):
                    for k in range(left):
                        self.collider[i].insert(0, 0)
                        self.collider[i].insert(0, 0)
            else:
                for i, j in enumerate(self.tilemap):
                    for k in range(abs(left)):
                        j.pop(0)

                for i, j in enumerate(self.collider):
                    for k in range(abs(left)):
                        self.collider[i].pop(0)
                        self.collider[i].pop(0)

            self.level_width += left

        if right != 0:
            if right > 0:
                for i, j in enumerate(self.tilemap):
                    for k in range(right):
                        self.tilemap[i].insert(-1, 0)
                for i, j in enumerate(self.collider):
                    for k in range(right):
                        self.collider[i].insert(-1, 0)
                        self.collider[i].insert(-1, 0)
            else:
                for i in self.tilemap:
                    for k in range(abs(right)):
                        i.pop(-1)
                for i in self.collider:
                    i.pop(-1)
                    i.pop(-1)

            self.level_width += right

        if up != 0:
            if up > 0:
                for i in range(up):
                    self.tilemap.insert(0, [0] * self.level_width)
                    self.collider.insert(0, [0] * self.level_width * 2)
                    self.collider.insert(0, [0] * self.level_width * 2)
            else:
                for i in range(abs(up)):
                    self.tilemap.pop(0)
                    self.collider.pop(0)
                    self.collider.pop(0)
            self.level_height += up

        if down != 0:
            if down > 0:
                for i in range(down):
                    self.tilemap.append([0] * self.level_width)
                    self.collider.append([0] * self.level_width * 2)
                    self.collider.append([0] * self.level_width * 2)
            else:
                for i in range(abs(down)):
                    self.tilemap.pop(-1)
                    self.collider.pop(-1)
                    self.collider.pop(-1)
            self.level_height += down

    def jsonify(self):
        """Convert the level to a JSON representation"""
        # Generate json string
        result = json.dumps({"tilemap": self.tilemap,
                             "decomap": self.decomap.jsonify(),
                             # "colliders": self.collider,
                             "loading_zones": self.loading_zones.jsonify(),
                             "lightmap": self.lightmap.jsonify(),
                             "spawn": self.default_start,
                             "world_pos": self.world_pos,
                             "name": self.name}, indent=2)
        # Format json string
        result = re.sub(r'\s+([0-9.\-]+),', r'\1, ', result)
        result = re.sub(r'\s+([0-9.\-]+)\s+\]', r' \1]', result)
        result = re.sub(r':([0-9.\-]+)', r': \1', result)
        return result


class Decomap:
    """Container structure for decomap data"""

    # Data structure: [[id, x, y],...]
    # TODO: Make this structure more consistent, perhaps by making elements their own data type
    def __init__(self):
        self.values = []

    def __repr__(self):
        return self.values.__repr__()

    def __getitem__(self, key):
        """Get a list of all entries with the given coordinates"""
        if len(key) == 2 and type(key[0]) == int and type(key[1]) == int:
            result = [i for i in self.values if i[1] == key[0] and i[2] == key[1]]
            if len(result) == 0:
                return None
            else:
                return result
        else:
            raise TypeError("'{}' is not a valid key!".format(key))

    def __contains__(self, key):
        """Check if decomap contains something at the coordinates x-y (deco-id is optional)"""
        if len(key) == 2 and type(key[0]) == int and type(key[1]) == int:
            for deco_id, x, y in self.values:
                if x == key[0] and y == key[1]:
                    return True
        elif len(key) == 3 and all([type(i) == int for i in key]):
            for deco_id, x, y in self.values:
                if x == key[0] and y == key[1] and deco_id == key[2]:
                    return True
        else:
            raise TypeError("'{}' is not a valid key!".format(key))
        return False

    def __iter__(self):
        """Returns an iterable version of the decomap"""
        return self.values.__iter__()

    def copy(self):
        """Returns a copy of the decomap"""
        result = Decomap()
        result.values = [i.copy() for i in self.values]
        return result

    def add(self, x, y, deco_id):
        """Add an item to the decomap"""
        already_exists = False
        for i, j, k in self.values:
            if j == x and k == y and i == deco_id:
                already_exists = True

        if not already_exists:
            self.values.append([deco_id, x, y])

    def remove(self, x, y, deco_id=None):
        """Remove all items at the coordinates x-y from the decomap"""
        if deco_id:
            self.values = [[i, j, k] for i, j, k in self.values if not (j == x and k == y and i == deco_id)]
        else:
            self.values = [[i, j, k] for i, j, k in self.values if not (j == x and k == y)]

    def set(self, x, y, deco_id):
        """Remove all entries that have the given coordinates and append a new value"""
        self.remove(x, y)
        self.add(x, y, deco_id)

    def sort(self):
        """Sort the decomap elements in order of height+row"""
        # TODO: Make accessing tiles in ids_data dependent on actual id tag
        self.values = sorted(self.values, key=lambda x: TilemapEditorWindow.ids_data["deco_ids"][x[0]]["height"] + x[2])

    def jsonify(self):
        """Convert the decomap into json format"""
        # Ensure decomap is properly sorted
        self.sort()
        # Return a copy
        return self.copy().values


@dataclass
class LoadingZone:
    """Data structure for loading zones"""
    target_level: str
    target_pos: List[int] = field(default_factory=list)

    def copy(self):
        """Return a copy of the loading zone"""
        return LoadingZone(self.target_level, self.target_pos.copy())


@dataclass
class ColorFade:
    """Data structure for color fading data present in lights"""
    amplitude: float = 0.0
    inner_diameter: float = 0.0
    outer_diameter: float = 0.0

    def copy(self):
        """Return a copy of the ColorFade"""
        return ColorFade(self.amplitude, self.inner_diameter, self.outer_diameter)

    def jsonify(self):
        """Return a dictionary representation ready for use in a JSON tag"""
        return self.copy().__dict__


@dataclass
class Light:
    """Data structure for lights"""
    diameter: float
    red: ColorFade
    green: ColorFade
    blue: ColorFade
    blacklight: bool = False
    active: bool = False

    def copy(self):
        """Return a copy of the light"""
        return Light(self.diameter,
                     self.red.copy(),
                     self.green.copy(),
                     self.blue.copy(),
                     self.blacklight,
                     self.active)


class CoordinateDict:
    """Data structure for dictionaries where the key MUST be a pair of coordinates"""

    def __init__(self):
        super().__init__()
        self.data = {}

    def __repr__(self):
        return self.data.__repr__()

    def __getitem__(self, key):
        """Obtain the loading zone given by 'key'"""
        if self.check_key(key):
            return self.data[key]
        else:
            raise TypeError("'{}' is not a valid key!".format(key))

    def __setitem__(self, key, value):
        """Modify/create the loading zone given by 'key'"""
        if self.check_key(key):
            if self.check_type(value):
                self.data[key] = value
            else:
                raise TypeError("'{}' is not a valid value!".format(value))
        else:
            raise TypeError("'{}' is not a valid key!".format(key))

    def __contains__(self, key):
        """Check if the dictionary contains a loading zones with 'key'"""
        return key in self.data

    @staticmethod
    def check_key(key):
        """Check the type of a key to make sure it is compatible.  Override in subclass"""
        return True

    @staticmethod
    def check_type(value):
        """Checks the type of a value to make sure it is compatible.  Override in subclass"""
        return True

    def pop(self, key):
        """Remove the loading zone given by 'key'"""
        return self.data.pop(key)

    def items(self):
        return self.data.items()

    def jsonify(self):
        """Convert into a list representation reading for use in a JSON tag.  Override in subclass"""
        pass


class LoadingZoneDict(CoordinateDict):
    """Data structure for loading zone lists"""

    # Structure:
    # [{"zone":[x, y], "target_level": "Level Name", "target_pos": [x, y]},{}...]

    @staticmethod
    def check_key(key):
        """Check to ake sure the key is a pair of integers"""
        return type(key) == tuple and len(key) == 2 and type(key[0]) == int and type(key[1]) == int

    @staticmethod
    def check_type(value):
        """Check to make sure the value type is a LoadingZone"""
        return type(value) == LoadingZone

    def copy(self):
        """Return a new copy of the loading zone dictionary"""
        result = LoadingZoneDict()
        result.data = self.data.copy()
        return result

    def jsonify(self):
        """Convert into a list representation for use in a JSON tag"""
        result = []
        for i, j in self.data.items():
            result.append({"zone": list(i),
                           "target_level": j.target_level,
                           "target_pos": j.target_pos})
        return result


class LightmapDict(CoordinateDict):
    """Data structure for lightmap lists"""

    # Structure:
    # [{"pos": [X, Y], "diameter": SIZE, "red": {"amplitude": AMP, "inner_diameter": ID,
    # "outer_diameter": OD}, "blue": {...}, "green": {...}}]

    @staticmethod
    def check_key(key):
        """Check if the key is a pair of floats or integers"""
        if type(key) == tuple and len(key) == 2:
            if type(key[0]) == int and type(key[1]) == int:
                return True
            elif type(key[0]) == float and type(key[1]) == float:
                return True
        return False

    @staticmethod
    def check_type(value):
        """Check to make sure the value type is a Light"""
        return type(value) == Light

    def copy(self):
        """Return a new copy of the lightmap dictionary"""
        result = LightmapDict()
        result.data = self.data.copy()
        return result

    def jsonify(self):
        """Convert into a list representation for use in a JSON tag"""
        result = []
        for i, j in self.data.items():
            result.append({"pos": list(i),
                           "diameter": j.diameter,
                           "blacklight": j.blacklight,
                           "red": j.red.jsonify(),
                           "green": j.green.jsonify(),
                           "blue": j.blue.jsonify()})
        return result


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
        self.selected_id = None
        super().__init__(parent, **kw)

    def add_option(self, value, mode):
        """Base function to add a new tile to the selection pane"""
        # Correct next position
        if self.current_x == 3:
            self.current_y += 1
            self.current_x = 0

        # If mode = "tile" load from tileset.  If mode = "deco" load from decoset
        if mode == "tile":
            image = TilemapEditorWindow.tile_dict[value]
        elif mode == "deco":
            image = TilemapEditorWindow.deco_dict[value]
        else:
            raise ValueError("Cannot initialize TileCollection with unknown mode '{}'."
                             "  Options are 'tile' and 'deco'".format(mode))

        radiobutton = tk.Radiobutton(self.canvas,
                                     indicator=0,
                                     value=value,
                                     variable=self.selected_id,
                                     image=image)

        # Configure new radiobutton
        self.canvas.create_window(self.current_x * 72 + 36, self.current_y * 72 + 36, window=radiobutton)
        self.current_x += 1

        # Configure scroll-region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


class TileCollection(TilePane):

    def __init__(self, parent, group, mode, **kw):
        """These are configurable groupings of tiles to make it easier to find specific tiles"""
        super().__init__(parent, **kw)
        # Save a reference to the tracker variable
        self.selected_id = tk.IntVar(self, 0, "selected_{}".format(mode))

        # If mode = "tile" load from tileset, if mode = "deco" load from decoset, etc.
        if mode == "tile":
            image_dict = TilemapEditorWindow.tile_dict
        elif mode == "deco":
            image_dict = TilemapEditorWindow.deco_dict
        elif mode == "collision":
            image_dict = TilemapEditorWindow.collider_dict
        elif mode == "height":
            image_dict = TilemapEditorWindow.height_dict
        elif mode == "loading":
            image_dict = TilemapEditorWindow.loading_dict
        elif mode == "light":
            image_dict = TilemapEditorWindow.light_dict
        else:
            raise ValueError("Cannot initialize TileCollection with unknown mode '{}'."
                             "  Options are 'tile,' 'deco,' 'collision,' 'height,' 'loading' and 'light'".format(mode))

        # TODO: Add a configuration option for changing the width of the pane
        # Iterate through group to declare tile images in a HEIGHT x 3 grid

        for i in group:
            if self.current_x == 3:
                self.current_y += 1
                self.current_x = 0

            if i != -1:
                radiobutton = tk.Radiobutton(self.canvas,
                                             indicator=0,
                                             value=i,
                                             variable=self.selected_id,
                                             image=image_dict[i])

                # Configure new radiobutton
                self.canvas.create_window(self.current_x * 72 + 36, self.current_y * 72 + 36, window=radiobutton)
            self.current_x += 1

        # Configure scroll-region
        self.canvas.config(scrollregion=self.canvas.bbox("all"))


class TileAssembly(SelectionPane):

    def __init__(self, parent, **kw):
        """These are multi-tile objects that allow one to place structures quickly—like trees, for example"""
        super().__init__(parent, **kw)


class WorldEditorWindow(tk.Frame):
    mini_maps = {}
    __initialized = False

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        # Perform first-time initialization, if applicable
        if not WorldEditorWindow.__initialized:
            WorldEditorWindow.__initialize()

        # Declare some variables
        self.start_x = 0
        self.start_y = 0
        self.selected_image = 0
        self.bounding_box = [0, 0, 0, 0]
        self.canvas_width = 0
        self.canvas_height = 0
        self.drag_mode = False

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=1)
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)

        # Create the canvas viewport
        self.canvas = tk.Canvas(self.canvas_frame, bg="GRAY", bd=0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.canvas.bind("<ButtonPress-1>", func=self.click_canvas)
        self.canvas.bind("<B1-Motion>", func=self.drag_canvas)
        self.canvas.bind("<ButtonRelease-1>", func=self.release_click)
        self.canvas.bind("<Control-s>", func=lambda event: App.save_project_data())

        # Add the scrollbars
        self.canvas_vbar = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas_vbar.grid(row=0, column=1, sticky=tk.NS)
        self.canvas_vbar.activate("slider")
        self.canvas_hbar = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas_hbar.grid(row=1, column=0, sticky=tk.EW)
        self.canvas_hbar.activate("slider")
        self.canvas.config(scrollregion=self.canvas.bbox("all"),
                           xscrollcommand=self.canvas_hbar.set,
                           yscrollcommand=self.canvas_vbar.set)
        self.canvas.xview(tk.MOVETO, 0.0)
        self.canvas.yview(tk.MOVETO, 0.0)

        # Add to parent frame
        parent.add(self, text="World Editor")

        # Load visible levels
        self.level_list = {}
        self.level_references = {}
        self.reload()

    def event_to_coords(self, event):
        """Convert the coordinates given by an event to actual coordinates on the canvas"""
        return int(self.canvas.xview()[0] * self.canvas_width + event.x), int(
            self.canvas.yview()[0] * self.canvas_height + event.y)

    def release_click(self, event=None):
        """Update the fact that nothing is selected"""
        self.selected_image = None
        self.drag_mode = False
        self.update_bounding_box()

    def click_canvas(self, event):
        """Event callback for when the canvas is clicked"""
        # If no image was selected, player is attempting to drag the canvas
        if self.selected_image is None:
            self.drag_mode = True
            self.canvas.scan_mark(event.x, event.y)

    def drag_canvas(self, event):
        """Event callback for when the canvas is being dragged"""
        # Only attempt to drag canvas when drag mode is enabled
        if self.drag_mode:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def click_event(self, event):
        """Mark the starting coordinates"""
        self.start_x, self.start_y = self.event_to_coords(event)
        self.selected_image = event.widget.find_withtag('current')[0]

    def move_event(self, event):
        """Handle user clicking on one of the images on the canvas"""
        # Determine which image is being interacted with
        x, y = self.event_to_coords(event)

        # Move the image with the mouse
        self.canvas.move(self.selected_image, x - self.start_x, y - self.start_y)
        self.level_list[self.level_references[self.selected_image]].world_pos[0] += x - self.start_x
        self.level_list[self.level_references[self.selected_image]].world_pos[1] += y - self.start_y

        # Set the starting x and y for next call to move_event
        self.start_x = x
        self.start_y = y

    def reload(self):
        """The generic reloading function for the World Editor Window"""
        # Update registered levels
        self.reload_levels()
        self.redraw_canvas()

    def update_bounding_box(self):
        """Update the bounding box/scroll region of the canvas"""
        bounding_box = list(self.canvas.bbox("all"))
        maximum = int(max(abs(i) for i in bounding_box) * 1.5)
        bounding_box = (-maximum, -maximum, maximum, maximum)
        self.canvas.config(scrollregion=bounding_box)
        self.canvas_width = bounding_box[2] - bounding_box[0]
        self.canvas_height = bounding_box[3] - bounding_box[1]
        self.bounding_box = bounding_box

    def reload_levels(self):
        """Updates the loaded levels"""
        for level_name, level_data in App.project_data["levels"].items():
            # Note: due to mutability, the world pos data should be automatically updated
            if level_name not in self.level_list:
                # Load any mini-level not already loaded
                self.level_list[level_name] = WorldEditorLevel(level_name, level_data["world_pos"])

    def redraw_canvas(self):
        """Redraw elements on the canvas"""
        self.canvas.delete('all')
        self.level_references = {}
        for level_name, level_data in self.level_list.items():
            level_reference = self.canvas.create_image(level_data.world_pos[0],
                                                       level_data.world_pos[1],
                                                       image=WorldEditorWindow.mini_maps[level_name],
                                                       tag=level_name)
            self.level_references[level_reference] = level_name
            self.canvas.tag_bind(level_name, '<Button-1>', self.click_event)
            self.canvas.tag_bind(level_name, '<B1-Motion>', self.move_event)

        # Update the scroll region
        self.update_bounding_box()

    @classmethod
    def __initialize(cls):
        """Initialization"""
        # Load all the minimaps in the project
        for level_name, level_data in App.project_data["levels"].items():
            try:
                img = Image.open(f'mini/{level_name}.png')
            except FileNotFoundError:
                img = Image.new('RGBA', (16, 16), 0)
                print("File not found!")
            cls.mini_maps[level_name] = ImageTk.PhotoImage(img)

        cls.__initialized = True


@dataclass
class WorldEditorLevel:
    """Class to represent levels in the World Editor Window"""
    level_name: str
    world_pos: List[int]


class SpriteEditorWindow(tk.Frame):

    def __init__(self, parent, **kwargs):
        # Initialize superclass
        super().__init__(parent, **kwargs)

        # Set up some variables
        self.project_pane_state = tk.BooleanVar(self, False, "ProjectPaneState")
        self.project_pane_state.trace('w', lambda name, index, op: self.set_project_pane())

        self.view_list = []
        self.view_index = 0

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=1)
        self.main_frame.columnconfigure(3, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Create the hidden sprite selector pane
        self.project_sprite_frame = tk.Frame(self.main_frame, width=512)

        self.project_sprite_button = tk.Checkbutton(self.main_frame, indicatoron=False, text=" » ",
                                                    var=self.project_pane_state)
        self.project_sprite_button.grid(row=0, column=1, sticky=tk.NS)

        # Create the editing notebook
        self.new_view_button = ttk.Button(self.main_frame, command=self.new_view,
                                          image=TilemapEditorWindow.imgs["add_new"])
        self.new_view_button.grid(row=0, column=2, sticky=tk.NW)

        self.editing_notebook = CustomNotebook(self.main_frame)
        self.editing_notebook.bind("<<NotebookTabClosed>>", self.close_view)
        self.editing_notebook.grid(row=0, column=3, sticky=tk.NSEW)

        # Add the menubar
        self.menubar = tk.Menu(self.master)

        self.filemenu = tk.Menu(self.menubar)
        self.filemenu.add_command()

        # TODO: Add keybindings
        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open Sprite (Ctrl-O)", command=self.open_sprite)
        self.filemenu.add_command(label="Save Sprite (Ctrl-S)", command=lambda: self.save_sprite(False))
        self.filemenu.add_command(label="Save Sprite As (Ctrl-Shift-S)", command=lambda: self.save_sprite(True))
        self.filemenu.add_command(label="New Sprite (Ctrl-N)", command=self.new_view)
        self.filemenu.add_command(label="Close Sprite (Ctrl-W)", command=self.close_view)
        #self.filemenu.add_separator()
        #self.filemenu.add_command(label="Settings", command=self.unimplemented)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Launch default untitled view
        self.new_view(ignore_viewable=True)

        # Add to parent frame
        parent.add(self, text="Sprite Editor")

    def set_project_pane(self):
        """Event callback for displaying the project pane"""
        if self.project_pane_state.get():
            self.project_sprite_frame.grid(row=0, column=0, sticky=tk.NS)
            self.project_sprite_button.config(text=" « ")
        else:
            self.project_sprite_frame.grid_forget()
            self.project_sprite_button.config(text=" » ")

    def open_sprite(self):
        """Open a sprite from a file"""
        if self.master.index("current") != 2:
            return
        file = filedialog.askopenfilename(filetypes=[("Json", "*.json")], defaultextension=[("Json", "*.json")])
        if file == "" or file is None:
            return
        self.new_view()
        if not self.view_list[-1].load_from_file(file):
            self.close_view(self.editing_notebook.index("end") - 1)

    def save_sprite(self, save_as=False):
        """Save a sprite to a file"""
        if self.master.index("current") != 2:
            return
        self.view_list[-1].save(save_as)

    def new_view(self, ignore_viewable=False):
        """Create a new, blank view"""
        if self.master.index("current") != 2 and not ignore_viewable:
            return
        # Create new view instance
        self.view_list.append(SpriteView(self.editing_notebook))
        self.editing_notebook.select(self.editing_notebook.index("end") - 1)

    def close_view(self, event):
        """Close the currently open view"""
        # Check with the view if it wants to close
        if type(event) == int:
            # Index of the view in question passed in directly
            index = event
        else:
            # Index of value was passed in through the x-coordinate of an event
            index = event.x
        if self.view_list[index].close():
            # Attempt to close view was not interrupted by user (such as by clicking "cancel" in an unsaved view)
            del self.view_list[index]

    def reload(self):
        """Reload all the views"""
        for view in self.view_list:
            view.reload_region()


class LabeledEntry:

    def __init__(self, parent, row, label, variable_name, variable_type, function):

        self.ignore_callback = False

        # Save some variables
        self.variable_name = variable_name
        self.variable_type = variable_type

        if self.variable_type == bool:
            # Create data variable (boolean)
            self.data_before = False
            self.data_var = tk.BooleanVar(parent, False)
            # Create the checkbox
            self.entry = tk.Checkbutton(parent, variable=self.data_var)
        else:
            # Create data variable (string)
            self.data_before = ""
            self.data_var = tk.StringVar(parent, "")
            # Create the entry box
            self.entry = tk.Entry(parent, textvariable=self.data_var)

        # Add the callback to the data variable
        self.data_var.trace('w', lambda name, index, op, x=function: self.entry_callback(x))

        # Create the label
        self.label = tk.Label(parent, text=f'{label}:')
        self.label.grid(row=row, column=0, sticky=tk.W)

        # Place the entry box
        self.entry.grid(row=row, column=1, padx=4, sticky=tk.W)

    def entry_callback(self, function):
        """Event callback for when the entry text is modified"""
        if self.ignore_callback:
            return
        if len(str(self.data_var.get())) != 0:
            try:
                text = self.variable_type(self.data_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid entry")
                self.ignore_callback = True
                self.data_var.set(self.data_before)
                self.ignore_callback = False
            else:
                self.data_before = self.data_var.get()
                function(self.variable_name, text)

    def insert_data(self, value):
        self.ignore_callback = True
        self.data_var.set(value)
        self.ignore_callback = False


class CategoryEditor(tk.LabelFrame):

    def __init__(self, parent, title, sprite_data_reference, **kwargs):
        super().__init__(parent, text=title, **kwargs)

        self.sprite_data_reference = sprite_data_reference
        self.entries = {}
        for i, (var, var_type) in enumerate(sprite_data_reference.__annotations__.items()):
            label = var.replace('_', ' ').title()
            self.entries[var] = LabeledEntry(self, i, label, var, var_type, self.modify_value)

    def modify_value(self, variable_name, value):
        """Override in subclass"""
        if variable_name in self.sprite_data_reference.__dict__:
            self.sprite_data_reference.__dict__[variable_name] = value

    def update_from_sprite(self, data_dict):
        """Insert data from a dictionary representing a sprite's attributes"""
        for i, j in self.entries.items():
            j.insert_data(data_dict[i])


class SpriteView(ttk.Frame):

    def __init__(self, parent, **kwargs):
        # Initialize the superclass
        super().__init__(parent, **kwargs)

        # Ensure the parent widget is a CustomNotebook
        if type(parent) != CustomNotebook:
            raise TypeError("Cannot assign a {} to a {}".format(SpriteView, type(parent)))

        # Declare some variables
        self.view_name = "Untitled"
        self.file_path = None
        self.saved = True

        # Declare sprite
        self.sprite = Sprite()

        # Add to parent widget
        parent.add(self, text=self.view_name)

        # Create scrollbar
        self.scrollable_canvas = tk.Canvas(self)
        self.scrollable_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.window = tk.Frame(self.scrollable_canvas)
        self.scrollable_canvas.create_window((0, 0), window=self.window, anchor="nw")

        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.scrollable_canvas.yview)
        self.scrollbar.activate("slider")

        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=0)

        self.scrollable_canvas.yview(tk.MOVETO, 0.0)

        # Create animation window
        self.animation_frame = tk.LabelFrame(self.window, text="Animations")
        self.animation_frame.pack(fill=tk.X, expand=1)

        self.animation_canvas = tk.Canvas(self.animation_frame, width=256, height=256, bg="WHITE", bd=1)
        self.animation_canvas.grid(row=1, column=0)

        self.animation_config_frame = tk.Frame(self.animation_frame)
        self.animation_config_frame.grid(row=1, column=1)

        self.image_dict = {}

        # self.name_entry = LabeledEntry(self.general_frame, 0, "Name", "name", self.modify_generic)
        # self.focus_entry = LabeledEntry(self.general_frame, 1, "Focus?", "focus", self.modify_generic)
        # self.path_type_entry = LabeledEntry(self.general_frame, 2, "Path Type", "path_type", self.modify_generic)
        # self.path_delay_entry = LabeledEntry(self.general_frame, 3, "Path Delay", "path_delay", self.modify_generic)
        # self.facing_type_entry = LabeledEntry(self.general_frame, 4, "Facing Type", "facing_type", self.modify_generic)

        # Create the general-purpose editing window
        self.general_table = CategoryEditor(self.window, "General", self.sprite)
        self.general_table.pack(fill=tk.X, expand=1)

        # Create the world data editing window
        self.world_table = CategoryEditor(self.window, "World Data", self.sprite.world_data)
        self.world_table.pack(fill=tk.X, expand=1)

        # Create the position editing window
        self.position_table = CategoryEditor(self.window, "Positioning", self.sprite.position)
        self.position_table.pack(fill=tk.X, expand=1)

        # Create the stats editing window
        self.stats_table = CategoryEditor(self.window, "Stats", self.sprite.stats)
        self.stats_table.pack(fill=tk.X, expand=1)

        self.update()
        self.reload_region()

    def reload_region(self):
        """Reload the scroll-region"""
        # Configure the scroll-region
        self.scrollable_canvas.config(scrollregion=self.scrollable_canvas.bbox("all"),
                                      yscrollcommand=self.scrollbar.set)

    def modify_generic(self, entry_name, value):
        """Event callback for a general-type entry being modified.  Value is trusted to be valid"""
        if entry_name in self.sprite.__dict__:
            self.sprite.__dict__[entry_name] = value

    def modify_world_data(self, entry_name, value):
        """Event callback for a general-type entry being modified.  Value is trusted to be valid"""
        if entry_name in self.sprite.world_data.__dict__:
            self.sprite.world_data.__dict__[entry_name] = value

    def close(self, ignore_saved=False):
        """Destroy this sprite-view"""
        if not(self.saved or ignore_saved):
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
        self.destroy()
        return True

    def load_from_file(self, file):
        with open(file, mode='r') as rf:
            json_dict = json.load(rf)

        # Load data to sprite from json dictionary
        if not self.sprite.load_from_json(json_dict):
            return False

        # Update status variables
        self.saved = True
        self.file_path = file
        self.view_name = path.split(file)[1]
        self.update_title()

        # Sync data from sprite to entries
        self.general_table.update_from_sprite(self.sprite.__dict__)
        self.world_table.update_from_sprite(self.sprite.world_data.__dict__)
        self.position_table.update_from_sprite(self.sprite.position.__dict__)
        self.stats_table.update_from_sprite(self.sprite.stats.__dict__)

        return True

    def save(self, save_as=False):
        if save_as:
            self.save_to_file(None)
        else:
            self.save_to_file(self.file_path)

    def save_to_file(self, file):
        """Save the sprite to a file"""
        # If this file is NOT part of the project and hasn't been excluded, ask whether it should be.
        if not self.sprite.ignore_from_project:
            if self.view_name not in App.project_data["sprites"]:
                result = messagebox.askyesnocancel(title="Unregistered Level", message="This sprite was not found in "
                                                                                       "the project.json file.  Would "
                                                                                       "you like to save it to the "
                                                                                       "project?  (Clicking 'No' will "
                                                                                       "exclude for as long as it "
                                                                                       "remains in the editor)")
                if result is None:
                    # User canceled the saving process
                    return
                elif result:
                    # User added level to project.json
                    App.project_data["sprites"][self.view_name] = {"path": ""}
                else:
                    # User excluded level from project.json
                    self.sprite.ignore_from_project = True

        # Save the project data to project.json
        App.save_project_data()

        # No file path has been set
        if file is None:
            file = filedialog.asksaveasfilename(filetypes=[('JSON File', '*.json')],
                                                defaultextension=[('JSON File', '*.json')])
            print("File: ", file)
            if file == "":
                # User canceled saving, exit function
                return

            # Obtain and save file path
            file = path.split(file)[1]
            self.sprite.name = path.splitext(file)[0]
            file = path.join("entities", file)
            self.file_path = file

        if self.view_name in App.project_data["sprites"]:
            print(file)
            relative_path = file.replace((getcwd() + '/').replace('\\', '/'), '')
            App.project_data["sprites"][self.view_name]["path"] = relative_path

        # Write json tag to file
        with open(file, mode="w") as f:
            f.write(self.sprite.jsonify())
        self.saved = True
        self.update_title()

    def update_title(self):
        """Update the view title"""
        # If not saved, add an asterisk in front of the displayed name
        if self.saved:
            self.master.tab(self, text=self.view_name)
        else:
            self.master.tab(self, text="*" + self.view_name)



@dataclass
class SpriteWorldData:
    level: str = "void"
    scope: str = "local"


@dataclass
class SpritePosition:
    x: float = 0.0
    y: float = 0.0
    z: int = 1
    base_speed: float = 1.0
    auto_size: bool = True
    w: float = 0.0
    h: float = 0.0
    collide: bool = False


@dataclass
class SpriteAnimation:
    root_path: str = "entities/"
    images: List[str] = field(default_factory=list)
    sequence: List[int] = field(default_factory=list)
    frame_time: List[float] = field(default_factory=list)
    scale_factor: int = 1


@dataclass
class SpriteStats:
    invulnerable: bool = True
    speed_modifier: float = 1.0
    health: int = 100


class Sprite:
    name: str
    focus: bool
    path_type: int
    path_delay: int
    facing_type: int

    def __init__(self):
        self.name = ""
        self.world_data = SpriteWorldData()
        self.focus = False
        self.position = SpritePosition()
        self.path_type = 0
        self.path_delay = 0
        self.facing_type = 0
        self.animation = {}
        self.stats = SpriteStats()
        self.ignore_from_project = False

    def load_from_json(self, json_dict):
        """Load a sprite from a json dictionary"""
        try:
            self.name = json_dict["name"]
            self.world_data.level = json_dict["world_data"]["level"]
            self.world_data.scope = json_dict["world_data"]["scope"]
            self.focus = json_dict["focus"]
            self.position = SpritePosition(x=json_dict["position"]["x"],
                                           y=json_dict["position"]["y"],
                                           z=json_dict["position"]["z"],
                                           base_speed=json_dict["position"]["base_speed"],
                                           auto_size=json_dict["position"]["auto_size"],
                                           w=json_dict["position"]["w"],
                                           h=json_dict["position"]["h"],
                                           collide=json_dict["position"]["collide"])
            self.path_type = json_dict["path_type"]
            self.path_delay = json_dict["path_delay"]
            self.facing_type = json_dict["facing_type"]
            self.animation = {}
            for animation_id, animation_data in json_dict["animation"].items():
                self.animation[animation_id] = SpriteAnimation(root_path=animation_data["root_path"],
                                                               images=animation_data["images"],
                                                               sequence=animation_data["sequence"],
                                                               frame_time=animation_data["frame_time"],
                                                               scale_factor=animation_data["scale_factor"])
            self.stats = SpriteStats(invulnerable=json_dict["stats"]["invulnerable"],
                                     speed_modifier=json_dict["stats"]["speed_modifier"],
                                     health=json_dict["stats"]["health"])
            return True
        except KeyError as error:
            messagebox.showerror("Error", f'An error occurred while loading this sprite:'
                                          f' could not find component {error}')
            return False

    def jsonify(self):
        """Convert sprite data to a formatted json string"""
        # Build the json string
        result = json.dumps({"name": self.name,
                             "world_data": self.world_data.__dict__,
                             "focus": self.focus,
                             "position": self.position.__dict__,
                             "path_type": self.path_type,
                             "path_delay": self.path_delay,
                             "facing_type": self.facing_type,
                             "animation": dict((i, j.__dict__) for i, j in self.animation.items()),
                             "stats": self.stats.__dict__},
                            indent=4)

        # Format the json string using regular expressions
        result = re.sub(r'\s+([0-9.\-]+),', r'\1, ', result)
        result = re.sub(r'\s+([0-9.\-]+)\s+\]', r' \1]', result)
        result = re.sub(r':([0-9.\-]+)', r': \1', result)

        return result


class NotesEditorWindow(tk.Frame):

    def __init__(self, parent, **kwargs):
        # Create the source frame
        super().__init__(**kwargs)

        # Create the text entry
        self.textbox = tk.Text(self, borderwidth=1, padx=10, pady=10, maxundo=10, font="consolas 11")
        self.textbox.pack(fill=tk.BOTH, expand=1)
        self.textbox.bind("<Control-z>", lambda event: self.undo_edit())
        self.textbox.bind("<Control-y>", lambda event: self.redo_edit())
        self.textbox.bind("<Control-s>", lambda event: self.save_notes())
        self.textbox.bind("<Control-BackSpace>", lambda event: self.delete_word())

        # Add text to textbox
        self.textbox.insert('1.0', App.project_data["notes"])

        # Add to parent frame
        parent.add(self, text="Notes")

    def save_notes(self):
        """Save notes to project.json"""
        App.project_data["notes"] = self.textbox.get('1.0', 'end-1c')
        App.save_project_data()

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
    # Forgive me, for I have used variables with excessive scope
    project_data = {}

    def __init__(self, parent):
        """World Builder 2"""
        # Load project data
        App.load_project_data()

        # Begin editor layout setup
        self.source = ttk.Notebook(parent)

        # Create the various editing windows
        self.tilemap_editor = TilemapEditorWindow(self.source)
        self.world_editor = WorldEditorWindow(self.source, borderwidth=1, relief=tk.SUNKEN)
        self.sprite_editor = SpriteEditorWindow(self.source)
        self.notepad = NotesEditorWindow(self.source, borderwidth=1, relief=tk.SUNKEN)

        self.source.pack(expand=1, fill="both")

        # Add toolbar
        self.menubar = tk.Menu(parent)

        # Add event listener to update the toolbar
        self.source.bind("<<NotebookTabChanged>>",
                         lambda event: self.update_toolbar(self.source.index("current")))

    def update_toolbar(self, value):
        """Updates the toolbar to match the current tab"""
        self.world_editor.reload()  # Ensure the world editor is reloaded.  I don't like putting this here.  Not Funland
        self.sprite_editor.reload() # Ensure the sprite editor is reloaded.
        self.menubar.forget()
        self.menubar = tk.Menu(self.source.master)
        # Tilemap editor window toolbar
        if value == 0:
            # Tilemap editor menubar
            self.source.master.config(menu=self.tilemap_editor.menubar)
        elif value == 2:
            # Sprite editor menubar
            self.source.master.config(menu=self.sprite_editor.menubar)
        else:
            # Default menubar
            self.source.master.config(menu=self.menubar)

    @classmethod
    def load_project_data(cls):
        """Load the project data from project.json"""
        with open("project.json", mode="r") as f:
            App.project_data = json.load(f)

    @classmethod
    def save_project_data(cls):
        """Save the project data to project.json"""
        with open("project.json", mode="w") as f:
            project_data = json.dumps(cls.project_data, indent=2)
            project_data = re.sub(r'\s+([0-9.\-]+),', r'\1, ', project_data)
            project_data = re.sub(r'\s+([0-9.\-]+)\s+\]', r' \1]', project_data)
            project_data = re.sub(r':([0-9.\-]+)', r': \1', project_data)
            f.write(project_data)


def main():
    root = tk.Tk()
    root.title("World Builder 2")
    icon = tk.PhotoImage("img_icon", data='''R0lGODlhEAAQAKU7ABIaVhIbVxckXhgkXh0rZR0sZSEybCU3ciU4cik9eCxBfS5
                                             Fgy9Fgy9GgzFJ\niDRNjTZQkjhUljlUljlUlztXmz1anz1aoJGRkZaWlZaWlpeX
                                             l5qbm5ubm5ycnJ+enp+foKCgoKGh\noaKioqOjo6SkpKWlpaampqenp6mpqamqq
                                             qqqqqurq6ysrK2tra6urq+vr7Cvr7CxsbKysrS0tLW1\ntbq6us/Pz9nZ2dra2u
                                             Tk5P///1J711J711J711J711J71yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5\nBAE
                                             KAD8ALAAAAAAQABAAAAZtwJ9wKPSMiEiiphMyJZEXDAdEWj2Hl8y0lHJdhZnNh6
                                             SCzb4/pkn1\nmtmuhYToxIrRbrokIeGYoFoyNTl5RAQIDBAWP202hEMDCA0QFUM
                                             1OEgCCAuTaAMHDA8UaAEGCqFo\nAKWnaKoRaEMOEq9CQQA7
                                             ''')

    root.iconphoto(False, icon)

    main_app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
