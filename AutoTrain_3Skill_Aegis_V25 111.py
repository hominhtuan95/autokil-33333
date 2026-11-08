# Auto Train 3Skill - Chien Quoc 2D Aegis V25 (DatVersion 2.01.09)
# Windows 10/11; Python 3.10+; standard library only.
import ctypes
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

user32 = ctypes.windll.user32
KEYS = {str(i): 0x30 + i for i in range(10)}
KEYS.update({chr(65 + i): 65 + i for i in range(26)})
KEYS.update({f'F{i}': 0x70 + i - 1 for i in range(1, 13)})
KEYS.update({'TAB': 0x09, 'SPACE': 0x20})
KEYEVENTF_KEYUP = 0x0002

class AutoTrain:
    def __init__(self, root):
        self.root = root
        root.title('Auto Train 3Skill - Chien Quoc 2D Aegis V25')
        root.geometry('570x485')
        root.resizable(False, False)
        self.running = False
        self.closing = False
        self.hotkey_down = False
        self.generation = 0
        self.target = tk.StringVar(value='Chien Quoc 2D')
        self.keys = [tk.StringVar(value=k) for k in ('1', '2', '3')]
        self.delays = [tk.StringVar(value=d) for d in ('600', '800', '1000')]
        self.auto_target = tk.BooleanVar(value=True)
        self.auto_loot = tk.BooleanVar(value=True)
        self.target_delay = tk.StringVar(value='3000')
        self.loot_delay = tk.StringVar(value='5000')
        self.status = tk.StringVar(value='Da dung - F8 de bat/tat')

        ttk.Label(root, text='AUTO TRAIN 3SKILL - AEGIS V25', font=('Segoe UI', 15, 'bold')).pack(pady=(14, 12))
        top = ttk.Frame(root)
        top.pack(fill='x', padx=24)
        ttk.Label(top, text='Ten cua so game chua:').pack(side='left')
        ttk.Entry(top, textvariable=self.target, width=34).pack(side='right')

        table = ttk.LabelFrame(root, text='3 ky nang')
        table.pack(fill='x', padx=24, pady=13)
        ttk.Label(table, text='Ky nang').grid(row=0, column=0, padx=16, pady=5)
        ttk.Label(table, text='Phim').grid(row=0, column=1, padx=16)
        ttk.Label(table, text='Khoang lap (ms)').grid(row=0, column=2, padx=16)
        for i in range(3):
            ttk.Label(table, text=f'Skill {i+1}').grid(row=i+1, column=0, pady=5)
            ttk.Combobox(table, textvariable=self.keys[i], values=list(KEYS), state='readonly', width=9).grid(row=i+1, column=1)
            ttk.Entry(table, textvariable=self.delays[i], width=15).grid(row=i+1, column=2)

        extra = ttk.LabelFrame(root, text='Tu tim quai va nhat do')
        extra.pack(fill='x', padx=24, pady=5)
        ttk.Checkbutton(extra, text='Tu chon quai (Tab)', variable=self.auto_target).grid(row=0, column=0, sticky='w', padx=14, pady=9)
        ttk.Label(extra, text='Moi (ms):').grid(row=0, column=1, padx=8)
        ttk.Entry(extra, textvariable=self.target_delay, width=12).grid(row=0, column=2, padx=8)
        ttk.Checkbutton(extra, text='Tu nhat do (Space)', variable=self.auto_loot).grid(row=1, column=0, sticky='w', padx=14, pady=9)
        ttk.Label(extra, text='Moi (ms):').grid(row=1, column=1, padx=8)
        ttk.Entry(extra, textvariable=self.loot_delay, width=12).grid(row=1, column=2, padx=8)

        controls = ttk.Frame(root)
        controls.pack(pady=12)
        ttk.Button(controls, text='Bat dau (F8)', command=self.start).pack(side='left', padx=8)
        ttk.Button(controls, text='Dung (F8)', command=self.stop).pack(side='left', padx=8)
        ttk.Label(root, textvariable=self.status).pack(pady=5)
        ttk.Label(root, text='Chi gui phim khi cua so game duoc chon. F8 bat/tat toan cuc.', foreground='#666').pack(pady=5)
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
        user32.keybd_event(vk, 0, 0, 0)
        try:
            time.sleep(0.035)
        finally:
            user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

    def start(self):
        if self.running or self.closing:
            return
        try:
            delays = [int(v.get()) for v in self.delays]
            if any(not 50 <= n <= 60000 for n in delays):
                raise ValueError('Khoang lap skill phai tu 50 den 60000 ms.')
            keys = [KEYS[k.get().upper()] for k in self.keys]
            needle = self.target.get().strip()
            if not needle:
                raise ValueError('Hay nhap mot phan ten cua so game.')
            target_ms = int(self.target_delay.get())
            loot_ms = int(self.loot_delay.get())
            if not 100 <= target_ms <= 60000 or not 100 <= loot_ms <= 60000:
                raise ValueError('Khoang lap Tab/Space phai tu 100 den 60000 ms.')
        except (ValueError, KeyError) as exc:
            messagebox.showerror('Cau hinh khong hop le', str(exc) or 'Hay kiem tra phim va khoang lap.')
            return
        tasks = [(vk, ms / 1000) for vk, ms in zip(keys, delays)]
        if self.auto_target.get():
            tasks.append((KEYS['TAB'], target_ms / 1000))
        if self.auto_loot.get():
            tasks.append((KEYS['SPACE'], loot_ms / 1000))
        self.generation += 1
        generation = self.generation
        self.running = True
        self.status.set('Dang chay - chuyen sang cua so game')
        threading.Thread(target=self.worker, args=(tasks, needle, generation), daemon=True).start()

    def stop(self):
        self.running = False
        self.generation += 1
        self.status.set('Da dung - F8 de bat/tat')

    def worker(self, tasks, needle, generation):
        # Each task is independently scheduled; avoid bursts when returning to game.
        due = [time.monotonic()] * len(tasks)
        while self.running and not self.closing and generation == self.generation:
            if not self.foreground_is_game(needle):
                due = [time.monotonic()] * len(tasks)
                time.sleep(0.1)
                continue
            now = time.monotonic()
            for i, (vk, interval) in enumerate(tasks):
                if not self.running or self.closing or generation != self.generation or not self.foreground_is_game(needle):
                    break
                if now >= due[i]:
                    self.send_key(vk)
                    due[i] = time.monotonic() + interval
            time.sleep(0.015)

    def hotkey_loop(self):
        while not self.closing:
            down = bool(user32.GetAsyncKeyState(0x77) & 0x8000)
            if down and not self.hotkey_down:
                self.root.after(0, self.stop if self.running else self.start)
            self.hotkey_down = down
            time.sleep(0.08)

    def close(self):
        self.closing = True
        self.running = False
        self.generation += 1
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    AutoTrain(root)
    root.mainloop()
