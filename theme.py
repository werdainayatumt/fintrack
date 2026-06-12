"""Centralized design system: color palette, fonts, and ttk styles.

Keeping every visual token in one place means all screens share a
consistent look and a single edit re-themes the whole app.
"""
from tkinter import ttk

# --- Palette (dark, deliberate accents rather than default greys) ----------
COLORS = {
    "bg":           "#0f1419",  # window background
    "surface":      "#1a2129",  # cards / panels
    "surface_alt":  "#232b35",  # inputs, hover, track backgrounds
    "sidebar":      "#141a21",
    "primary":      "#4f9eff",  # accent blue
    "primary_dark": "#3b7fd4",
    "success":      "#3ecf8e",  # income / positive
    "danger":       "#ff5d5d",  # expense / over-budget
    "warning":      "#f5b945",
    "text":         "#e6edf3",
    "text_muted":   "#8b98a5",
    "border":       "#2d3640",
}

FONTS = {
    "title":   ("Segoe UI Semibold", 20),
    "heading": ("Segoe UI Semibold", 14),
    "subhead": ("Segoe UI Semibold", 11),
    "body":    ("Segoe UI", 10),
    "small":   ("Segoe UI", 9),
    "metric":  ("Segoe UI Semibold", 22),
}


def apply_theme(root):
    """Configure ttk styles and base options on the root window."""
    c = COLORS
    style = ttk.Style(root)
    style.theme_use("clam")
    root.configure(bg=c["bg"])

    style.configure(".", background=c["bg"], foreground=c["text"],
                    fieldbackground=c["surface"], bordercolor=c["border"],
                    font=FONTS["body"])

    # Frames
    style.configure("TFrame", background=c["bg"])
    style.configure("Surface.TFrame", background=c["surface"])
    style.configure("Sidebar.TFrame", background=c["sidebar"])

    # Labels
    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["text_muted"])
    style.configure("Title.TLabel", background=c["bg"], foreground=c["text"],
                    font=FONTS["title"])
    style.configure("Surface.TLabel", background=c["surface"], foreground=c["text"])
    style.configure("SurfaceMuted.TLabel", background=c["surface"],
                    foreground=c["text_muted"])
    style.configure("Sidebar.TLabel", background=c["sidebar"], foreground=c["text"])
    style.configure("Heading.TLabel", background=c["surface"], foreground=c["text"],
                    font=FONTS["heading"])
    style.configure("Metric.TLabel", background=c["surface"], foreground=c["text"],
                    font=FONTS["metric"])

    # Buttons
    style.configure("TButton", background=c["surface_alt"], foreground=c["text"],
                    borderwidth=0, focuscolor=c["surface_alt"], padding=(12, 8))
    style.map("TButton", background=[("active", c["border"]), ("pressed", c["border"])])

    style.configure("Accent.TButton", background=c["primary"], foreground="#ffffff",
                    borderwidth=0, padding=(14, 9), font=FONTS["subhead"])
    style.map("Accent.TButton",
              background=[("active", c["primary_dark"]), ("pressed", c["primary_dark"])])

    style.configure("Danger.TButton", background=c["danger"], foreground="#ffffff",
                    borderwidth=0, padding=(10, 7))
    style.map("Danger.TButton", background=[("active", "#e04848")])

    # Sidebar navigation buttons
    style.configure("Nav.TButton", background=c["sidebar"], foreground=c["text_muted"],
                    borderwidth=0, anchor="w", padding=(18, 12), font=FONTS["subhead"])
    style.map("Nav.TButton", background=[("active", c["surface"])],
              foreground=[("active", c["text"])])
    style.configure("NavActive.TButton", background=c["surface"], foreground=c["primary"],
                    borderwidth=0, anchor="w", padding=(18, 12), font=FONTS["subhead"])

    # Entry
    style.configure("TEntry", fieldbackground=c["surface_alt"], foreground=c["text"],
                    bordercolor=c["border"], insertcolor=c["text"], padding=6)

    # Combobox (incl. read-only field + dropdown list)
    style.configure("TCombobox", fieldbackground=c["surface_alt"], foreground=c["text"],
                    background=c["surface_alt"], arrowcolor=c["text"], padding=6,
                    bordercolor=c["border"])
    style.map("TCombobox",
              fieldbackground=[("readonly", c["surface_alt"])],
              foreground=[("readonly", c["text"])],
              selectbackground=[("readonly", c["surface_alt"])],
              selectforeground=[("readonly", c["text"])])
    root.option_add("*TCombobox*Listbox.background", c["surface_alt"])
    root.option_add("*TCombobox*Listbox.foreground", c["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", c["primary_dark"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    # Radiobutton
    style.configure("TRadiobutton", background=c["surface"], foreground=c["text"],
                    focuscolor=c["surface"], indicatorcolor=c["surface_alt"])
    style.map("TRadiobutton", background=[("active", c["surface"])],
              foreground=[("active", c["text"])],
              indicatorcolor=[("selected", c["primary"])])

    # Treeview
    style.configure("Treeview", background=c["surface"], fieldbackground=c["surface"],
                    foreground=c["text"], borderwidth=0, rowheight=30)
    style.configure("Treeview.Heading", background=c["surface_alt"],
                    foreground=c["text_muted"], borderwidth=0, font=FONTS["subhead"],
                    padding=8)
    style.map("Treeview.Heading", background=[("active", c["border"])])
    style.map("Treeview", background=[("selected", c["primary_dark"])],
              foreground=[("selected", "#ffffff")])

    # Scrollbar
    style.configure("Vertical.TScrollbar", background=c["surface_alt"],
                    troughcolor=c["bg"], bordercolor=c["bg"],
                    arrowcolor=c["text_muted"], borderwidth=0)
    style.map("Vertical.TScrollbar", background=[("active", c["border"])])

    return style
