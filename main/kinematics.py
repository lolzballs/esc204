import math
import subprocess

LINK1_LEN = 0.5
LINK2_LEN = 0.5
LINK3_LEN = 0.1

# solves forward kinematics system to return:
# (x, y, yaw)
def _forward(a1, a2, a3):
    x = LINK1_LEN * math.cos(a1) + LINK2_LEN * math.cos(a1 + a2) + \
            LINK3_LEN * math.cos(a1 + a2 + a3)
    y = LINK1_LEN * math.sin(a1) + LINK2_LEN * math.sin(a1 + a2) + \
            LINK3_LEN * math.sin(a1 + a2 + a3)

    return (x, y, a1 + a2 + a3)

# solves inverse kinematics system to return
# (stepper 1 angle, stepper 2 angle, stepper 3 angle)
def _inverse(x, y, phi, right_hand=False):
    xb = x - LINK3_LEN * math.cos(phi)
    yb = y - LINK3_LEN * math.sin(phi)
    gamma2 = xb ** 2 + yb ** 2
    gamma = math.sqrt(gamma2)

    alpha = math.atan2(yb, xb)
    beta = math.acos((LINK1_LEN ** 2 + LINK2_LEN ** 2 - gamma2) / (2 * LINK1_LEN * LINK2_LEN))
    c = math.acos((gamma2 + LINK1_LEN ** 2  - LINK2_LEN ** 2) / (2 * gamma * LINK1_LEN))

    a1 = alpha - c
    a2 = math.pi - beta
    a3 = phi - a1 - a2

    if right_hand:
        a1 = a1 + 2 * c
        a2 = -a2
        a3 = phi - a1 - a2

    return (a1, a2, a3)

class Motion:
    def __init__(self):
        # initialize daemons
        self.servo = _servo([12, 0.025, 0.125], [13, 0, 1])
        #self.stepper = _stepperd(1000, 5370, 5370)

        # set to initial state
        self.a1, self.a2, self.a3 = _inverse(-0.5, -0.1, 0)

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
        return _forward(self.a1, self.a2, self.a3)

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

