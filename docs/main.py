#!/bin/env python

from functools import reduce
import os
import psutil
import sys
import threading
import time
import traceback
from random import randint
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

ex = None # a window

def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Event:
    def __init__(self, when, duration, name, act):
        self.when = when
        self.duration = duration
        self.name = name
        self._act = act
    def act(self, progress):
        self._act(progress)
    def __str__(self):
        return '(' + self.name + ': ' + str(self.when) + ', ' + str(self.duration) + ')'
    def repr(self):
        return self.__str__()

class Timeline:
    def __init__(self):
        self.start_time = 0
        self.now = 0
        self.prev = 0
        self.future = []
        self.present = []

    def update_now(self, now):
        self.prev = self.now
        self.now = now
    def start(self, now):
        self.start_time = now
        self.update_now(now)
    def elapsed(self):
        return self.now - self.start_time
    def diff(self):
        return self.now - self.prev
    def add(self, event):
        if event.name not in [f.name for f in self.future]:
            self.future.append(event)
            self.future.sort(key=lambda x: x.when)
    def process(self):
        elapsed = self.elapsed()
        i = 0
        rrrr = randint(1, 100)
        while i < len(self.present):
            p = self.present[i]
            progress = (elapsed - p.when) / p.duration
            if progress >= 1:
                progress = 1
            p.act(progress)
            if progress == 1:
                self.present.pop(i)
            else:
                i += 1
        while i < len(self.future) and self.future[0].when <= elapsed:
            if self.future[i].name not in [p.name for p in self.present]:
                self.future[i].act(0)
                self.present.append(self.future[0])
                self.future.pop(0)

timeline = Timeline()

class App(QWidget):
    def __init__(self, app):
        super().__init__()
        self.title = 'Woah There!'
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(), app.desktop().availableGeometry()))
        self.msg_label = QLabel('Woah there! This is a no-no application! You can come back to this program after 15 seconds.')
        self.initUI()
        self.event = Event(0, 0, '', lambda x: None)

    def closeEvent(self, e):
        QApplication.instance().quit()
        e.accept()

    def click(self, e):
        global timeline
        timeline.add(self.event)
        self.hide()
        
    def initUI(self):
        global timeline
        self.setWindowTitle(self.title)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        _layout = QVBoxLayout()
        self.setLayout(_layout)
        _layout.addWidget(self.msg_label)
        _button = QPushButton('OK', self)
        _button.clicked.connect(self.click)
        _layout.addWidget(_button)


program_kill_set = {('vi', 15), ('geeqie', 10), ('gnome-manual-duplex', 20)}
program_allow_set = set()

def kill_bad_processes(timeline,
                       kill_set,
                       global_blacklist={'flake8',
                                         'emacs',
                                         'systemd',
                                         'firefox'}):
    global program_allow_set
    for a in psutil.process_iter():
        try:
            nm = a.name()
            if nm in program_allow_set:
                continue
            if nm not in global_blacklist and nm in (l for l, r in kill_set):
                temp = ''.join(nm)
                print('program killed', temp, flush=True)
                a.kill()
                l, r = [(l, r) for l, r in kill_set if l == temp][0]
                def ding(progress):
                    global program_allow_set
                    if progress == 0:
                        program_allow_set.add(temp)
                    elif progress == 1:
                        program_allow_set.remove(temp)
                ex.event = Event(timeline.now + r, 15, temp, ding)
                ex.msg_label.setText('Woah there! You cannot use this program for another ' + str(r) + ' seconds!')
                ex.show()
        except psutil.NoSuchProcess:
            pass

site_block_set = {('reddit.com', 10), ('amazon.com', 15), ('dmoj.com', 20)}
website_allow_set = set()

def block_bad_websites(timeline,
                       block_set,
                       curr_site,
                       global_blacklist={'localhost'}):
    global website_allow_set
    if curr_site not in global_blacklist and curr_site in (l for l, r in block_set):
        temp = ''.join(curr_site)
        l, r = [(l, r) for l, r in block_set if l == curr_site][0]
        def ding(progress):
            global program_allow_set
            if progress == 0:
                website_allow_set.add(temp)
                print('site remove', temp, flush=True)
                perror('python: site remove', temp)
            elif progress == 1:
                website_allow_set.remove(temp)
                print('site add', temp, flush=True)
        ex.event = Event(timeline.now + r, 15, temp, ding)
        ex.msg_label.setText('Woah there! You cannot visit this site for another ' + str(r) + ' seconds!')
        ex.show()


class ProcKiller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    def run(self):
        global timeline
        timeline.start(time.process_time())
        while self.running:
            timeline.update_now(time.process_time())
            kill_bad_processes(timeline, program_kill_set)
            timeline.process()


class IManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    def run(self):
        while self.running:
            cmd = input().split()
            def manage_set(st, args):
                global timeline
                if args[0] == 'set':
                    st.clear()
                    for a, b in ((a, b) for a, b, i in zip(args[1:], args[2:], range(len(args))) if i % 2 == 0):
                        st.add((a, int(b)))
            if cmd[0] == 'site':
                if cmd[1] == 'set':
                    manage_set(site_block_set, cmd[1:])
                    perror(site_block_set)
                elif cmd[1] == 'block':
                    block_bad_websites(timeline, site_block_set, cmd[2])
                    perror(site_block_set, cmd[2])
            elif cmd[0] == 'program':
                if cmd[1] == 'set':
                    manage_set(program_kill_set, cmd[1:])
            elif cmd[0] == 'kill':
                self.running = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(app)
    app.setStyle('Fusion')
    pt = ProcKiller()
    im = IManager()
    try:
        pt.start()
        im.start()
        app.exec()
    except KeyboardInterrupt:
        self.running = False

