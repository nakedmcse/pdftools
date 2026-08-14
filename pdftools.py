from pypdf import PdfReader, PdfWriter
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
            info_label.configure(text=f"Read {len(reader.pages)} pages and {len(fields)} fields")
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
            pages = [int(p) for p in pages_entry.get().split(',')]
            if len(pages) == 0:
                pages = [p+1 for p in range(len(reader.pages))]
            for page in pages:
                writer.add_page(reader.pages[page-1])
            with open(file_path, "wb") as f:
                writer.write(f)
            info_label.configure(text=f"Wrote {len(pages)} pages")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

# Main window
main_window = tk.Tk()
main_window.title("PDF Tools")
main_window.geometry("600x600")

pane = ttk.PanedWindow(main_window, orient=tk.VERTICAL)
pane.pack(fill=tk.BOTH, expand=True)

controls = ttk.Frame(pane, height=40)
controls.pack_propagate(False)
load_button = ttk.Button(controls, text="Load PDF", command=load_pdf)
load_button.pack(side="left", padx=5, pady=5)
save_button = ttk.Button(controls, text="Save PDF", command=save_pdf)
save_button.pack(side="left", padx=5, pady=5)
pages_label = ttk.Label(controls, text="Pages:")
pages_label.pack(side="left", padx=5, pady=5)
pages_entry = ttk.Entry(controls, width=30)
pages_entry.pack(side="left", padx=5, pady=5)

info = ttk.Frame(pane, height=30)
info_label = ttk.Label(info)
info_label.pack(side="left", padx=5, pady=5)

output = ttk.Frame(pane, height=400)
output_text = tk.Text(output, state=tk.DISABLED)
output_text.pack(expand=True, fill=tk.BOTH)

pane.add(controls)
pane.add(info)
pane.add(output)

main_window.mainloop()