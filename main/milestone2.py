import camera
import kinematics
import math
import time


def main():
    cam = camera.SetCam()
    mot = kinematics.Motion()
    dist = input('enter value in mm:')

    mot.step_left(100)
    mot.step_forward(100)
    mot.rotate_cw(90)

    time.sleep(5)

    for _i in range(0,500):
        mot.step_left(1)


    move = cam.determine_move(dist)

    if move[0] == -1:
         for _i in range(0,dist):
            mot.step_right(1)
        
    if move[0] == 1:
        for _i in range(0,dist):
            mot.step_left(1)

    if move[0] == 0:
        return("DONE")

main()
