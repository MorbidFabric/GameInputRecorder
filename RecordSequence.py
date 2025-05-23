import pynput.mouse as mouse
import pynput.keyboard as keyboard
import json
import time

events = []
recording = False

def on_move(x, y):
    if recording:
        events.append({'type': 'move', 'x': x, 'y': y, 'time': time.time()})

def on_click(x, y, button, pressed):
    if recording:
        events.append({'type': 'click', 'x': x, 'y': y, 'button': str(button), 'pressed': pressed, 'time': time.time()})

def on_scroll(x, y, dx, dy):
    if recording:
        events.append({'type': 'scroll', 'x': x, 'y': y, 'dx': dx, 'dy': dy, 'time': time.time()})

def on_press(key):
    global recording
    if key == keyboard.Key.f6:
        recording = not recording
        if recording:
            print("Recording started")
        else:
            print("Recording stopped")
            return False  # Stop the listener
    if recording:
        events.append({'type': 'key_press', 'key': str(key), 'time': time.time()})

def on_release(key):
    if recording:
        events.append({'type': 'key_release', 'key': str(key), 'time': time.time()})

mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)

mouse_listener.start()
keyboard_listener.start()

keyboard_listener.join()  # Wait for the keyboard listener to stop

with open('Absolute_events.json', 'w') as f:
    json.dump(events, f)

mouse_listener.stop()
keyboard_listener.stop()