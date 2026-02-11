import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import json
from pathlib import Path


class GitManagerModule:
    """Module to manage git repositories with custom tasks."""

    name = "Git Manager"
    
    # Git-themed dark theme
    THEME = {
        "name": "Git Dark",
        "bg_color": "#0d1117",
        "fg_color": "#58a6ff",
        "accent_color": "#238636",
        "secondary_bg": "#161b22"
    }

    # Config file location
    CONFIG_DIR = Path.home() / ".config" / "qt_git_manager"
    CONFIG_FILE = CONFIG_DIR / "tasks.json"

    def __init__(
        self,
        app,
        bg_color="#ffffff",
        fg_color="#000000"
    ):
        """
        Initialize the Git Manager module.

        Args:
            app: Reference to the main App instance.
            bg_color: Background color for the module.
            fg_color: Foreground color for the module.
        """
        self.app = app
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.tasks = []
        self.repos_frame = None

        # Ensure config directory exists
        self._ensure_config_dir()

        # Load saved tasks on initialization
        self._load_tasks()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_tasks(self):
        """Load tasks from the config file."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    self.tasks = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.tasks = []

    def _save_tasks(self):
        """Save tasks to the config file."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.tasks, f, indent=2)
        except IOError:
            pass

    def build(self, parent):
        """Build the Git Manager UI."""
        # Clear existing content
        for widget in parent.winfo_children():
            widget.destroy()

        # Configure parent background
        parent.configure(bg=self.bg_color)

        # --- Repositories Display Section ---
        repos_label = tk.Label(
            parent,
            text="Repositories:",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w"
        )
        repos_label.pack(fill="x", padx=10, pady=(10, 5))

        self.repos_frame = tk.Frame(parent, bg=self.bg_color)
        self.repos_frame.pack(fill="x", padx=10, pady=(0, 5))

        # --- Add Task Button ---
        add_btn = tk.Button(
            parent,
            text="+ Add Task",
            font=("Helvetica", 11, "bold"),
            command=self._show_add_task_dialog,
            cursor="hand2",
            bg="#27ae60",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=5
        )
        add_btn.pack(anchor="w", padx=10, pady=(15, 5))

        # --- Tasks Section ---
        tasks_label = tk.Label(
            parent,
            text="Tasks:",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor="w"
        )
        tasks_label.pack(fill="x", padx=10, pady=(15, 5))

        self.tasks_frame = tk.Frame(parent, bg=self.bg_color)
        self.tasks_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Canvas with scrollbar for tasks
        self.canvas = tk.Canvas(self.tasks_frame, bg=self.bg_color)
        self.scrollbar = tk.Scrollbar(
            self.tasks_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollable_tasks = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_tasks.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.scrollable_tasks,
            anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", expand=True, fill="both")

        # Create buttons for all loaded tasks
        self._recreate_all_task_buttons()

        # Display repositories for first task if available
        if self.tasks:
            self._display_task_repos(self.tasks[0])

    def _show_add_task_dialog(self):
        """Show a dialog to add a new task."""
        dialog = tk.Toplevel(
            self.app.root if hasattr(self.app, 'root') else None
        )
        dialog.title("Add New Task")
        dialog.transient(self.app.root if hasattr(self.app, 'root') else None)
        dialog.grab_set()
        dialog.resizable(False, False)

        parent_x = self.app.root.winfo_x() if hasattr(self.app, 'root') else 0
        parent_y = self.app.root.winfo_y() if hasattr(self.app, 'root') else 0
        dialog.geometry("+{}+{}".format(parent_x + 200, parent_y + 100))

        main_frame = tk.Frame(dialog, bg="#ecf0f1", padx=20, pady=20)
        main_frame.pack()

        # --- Name Input ---
        tk.Label(
            main_frame,
            text="Task Name:",
            font=("Helvetica", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 2))

        name_entry = tk.Entry(main_frame, font=("Helvetica", 10), width=50)
        name_entry.pack(pady=(0, 10))

        # --- Root Path Input ---
        tk.Label(
            main_frame,
            text="Root Path (git repositories):",
            font=("Helvetica", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 2))

        root_frame = tk.Frame(main_frame, bg="#ecf0f1")
        root_frame.pack(fill="x", pady=(0, 10))

        root_entry = tk.Entry(root_frame, font=("Helvetica", 10), width=42)
        root_entry.pack(side="left")

        def browse_root():
            directory = filedialog.askdirectory(
                title="Select Root Path",
                parent=dialog
            )
            if directory:
                root_entry.delete(0, tk.END)
                root_entry.insert(0, directory)

        tk.Button(
            root_frame,
            text="Browse",
            font=("Helvetica", 9),
            command=browse_root,
            cursor="hand2",
            bg="#3498db",
            fg="#ffffff",
            relief="flat"
        ).pack(side="left", padx=(5, 0))

        # --- Script Path Input (Optional) ---
        tk.Label(
            main_frame,
            text="Script Path (optional):",
            font=("Helvetica", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(anchor="w", pady=(0, 2))

        script_frame = tk.Frame(main_frame, bg="#ecf0f1")
        script_frame.pack(fill="x", pady=(0, 15))

        script_entry = tk.Entry(script_frame, font=("Helvetica", 10), width=42)
        script_entry.pack(side="left")

        def browse_script():
            file_path = filedialog.askopenfilename(
                title="Select Script",
                parent=dialog,
                filetypes=[
                    ("All Files", "*.*"),
                    ("Python Scripts", "*.py"),
                    ("Shell Scripts", "*.sh")
                ]
            )
            if file_path:
                script_entry.delete(0, tk.END)
                script_entry.insert(0, file_path)

        tk.Button(
            script_frame,
            text="Browse",
            font=("Helvetica", 9),
            command=browse_script,
            cursor="hand2",
            bg="#3498db",
            fg="#ffffff",
            relief="flat"
        ).pack(side="left", padx=(5, 0))

        # --- Buttons ---
        btn_frame = tk.Frame(main_frame, bg="#ecf0f1")
        btn_frame.pack(pady=(10, 0))

        def add_task():
            name = name_entry.get().strip()
            root_path = root_entry.get().strip()
            script_path = script_entry.get().strip()

            # Validate inputs
            if not name:
                messagebox.showwarning(
                    "Validation Error",
                    "Please enter a name for the task.",
                    parent=dialog
                )
                return

            if not root_path:
                messagebox.showwarning(
                    "Validation Error",
                    "Please select a root path.",
                    parent=dialog
                )
                return

            if not os.path.exists(root_path):
                messagebox.showwarning(
                    "Validation Error",
                    "Root path does not exist.",
                    parent=dialog
                )
                return

            # Validate script path if provided
            if script_path and not os.path.exists(script_path):
                messagebox.showwarning(
                    "Validation Error",
                    "Script path does not exist.",
                    parent=dialog
                )
                return

            # Find ALL git repositories in root path
            git_repos = self._find_all_git_repositories(root_path)

            if not git_repos:
                messagebox.showwarning(
                    "No Git Repository",
                    "No git repositories found in:\n" + root_path,
                    parent=dialog
                )
                return

            # Store task data with all repositories
            task_data = {
                "name": name,
                "root_path": root_path,
                "script_path": script_path if script_path else None,
                "git_repos": git_repos
            }

            self.tasks.append(task_data)
            self._save_tasks()

            task_index = len(self.tasks) - 1
            self._create_task_button(task_data, task_index)
            self._display_task_repos(task_data)

            dialog.destroy()

        tk.Button(
            btn_frame,
            text="Add Task",
            font=("Helvetica", 10, "bold"),
            command=add_task,
            cursor="hand2",
            bg="#27ae60",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=5
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Helvetica", 10),
            command=dialog.destroy,
            cursor="hand2",
            bg="#e74c3c",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=5
        ).pack(side="left")

        dialog.wait_window()

    def _find_all_git_repositories(self, root_path):
        """Find all git repositories in the given root path."""
        repos = []
        found_paths = set()

        def search_directory(path, depth=0):
            if depth > 3:
                return

            try:
                for item in os.listdir(path):
                    if item.startswith("."):
                        continue

                    item_path = os.path.join(path, item)

                    if os.path.isdir(item_path):
                        git_path = os.path.join(item_path, ".git")

                        if os.path.isdir(git_path) and item_path not in found_paths:
                            found_paths.add(item_path)
                            branch = self._get_branch_name(item_path)

                            repos.append({
                                "path": item_path,
                                "name": item,
                                "branch": branch
                            })

                        search_directory(item_path, depth + 1)

            except PermissionError:
                pass

        search_directory(root_path)
        return repos

    def _display_task_repos(self, task_data):
        """Display repositories for a specific task."""
        # Clear existing widgets
        for widget in self.repos_frame.winfo_children():
            widget.destroy()

        repos = task_data.get("git_repos", [])

        if not repos:
            tk.Label(
                self.repos_frame,
                text="No repositories found.",
                font=("Helvetica", 10),
                bg=self.bg_color,
                fg="#7f8c8d",
                anchor="w"
            ).pack(anchor="w", pady=5)
            return

        # Create labels for each repository
        for repo in repos:
            repo_text = " - ".join([repo["name"], repo["branch"]])

            tk.Label(
                self.repos_frame,
                text=repo_text,
                font=("Helvetica", 10),
                bg=self.bg_color,
                fg="#2980b9",
                anchor="w"
            ).pack(anchor="w", pady=1)

    def _get_branch_name(self, repo_path):
        """Get the current branch name of a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()

            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return "detached-" + result.stdout.strip()

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        return "Unknown"

    def _recreate_all_task_buttons(self):
        """Clear and recreate all task buttons."""
        for widget in self.scrollable_tasks.winfo_children():
            widget.destroy()

        for idx, task_data in enumerate(self.tasks):
            self._create_task_button(task_data, idx)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _create_task_button(self, task_data, task_index):
        """Create a button for a task."""
        btn_frame = tk.Frame(self.scrollable_tasks, bg=self.bg_color)
        btn_frame.pack(fill="x", pady=2)

        repo_count = len(task_data.get("git_repos", []))
        has_script = task_data.get("script_path") is not None
        script_text = " (script)" if has_script else ""
        btn_text = task_data["name"] + " (" + str(repo_count) + " repos)" + script_text

        tk.Button(
            btn_frame,
            text=btn_text,
            font=("Helvetica", 10),
            command=lambda t=task_data: self._launch_task(t),
            cursor="hand2",
            bg="#3498db",
            fg="#ffffff",
            relief="flat",
            anchor="w",
            padx=10
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            btn_frame,
            text="x",
            font=("Helvetica", 12, "bold"),
            command=lambda: self._delete_task(task_index, btn_frame),
            cursor="hand2",
            bg="#e74c3c",
            fg="#ffffff",
            relief="flat",
            padx=8,
            pady=2
        ).pack(side="left", padx=(2, 0))

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _delete_task(self, task_index, btn_frame):
        """Delete a task."""
        if messagebox.askyesno("Delete Task", "Delete this task?"):
            self.tasks.pop(task_index)
            self._save_tasks()
            btn_frame.destroy()
            self._recreate_all_task_buttons()

            # Show repos for first remaining task or clear
            if self.tasks:
                self._display_task_repos(self.tasks[0])
            else:
                self._clear_repos_display()

    def _clear_repos_display(self):
        """Clear the repositories display."""
        for widget in self.repos_frame.winfo_children():
            widget.destroy()

    def _launch_task(self, task_data):
        """Launch the task and display repository info."""
        repos = task_data.get("git_repos", [])
        script_path = task_data.get("script_path")

        # Update repository display
        self._display_task_repos(task_data)

        # Only execute script if one is provided
        if script_path and os.path.exists(script_path):
            self._execute_script(task_data, repos)

    def _execute_script(self, task_data, repos):
        """Execute the script and display results."""
        script_path = task_data["script_path"]
        script_dir = os.path.dirname(script_path)
        script_name = os.path.basename(script_path)

        try:
            result = subprocess.run(
                [script_path],
                cwd=script_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout
            error = result.stderr

            if result.returncode == 0:
                status = "OK"
            else:
                status = "Error: " + str(result.returncode)

            # Build output text
            repo_names = ", ".join(r["name"] for r in repos)
            output_text = "Repo: " + repo_names + " | " + status
            if output:
                output_text = output_text + "\n\n" + output
            if error:
                output_text = output_text + "\n\nError:\n" + error

            # Show result in a dialog
            messagebox.showinfo("Script Result", output_text)

        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Script execution timed out (60s)")

        except Exception as e:
            messagebox.showerror("Error", "Error executing script: " + str(e))

