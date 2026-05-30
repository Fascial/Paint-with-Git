# <img src="assets/logo.png" width="30" height="30" align="center"> Paint with Git

Draw pixel art on your GitHub contribution graph.

Pick a year, paint your design on the grid, hit **Generate**, and push the result to GitHub. Your profile will display your artwork.

<p align="center">
  <img src="assets/ui_screenshot.png" alt="App UI" width="100%">
</p>

---

## Usage

### Step 1: Getting Started

1. **Download this project** and open the folder.
2. **Install Python & Git** if you don't have them already:
   - [Download Python](https://www.python.org/downloads/)
   - [Download Git](https://git-scm.com/downloads)
3. **Launch the App!**
   - **Windows:** Just double-click the `run.bat` file!
   - **Mac/Linux:** Open a terminal in this folder and type: `chmod +x run.sh && ./run.sh`

### Step 2: Draw Your Masterpiece

- **Left-Click (or drag):** Paint a green square.
- **Right-Click (or drag):** Erase a square.
- **Change Year:** Use the `<` and `>` arrows at the bottom to pick which year you want to paint on.
- _Tip: Don't worry about breaking anything! This is completely safe and won't mess up your actual real code contributions._

### Step 3: Put it on GitHub!

1. Click the big **Generate** button in the app.
2. Click the **Go to output** button. This will automatically pop open your computer's file explorer and highlight a folder called `paintwithgit`.
3. Go to [github.com](https://github.com/new) and **Create a new repository**.
   - _Important:_ You can name it whatever you want, but make sure to set it to **Private** so it doesn't clutter your public repositories! (Don't worry, your green squares will still show up on your public profile).
4. Right-click inside that `paintwithgit` folder you just opened and select **Open in Terminal** (or Open Git Bash here).
5. Copy and paste these two commands into the terminal (make sure to replace the link with your new repo's link!):
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-NEW-REPO.git
   git push -u origin main -f
   ```
6. Go check your GitHub profile page. Boom! Your art is on your graph!

<p align="center">
  <img src="assets/github_chart.png" alt="GitHub Chart" width="100%">
</p>

### How to Edit or Remove it later?

- **To edit it:** Just open the app again, change your drawing, click **Generate**, and type `git push -f` in that same terminal.
- **To delete it completely:** Just go to GitHub and delete the private repository you created. Your graph will instantly go back to normal.

---

## Project Structure

```
Paint with Git/
├── src/
│   ├── ui.py              # Application GUI
│   ├── components.py      # Custom UI components
│   ├── config.py          # State and constants
│   └── git_processor.py   # Fast-import commit engine
├── assets/                # Images & icons
├── run.bat                # Windows launcher
├── run.sh                 # Linux/macOS launcher
└── pyproject.toml         # Dependencies
```
