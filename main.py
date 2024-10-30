import os
from time import sleep
from threading import Thread
import keyboard
from openai import OpenAI
import pyperclip
import pythoncom
from wmi import WMI
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# API key for OpenAI API
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

# Keybindings for functions
KEYBINDS = {
    'get_result': 'ctrl+space',
    'toggle_write_mode': 'ctrl+tab',
    'exit': 'esc'
}

# Enable program exit if certain processes are detected
PROCESS_MONITORING = True

# Processes that trigger program exit
BLACKLISTED_PROCESSES = [
    'taskmgr.exe',        # Windows Task-Manager
    'processhacker.exe',  # Process Hacker
    'procexp.exe',        # Process Explorer
    'perfmon.exe',        # Performance Monitor
    'resmon.exe',         # Resource Monitor
    'systemexplorer.exe'  # System Explorer
]


class Controller:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_KEY)  # OpenAI client
        self.result = None  # Stores API response
        self.write_mode_active = False  # Indicates if writing mode is active
        self.result_index = 0  # Tracks current position in writing mode
        self.pressed_keys = set()  # Set of currently pressed keys
        self.results_pending = False  # Indicates whether the result is pending
        self.keybinds = self.convert_keybinds(KEYBINDS)  # Converts and stores the key bindings

        keyboard.on_press(self.on_press, suppress=True)
        keyboard.on_release(self.on_release, suppress=True)

        if PROCESS_MONITORING:
            Thread(target=self.process_monitor).start()

    def get_result(self):
        pythoncom.CoInitialize()

        self.results_pending = True

        # Stores selected text in clipboard_content
        keyboard.press_and_release('ctrl+c')
        sleep(0.1)
        clipboard_content = pyperclip.paste()
        pyperclip.copy('')

        # Changes mute status to display the response status
        volume = cast(AudioUtilities.GetSpeakers().Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None), POINTER(IAudioEndpointVolume))
        initally_mute = volume.GetMute()
        volume.SetMute(not initally_mute, None)

        response = self.openai_client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': f'Beantworte die folgende Frage kurz und antworte nur mit der Antwort auf die Frage ohne eine Bestätigung:\n\n{clipboard_content}'
                        }
                    ]
                }
            ],
            response_format={
                'type': 'text'
            }
        )

        self.result = response.choices[0].message.content
        pyperclip.copy(self.result)

        volume.SetMute(initally_mute, None)  # Changes mute status back to inital value

        self.results_pending = False

    def toggle_write_mode(self):
        if not self.result:
            return

        self.write_mode_active = not self.write_mode_active  # updates active status

        if not self.write_mode_active:
            self.result_index = 0

    def write_mode(self, event):
        # (len(event.name) < 2 or event.name == 'space') = is printable key
        if not (len(event.name) < 2 or event.name == 'space'):
            return False

        if self.result_index < len(self.result):
            keyboard.write(self.result[self.result_index])
            self.result_index += 1
            return False

    def on_press(self, event):
        self.pressed_keys.add(event.scan_code)

        # toggle write mode if keybind pressed
        if self.pressed_keys == self.keybinds['toggle_write_mode']:
            Thread(target=self.toggle_write_mode).start()
            return False
        
        # exit if keybind pressed
        elif self.pressed_keys == self.keybinds['exit']:
            try:
                os._exit(0)
            except SystemExit:
                pass

        # write next char in write mode if write mode active
        elif self.write_mode_active:
            return self.write_mode(event)

        # get chatgpt response if keybind pressed
        elif self.pressed_keys == self.keybinds['get_result']:
            if not self.results_pending:
                Thread(target=self.get_result).start()
            return False

        # True  =  Allow input
        # False =  Supress input

        return True

    def on_release(self, event):
        self.pressed_keys.discard(event.scan_code)
        return True
    
    def convert_keybinds(self, keymap):
        result = {}
        for name, keybind in keymap.items():
            f_keybind = set()

            for key in keybind.split('+'):
                f_keybind.add(keyboard.key_to_scan_codes(key)[0])

            result[name] = f_keybind

        return result

    def process_monitor(self):
        pythoncom.CoInitialize()
        c = WMI()
        process_watcher = c.Win32_Process.watch_for('creation')

        while True:
            new_process = process_watcher()

            if new_process.Name.lower() in BLACKLISTED_PROCESSES:
                os._exit(0)

            sleep(1)


if __name__ == "__main__":
    Controller()
    keyboard.wait(KEYBINDS['exit'])