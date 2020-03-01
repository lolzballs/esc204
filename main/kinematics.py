import subprocess

class Motion:
    def __init__(self):
        # initialize daemons
        self.servo = _servo([12, 0.025, 0.125], [13, 0, 1])
        #self.stepper = _stepperd(1000, 5370, 5370)

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

class _stepperd:
    def __init__(self, step_time, rot1, rot2):
        self.process = subprocess.Popen(["stepperd"], universal_newlines=True,\
                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.pending = None
        self.configure(step_time, rot1, rot2)


    def __block_pending(self):
        while self.pending != None:
            output = self.process.stdout.readline()
            if output == "done " + self.pending:
                self.pending = None

    def configure(self, step_time, rot1, rot2):
        self.__block_pending()

        self.pending = "configure"
        self.process.stdin.write("configure {} {} {}".format(step_time, rot1, rot2))
        self.process.stdin.flush()

    def set(self, step1, step2):
        self.__block_pending()

        self.pending = "set"
        self.process.stdin.write("set {} {}\n".format(step1, step2))
        self.process.stdin.flush()

class _servo:
    def __init__(self, joint, end):
        self.blaster = open('/dev/pi-blaster', 'w')
        self.joint = joint
        self.end = end

    def set_joint(self, angle):
        duty = (self.joint[2] - self.joint[1]) * (angle / 180.0) + self.joint[1]
        self.blaster.write("{}={}\n".format(self.joint[0], duty))
        self.blaster.flush()

