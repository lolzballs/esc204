import math
import subprocess
import time

LINK1_LEN = 500
LINK2_LEN = 500
LINK3_LEN = 100

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
        self.servo = _servo([13, 0.025, 0.125], [6, 0, 1])
        self.stepper = _stepperd(1000, 5370, 5370)

        # set to initial state
        self.a1, self.a2, self.a3 = _inverse(1100, 0, 0)
        self.x, self.y, self.phi = _forward(self.a1, self.a2, self.a3)
        self.servo.set_joint(self.a3)

    # linear step right
    # relative to the end effector frame
    def step_right(self, steps=1):
        # TODO: relativity
        self.x += steps
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            self.x -= steps
            return
        self.update_system()

    # linear step left 
    # relative to the end effector frame
    def step_left(self, steps=1):
        # TODO: relativity
        self.x -= steps
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            print("out of range")
            self.x += steps
            return
        self.update_system()

    # linear step forward 
    # relative to the end effector frame
    def step_forward(self, steps=1):
        # TODO: relativity
        self.y += steps
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            self.y -= steps
            return False
        self.update_system()
        return True

    # linear step back 
    # relative to the end effector frame
    def step_back(self, steps=1):
        # TODO: relativity
        self.y -= steps
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            print("out of range")
            self.y += steps
            return
        self.update_system()

    # rotate end effector cw
    def rotate_cw(self, angle=1):
        # TODO: Modular arithmetic
        self.phi += angle * math.pi / 180
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            print("out of range")
            self.phi -= angle * math.pi / 180
            return
        self.update_system()

    # rotate end effector ccw
    def rotate_ccw(self, angle=1):
        # TODO: Modular arithmetic
        self.phi -= angle * math.pi / 180
        try:
            self.a1, self.a2, self.a3 = _inverse(self.x, self.y, self.phi, False)
        except:
            print("out of range")
            self.phi += angle * math.pi / 180
            return
        self.update_system()

    def update_system(self):
        self.stepper.set(-self.a1 * 5370 / (2 * math.pi), -self.a2 * 5370 / (2 * math.pi))
        self.servo.set_joint(self.a3)

class _stepperd:
    def __init__(self, step_time, rot1, rot2):
        self.process = subprocess.Popen(["stepperd"], universal_newlines=True,\
                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.pending = None
        self.configure(step_time, rot1, rot2)

    def __block_pending(self):
        while self.pending != None:
            output = self.process.stdout.readline().strip().strip('\0')
            if output == self.pending + " done":
                self.pending = None

    def configure(self, step_time, rot1, rot2):
        self.__block_pending()

        self.pending = "configure"
        self.process.stdin.write("configure {} {} {}\n".format(step_time, rot1, rot2))
        self.process.stdin.flush()

    def set(self, step1, step2):
        self.__block_pending()

        self.pending = "set"
        self.process.stdin.write("set {} {}\n".format(int(round(step1)), int(round(step2))))
        self.process.stdin.flush()

class _servo:
    def __init__(self, joint, end):
        self.blaster = open('/dev/pi-blaster', 'w')
        self.joint = joint
        self.end = end

    def set_joint(self, angle):
        angle = angle * 180 / math.pi
        duty = (self.joint[2] - self.joint[1]) * ((angle + 90) / 180.0) + self.joint[1]
        self.blaster.write("{}={}\n".format(self.joint[0], duty))
        self.blaster.flush()

    def kill_joint(self):
        self.blaster.write("{}=0\n".format(self.joint[0]))
        self.blaster.flush()
