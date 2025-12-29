import tkinter as tk
import sys
import os

# Import the stop logic
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from scripts.tts_engine import stop_playback
except ImportError:
    def stop_playback():
        print("Error: stop_playback logic not found.")

class VoiceRemote:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mind-OS 语音助手")
        
        # --- MAX VISIBILITY SETTINGS ---
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 1.0)     # Fully opaque for focus
        
        # Center of screen initially
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width, height = 280, 120
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Style
        self.root.configure(bg='#1e1e1e') # VS Code style dark
        
        # Main Container
        self.container = tk.Frame(self.root, bg='#1e1e1e', padx=10, pady=10)
        self.container.pack(fill='both', expand=True)

        # Title / Drag handle
        self.title_label = tk.Label(self.container, text="🎧 语音控制中心", 
                                   bg='#2d2d2d', fg='#007acc', 
                                   font=('微软雅黑', 10, 'bold'),
                                   padx=5, pady=5)
        self.title_label.pack(fill='x', pady=(0, 10))
        self.title_label.bind("<Button-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)

        # BUTTON ROWS
        self.btn_frame = tk.Frame(self.container, bg='#1e1e1e')
        self.btn_frame.pack(fill='both', expand=True)

        # BIG STOP BUTTON
        self.stop_btn = tk.Button(self.btn_frame, text="⏹️ 停止朗读 (STOP)", 
                                  command=self.on_stop,
                                  bg='#d32f2f', fg='white', 
                                  activebackground='#b71c1c',
                                  font=('微软雅黑', 11, 'bold'),
                                  cursor='hand2',
                                  bd=0, height=2)
        self.stop_btn.pack(fill='x')

        # Status Label
        self.status_label = tk.Label(self.container, text="就绪", bg='#1e1e1e', fg='gray', font=('Arial', 8))
        self.status_label.pack(side='bottom')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def on_stop(self):
        try:
            stop_playback()
            self.status_label.configure(text="已停止", fg='#4caf50')
            self.root.after(2000, lambda: self.status_label.configure(text="就绪", fg='gray'))
        except Exception as e:
            self.status_label.configure(text=f"错误: {str(e)[:20]}", fg='#f44336')

    def run(self):
        print("Remote active. Always on top.")
        self.root.mainloop()

if __name__ == "__main__":
    app = VoiceRemote()
    app.run()
