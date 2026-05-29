import tkinter as tk
import customtkinter as ctk
import datetime as dt
from tkinter import filedialog, messagebox

from src.config import (
    BG_PRIMARY, BG_SECONDARY, BG_BUTTON, BG_BUTTON_HOVER,
    TEXT_PRIMARY, TEXT_MUTED, COLOR_PAINTED, COLOR_HOVER,
    COLOR_RED, COLOR_RED_HOVER, COLOR_GEN, COLOR_GEN_HOVER,
    BOX_SIZE, BOX_GAP, TOP_MARGIN, LEFT_MARGIN
)

class ControlPanel(ctk.CTkFrame):
    def __init__(self, master, config, callbacks):
        super().__init__(master, fg_color="transparent")
        self.config = config
        self.callbacks = callbacks
        self.option_var = ctk.StringVar(value=str(self.config.year))
        
        # TOP ROW: Repository Settings
        self.repo_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=10)
        self.repo_frame.pack(fill="x", pady=(0, 10))
        self.repo_frame.grid_columnconfigure(1, weight=1)

        paddings = {"padx": 15, "pady": 15}

        self.dir_btn = ctk.CTkButton(
            self.repo_frame, text="Choose Directory", command=self._choose_directory,
            fg_color=BG_BUTTON, hover_color=BG_BUTTON_HOVER, width=140
        )
        self.dir_btn.grid(column=0, row=0, sticky="w", **paddings)

        display_dir = self.config.dir if len(self.config.dir) < 60 else "..." + self.config.dir[-57:]
        self.dir_label = ctk.CTkLabel(
            self.repo_frame, text=display_dir, anchor="w", text_color=TEXT_PRIMARY, font=("Arial", 13)
        )
        self.dir_label.grid(column=1, row=0, sticky="w", padx=10)

        self.button = ctk.CTkButton(
            self.repo_frame, text="Generate", command=callbacks["generate"],
            fg_color=COLOR_GEN, hover_color=COLOR_GEN_HOVER, width=140, font=("Arial", 14, "bold")
        )
        self.button.grid(column=2, row=0, sticky="e", **paddings)

        # BOTTOM ROW: Drawing Tools
        self.tools_frame = ctk.CTkFrame(self, fg_color=BG_SECONDARY, corner_radius=10)
        self.tools_frame.pack(fill="x")

        self.tools_inner = ctk.CTkFrame(self.tools_frame, fg_color="transparent")
        self.tools_inner.pack(pady=10)

        self.year_left_btn = ctk.CTkButton(
            self.tools_inner, text="<", width=35, command=self._year_decrement,
            fg_color=BG_BUTTON, hover_color=BG_BUTTON_HOVER
        )
        self.year_left_btn.grid(column=0, row=0, padx=(0, 10))

        self.year_entry = ctk.CTkEntry(
            self.tools_inner, textvariable=self.option_var, width=70, justify="center",
            fg_color=BG_BUTTON, border_color=BG_BUTTON_HOVER, text_color=TEXT_PRIMARY, font=("Arial", 13)
        )
        self.year_entry.grid(column=1, row=0)
        self.year_entry.bind("<Return>", self._year_entry_submit)

        self.year_right_btn = ctk.CTkButton(
            self.tools_inner, text=">", width=35, command=self._year_increment,
            fg_color=BG_BUTTON, hover_color=BG_BUTTON_HOVER
        )
        self.year_right_btn.grid(column=2, row=0, padx=(10, 20))

        self.week_btn = ctk.CTkButton(
            self.tools_inner, text="Sun" if self.config.week_start == "sunday" else "Mon", width=70,
            command=self._toggle_week_start,
            fg_color=BG_BUTTON, hover_color=BG_BUTTON_HOVER
        )
        self.week_btn.grid(column=3, row=0, padx=(0, 20))

        self.clear_btn = ctk.CTkButton(
            self.tools_inner, text="Clear All", command=callbacks["clear_all"],
            fg_color=COLOR_RED, hover_color=COLOR_RED_HOVER, width=90
        )
        self.clear_btn.grid(column=4, row=0)

    def _choose_directory(self):
        import os
        directory = filedialog.askdirectory(
            initialdir=self.config.dir, title="Select Directory"
        )
        if directory:
            git_dir = os.path.join(directory, ".git")
            if os.path.exists(git_dir):
                if not messagebox.askyesno(
                    "Warning",
                    f"This directory already contains a git repository:\n\n{directory}\n\nGenerating will overwrite it. Continue?"
                ):
                    return
            self.config.dir = directory
            self.config.save()
            display_dir = directory if len(directory) < 40 else "..." + directory[-37:]
            self.dir_label.configure(text=display_dir)
            self.callbacks["on_dir_change"]()

    def _update_year(self, new_year):
        self.config.year = self.config.clamp_year(new_year)
        self.option_var.set(str(self.config.year))
        self.config.save()
        self.callbacks["on_year_change"]()

    def _year_decrement(self):
        self._update_year(self.config.year - 1)

    def _year_increment(self):
        self._update_year(self.config.year + 1)

    def _year_entry_submit(self, event=None):
        try:
            self._update_year(int(self.option_var.get()))
        except ValueError:
            self._update_year(self.config.year)

    def _toggle_week_start(self):
        self.config.week_start = "monday" if self.config.week_start == "sunday" else "sunday"
        self.week_btn.configure(text="Sun" if self.config.week_start == "sunday" else "Mon")
        self.config.save()
        self.callbacks["on_week_start_change"]()

    def set_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.button.configure(state=state)
        self.clear_btn.configure(state=state)
        self.dir_btn.configure(state=state)
        self.year_left_btn.configure(state=state)
        self.year_right_btn.configure(state=state)
        self.year_entry.configure(state=state)
        self.week_btn.configure(state=state)


class ContributionGrid(tk.Canvas):
    def __init__(self, master, config, dates_set, on_hover_cb):
        canvas_width = BOX_SIZE * 55 + BOX_GAP * 55 + LEFT_MARGIN
        canvas_height = BOX_SIZE * 7 + BOX_GAP * 7 + TOP_MARGIN
        super().__init__(
            master, width=canvas_width, height=canvas_height,
            bg=BG_PRIMARY, highlightthickness=0
        )
        self.config = config
        self.dates = dates_set
        self.on_hover_cb = on_hover_cb
        self.hovered_item = None
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.bind("<Button-1>", self._paint)
        self.bind("<B1-Motion>", self._paint)
        self.bind("<Button-3>", self._erase)
        self.bind("<B3-Motion>", self._erase)
        self.bind("<Motion>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def draw(self):
        self.delete("all")
        year = self.config.year

        day_labels = ["Mon", "Wed", "Fri"]
        day_y_offsets = [1, 3, 5] if self.config.week_start == "sunday" else [0, 2, 4]

        for day, offset in zip(day_labels, day_y_offsets):
            y = TOP_MARGIN + BOX_GAP + offset * (BOX_SIZE + BOX_GAP) + BOX_SIZE / 2
            self.create_text(
                LEFT_MARGIN - 5, y, text=day, fill=TEXT_MUTED, anchor="e", font=("Arial", 10)
            )

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        current_month = -1

        year_date = dt.datetime(year=year, month=1, day=1)
        day_delta = dt.timedelta(days=1)
        counter = 0

        start = (year_date.weekday() + 1) % 7 if self.config.week_start == "sunday" else year_date.weekday()

        for x in range(LEFT_MARGIN + BOX_GAP, self.canvas_width, BOX_SIZE + BOX_GAP):
            for y in range(TOP_MARGIN + BOX_GAP, self.canvas_height, BOX_SIZE + BOX_GAP):
                counter += 1
                if counter <= start:
                    self.create_rectangle(x, y, x + BOX_SIZE, y + BOX_SIZE, fill=BG_PRIMARY, outline=BG_PRIMARY, width=1)
                elif year_date.year == year:
                    if year_date.month != current_month:
                        self.create_text(
                            x, TOP_MARGIN - 5, text=month_names[year_date.month - 1],
                            fill=TEXT_MUTED, anchor="w", font=("Arial", 10)
                        )
                        current_month = year_date.month

                    date_str = year_date.strftime("%Y-%m-%d")
                    color = COLOR_PAINTED if date_str in self.dates else BG_SECONDARY
                    self.create_rectangle(
                        x, y, x + BOX_SIZE, y + BOX_SIZE, fill=color, outline=BG_PRIMARY, width=1, tags=(date_str, "day")
                    )
                    year_date += day_delta

    def _item_at_point(self, x, y):
        item = self.find_closest(x, y)
        if not item or not self.bbox(item[0]):
            return None
        x1, y1, x2, y2 = self.bbox(item[0])
        return item[0] if x1 <= x <= x2 and y1 <= y <= y2 else None

    def _paint(self, event):
        item_id = self._item_at_point(event.x, event.y)
        if item_id and "day" in self.gettags(item_id):
            self.itemconfig(item_id, fill=COLOR_PAINTED)
            self.dates.add(self.gettags(item_id)[0])

    def _erase(self, event):
        item_id = self._item_at_point(event.x, event.y)
        if item_id and "day" in self.gettags(item_id):
            self.itemconfig(item_id, fill=BG_SECONDARY)
            self.dates.discard(self.gettags(item_id)[0])

    def _on_hover(self, event):
        if event.state & 0x0100 or event.state & 0x0400: return # Skip if drawing

        item_id = self._item_at_point(event.x, event.y)

        if self.hovered_item and self.hovered_item != item_id:
            try:
                tags = self.gettags(self.hovered_item)
                if "day" in tags:
                    self.itemconfig(self.hovered_item, fill=COLOR_PAINTED if tags[0] in self.dates else BG_SECONDARY)
            except tk.TclError:
                pass

        if item_id and "day" in self.gettags(item_id):
            tags = self.gettags(item_id)
            if tags[0] not in self.dates:
                self.itemconfig(item_id, fill=COLOR_HOVER)
            self.hovered_item = item_id
            self.on_hover_cb(tags[0])
        else:
            self.hovered_item = None
            self.on_hover_cb(None)

    def _on_leave(self, event):
        if self.hovered_item:
            try:
                tags = self.gettags(self.hovered_item)
                if "day" in tags:
                    self.itemconfig(self.hovered_item, fill=COLOR_PAINTED if tags[0] in self.dates else BG_SECONDARY)
            except tk.TclError:
                pass
            self.hovered_item = None
        self.on_hover_cb(None)
