from subprocess import call

class Indicator:
    def __init__(self):
        pass
    def located(self):
        call(["mpv", ".mp3"])
    def delivered(self):
        call(["mpv", ".mp3"])
    def inserted(self):
        call(["mpv", ".mp3"])
