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
        _layout.addWidget(QLabel('Woah there! This is a no-no application! You can come back to this program after 15 seconds.'))
        _button = QPushButton('OK', self)
        _button.clicked.connect(self.click)
        _layout.addWidget(_button)


kill_set = {'vi', 'geeqie', 'jupyter-console'}
allow_set = set()

def kill_bad_processes(timeline,
                       kill_set,
                       global_blacklist={'flake8',
                                         'emacs',
                                         'systemd',
                                         'firefox'}):
    global allow_set
    for a in psutil.process_iter():
        try:
            nm = str(a.name())
            if nm in allow_set:
                continue
            if nm not in global_blacklist and nm in kill_set:
                temp = ''.join(nm)
                print(temp, flush=True)
                a.kill()
                def ding(progress):
                    global allow_set
                    if progress == 0:
                        allow_set.add(temp)
                    elif progress == 1:
                        allow_set.remove(temp)
                ex.event = Event(timeline.now + 10, 15, temp, ding)
                ex.show()
        except psutil.NoSuchProcess:
            pass

class ProcKiller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
    def run(self):
        global timeline
        timeline.start(time.process_time())
        while self.running:
            timeline.update_now(time.process_time())
            kill_bad_processes(timeline, kill_set)
            timeline.process()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(app)
    app.setStyle('Fusion')
    t = ProcKiller()
    try:
        t.start()
        app.exec()
    except KeyboardInterrupt:
        self.running = False

