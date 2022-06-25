from coppeliasim import CoppeliaSim, Robot
import time

# add command to this file
# Cool I think this already connected to the file
# Another command to be updated to the server, check this if you are okay and see this change

sim = CoppeliaSim()
sim.connect(19997)

robot = Robot('UR10')
pos = robot.read_position()
print('Initial Robot Position: ', pos)

while True:
    pos1 = [400, 300, 200, 180, 0, 0]
    pos2 = [800, 300, 200, 180, 0, 0]
    pos3 = [800, -300, 200, 180, 15, 0]
    pos4 = [400, -300, 200, 180, -15, 0]
    robot.set_position2(pos1, True)
    robot.set_position2(pos2, True)
    robot.set_position2(pos3, True)
    robot.set_position2(pos4, True)
