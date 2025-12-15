import tkinter as tk
from tkinter import filedialog, messagebox
import os

class CatsDecompiler64:
    """
    A simple Hex Viewer for N64 ROM files.
    This is the first step in reverse engineering, not a full decompiler.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Cat's Decompiler 64 Awesomesauce 0.1")
        self.root.geometry("900x600")

        # --- Configure the main window grid ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Create Menu Bar ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open ROM...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # --- Create Main Frame ---
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # --- Create Text Widget for Hex Display ---
        # Use a monospaced font for proper alignment
        self.hex_display = tk.Text(main_frame, wrap=tk.NONE, font=('Courier', 10), state=tk.DISABLED)
        
        # --- Create Scrollbars ---
        y_scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.hex_display.yview)
        x_scrollbar = tk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.hex_display.xview)
        self.hex_display.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)

        # --- Grid all widgets ---
        self.hex_display.grid(row=0, column=0, sticky="nsew")
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        x_scrollbar.grid(row=1, column=0, sticky="ew")

        self.current_rom_data = None
        self.status_bar = tk.Label(self.root, text="Ready to purr-spect some ROMs!", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky="ew")


    def open_file(self):
        """Opens a file dialog to select an N64 ROM."""
        file_path = filedialog.askopenfilename(
            title="Select an N64 ROM",
            filetypes=(("N64 ROM Files", "*.z64 *.v64 *.n64"), ("All files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    self.current_rom_data = f.read()
                self.display_hex()
                self.status_bar.config(text=f"Opened: {os.path.basename(file_path)} | Size: {len(self.current_rom_data):,} bytes")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")

    def display_hex(self):
        """Displays the loaded ROM data in the hex viewer."""
        if not self.current_rom_data:
            return

        self.hex_display.config(state=tk.NORMAL)
        self.hex_display.delete(1.0, tk.END)

        # Display 16 bytes (0x10) per line
        bytes_per_line = 16
        data_length = len(self.current_rom_data)

        for i in range(0, data_length, bytes_per_line):
            # 1. The memory offset (e.g., 00000010)
            offset_str = f"{i:08X}"

            # 2. The hex values of the 16 bytes
            chunk = self.current_rom_data[i:i+bytes_per_line]
            hex_parts = []
            for byte in chunk:
                hex_parts.append(f"{byte:02X}")
            
            # Pad the last line with spaces if it's not full
            hex_str = ' '.join(hex_parts).ljust(bytes_per_line * 3 - 1)

            # 3. The ASCII representation of the 16 bytes
            ascii_parts = []
            for byte in chunk:
                # Check if the byte is a printable ASCII character
                if 32 <= byte <= 126:
                    ascii_parts.append(chr(byte))
                else:
                    ascii_parts.append('.')
            ascii_str = "".join(ascii_parts)

            # Combine and insert into the text widget
            line = f"{offset_str}   {hex_str}   |{ascii_str}|\n"
            self.hex_display.insert(tk.END, line)
        
        self.hex_display.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = CatsDecompiler64(root)
    root.mainloop()
