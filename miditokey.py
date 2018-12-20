# encoding: utf-8


'''
author: Taehong Kim
email: peppy0510@hotmail.com
'''


import mido
import pyautogui
import threading
import time

# pyautogui.press('a')
# pyautogui.typewrite('quick brown fox')
# for i in range(10):
#     pyautogui.hotkey('alt', 'ctrl', 'shift', 'w')

pyautogui.PAUSE = 0.0


class RepeatHandler():

    def __init__(self, hotkey):
        self.hotkey = hotkey
        self.timestamp = time.time()


class MidiKey():

    def __init__(self):
        self.repeats = []

    def timer(self):
        while True:
            time.sleep(0.001)
            timestamp = time.time()
            for repeat in self.repeats:
                if timestamp < repeat.timestamp + 0.5:
                    continue
                pyautogui.hotkey(*repeat.hotkey)

    def insert_repeat(self, hotkey):
        self.repeats += [RepeatHandler(hotkey)]

    def remove_repeat(self, hotkey):
        for i in range(len(self.repeats) - 1, -1, -1):
            if self.repeats[i].hotkey == hotkey:
                self.repeats.pop(i)

    def handle_notes(self, msg, notes, hotkey):
        if msg.note in notes:
            if msg.type == 'note_on':
                pyautogui.hotkey(*hotkey)
                self.insert_repeat(hotkey)
            if msg.type == 'note_off':
                self.remove_repeat(hotkey)

    def frame(self, msg):
        print(msg)

        if msg.type.startswith('note'):

            if msg.note in (41,):
                self.handle_notes(msg, (41,), ('ctrl', 'alt', 'shift', '1',))

            if msg.note in (43,):
                self.handle_notes(msg, (43,), ('ctrl', 'alt', 'shift', 'q',))

            if msg.note in (45,):
                self.handle_notes(msg, (45,), ('ctrl', 'alt', 'shift', 'w',))

            if msg.note in (47,):
                self.handle_notes(msg, (47,), ('ctrl', 'alt', 'shift', '2',))

        # if msg.type == 'control_change' and msg.control in (16, 26) and msg.value == 127:
        #     pyautogui.hotkey('ctrl', 'alt', 'shift', '1')
        # if msg.type == 'control_change' and msg.control in (16, 26) and msg.value == 1:
        #     pyautogui.hotkey('ctrl', 'alt', 'shift', '2')

        # if msg.type == 'control_change' and msg.control in (17, 27) and msg.value == 127:
        #     pyautogui.hotkey('ctrl', 'alt', 'shift', 'q')
        # if msg.type == 'control_change' and msg.control in (17, 27) and msg.value == 1:
        #     pyautogui.hotkey('ctrl', 'alt', 'shift', 'w')

    def run(self):

        self.timer_thread = threading.Thread(target=self.timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()

        with mido.open_input() as inport:
            for msg in inport:
                self.frame(msg)


if __name__ == '__main__':
    midikey = MidiKey()
    midikey.run()
