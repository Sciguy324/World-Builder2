import tkinter as tk
from tkinter import ttk


class TilemapEditorWindow:

    def __init__(self, parent):
        """Editor window for a level"""
        self.panel = ttk.Frame(parent)
        parent.add(self.panel, text="Map Editor")


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
        # Begin editor setup
        self.source = ttk.Notebook(parent)

        tab1 = ttk.Frame(self.source)
        tab2 = ttk.Frame(self.source)

        self.source.add(tab1, text="Tab 1")
        self.source.add(tab2, text="Tab 2")

        self.source.pack(expand=1, fill="both")


if __name__ == "__main__":
    root = tk.Tk()

    main = App(root)

    root.mainloop()
