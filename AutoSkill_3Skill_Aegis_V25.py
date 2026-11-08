# Auto Skill 3Skill - Chiến Quốc 2D Aegis V25
# Windows 10/11, Python 3.10+. No third-party runtime dependencies.
import ctypes
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

user32 = ctypes.windll.user32
KEYS = {str(i): 0x30+i for i in range(10)}
KEYS.update({chr(65+i): 65+i for i in range(26)})
KEYS.update({f'F{i}': 0x70+i-1 for i in range(1, 13)})
KEYEVENTF_KEYUP = 0x0002

class AutoSkill:
    def __init__(self, root):
        self.root = root
        root.title('Auto Skill 3Skill - Chien Quoc 2D Aegis V25')
        root.geometry('510x360')
        root.resizable(False, False)
        self.running = False
        self.closing = False
        self.hotkey_down = False
        self.lock = threading.Lock()
        self.target = tk.StringVar(value='Chiến Quốc')
        self.keys = [tk.StringVar(value=k) for k in ('1', '2', '3')]
        self.delays = [tk.StringVar(value=d) for d in ('600', '800', '1000')]
        self.status = tk.StringVar(value='Đã dừng - F8 để bật/tắt')
        ttk.Label(root, text='AUTO SKILL 3SKILL - AEGIS V25', font=('Segoe UI', 15, 'bold')).pack(pady=14)
        top = ttk.Frame(root)
        top.pack(fill='x', padx=24)
        ttk.Label(top, text='Tên cửa sổ game chứa:').pack(side='left')
        ttk.Entry(top, textvariable=self.target, width=30).pack(side='right')
        table = ttk.Frame(root)
        table.pack(pady=16)
        ttk.Label(table, text='Kỹ năng').grid(row=0, column=0, padx=15)
        ttk.Label(table, text='Phím').grid(row=0, column=1, padx=15)
        ttk.Label(table, text='Khoảng lặp (ms)').grid(row=0, column=2, padx=15)
        for i in range(3):
            ttk.Label(table, text=f'Skill {i+1}').grid(row=i+1, column=0, pady=7)
            ttk.Combobox(table, textvariable=self.keys[i], values=list(KEYS), state='readonly', width=8).grid(row=i+1, column=1)
            ttk.Entry(table, textvariable=self.delays[i], width=13).grid(row=i+1, column=2)
        controls = ttk.Frame(root)
        controls.pack(pady=8)
        ttk.Button(controls, text='Bắt đầu (F8)', command=self.start).pack(side='left', padx=8)
        ttk.Button(controls, text='Dừng (F8)', command=self.stop).pack(side='left', padx=8)
        ttk.Label(root, textvariable=self.status).pack(pady=8)
        ttk.Label(root, text='Chỉ gửi phím khi cửa sổ game đang được chọn. F8 bật/tắt toàn cục.', foreground='#666').pack()
        root.protocol('WM_DELETE_WINDOW', self.close)
        threading.Thread(target=self.hotkey_loop, daemon=True).start()

    def foreground_is_game(self, needle):
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return False
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, len(buf))
        return needle.casefold() in buf.value.casefold()

    def send_key(self, vk):
        # Windows keyboard injection; some DirectInput clients may ignore this.
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.035)
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

    def start(self):
        if self.running:
            return
        try:
            intervals = [int(v.get()) / 1000 for v in self.delays]
            if any(not 50 <= int(v.get()) <= 60000 for v in self.delays):
                raise ValueError()
            keys = [KEYS[k.get().upper()] for k in self.keys]
            needle = self.target.get().strip()
            if not needle:
                messagebox.showerror('Thiếu tên cửa sổ', 'Hãy nhập một phần tên cửa sổ game.')
                return
        except (ValueError, KeyError):
            messagebox.showerror('Cấu hình không hợp lệ', 'Thời gian mỗi skill phải từ 50 đến 60000 ms.')
            return
        self.running = True
        self.status.set('Đang chạy - chuyển sang cửa sổ game')
        threading.Thread(target=self.worker, args=(keys, intervals, needle), daemon=True).start()

    def stop(self):
        self.running = False
        self.status.set('Đã dừng - F8 để bật/tắt')

    def worker(self, keys, intervals, needle):
        due = [time.monotonic()] * 3
        while self.running and not self.closing:
            if not self.foreground_is_game(needle):
                # Reset schedule while game is not focused, avoiding a burst on return.
                due = [time.monotonic()] * 3
                time.sleep(0.1)
                continue
            now = time.monotonic()
            for i in range(3):
                if not self.running or not self.foreground_is_game(needle):
                    break
                if now >= due[i]:
                    self.send_key(keys[i])
                    due[i] = time.monotonic() + intervals[i]
            time.sleep(0.015)

    def hotkey_loop(self):
        while not self.closing:
            down = bool(user32.GetAsyncKeyState(0x77) & 0x8000)  # F8
            if down and not self.hotkey_down:
                self.root.after(0, self.stop if self.running else self.start)
            self.hotkey_down = down
            time.sleep(0.08)

    def close(self):
        self.closing = True
        self.running = False
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    AutoSkill(root)
    root.mainloop()
