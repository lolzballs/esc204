from subprocess import call

class Indicator:
    def __init__(self):
        pass
    def located(self):
        subprocess.call(["mpv", ".mp3"])
    def delivered(self):
        subprocess.call(["mpv", ".mp3"])
    def inserted(self):
        subprocess.call(["mpv", ".mp3"])
