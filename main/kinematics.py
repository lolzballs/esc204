class Motion:
    def __init__(self):
        # initialize daemons
        pass

    # solves forward kinematics system to return:
    # (x, y, yaw)
    def __forward(self):
        return (0, 0, 0)

    # solves inverse kinematics system to return
    # (stepper 1 angle, stepper 2 angle, stepper 3 angle)
    def __inverse(self, x, y, yaw, left_hand=False):
        return (0, 0, 0)

    # linear step right
    # relative to the end effector frame
    def step_right(self, steps=1):
        pass

    # linear step left 
    # relative to the end effector frame
    def step_left(self, steps=1):
        pass

    # linear step forward 
    # relative to the end effector frame
    def step_forward(self, steps=1):
        pass

    # linear step back 
    # relative to the end effector frame
    def step_back(self, steps=1):
        pass

    # rotate end effector cw
    def rotate_cw(self, angle=1):
        pass

    # rotate end effector ccw
    def rotate_ccw(self, angle=1):
        pass

    def get_pos(self):
        return self.__forward()

