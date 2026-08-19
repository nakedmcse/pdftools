from pypdf import PdfReader, PdfWriter
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Globals
reader = None

# Load PDF
def load_pdf():
    global reader
    file_path = filedialog.askopenfilename(
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        try:
            reader = PdfReader(file_path)
            fields = reader.get_fields() or {}
            info_label = pane.nametowidget("info").nametowidget("info_label")
            pages_entry = pane.nametowidget("controls").nametowidget("pages_entry")
            output_text = pane.nametowidget("output").nametowidget("output_text")
            info_label.configure(text=f"{Path(file_path).stem}: {len(reader.pages)} pages and {len(fields)} fields")
            pages_entry.delete(0, tk.END)
            for p in range(len(reader.pages)):
                pages_entry.insert(tk.END, f"{p+1},")
            pages_entry.delete(len(pages_entry.get())-1,tk.END)
            output_text.configure(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            for name, field in fields.items():
                output_text.insert(tk.END, f"{name} {field.get('/FT')}\n")
            output_text.configure(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

# Save PDF
def save_pdf():
    global reader
    if reader is None:
        return
    file_path = filedialog.asksaveasfilename(
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        try:
            writer = PdfWriter()
            pages_entry = pane.nametowidget("controls").nametowidget("pages_entry")
            pages = [int(p) for p in pages_entry.get().split(',')]
            if len(pages) == 0:
                pages = [p+1 for p in range(len(reader.pages))]
            for page in pages:
                writer.add_page(reader.pages[page-1])
            with open(file_path, "wb") as f:
                writer.write(f)
            pane.nametowidget("info").nametowidget("info_label").configure(text=f"{Path(file_path).stem}: Wrote {len(pages)} pages")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

# Build Controls
def build_controls() -> ttk.Frame:
    controls = ttk.Frame(pane, height=40, name="controls")
    controls.pack_propagate(False)
    load_button = ttk.Button(controls, text="Load PDF", command=load_pdf)
    load_button.pack(side="left", padx=5, pady=5)
    save_button = ttk.Button(controls, text="Save PDF", command=save_pdf)
    save_button.pack(side="left", padx=5, pady=5)
    pages_label = ttk.Label(controls, text="Pages:")
    pages_label.pack(side="left", padx=5, pady=5)
    pages_entry = ttk.Entry(controls, width=30, name="pages_entry")
    pages_entry.pack(side="left", padx=5, pady=5)
    return controls

# Build Info
def build_info() -> ttk.Frame:
    info = ttk.Frame(pane, height=30, name="info")
    info_label = ttk.Label(info, name="info_label")
    info_label.pack(side="left", padx=5, pady=5)
    return info

# Build Output
def build_output() -> ttk.Frame:
    output = ttk.Frame(pane, height=400, name="output")
    output_text = tk.Text(output, state=tk.DISABLED, name="output_text")
    output_text.pack(expand=True, fill=tk.BOTH)
    return output

# Main window
main_window = tk.Tk()
main_window.title("PDF Tools")
main_window.geometry("600x600")

pane = ttk.PanedWindow(main_window, orient=tk.VERTICAL)
pane.pack(fill=tk.BOTH, expand=True)
pane.add(build_controls())
pane.add(build_info())
pane.add(build_output())

main_window.mainloop()