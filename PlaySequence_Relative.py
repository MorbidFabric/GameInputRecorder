# playback_script.py
import pynput.keyboard as keyboard
import win32api
import win32con
import json
import time

# Load events from the file
try:
    with open('./projects/input_events.json', 'r') as f:
        events = json.load(f)
except FileNotFoundError:
    print("Error: events.json file not found.")
    events = []
except json.JSONDecodeError:
    print("Error: events.json file is not properly formatted.")
    events = []

keyboard_controller = keyboard.Controller()

# Function to start playback
def start_playback():
    if not events:
        print("Error: No events to playback.")
        return

    start_time = events[0]['time']
    playback_start_time = time.time()

    for event in events:
        event_time = event['time']
        elapsed_time = event_time - start_time
        current_time = time.time()
        time_to_wait = playback_start_time + elapsed_time - current_time

        if time_to_wait > 0:
            time.sleep(time_to_wait)

        if event['type'] == 'move':
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, event['dx'], event['dy'], 0, 0)
        elif event['type'] == 'click':
            button_down = win32con.MOUSEEVENTF_LEFTDOWN if event['button'] == 'Button.left' else win32con.MOUSEEVENTF_RIGHTDOWN
            button_up = win32con.MOUSEEVENTF_LEFTUP if event['button'] == 'Button.left' else win32con.MOUSEEVENTF_RIGHTUP
            if event['pressed']:
                win32api.mouse_event(button_down, 0, 0)
            else:
                win32api.mouse_event(button_up, 0, 0)
        elif event['type'] == 'scroll':
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, event['dy'], 0)
        elif event['type'] == 'key_press':
            key = getattr(keyboard.Key, event['key'].split('.')[1]) if 'Key.' in event['key'] else event['key'].strip("'")
            keyboard_controller.press(key)
        elif event['type'] == 'key_release':
            key = getattr(keyboard.Key, event['key'].split('.')[1]) if 'Key.' in event['key'] else event['key'].strip("'")
            keyboard_controller.release(key)

# Function to handle key press events
def on_press(key):
    if key == keyboard.Key.f7:
        print("F7 pressed, starting playback")
        return False  # Stop the listener

# Wait for F7 key press to start playback
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()
keyboard_listener.join()

# Start playback after F7 is pressed
start_playback()