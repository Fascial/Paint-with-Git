import os
import sys
import threading
import subprocess
import datetime as dt
import customtkinter as ctk

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("fascial.paintwithgit.ui.1.0")
    except Exception:
        pass

from src.config import Config, BG_PRIMARY, BG_SECONDARY, TEXT_MUTED, COLOR_PAINTED, COLOR_RED_HOVER, TEXT_PRIMARY, COLOR_GEN
from src.components import ControlPanel, ContributionGrid
import src.git_processor as git_processor

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("1650x550")
        self.minsize(1600, 500)
        self.title("Paint with Git")
        self.configure(fg_color=BG_PRIMARY)

        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.ico")
        if os.path.exists(icon_path):
            try:
                self.wm_iconbitmap(icon_path)
            except Exception:
                pass

        self.config = Config()
        self.dates = set()
        
        self.load_existing_commits()

        callbacks = {
            "on_dir_change": self._on_dir_change,
            "on_year_change": self._redraw,
            "on_week_start_change": self._redraw,
            "clear_all": self.clear_all,
            "generate": self.generate,
        }

        self.control_panel = ControlPanel(self, self.config, callbacks)
        self.control_panel.pack(pady=20, padx=20, fill="x")

        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(expand=True, fill="both", pady=10)
        
        self.contribution_grid = ContributionGrid(self.grid_frame, self.config, self.dates, self._on_grid_hover)
        self.contribution_grid.pack(expand=True)
        self.contribution_grid.draw()

        self.date_label = ctk.CTkLabel(self, text="", text_color=TEXT_MUTED, font=("Arial", 11))
        self.date_label.pack(pady=(0, 2))

        self.status_label = ctk.CTkLabel(self, text="", text_color=TEXT_MUTED, font=("Arial", 12))
        self.status_label.pack(pady=(0, 5))

        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", width=300, fg_color=BG_SECONDARY, progress_color=COLOR_GEN)
        self.progress.set(0)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.config.save()
        self.destroy()

    def load_existing_commits(self):
        self.dates.clear()
        if hasattr(self, 'contribution_grid'):
            self.contribution_grid.draw()
            
        def _load_task():
            new_dates = set()
            if os.path.exists(os.path.join(self.config.dir, ".git")):
                try:
                    kwargs = {}
                    if sys.platform == "win32":
                        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                        
                    result = subprocess.run(
                        ["git", "log", "--format=%ad", "--date=short"],
                        cwd=self.config.dir, capture_output=True, text=True, **kwargs
                    )
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            new_dates.add(line)
                except Exception:
                    pass
            self.after(0, lambda: self._apply_loaded_commits(new_dates))
            
        threading.Thread(target=_load_task, daemon=True).start()

    def _apply_loaded_commits(self, new_dates):
        self.dates.clear()
        self.dates.update(new_dates)
        if hasattr(self, 'contribution_grid'):
            self._redraw()

    def _on_dir_change(self):
        self.load_existing_commits()
        self._redraw()

    def _redraw(self):
        self.contribution_grid.draw()

    def clear_all(self):
        year_str = str(self.config.year)
        self.dates.difference_update({d for d in self.dates if d.startswith(year_str)})
        self._redraw()

    def _on_grid_hover(self, date_str):
        if date_str:
            try:
                d = dt.datetime.strptime(date_str, "%Y-%m-%d")
                self.date_label.configure(text=d.strftime("%A, %b %d %Y"))
            except ValueError:
                self.date_label.configure(text="")
        else:
            self.date_label.configure(text="")

    def generate(self):
        self.control_panel.button.configure(text="Generating...")
        self.control_panel.set_enabled(False)
        self.status_label.configure(text="Creating commits...", text_color=TEXT_PRIMARY)
        
        self.progress.pack(pady=(0, 10))
        self.progress.start()

        dates_list = sorted(self.dates)
        target_dir = self.config.dir

        def run():
            try:
                import time
                time.sleep(0.6) # Minimum delay to show the sleek progress bar
                msg = git_processor.main(target_dir, dates_list)
                self.after(0, lambda: self._on_generate_done(True, msg))
            except Exception as e:
                self.after(0, lambda: self._on_generate_done(False, str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _on_generate_done(self, success, message):
        self.progress.stop()
        self.progress.pack_forget()
        
        self.control_panel.button.configure(text="Generate")
        self.control_panel.set_enabled(True)
        if success:
            self.status_label.configure(text=f"[OK] {message}", text_color=COLOR_PAINTED)
        else:
            self.status_label.configure(text=f"[FAIL] {message}", text_color=COLOR_RED_HOVER)

def main():
    ctk.deactivate_automatic_dpi_awareness()
    App().mainloop()

if __name__ == "__main__":
    main()
