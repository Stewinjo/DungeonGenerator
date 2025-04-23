"""
main.py

Graphical user interface for the Rosecrypt Dungeon Generator.

This module defines the `DungeonApp` class, which provides an interactive Tkinter-based GUI
for generating, previewing, and exporting procedural dungeons. It integrates with the
rendering, generation, and exporting subsystems,
offering a visual front end to the Rosecrypt engine.
"""

import tkinter as tk
import uuid
from collections import defaultdict
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk


from rosecrypt.rendering.dungeon_renderer import DungeonRenderer
from rosecrypt.rendering.rendering_settings import RenderingSettings
from rosecrypt.rendering.enums.rendering_tag import RenderingTag
from rosecrypt.generation.dungeon_generator import DungeonGenerator
from rosecrypt.generation.generation_settings import GenerationSettings
from rosecrypt.generation.enums.generation_tag import GenerationTag
from rosecrypt.exporting.dungeon_exporter import DungeonExporter
from rosecrypt.exporting.exporter_settings import ExporterSettings

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class DungeonApp:
    """
    Main application window for the Rosecrypt Dungeon Generator GUI.

    Provides an interface for dungeon generation settings, rendering preview,
    and exporting to virtual tabletop formats.

    :param root: The root Tkinter window instance.
    :type root: tk.Tk
    """

    def __init__(self, root):
        """
        Initialize the main GUI application and layout.

        :param root: The Tkinter root window.
        :type root: tk.Tk
        """
        self.root = root
        self.root.title("Dungeon Generator")
        self.root.geometry("1200x800")  # width x height in pixels

        # Pre-declare variables before any init function uses them
        self.seed_entry = None
        self.width_entry = None
        self.height_entry = None
        self.generate_button = None
        self.canvas = None
        self.h_scroll = None
        self.v_scroll = None
        self.zoom_level = 1.0
        self._pan_start = None
        self.rendered_image = None
        self.rendered_pil_image = None
        self.dungeon = None
        self.tooltip = None
        self.active_tags = set()
        self.tag_buttons = {}

        # === Main layout frames ===
        self.navbar = ttk.Frame(root)
        self.toolbar = ttk.Frame(root, width=200)
        self.viewport = ttk.Frame(root)

        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.toolbar.grid(row=1, column=0, sticky="ns")
        self.viewport.grid(row=1, column=1, sticky="nsew")

        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        self._init_navbar()
        self._init_toolbar()
        self._init_viewport()

    def _init_navbar(self):
        """
        Initializes the top navigation bar, including export dropdown
        and an exit button.
        """

        # Dropdown-style export menu
        export_menu = tk.Menubutton(self.navbar, text="Export", relief=tk.RAISED)
        export_dropdown = tk.Menu(export_menu, tearoff=0)

        export_dropdown.add_command(label="Export to Foundry", command=self._export_to_foundry)

        # Add disabled Universal option with a tooltip
        export_dropdown.add_command(label="Export to Universal VTT", state="disabled")
        export_menu.config(menu=export_dropdown)
        export_menu.pack(side="left", padx=5, pady=5)

        # Add tooltip manually using a simple hover event
        def on_enter(event):
            # pylint: disable=unused-argument
            self.__show_tooltip(
                export_menu,
                "Exporting to Universal will not include all functionality."
            )

        def on_leave(event):
            # pylint: disable=unused-argument
            self.__hide_tooltip()

        export_menu.bind("<Enter>", on_enter)
        export_menu.bind("<Leave>", on_leave)

        # Exit button
        exit_btn = ttk.Button(self.navbar, text="Exit", command=self.root.quit)
        exit_btn.pack(side="right", padx=5, pady=5)

    def _init_toolbar(self):
        """
        Initializes the sidebar toolbar, including inputs for seed,
        width, height, and category-tagged generation options.
        """

        self.toolbar.columnconfigure(1, weight=1)

        # Seed row
        ttk.Label(self.toolbar, text="Seed:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.seed_entry = ttk.Entry(self.toolbar)
        self.seed_entry.insert(0, str(uuid.uuid4().hex[:8]))
        self.seed_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        reroll_button = ttk.Button(self.toolbar, text="🔁", width=3, command=self._reroll_seed)
        reroll_button.grid(row=0, column=2, padx=5)

        # Width row
        ttk.Label(self.toolbar, text="Width:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.width_entry = ttk.Entry(self.toolbar)
        self.width_entry.insert(0, "40")
        self.width_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Height row
        ttk.Label(self.toolbar, text="Height:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.height_entry = ttk.Entry(self.toolbar)
        self.height_entry.insert(0, "40")
        self.height_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Define a style for selected tags
        style = ttk.Style()
        style.configure("Selected.TButton", background="grey", foreground="black")

        # Group tags by category
        tag_groups = defaultdict(list)
        for tag in GenerationTag:
            tag_groups[tag.category].append(tag)

        current_row = 3

        # Create tag sections, grouped by category
        for category, tags in tag_groups.items():
            ttk.Label(self.toolbar, text=category).grid(
                row=current_row,
                column=0,
                columnspan=3,
                sticky="w",
                padx=5,
                pady=(10, 2)
                )
            current_row += 1

            for i, tag in enumerate(tags):
                row = current_row + (i // 3)
                col = i % 3
                btn = ttk.Button(
                    self.toolbar,
                    text=tag.name.replace("_", " ").title(),
                    command=lambda t=tag: self.__toggle_tag(t)
                    )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
                self.tag_buttons[tag] = btn

            current_row += (len(tags) + 2) // 3  # account for used rows

        # Generate button
        self.generate_button = ttk.Button(
            self.toolbar,
            text="Generate",
            command=self._generate_dungeon
            )
        self.generate_button.grid(row=current_row, column=0, columnspan=3, pady=20)

        self.root.bind("<Return>", lambda event: self._generate_dungeon())

    def _reroll_seed(self):
        """Generates a new random seed and populates the seed entry widget."""
        new_seed = uuid.uuid4().hex[:8]
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, new_seed)

    def _init_viewport(self):
        """
        Initializes the central canvas viewport used for dungeon rendering.
        Includes scrollbars and canvas zoom/pan bindings.
        """

        # Frame to hold canvas + scrollbars
        self.viewport_canvas_frame = ttk.Frame(self.viewport)
        self.viewport_canvas_frame.pack(fill="both", expand=True)

        # Scrollbars
        self.h_scroll = tk.Scrollbar(self.viewport_canvas_frame, orient="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")

        self.v_scroll = tk.Scrollbar(self.viewport_canvas_frame, orient="vertical")
        self.v_scroll.pack(side="right", fill="y")

        # Canvas
        self.canvas = tk.Canvas(
            self.viewport_canvas_frame,
            bg="black",
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)

        # Setup auto zoom-out
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Setup pan
        self._pan_start = None
        self.canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self.canvas.bind("<B1-Motion>", self._on_pan_move)

        # Setup zoom
        self.zoom_level = 1.0
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<Button-4>", self._on_zoom)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_zoom)  # Linux scroll down

    def _generate_dungeon(self):
        """
        Reads current input values and generation settings, then generates
        and renders a dungeon instance on the canvas.
        """

        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            seed = self.seed_entry.get()
        except ValueError:
            print("[!] Invalid input")
            return

        generation_settings = GenerationSettings.from_gui(
            width,
            height,
            seed,
            list(self.active_tags)
            )
        self.dungeon = DungeonGenerator(generation_settings).generate_dungeon(width, height)

        rendering_settings = RenderingSettings.from_gui(seed, RenderingTag.make_full_set())
        self.rendered_pil_image = DungeonRenderer(self.dungeon, rendering_settings).render_dungeon()

        img_w, img_h = self.rendered_pil_image.size
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w > 1 and canvas_h > 1:
            scale_x = canvas_w / img_w
            scale_y = canvas_h / img_h
            fit_zoom = min(scale_x, scale_y, 1.0)
            self.zoom_level = fit_zoom

        self.__display_image(self.rendered_pil_image)

    def __display_image(self, pil_image):
        """
        Displays a PIL image on the canvas with zoom and centering applied.

        :param pil_image: The rendered dungeon image.
        :type pil_image: PIL.Image.Image
        """

        if not pil_image:
            return

        zoomed_width = int(pil_image.width * self.zoom_level)
        zoomed_height = int(pil_image.height * self.zoom_level)

        resized = pil_image.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
        self.rendered_image = ImageTk.PhotoImage(resized)

        # Clear old content
        self.canvas.delete("all")

        # Update scroll region
        self.canvas.config(scrollregion=(
            0,
            0,
            max(zoomed_width, self.canvas.winfo_width()),
            max(zoomed_height, self.canvas.winfo_height())
        ))

        # Get actual canvas visible size
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Compute top-left coordinates to center image if smaller
        x_offset = max((canvas_width - zoomed_width) // 2, 0)
        y_offset = max((canvas_height - zoomed_height) // 2, 0)

        self.canvas.create_image(x_offset, y_offset, anchor="nw", image=self.rendered_image)

    def _export_to_foundry(self):
        """
        Exports the currently rendered dungeon to Foundry VTT format.
        Includes a prompt for selecting an export folder.
        """

        if not hasattr(self, "dungeon"):
            print("[!] No dungeon to export.")
            return

        try:
            seed = self.seed_entry.get()
        except ValueError:
            print("[!] Invalid input")
            return

        folder = filedialog.askdirectory(title="Select export folder")
        if not folder:
            return  # Cancelled

        rendering_settings = RenderingSettings.from_gui(seed, RenderingTag.make_full_set())
        exporter_settings = ExporterSettings.from_gui(rendering_settings)
        DungeonExporter(self.dungeon, exporter_settings).export_to_foundry_scene(folder)

    def __show_tooltip(self, widget, text):
        """
        Displays a tooltip near the specified widget.

        :param widget: The widget to anchor the tooltip to.
        :type widget: tk.Widget
        :param text: The tooltip text to display.
        :type text: str
        """

        x = widget.winfo_rootx() + 50
        y = widget.winfo_rooty() + 30
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tooltip,
            text=text,
            background="#ffffcc",
            relief="solid",
            borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=1)

    def __hide_tooltip(self):
        """Hides the currently displayed tooltip if present."""

        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

    def _on_zoom(self, event):
        """
        Zooms in or out on the dungeon render based on mouse scroll input.

        :param event: The mouse wheel scroll event.
        :type event: tk.Event
        """

        if event.num == 5 or event.delta == -120:
            self.zoom_level = max(0.1, self.zoom_level - 0.1)
        elif event.num == 4 or event.delta == 120:
            self.zoom_level = min(5.0, self.zoom_level + 0.1)

        self.__display_image(self.rendered_pil_image)  # Re-render with new zoom

    def _on_pan_start(self, event):
        """
        Begins a panning operation on mouse press.

        :param event: The mouse press event.
        :type event: tk.Event
        """

        self._pan_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _on_pan_move(self, event):
        """
        Drags the image on the canvas based on mouse motion.

        :param event: The mouse drag event.
        :type event: tk.Event
        """

        if self._pan_start is None:
            return

        # Skip if canvas is empty
        if not self.canvas.bbox("all"):
            return

        x0, y0, x1, y1 = self.canvas.bbox("all")

        # Convert mouse position to canvas coords (adjusted for zoom and scroll)
        start_x, start_y = self._pan_start
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)

        # Get current scroll fractions
        x_scroll = self.canvas.xview()
        y_scroll = self.canvas.yview()

        # Adjust scroll position based on pixel delta
        new_x = x_scroll[0] + (start_x - current_x) / (x1 - x0)
        new_y = y_scroll[0] + (start_y - current_y) / (y1 - y0)

        self.canvas.xview_moveto(new_x)
        self.canvas.yview_moveto(new_y)

        # Update pan start position
        self._pan_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))


    def __toggle_tag(self, tag: GenerationTag):
        """
        Toggles a generation tag from the set of active tags,
        and updates button visuals accordingly.

        :param tag: The tag to toggle.
        :type tag: GenerationTag
        """
        self.active_tags = GenerationTag.toggle_tag(self.active_tags, tag)
        self.__update_tag_button_states()

    def __update_tag_button_states(self):
        """
        Updates tag button visual styles to reflect the current
        selection state for all available generation tags.
        """
        for tag, btn in self.tag_buttons.items():
            if tag in self.active_tags:
                btn.config(style="Selected.TButton")
            else:
                btn.config(style="TButton")

    def _on_canvas_resize(self, event):
        # pylint: disable=unused-argument
        """
        Re-renders the image to maintain centering and zoom level when
        the canvas is resized.

        :param event: The canvas resize event.
        :type event: tk.Event
        """

        if hasattr(self, "rendered_pil_image"):
            self.__display_image(self.rendered_pil_image)

def launch_gui():
    """
    Entry point for launching the Dungeon Generator GUI.
    Initializes the main window and starts the Tkinter event loop.
    """
    tk_root = tk.Tk()
    DungeonApp(tk_root)
    tk_root.mainloop()
