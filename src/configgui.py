import tkinter as tk
from tkinter import messagebox
import ast
import os
from Event import Event

class ConfigGUI:
    def __init__(self, config_filename='config.py'):
        # Dynamically determine the path to config.py based on this script's location
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, config_filename)
        self.config = {}
        self.gui_elements = {}
        self.root = tk.Tk()
        self.root.title('Configuration Editor')
        self._load_config()
        self._build_gui()
        self.on_start = Event()
        self.on_stop = Event()


                # Set desired window width and height
        window_width = 500
        window_height = 500
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position for window to be centered
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Set window position
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = ast.literal_eval(value.strip())
        except FileNotFoundError as e:
            messagebox.showerror("File Not Found Error", f"Could not find the config file: {self.config_path}")
            self.closegui()  # Close the GUI if the config file is not found


    def _build_gui(self):
        for i, (key, value) in enumerate(self.config.items()):
            tk.Label(self.root, text=key).grid(row=i, column=0)
            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                entry = tk.Checkbutton(self.root, variable=var)
            else:
                var = tk.StringVar(value=str(value))
                entry = tk.Entry(self.root, textvariable=var)
            entry.grid(row=i, column=1)
            self.gui_elements[key] = var

        save_button = tk.Button(self.root, text="Save", command=self.save)
        save_button.grid(row=len(self.config) + 1, column=0, columnspan=2)
        start_button = tk.Button(self.root, text="Start", command=self.start)
        start_button.grid(row=len(self.config) + 1, column=1, columnspan=2)
        stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        stop_button.grid(row=len(self.config) + 1, column=2, columnspan=2)

    def showgui(self):
        # Example usage of periodic_task: Print a message every 1000ms (1 second)
        self.root.mainloop()

    def start(self):
        self.on_start.trigger(self, "Event triggered by Producer")
    def stop(self):
        self.on_stop.trigger(self, "Event triggered by Producer")

    def save(self):
        new_config = {key: var.get() for key, var in self.gui_elements.items()}
        with open(self.config_path, 'w') as f:
            for key, value in new_config.items():
                if isinstance(value, bool):
                    f.write(f"{key} = {value}\n")
                else:
                    try:
                        # Attempt to convert to float or int, else keep as string
                        numeric_value = ast.literal_eval(value)
                        f.write(f"{key} = {numeric_value}\n")
                    except:
                        f.write(f"{key} = '{value}'\n")
        messagebox.showinfo("Info", "Configuration saved successfully.")

    def closegui(self):
        self.root.destroy()

# Usage example
if __name__ == '__main__':
    config_editor = ConfigGUI('config.py')
    config_editor.showgui()
