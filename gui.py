import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

from dungeon_generator.renderer import render_dungeon, TILE_SIZE
from dungeon_generator.exporter import export_to_foundry_scene
from dungeon_generator.generator import generate_basic_dungeon

class DungeonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dungeon Generator")
        self.root.geometry("1200x800")  # width x height in pixels

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
        # Dropdown-style export menu
        export_menu = tk.Menubutton(self.navbar, text="Export", relief=tk.RAISED)
        export_dropdown = tk.Menu(export_menu, tearoff=0)

        export_dropdown.add_command(label="Export to Foundry", command=self.export_to_foundry)

        # Add disabled Universal option with a tooltip
        export_dropdown.add_command(label="Export to Universal VTT", state="disabled")
        export_menu.config(menu=export_dropdown)
        export_menu.pack(side="left", padx=5, pady=5)

        # Add tooltip manually using a simple hover event
        def on_enter():
            self._show_tooltip(
                export_menu,
                "Exporting to Universal will not include all functionality."
                )

        def on_leave():
            self._hide_tooltip()

        export_menu.bind("<Enter>", on_enter)
        export_menu.bind("<Leave>", on_leave)

        # Exit button
        exit_btn = ttk.Button(self.navbar, text="Exit", command=self.root.quit)
        exit_btn.pack(side="right", padx=5, pady=5)

    def _init_toolbar(self):
        ttk.Label(self.toolbar, text="Seed:").pack(pady=(10, 0))
        self.seed_entry = ttk.Entry(self.toolbar)
        self.seed_entry.pack(pady=5)

        ttk.Label(self.toolbar, text="Width:").pack(pady=(10, 0))
        self.width_entry = ttk.Entry(self.toolbar)
        self.width_entry.insert(0, "20")
        self.width_entry.pack(pady=5)

        ttk.Label(self.toolbar, text="Height:").pack(pady=(10, 0))
        self.height_entry = ttk.Entry(self.toolbar)
        self.height_entry.insert(0, "20")
        self.height_entry.pack(pady=5)

        self.generate_button = ttk.Button(
            self.toolbar, text="Generate",
            command=self.generate_dungeon
            )
        self.generate_button.pack(pady=20)

        # Bind Enter key to generate
        self.root.bind("<Return>", lambda event: self.generate_dungeon())

    def _init_viewport(self):

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

    def generate_dungeon(self):
        try:
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            seed = self.seed_entry.get()
        except ValueError:
            print("[!] Invalid input")
            return

        self.dungeon = generate_basic_dungeon(width, height, seed)

        self.rendered_pil_image = render_dungeon(self.dungeon)

        # Auto zoom-out to fit if needed
        img_w, img_h = self.rendered_pil_image.size
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w > 1 and canvas_h > 1:  # avoid 0 during startup
            scale_x = canvas_w / img_w
            scale_y = canvas_h / img_h
            fit_zoom = min(scale_x, scale_y, 1.0)  # only zoom out, never in
            self.zoom_level = fit_zoom

        self.display_image(self.rendered_pil_image)

    def display_image(self, pil_image):
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

    def export_to_foundry(self):
        if not hasattr(self, "dungeon") or not hasattr(self, "rendered_pil_image"):
            print("[!] No dungeon or image to export.")
            return

        folder = filedialog.askdirectory(title="Select export folder")
        if not folder:
            return  # Cancelled

        # File paths
        img_path = os.path.join(folder, "dungeon.png")
        json_path = os.path.join(folder, "dungeon.scene.json")

        # Save image
        self.rendered_pil_image.save(img_path)
        print(f"[✓] Image saved to {img_path}")

        # Export scene JSON
        walls = [w.to_foundry_dict() for w in self.dungeon.walls]
        lights = [l.to_foundry_dict() for l in self.dungeon.lights]
        notes = [n.to_foundry_dict() for n in self.dungeon.notes]
        tiles = [t.to_foundry_dict() for t in self.dungeon.tiles]

        export_to_foundry_scene(
            scene_name="My Dungeon",
            background_image_path=os.path.basename(img_path),  # relative path
            width=self.dungeon.width * TILE_SIZE,
            height=self.dungeon.height * TILE_SIZE,
            grid_size=TILE_SIZE,
            walls=walls,
            lights=lights,
            notes=notes,
            tiles=tiles,
            output_path=json_path
        )

    def _show_tooltip(self, widget, text):
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

    def _hide_tooltip(self):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            del self.tooltip

    def _on_zoom(self, event):
        if event.num == 5 or event.delta == -120:
            self.zoom_level = max(0.1, self.zoom_level - 0.1)
        elif event.num == 4 or event.delta == 120:
            self.zoom_level = min(5.0, self.zoom_level + 0.1)

        self.display_image(self.rendered_pil_image)  # Re-render with new zoom

    def _on_pan_start(self, event):
        self._pan_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _on_pan_move(self, event):
        if self._pan_start is None:
            return

        # Convert mouse position to canvas coords (adjusted for zoom and scroll)
        start_x, start_y = self._pan_start
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)

        # Delta movement in pixels
        dx = start_x - current_x
        dy = start_y - current_y

        # Get current scroll region
        x0, y0, x1, y1 = self.canvas.bbox("all")
        canvas_width = x1 - x0
        canvas_height = y1 - y0

        # Get current scroll fractions
        x_scroll = self.canvas.xview()
        y_scroll = self.canvas.yview()

        # Adjust scroll position based on pixel delta
        new_x = x_scroll[0] + dx / canvas_width
        new_y = y_scroll[0] + dy / canvas_height

        self.canvas.xview_moveto(new_x)
        self.canvas.yview_moveto(new_y)

        # Update pan start position
        self._pan_start = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _on_canvas_resize(self, event):
        if hasattr(self, "rendered_pil_image"):
            self.display_image(self.rendered_pil_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = DungeonApp(root)
    root.mainloop()
