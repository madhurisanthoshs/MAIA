def clear_screen(master):
    """Clears all widgets from the given master widget."""
    for widget in master.winfo_children():
        widget.destroy()
