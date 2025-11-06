import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import pygame
from pynput import keyboard
import os
import json
import ctypes

ctk.set_default_color_theme("blue")

class ThemeManager:
    DARK = {
        'bg_dark': '#0D0D0D',
        'bg_medium': '#1C1C1C',
        'bg_light': '#2A2A2A',
        'bg_card': '#212121',
        'accent_green': '#00E676',
        'accent_green_hover': '#00C853',
        'accent_red': '#FF1744',
        'accent_red_hover': '#D50000',
        'accent_blue': '#2196F3',
        'accent_blue_hover': '#1976D2',
        'accent_purple': '#9C27B0',
        'accent_purple_hover': '#7B1FA2',
        'text_primary': '#FFFFFF',
        'text_secondary': '#B0B0B0',
        'text_gray': '#707070',
        'border': '#333333',
        'shadow': '#000000'
    }
    
    LIGHT = {
        'bg_dark': '#F5F5F5',
        'bg_medium': '#FFFFFF',
        'bg_light': '#FAFAFA',
        'bg_card': '#FFFFFF',
        'accent_green': '#00C853',
        'accent_green_hover': '#00E676',
        'accent_red': '#D50000',
        'accent_red_hover': '#FF1744',
        'accent_blue': '#1976D2',
        'accent_blue_hover': '#2196F3',
        'accent_purple': '#7B1FA2',
        'accent_purple_hover': '#9C27B0',
        'text_primary': '#212121',
        'text_secondary': '#616161',
        'text_gray': '#9E9E9E',
        'border': '#E0E0E0',
        'shadow': '#CCCCCC'
    }
    
    current = DARK.copy()
    is_dark = True
    
    @classmethod
    def get(cls, key):
        return cls.current.get(key, '#000000')
    
    @classmethod
    def switch(cls, to_dark=True):
        cls.is_dark = to_dark
        if to_dark:
            cls.current = cls.DARK.copy()
            ctk.set_appearance_mode("dark")
        else:
            cls.current = cls.LIGHT.copy()
            ctk.set_appearance_mode("light")
        return cls.current

def C(key):
    return ThemeManager.get(key)

DEFAULT_FONT = "Microsoft YaHei UI"
DEFAULT_FONT_EN = "Segoe UI"

ICONS = {
    'logo': '♪',
    'volume_high': '|||',
    'volume_mid': '|| ',
    'volume_low': '|  ',
    'volume_mute': '   ',
    'keyboard': 'KB',
    'folder': '[]',
    'list': '☰',
    'play': '▶',
    'stop': '■',
    'pause': '||',
    'delete': '×',
    'plus': '+',
    'status_playing': '●',
    'status_idle': '○',
    'check': '✓',
    'arrow_right': '>',
    'record': '●',
    'edit': '≡',
    'theme': '◐',
    'wave': '～',
    'sun': '☼',
    'moon': '☾'
}

class AudioItem:
    def __init__(self, file_path, hotkey="", name=""):
        self.file_path = file_path
        self.hotkey = hotkey
        self.name = name or os.path.basename(file_path)
        self.is_playing = False
        self.is_recording_hotkey = False

class ZanePro:
    def __init__(self):
        self.load_theme_preference_early()
        
        self.window = ctk.CTk()
        self.window.title("Zane Pro")
        self.window.geometry("920x680")
        self.window.minsize(850, 600)
        
        self.window.overrideredirect(True)
        
        self.window.configure(fg_color=C('bg_dark'))
        
        try:
            self.window.after(100, self.set_window_corner)
        except:
            pass
        
        pygame.mixer.init()
        
        self.audio_items = []
        self.volume = 0.7
        self.hotkey_enabled = True
        self.audio_ducking = True
        self.hotkey_listener = None
        self.current_playing = None
        
        self.setup_ui()
        self.load_settings()
        self.start_hotkey_listener()
        self.animate_window_in()
        
        self.window.bind('<Button-1>', self.start_move)
        self.window.bind('<B1-Motion>', self.on_move)
    
    def load_theme_preference_early(self):
        try:
            if os.path.exists("zane_pro_settings.json"):
                with open("zane_pro_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                is_dark = settings.get("is_dark_theme", True)
                ThemeManager.switch(is_dark)
        except:
            ThemeManager.switch(True)
    
    def set_window_corner(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWM_WINDOW_CORNER_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWM_WINDOW_CORNER_ROUND)),
                ctypes.sizeof(ctypes.c_int)
            )
        except:
            pass
        
    def setup_ui(self):
        titlebar = ctk.CTkFrame(
            self.window, 
            height=50, 
            corner_radius=0, 
            fg_color=C('bg_medium'),
            border_width=0
        )
        titlebar.pack(fill="x", side="top")
        titlebar.pack_propagate(False)
        
        title_container = ctk.CTkFrame(titlebar, fg_color="transparent")
        title_container.pack(side="left", padx=25, pady=12)
        
        name_label = ctk.CTkLabel(
            title_container,
            text="Zane Pro",
            font=ctk.CTkFont(family=DEFAULT_FONT_EN, size=18, weight="bold"),
            text_color=C('text_primary')
        )
        name_label.pack(side="left")
        
        version_label = ctk.CTkLabel(
            title_container,
            text="v2.0",
            font=ctk.CTkFont(family=DEFAULT_FONT_EN, size=10),
            text_color=C('text_gray')
        )
        version_label.pack(side="left", padx=(8, 0))
        
        buttons_container = ctk.CTkFrame(titlebar, fg_color="transparent")
        buttons_container.pack(side="right")
        
        theme_icon = ICONS['sun'] if ThemeManager.is_dark else ICONS['moon']
        self.theme_btn = ctk.CTkButton(
            buttons_container,
            text=theme_icon,
            width=50,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=C('bg_light'),
            text_color=C('text_secondary'),
            command=self.toggle_theme,
            border_width=0
        )
        self.theme_btn.pack(side="left")
        
        minimize_btn = ctk.CTkButton(
            buttons_container,
            text="─",
            width=50,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=C('bg_light'),
            text_color=C('text_secondary'),
            command=self.minimize_window,
            border_width=0
        )
        minimize_btn.pack(side="left")
        
        close_btn = ctk.CTkButton(
            buttons_container,
            text="✕",
            width=50,
            height=50,
            corner_radius=0,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="transparent",
            hover_color=C('accent_red'),
            text_color=C('text_secondary'),
            command=self.on_closing,
            border_width=0
        )
        close_btn.pack(side="left")
        
        titlebar.bind('<Button-1>', self.start_move)
        titlebar.bind('<B1-Motion>', self.on_move)
        title_container.bind('<Button-1>', self.start_move)
        title_container.bind('<B1-Motion>', self.on_move)
        name_label.bind('<Button-1>', self.start_move)
        name_label.bind('<B1-Motion>', self.on_move)
        
        main_container = ctk.CTkFrame(self.window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        top_frame = ctk.CTkFrame(
            main_container, 
            fg_color=C('bg_card'),
            corner_radius=12,
            border_width=1,
            border_color=C('border')
        )
        top_frame.pack(fill="x", padx=5, pady=(10, 5))
        
        volume_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        volume_frame.pack(fill="x", padx=20, pady=15)
        
        self.volume_icon = ctk.CTkLabel(
            volume_frame,
            text=ICONS['volume_high'],
            font=ctk.CTkFont(size=18)
        )
        self.volume_icon.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            volume_frame,
            text="音量",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
            text_color=C('text_primary')
        ).pack(side="left", padx=(0, 15))
        
        self.volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=2.0,
            number_of_steps=200,
            command=self.update_volume,
            height=18,
            button_color=C('accent_blue'),
            button_hover_color=C('accent_blue_hover'),
            progress_color=C('accent_blue'),
            fg_color=C('bg_light')
        )
        self.volume_slider.set(0.7)
        self.volume_slider.pack(side="left", fill="x", expand=True, padx=10)
        
        self.volume_slider.bind('<Button-1>', lambda e: e.widget.focus_set() or "break")
        self.volume_slider.bind('<B1-Motion>', lambda e: "break")
        
        self.volume_label = ctk.CTkLabel(
            volume_frame,
            text="70%",
            width=60,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
            text_color=C('accent_blue')
        )
        self.volume_label.pack(side="left", padx=(10, 0))
        
        separator = ctk.CTkFrame(top_frame, height=1, fg_color=C('border'))
        separator.pack(fill="x", padx=20, pady=10)
        
        hotkey_toggle_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        hotkey_toggle_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        hotkey_icon = ctk.CTkLabel(
            hotkey_toggle_frame,
            text=ICONS['keyboard'],
            font=ctk.CTkFont(size=18)
        )
        hotkey_icon.pack(side="left", padx=(0, 10))
        
        self.hotkey_switch = ctk.CTkSwitch(
            hotkey_toggle_frame,
            text="热键响应",
            command=self.toggle_hotkey,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
            button_color=C('accent_green'),
            button_hover_color=C('accent_green_hover'),
            progress_color=C('accent_green')
        )
        self.hotkey_switch.select()
        self.hotkey_switch.pack(side="left")
        
        ctk.CTkLabel(
            hotkey_toggle_frame,
            text="关闭后热键将穿透到其他程序",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=12),
            text_color=C('text_gray')
        ).pack(side="left", padx=15)
        
        ducking_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        ducking_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        self.ducking_switch = ctk.CTkSwitch(
            ducking_frame,
            text="音频闪避",
            command=self.toggle_ducking,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=14, weight="bold"),
            button_color=C('accent_blue'),
            button_hover_color=C('accent_blue_hover'),
            progress_color=C('accent_blue')
        )
        self.ducking_switch.select()
        self.ducking_switch.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            ducking_frame,
            text="开启后，播放新音频时自动停止上一个",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=12),
            text_color=C('text_gray')
        ).pack(side="left", padx=5)
        
        separator2 = ctk.CTkFrame(top_frame, height=1, fg_color=C('border'))
        separator2.pack(fill="x", padx=20, pady=(0, 15))
        
        add_btn = ctk.CTkButton(
            top_frame,
            text=f"{ICONS['plus']}  添加音频文件",
            command=self.add_audio_file,
            height=45,
            corner_radius=10,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=15, weight="bold"),
            fg_color=C('accent_green'),
            hover_color=C('accent_green_hover'),
            border_width=0
        )
        add_btn.pack(fill="x", padx=20, pady=(0, 15))
        
        list_header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        list_header_frame.pack(fill="x", padx=5, pady=(15, 5))
        
        list_label = ctk.CTkLabel(
            list_header_frame,
            text=f"{ICONS['list']} 媒体列表",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=16, weight="bold"),
            text_color=C('text_primary'),
            anchor="w"
        )
        list_label.pack(side="left", padx=20)
        
        self.count_label = ctk.CTkLabel(
            list_header_frame,
            text="0 个文件",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=13),
            text_color=C('text_gray')
        )
        self.count_label.pack(side="left", padx=10)
        
        self.audio_list_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color=C('bg_card'),
            corner_radius=12,
            border_width=1,
            border_color=C('border')
        )
        self.audio_list_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        status_frame = ctk.CTkFrame(
            main_container, 
            fg_color=C('bg_card'),
            height=40, 
            corner_radius=12,
            border_width=1,
            border_color=C('border')
        )
        status_frame.pack(fill="x", padx=5, pady=(5, 0))
        status_frame.pack_propagate(False)
        
        status_icon = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=C('accent_green')
        )
        status_icon.pack(side="left", padx=(20, 5), pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=ctk.CTkFont(family=DEFAULT_FONT, size=13),
            text_color=C('text_secondary'),
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, pady=10)
        
    def animate_window_in(self):
        try:
            self.window.attributes('-alpha', 1.0)
        except:
            pass
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
        
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
        
    def minimize_window(self):
        self.window.iconify()
    
    def toggle_theme(self):
        ThemeManager.switch(not ThemeManager.is_dark)
        self.save_settings()
        self.restart_app()
    
    def restart_app(self):
        self.save_settings()
        
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
        
        self.window.destroy()
        
        new_app = ZanePro()
        new_app.run()
        
    def update_volume(self, value):
        self.volume = float(value)
        percentage = int(self.volume * 100)
        self.volume_label.configure(text=f"{percentage}%")
        
        if self.volume == 0:
            icon = ICONS['volume_mute']
        elif self.volume < 0.3:
            icon = ICONS['volume_low']
        elif self.volume < 0.7:
            icon = ICONS['volume_mid']
        else:
            icon = ICONS['volume_high']
        
        self.volume_icon.configure(text=icon)
        
        pygame_volume = min(self.volume, 1.0)
        pygame.mixer.music.set_volume(pygame_volume)
        self.save_settings()
        
    def toggle_hotkey(self):
        self.hotkey_enabled = self.hotkey_switch.get()
        status = "已启用" if self.hotkey_enabled else "已禁用"
        self.update_status(f"热键响应{status}")
        self.save_settings()
        
    def toggle_ducking(self):
        self.audio_ducking = self.ducking_switch.get()
        status = "已启用" if self.audio_ducking else "已禁用"
        self.update_status(f"音频闪避{status}")
        self.save_settings()
        
    def add_audio_file(self):
        file_paths = filedialog.askopenfilenames(
            title="选择音频文件（可多选）",
            filetypes=[
                ("音频文件", "*.mp3 *.wav *.ogg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            added_count = 0
            for file_path in file_paths:
                if any(item.file_path == file_path for item in self.audio_items):
                    continue
                    
                audio_item = AudioItem(file_path)
                self.audio_items.append(audio_item)
                self.create_audio_item_widget(audio_item)
                added_count += 1
            
            self.update_count_label()
            self.save_settings()
            if added_count > 0:
                self.update_status(f"已添加 {added_count} 个文件")
    
    def update_count_label(self):
        count = len(self.audio_items)
        self.count_label.configure(text=f"{count} 个文件")
            
    def create_audio_item_widget(self, audio_item):
        item_frame = ctk.CTkFrame(
            self.audio_list_frame,
            fg_color=C('bg_light'),
            corner_radius=10,
            border_width=1,
            border_color=C('border')
        )
        item_frame.pack(fill="x", padx=8, pady=6)
        
        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=12)
        
        status_label = ctk.CTkLabel(
            left_frame,
            text=ICONS['status_idle'],
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=C('text_gray'),
            width=25
        )
        status_label.pack(side="left", padx=(0, 12))
        audio_item.status_label = status_label
        
        name_label = ctk.CTkLabel(
            left_frame,
            text=audio_item.name,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=14),
            text_color=C('text_primary'),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        right_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=12)
        
        hotkey_text = audio_item.hotkey.upper() if audio_item.hotkey else "设置热键"
        hotkey_btn = ctk.CTkButton(
            right_frame,
            text=hotkey_text,
            width=90,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family=DEFAULT_FONT, size=12, weight="bold"),
            fg_color=C('bg_dark'),
            hover_color=C('accent_blue'),
            border_width=1,
            border_color=C('border'),
            text_color=C('text_secondary') if not audio_item.hotkey else C('accent_blue'),
            command=lambda: self.start_hotkey_recording(audio_item, hotkey_btn)
        )
        hotkey_btn.pack(side="left", padx=(0, 8))
        audio_item.hotkey_btn = hotkey_btn
        
        play_btn = ctk.CTkButton(
            right_frame,
            text=ICONS['play'],
            width=42,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C('accent_green'),
            hover_color=C('accent_green_hover'),
            border_width=0,
            command=lambda: self.play_audio_with_animation(audio_item)
        )
        play_btn.pack(side="left", padx=3)
        
        stop_btn = ctk.CTkButton(
            right_frame,
            text=ICONS['stop'],
            width=42,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=C('accent_red'),
            hover_color=C('accent_red_hover'),
            border_width=0,
            command=lambda: self.stop_audio_with_animation(audio_item)
        )
        stop_btn.pack(side="left", padx=3)
        
        delete_btn = ctk.CTkButton(
            right_frame,
            text=ICONS['delete'],
            width=42,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=14),
            fg_color=C('bg_dark'),
            hover_color=C('bg_light'),
            border_width=1,
            border_color=C('border'),
            command=lambda: self.delete_audio_item(audio_item, item_frame)
        )
        delete_btn.pack(side="left", padx=3)
        
        audio_item.widget_frame = item_frame
        
    def start_hotkey_recording(self, audio_item, btn):
        if audio_item.is_recording_hotkey:
            audio_item.is_recording_hotkey = False
            btn.configure(
                text=audio_item.hotkey.upper() if audio_item.hotkey else "设置热键",
                fg_color=C('bg_dark'),
                border_color=C('border'),
                border_width=1,
                text_color=C('text_secondary') if not audio_item.hotkey else C('accent_blue')
            )
            try:
                self.window.unbind('<KeyPress>')
            except:
                pass
            return
        
        audio_item.is_recording_hotkey = True
        btn.configure(
            text="按任意键...",
            fg_color=C('accent_blue'),
            border_color=C('accent_blue'),
            border_width=2,
            text_color=C('text_primary')
        )
        
        def on_key_press(event):
            if not audio_item.is_recording_hotkey:
                return
            
            key_name = event.keysym.lower()
            
            if key_name in ['shift_l', 'shift_r', 'control_l', 'control_r', 'alt_l', 'alt_r',
                           'super_l', 'super_r', 'caps_lock', 'num_lock', 'scroll_lock']:
                return
            
            audio_item.hotkey = key_name
            audio_item.is_recording_hotkey = False
            
            btn.configure(
                text=key_name.upper(),
                fg_color=C('bg_dark'),
                border_color=C('border'),
                border_width=1,
                text_color=C('accent_blue')
            )
            
            try:
                self.window.unbind('<KeyPress>')
            except:
                pass
            
            self.save_settings()
            self.update_status(f"已设置热键: {audio_item.name} -> {key_name}")
        
        self.window.bind('<KeyPress>', on_key_press)
    
    def update_hotkey(self, audio_item, hotkey):
        audio_item.hotkey = hotkey.strip().lower()
        self.save_settings()
        if hotkey:
            self.update_status(f"已设置热键: {audio_item.name} -> {hotkey}")
        
    def play_audio_with_animation(self, audio_item):
        self.play_audio(audio_item)
    
    def play_audio(self, audio_item):
        try:
            if self.audio_ducking and self.current_playing and self.current_playing != audio_item:
                self.current_playing.is_playing = False
                self.current_playing.status_label.configure(
                    text=ICONS['status_idle'], 
                    text_color=C('text_gray')
                )
            
            pygame.mixer.music.load(audio_item.file_path)
            pygame.mixer.music.set_volume(min(self.volume, 1.0))
            pygame.mixer.music.play()
            
            audio_item.is_playing = True
            audio_item.status_label.configure(
                text=ICONS['status_playing'], 
                text_color=C('accent_green')
            )
            self.current_playing = audio_item
            self.update_status(f"正在播放: {audio_item.name}")
            
            self.check_playback_finished(audio_item)
                
        except Exception as e:
            self.update_status(f"播放失败: {audio_item.name}")
    
    def check_playback_finished(self, audio_item):
        if self.current_playing != audio_item:
            return
        
        if not pygame.mixer.music.get_busy():
            audio_item.is_playing = False
            audio_item.status_label.configure(
                text=ICONS['status_idle'], 
                text_color=C('text_gray')
            )
            self.current_playing = None
            self.update_status(f"播放完成: {audio_item.name}")
        else:
            self.window.after(500, lambda: self.check_playback_finished(audio_item))
    
    def stop_audio_with_animation(self, audio_item):
        self.stop_audio(audio_item)
    
    def stop_audio(self, audio_item):
        try:
            pygame.mixer.music.stop()
            
            audio_item.is_playing = False
            audio_item.status_label.configure(
                text=ICONS['status_idle'], 
                text_color=C('text_gray')
            )
            
            if self.current_playing == audio_item:
                self.current_playing = None
            
            self.update_status(f"已停止: {audio_item.name}")
            
        except Exception as e:
            self.update_status(f"停止失败: {str(e)}")
            
    def delete_audio_item(self, audio_item, widget_frame):
        if audio_item.is_playing:
            self.stop_audio(audio_item)
        
        self.audio_items.remove(audio_item)
        
        widget_frame.destroy()
        
        self.update_count_label()
        self.save_settings()
        self.update_status(f"已删除: {audio_item.name}")
        
    def start_hotkey_listener(self):
        def on_press(key):
            if not self.hotkey_enabled:
                return
                
            try:
                if hasattr(key, 'char') and key.char:
                    key_name = key.char.lower()
                elif hasattr(key, 'name'):
                    key_name = key.name.lower()
                else:
                    key_name = str(key).replace("Key.", "").lower()
                
                for audio_item in self.audio_items:
                    if audio_item.hotkey and audio_item.hotkey == key_name:
                        if audio_item.is_playing:
                            self.stop_audio_with_animation(audio_item)
                        else:
                            self.play_audio_with_animation(audio_item)
                        break
                        
            except Exception as e:
                pass
                
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()
        
    def update_status(self, message):
        self.status_label.configure(text=message)
        
    def save_settings(self):
        settings = {
            "volume": self.volume,
            "hotkey_enabled": self.hotkey_enabled,
            "audio_ducking": self.audio_ducking,
            "is_dark_theme": ThemeManager.is_dark,
            "audio_items": [
                {
                    "file_path": item.file_path,
                    "hotkey": item.hotkey,
                    "name": item.name
                }
                for item in self.audio_items
            ]
        }
        
        try:
            with open("zane_pro_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            pass
            
    def load_settings(self):
        try:
            if os.path.exists("zane_pro_settings.json"):
                with open("zane_pro_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    
                self.volume = settings.get("volume", 0.7)
                self.volume_slider.set(self.volume)
                percentage = int(self.volume * 100)
                self.volume_label.configure(text=f"{percentage}%")
                
                if self.volume == 0:
                    icon = ICONS['volume_mute']
                elif self.volume < 0.3:
                    icon = ICONS['volume_low']
                elif self.volume < 0.7:
                    icon = ICONS['volume_mid']
                else:
                    icon = ICONS['volume_high']
                self.volume_icon.configure(text=icon)
                
                self.hotkey_enabled = settings.get("hotkey_enabled", True)
                if self.hotkey_enabled:
                    self.hotkey_switch.select()
                else:
                    self.hotkey_switch.deselect()
                
                self.audio_ducking = settings.get("audio_ducking", True)
                if self.audio_ducking:
                    self.ducking_switch.select()
                else:
                    self.ducking_switch.deselect()
                
                audio_items_data = settings.get("audio_items", [])
                for item_data in audio_items_data:
                    if os.path.exists(item_data["file_path"]):
                        audio_item = AudioItem(
                            item_data["file_path"],
                            item_data.get("hotkey", ""),
                            item_data.get("name", "")
                        )
                        self.audio_items.append(audio_item)
                        self.create_audio_item_widget(audio_item)
                
                self.update_count_label()
                        
        except Exception as e:
            pass
            
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()
        
    def on_closing(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.quit()
        except:
            pass
        
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except:
                pass
        
        self.window.destroy()

if __name__ == "__main__":
    try:
        app = ZanePro()
        app.run()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

