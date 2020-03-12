import camera
import kinematics

class milestone2:

    def __init__(self):
        self.cam = camera.SetCam()
        self.mot = kinematics.Motion()
        self.dist = input('enter value in mm:')
    
    def main(self):

        move = self.cam.determine_move(self.dist)

        if move[0] == -1:
            self.mot.step_left(move[1])
        
        if move[0] == 1:
            self.mot.step_right(move[1])

        if move[0] == 0:
            return("DONE")
