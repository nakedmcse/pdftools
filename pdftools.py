from pypdf import PdfReader, PdfWriter
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Globals
reader = None
flatten_var = None

# Helpers
def coords_to_string(c: list) -> str:
    if len(c) < 4:
        return ""
    return f"({c[0]},{c[1]}) x ({c[2]},{c[3]})"

def flatten_pdf(writer: PdfWriter) -> None:
    global reader
    fields = reader.get_fields() or {}
    values = {name: field.get("/V", "") for name, field in fields.items()}
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False, flatten=True)
    writer.remove_annotations("/Widget")
    writer._root_object.pop("/AcroForm", None)

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
            output_tree = pane.nametowidget("output").nametowidget("output_tree")
            info_label.configure(text=f"{Path(file_path).stem}: {len(reader.pages)} pages and {len(fields)} fields")
            pages_entry.delete(0, tk.END)
            for p in range(len(reader.pages)):
                pages_entry.insert(tk.END, f"{p+1},")
            pages_entry.delete(len(pages_entry.get())-1,tk.END)
            output_tree.delete(*output_tree.get_children())
            for page_num, page in enumerate(reader.pages):
                annotations = page.get("/Annots", [])
                for annotation_ref in annotations:
                    annotation = annotation_ref.get_object()

                    if annotation.get("/Subtype") == "/Widget":
                        rect = annotation.get("/Rect")
                        coords = [float(coord) for coord in rect] if rect else []
                        name = annotation.get("/T")
                        parent_ref = annotation.get("/Parent")
                        parent = parent_ref.get_object() if parent_ref else None

                        if not name and parent:
                            name = parent.get("/T")

                        field_type = annotation.get("/FT")
                        if not field_type and parent:
                            field_type = parent.get("/FT")

                        output_tree.insert("", tk.END, values=(name, field_type, page_num+1, coords_to_string(coords)))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

# Save PDF
def save_pdf():
    global reader, flatten_var
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
            writer.append(reader, pages=[p - 1 for p in pages])
            if (flatten_var.get()):
                flatten_pdf(writer)
            with open(file_path, "wb") as f:
                writer.write(f)
            pane.nametowidget("info").nametowidget("info_label").configure(text=f"{Path(file_path).stem}: Wrote {len(pages)} pages")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

# Build Controls
def build_controls() -> ttk.Frame:
    global flatten_var
    controls = ttk.Frame(pane, height=40, name="controls")
    controls.pack_propagate(False)
    load_button = ttk.Button(controls, text="Load PDF", command=load_pdf)
    load_button.pack(side="left", padx=5, pady=5)
    save_button = ttk.Button(controls, text="Save PDF", command=save_pdf)
    save_button.pack(side="left", padx=5, pady=5)
    flatten_var = tk.BooleanVar(value=False)
    flatten_check = ttk.Checkbutton(controls, text="Flatten", variable=flatten_var)
    flatten_check.pack(side="left", padx=5, pady=5)
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
    output = ttk.Frame(pane, name="output")
    output_tree = ttk.Treeview(output, columns=["name", "type", "page", "coords"], show="headings", name="output_tree")
    output_tree.heading("name", text="Name")
    output_tree.heading("type", text="Type")
    output_tree.heading("page", text="Page")
    output_tree.heading("coords", text="Coords")
    output_tree.column("name", width=400, anchor="w")
    output_tree.column("type", width=50, anchor="center")
    output_tree.column("page", width=50, anchor="center")
    output_tree.column("coords", width=300, anchor="w")
    scrollbar = ttk.Scrollbar(output, orient="vertical", command=output_tree.yview)
    output_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    output_tree.pack(side="left", fill=tk.BOTH, expand=True, padx=5, pady=5)
    return output

# Main window
main_window = tk.Tk()
main_window.title("PDF Tools")
main_window.geometry("800x600")

pane = ttk.PanedWindow(main_window, orient=tk.VERTICAL)
pane.pack(fill=tk.BOTH, expand=True)
pane.add(build_controls())
pane.add(build_info())
pane.add(build_output())

main_window.mainloop()