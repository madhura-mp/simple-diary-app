import tkinter as tk
from tkinter import messagebox
import os
import sys
import datetime

# ── Setup ──────────────────────────────────────────────────
# Always store entries next to this program, regardless of the folder
# the terminal happened to be in when it was launched, AND regardless
# of whether this is running as a plain .py script or as a PyInstaller
# .exe (a bundled --onefile exe unpacks to a temp folder at runtime,
# so __file__ there points to that temp folder, not the real exe
# location — sys.executable is the one that's reliable when frozen).
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIARY_DIR = os.path.join(BASE_DIR, "diary_entries")

def ensure_dir():
    if not os.path.exists(DIARY_DIR):
        os.makedirs(DIARY_DIR)

def list_entries():
    ensure_dir()
    files = sorted([f for f in os.listdir(DIARY_DIR) if f.endswith(".txt")], reverse=True)
    return files

def read_entry(filename):
    with open(os.path.join(DIARY_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

def save_entry(filename, content):
    with open(os.path.join(DIARY_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

def sanitize_title(title):
    return "".join(c if c.isalnum() or c == " " else "_" for c in title).strip()

def get_title_from_filename(filename):
    name = filename[:-4]
    parts = name.split("__", 1)
    return parts[1].replace("_", " ") if len(parts) > 1 else name

def get_date_from_filename(filename):
    return filename[:10]

# ── App ────────────────────────────────────────────────────
class DiaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NOVA-capture your thoughts")
        self.root.geometry("900x600")
        self.root.configure(bg="#FFF0E6")
        self.selected_file = None
        ensure_dir()
        self.build()
        self.refresh_list()

    def build(self):
        # Top bar
        top = tk.Frame(self.root, bg="#FF6B9D", height=50)
        top.pack(fill="x")
        tk.Label(top, text="📔  NOVA-capture your thoughts", font=("Georgia", 18, "bold"),
                 bg="#FF6B9D", fg="white").pack(side="left", padx=20, pady=8)
        tk.Label(top, text=datetime.datetime.now().strftime("%d %B %Y"),
                 font=("Helvetica", 10), bg="#FF6B9D", fg="#FFE0EE").pack(side="right", padx=20)

        # Main
        main = tk.Frame(self.root, bg="#FFF0E6")
        main.pack(fill="both", expand=True)

        # Sidebar
        side = tk.Frame(main, bg="#FFE4C8", width=220)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(side, text="MY ENTRIES", font=("Helvetica", 9, "bold"),
                 bg="#FFE4C8", fg="#8B6B5A").pack(anchor="w", padx=12, pady=(12,4))

        tk.Button(side, text="+ New Entry", command=self.new_entry,
                  font=("Helvetica", 11, "bold"), bg="#FF6B9D", fg="white",
                  relief="flat", pady=8, cursor="hand2").pack(fill="x", padx=10, pady=(0,8))

        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_list())
        tk.Entry(side, textvariable=self.search_var, font=("Helvetica", 10),
                 bg="white", relief="flat").pack(fill="x", padx=10, pady=(0,8), ipady=5)

        # Listbox
        self.listbox = tk.Listbox(side, font=("Helvetica", 10), bg="white",
                                  fg="#3D2B1F", selectbackground="#FF6B9D",
                                  selectforeground="white", relief="flat",
                                  highlightthickness=0, cursor="hand2")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Right panel
        right = tk.Frame(main, bg="#FFF0E6")
        right.pack(side="left", fill="both", expand=True, padx=16, pady=10)

        # Title
        trow = tk.Frame(right, bg="#FFF0E6")
        trow.pack(fill="x", pady=(0,6))
        tk.Label(trow, text="Title:", font=("Helvetica", 11, "bold"),
                 bg="#FFF0E6", fg="#8B6B5A").pack(side="left")
        self.title_var = tk.StringVar()
        tk.Entry(trow, textvariable=self.title_var, font=("Georgia", 13, "bold"),
                 bg="white", fg="#C084FC", relief="flat",
                 insertbackground="#C084FC").pack(side="left", fill="x",
                 expand=True, padx=8, ipady=5)

        # Buttons
        brow = tk.Frame(right, bg="#FFF0E6")
        brow.pack(fill="x", pady=(0,8))

        tk.Button(brow, text="💾 Save", command=self.save,
                  font=("Helvetica", 10, "bold"), bg="#34D399", fg="white",
                  relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=(0,6))

        tk.Button(brow, text="➕ Add to Entry", command=self.append_entry,
                  font=("Helvetica", 10, "bold"), bg="#60A5FA", fg="white",
                  relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=(0,6))

        tk.Button(brow, text="🗑 Delete", command=self.delete_entry,
                  font=("Helvetica", 10, "bold"), bg="#FF4757", fg="white",
                  relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left")

        self.date_label = tk.Label(brow, text="", font=("Helvetica", 9),
                                   bg="#FFF0E6", fg="#8B6B5A")
        self.date_label.pack(side="right")

        # Text area
        self.text = tk.Text(right, font=("Georgia", 12), bg="white",
                            fg="#3D2B1F", relief="flat", wrap="word",
                            padx=16, pady=12, insertbackground="#FF6B9D")
        self.text.pack(fill="both", expand=True)

        # Status
        self.status = tk.StringVar(value="✨ Ready to write!")
        tk.Label(right, textvariable=self.status, font=("Helvetica", 9),
                 bg="#FFE4C8", fg="#8B6B5A", anchor="w",
                 padx=10, pady=4).pack(fill="x")

    def refresh_list(self):
        query = self.search_var.get().lower() if hasattr(self, "search_var") else ""
        self.listbox.delete(0, "end")
        self._files = []
        for fn in list_entries():
            title = get_title_from_filename(fn)
            date = get_date_from_filename(fn)
            if query and query not in title.lower() and query not in date:
                continue
            self.listbox.insert("end", f"  {title}  [{date}]")
            self._files.append(fn)
        if not self._files:
            self.listbox.insert("end", "  No entries yet...")

    def on_select(self, event):
        sel = self.listbox.curselection()
        if not sel or not self._files or sel[0] >= len(self._files):
            return
        fn = self._files[sel[0]]
        self.selected_file = fn
        content = read_entry(fn)
        title = get_title_from_filename(fn)
        date = get_date_from_filename(fn)
        self.title_var.set(title)
        self.date_label.config(text=f"📅 {date}")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.status.set(f"📖 Reading: {title}")

    def new_entry(self):
        self.selected_file = None
        self.title_var.set("")
        self.text.delete("1.0", "end")
        self.date_label.config(text=f"📅 {datetime.datetime.now().strftime('%Y-%m-%d')}")
        self.status.set("✏️ Writing new entry...")
        self.text.focus_set()

    def save(self):
        title = self.title_var.get().strip()
        content = self.text.get("1.0", "end").strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title!")
            return
        if not content:
            messagebox.showwarning("Empty", "Please write something!")
            return
        safe_title = sanitize_title(title)
        if self.selected_file:
            # Keep the original date/time prefix, but rename the file if the
            # title changed (title used to be silently ignored on edit).
            prefix = self.selected_file.split("__", 1)[0]
            new_filename = f"{prefix}__{safe_title}.txt"
            if new_filename != self.selected_file:
                old_path = os.path.join(DIARY_DIR, self.selected_file)
                if os.path.exists(old_path):
                    os.remove(old_path)
                self.selected_file = new_filename
            save_entry(self.selected_file, content)
        else:
            now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"{now}__{safe_title}.txt"
            save_entry(filename, content)
            self.selected_file = filename
        self.status.set(f"✅ Saved: {title}")
        self.refresh_list()

    def append_entry(self):
        if not self.selected_file:
            messagebox.showinfo("Select Entry", "Please select an entry first!")
            return
        existing = read_entry(self.selected_file)
        new_content = self.text.get("1.0", "end").strip()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        updated = existing + f"\n\n--- Added on {now} ---\n" + new_content
        save_entry(self.selected_file, updated)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", updated)
        self.status.set("➕ Content added!")

    def delete_entry(self):
        if not self.selected_file:
            messagebox.showinfo("Select Entry", "Please select an entry to delete!")
            return
        title = get_title_from_filename(self.selected_file)
        if messagebox.askyesno("Delete", f"Delete '{title}'? Cannot be undone!"):
            os.remove(os.path.join(DIARY_DIR, self.selected_file))
            self.selected_file = None
            self.title_var.set("")
            self.text.delete("1.0", "end")
            self.status.set("🗑 Deleted!")
            self.refresh_list()

# ── Launch ─────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = DiaryApp(root)
    root.mainloop()
