# playback_script.py
import pynput.keyboard as keyboard
import mouse
import json
import time

# Load events from the file
with open('events.json', 'r') as f:
    events = json.load(f)

keyboard_controller = keyboard.Controller()

# Function to start playback
def start_playback():
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
            mouse.move(event['x'], event['y'], absolute=True)
        elif event['type'] == 'click':
            button = 'left' if event['button'] == 'Button.left' else 'right'
            if event['pressed']:
                mouse.press(button=button)
            else:
                mouse.release(button=button)
        elif event['type'] == 'scroll':
            mouse.wheel(event['dy'])
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