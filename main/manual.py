import curses
import signal
import kinematics
import math

def to_degrees(rad):
    return rad * 180 / math.pi

def main(stdscr):
    mot = kinematics.Motion()

    stdscr.box(10, 10)

    stdscr.addstr(0, 10, "Hit 'q' to quit")
    stdscr.refresh()
    stdscr.timeout(100)

    while True:
        stdscr.addstr(5, 0, "X: {}, Y: {}, Phi: {}".format(mot.x, mot.y, mot.phi))
        stdscr.addstr(6, 0, "a1: {:2f}, a2: {:2f}, a3: {:2f}".format(to_degrees(mot.a1), to_degrees(mot.a2), to_degrees(mot.a3)))
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('a'):
            mot.step_left()
        elif key == ord('d'):
            mot.step_right()
        elif key == ord('s'):
            mot.step_back()
        elif key == ord('w'):
            mot.step_forward()
        elif key == ord('q'):
            mot.rotate_ccw()
        elif key == ord('e'):
            mot.rotate_cw()

        stdscr.erase()

curses.wrapper(main)

