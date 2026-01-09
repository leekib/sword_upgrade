import pyautogui
import time

def print_mouse_position():
    print("Press Ctrl+C to stop.")
    try:
        while True:
            x, y = pyautogui.position()
            position_str = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(position_str, end='')
            print('\b' * len(position_str), end='', flush=True)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\nDone.')

if __name__ == "__main__":
    print_mouse_position()
