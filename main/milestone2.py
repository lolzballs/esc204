import camera
import kinematics

class milestone2:

    def __init__(self):
        self.cam = camera.SetCam()
        self.mot = kinematics.Motion()

    def main(self):
        y = input('distance')

        move = self.cam.determine_move(y)

        if move[0] == -1:
            self.mot.step_left()
        
        if move[0] == 1:
            self.mot.step_right()
