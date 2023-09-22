import time
import tkinter as tk
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Listener as MouseListener, Controller as MouseController
import pyautogui
import keyboard as keyboard_lib  # Rename the keyboard library

class MacroRecorder:
    def __init__(self, root):
        self.recorded_actions = []
        self.is_recording = False
        self.pressed_keys = set()  # To track currently pressed keys
        self.mouse_positions = []  # To track mouse positions for swipes
        self.recording_start_time = None
        self.keyboard_listener = None
        self.mouse_listener = None
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        # Create the GUI
        self.root = root
        self.root.title("Macro Recorder")
        
        self.action_listbox = tk.Listbox(root, height=10, width=40)
        self.action_listbox.pack(pady=10)
        
        self.record_button = tk.Button(root, text="Start Recording", command=self.start_recording)
        self.record_button.pack()
        
        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording)
        self.stop_button.pack()
        
        self.replay_button = tk.Button(root, text="Replay", command=self.replay)
        self.replay_button.pack()

    def clear_action_listbox(self):
        self.action_listbox.delete(0, tk.END)

    def simulate_key_down(self, key_text):
        try:
            key_code = key_text.replace("'", "")
            keyboard_lib.press_and_release(key_code)  # Simulate key press and release
        except Exception as e:
            print(f"Failed to simulate key down: {e}")

    def on_mouse_move(self, x, y):
        if self.is_recording:
            elapsed = time.time() - self.recording_start_time
            self.mouse_positions.append(f"MouseMove: {x};{y};{int(elapsed * 1000)}ms")

    def on_click(self, x, y, button, pressed):
        if self.is_recording and pressed:
            if button == mouse.Button.left:
                action_type = "LeftClick"
            elif button == mouse.Button.right:
                action_type = "RightClick"
            else:
                action_type = "UnknownClick"

            elapsed = time.time() - self.recording_start_time
            self.recorded_actions.append(f"{action_type}: {x};{y} at {int(elapsed * 1000)}ms")
            self.action_listbox.insert(tk.END, f"{action_type}: {x};{y} at {int(elapsed * 1000)}ms")

    def start_recording(self):
        self.is_recording = True
        self.recorded_actions.clear()
        self.clear_action_listbox()  # Clear the action listbox
        self.pressed_keys.clear()  # Clear pressed keys
        self.mouse_positions.clear()  # Clear mouse positions
        self.recording_start_time = time.time()
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_down, on_release=self.on_key_up)
        self.mouse_listener = MouseListener(on_click=self.on_click, on_move=self.on_mouse_move)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
    def on_key_down(self, key):
        if self.is_recording:
            try:
                key_text = key.char  # Only record printable characters
            except AttributeError:
                key_text = str(key)

            if key_text not in self.pressed_keys:
                elapsed = time.time() - self.recording_start_time
                self.pressed_keys.add(key_text)
                self.recorded_actions.append(f"KeyDown: {key_text} at {int(elapsed * 1000)}ms")
                self.action_listbox.insert(tk.END, f"KeyDown: {key_text} at {int(elapsed * 1000)}ms")
                # Simulate holding the key down immediately
                self.simulate_key_down(key_text)

    def on_key_up(self, key):
        if self.is_recording:
            try:
                key_text = key.char  # Only record printable characters
            except AttributeError:
                key_text = str(key)

            if key_text in self.pressed_keys:
                elapsed = time.time() - self.recording_start_time
                self.pressed_keys.remove(key_text)
                self.recorded_actions.append(f"KeyUp: {key_text} at {int(elapsed * 1000)}ms")
                self.action_listbox.insert(tk.END, f"KeyUp: {key_text} at {int(elapsed * 1000)}ms")
                # Simulate releasing the key immediately
                self.simulate_key_up(key_text)

    def simulate_key_up(self, key_text):
        # Since 'keyboard_lib' does not have a direct 'release' method, we do nothing for key release in this case
        pass

    def stop_recording(self):
        self.is_recording = False
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def replay(self):
        for action in self.recorded_actions:
            action_parts = action.split(": ", 1)
            if len(action_parts) == 2:
                action_type, action_details = action_parts
                if action_type == "KeyDown":
                    key_text, elapsed = action_details.split(" at ")
                    self.simulate_key_down(key_text)
                elif action_type in ["LeftClick", "RightClick"]:  # Handle left and right-click
                    coords, elapsed = action_details.split(" at ")
                    x, y = map(int, coords.split(" at ")[0].split(";"))
                    button = mouse.Button.left if action_type == "LeftClick" else mouse.Button.right
                    self.simulate_mouse_click(x, y, button, int(elapsed.replace("ms", "")) / 10000)
                elif action_type == "Scroll":  # Handle scrolling
                    parts = action_details.split(";")
                    if len(parts) == 3:
                        dx, dy, elapsed = parts
                        self.simulate_scroll(int(dx), int(dy), int(elapsed.replace("ms", "")) / 10000)
                elif action_type == "MouseMove":
                    x, y, elapsed = action_details.split(";")
                    self.simulate_mouse_move(int(x), int(y), int(elapsed.replace("ms", "")) / 10000)
            else:
                # Handle improperly formatted actions here
                print(f"Skipping improperly formatted action: {action}")

    def simulate_mouse_click(self, x, y, button, delay):
        time.sleep(delay)
        try:
            self.mouse.position = (x, y)
            self.mouse.click(button, 1)
        except Exception as e:
            print(f"Failed to simulate mouse click: {e}")

    def simulate_scroll(self, dx, dy, delay):
        time.sleep(delay)
        try:
            pyautogui.scroll(dx, dy)
        except Exception as e:
            print(f"Failed to simulate scroll: {e}")

    def simulate_mouse_move(self, x, y, delay):
        time.sleep(delay)
        try:
            self.mouse.position = (x, y)
        except Exception as e:
            print(f"Failed to simulate mouse move: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    macro_recorder = MacroRecorder(root)
    root.mainloop()
