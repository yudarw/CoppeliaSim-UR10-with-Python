import sim
import time

class CoppeliaSim:
    clientId = 0

    def __init__(self):
        self.clientID = 0

    def connect(self, port):
        sim.simxFinish(-1)
        self.clientID = sim.simxStart('127.0.0.1', port, True, True, 5000, 5)
        CoppeliaSim.clientId = self.clientID
        if self.clientID != -1:
            sim.simxStartSimulation(self.clientID, sim.simx_opmode_blocking)
            print('Connected to remote API server')
        else:
            print('Failed connecting to remote API server')

    def get_object_handle(self, obj_name):
        res, handle = sim.simxGetObjectHandle(self.clientID, obj_name, sim.simx_opmode_blocking)
        return handle


class Robot(CoppeliaSim):

    def __init__(self, robot_name):
        self.clientID = CoppeliaSim.clientId
        self.robot_name = robot_name
        self.targetName = "./" + robot_name + '/ikTarget'
        self.ftSensorName = './' + robot_name + '/force_sensor'

        # Retrieve object handle
        res, self.robot_handle = sim.simxGetObjectHandle(self.clientID, robot_name, sim.simx_opmode_blocking)
        res, self.target_handle = sim.simxGetObjectHandle(self.clientID, self.targetName, sim.simx_opmode_blocking)
        res, self.ftSensor_handle = sim.simxGetObjectHandle(self.clientID, self.ftSensorName, sim.simx_opmode_blocking)

        # Start position data streaming
        self.script = '/' + robot_name
        sim.simxCallScriptFunction(self.clientID, self.script,
                                   sim.sim_scripttype_childscript,
                                   'remoteApi_getPosition',
                                   [], [], [], '',
                                   sim.simx_opmode_streaming)
        # Moving status data streaming
        sim.simxGetInt32Signal(self.clientID, 'moving_status', sim.simx_opmode_streaming)
        sim.simxGetStringSignal(self.clientID, 'test_signal', sim.simx_opmode_streaming)

        time.sleep(0.05)

    def read_object_handle(self):
        print('Robot handle  = %d' % self.robot_handle)
        print('Target handle = %d' % self.target_handle)

    def get_object_position(self, obj_name):
        res, handle = sim.simxGetObjectHandle(self.clientID, obj_name, sim.simx_opmode_blocking)
        res, pos = sim.simxGetObjectPosition(self.clientID, handle, self.robot_handle, sim.simx_opmode_oneshot_wait)
        res, ori = sim.simxGetObjectOrientation(self.clientID, handle, self.robot_handle, sim.simx_opmode_oneshot_wait)
        ret = [0, 0, 0, 0, 0, 0]
        for i in range(3):
            ret[i] = pos[i] * 1000
            ret[i + 3] = ori[i] * 180 / 3.14
        return ret

    def read_position(self):
        ret = sim.simxCallScriptFunction(self.clientID, self.script,
                                         sim.sim_scripttype_childscript,
                                         'remoteApi_getPosition',
                                         [], [], [], '',
                                         sim.simx_opmode_buffer)
        posData = ret[2]
        for i in range(3):
            posData[i] = posData[i] * 1000
            posData[i + 3] = posData[i + 3] * 180 / 3.14
        return posData

    def set_position(self, pos):
        cmdPos = [0, 0, 0, 0, 0, 0]
        for i in range(3):
            cmdPos[i] = pos[i] / 1000
            cmdPos[i + 3] = pos[i + 3] * 3.141592 / 180

        ret = sim.simxCallScriptFunction(self.clientID, self.script,
                                         sim.sim_scripttype_childscript,
                                         'remoteApi_movePosition',
                                         [], cmdPos, [], '',
                                         sim.simx_opmode_blocking)

    def set_position2(self, pos, wait):
        self.set_position(pos)
        if wait:
            while True:
                time.sleep(0.05)
                if self.isMoving() == 'NOT_MOVING':
                    break

    # Check whether the robot is moving
    def isMoving(self):
        ret, s = sim.simxGetStringSignal(self.clientID, 'test_signal', sim.simx_opmode_buffer)
        s = s.decode('ascii')
        return s

    # Set Robot Speed: 0 - 100
    def set_speed(self, velocity):
        ret = sim.simxCallScriptFunction(self.clientID, self.script,
                                         sim.sim_scripttype_childscript,
                                         'remoteApi_setSpeed',
                                         velocity, [], [], '',
                                         sim.simx_opmode_blocking)

    # Set Robot Gripper ON-OFF
    def gripper(self, state):
        ret = sim.simxCallScriptFunction(self.clientID, self.script,
                                         sim.sim_scripttype_childscript,
                                         'remoteApi_setGripper',
                                         state, [], [], '',
                                         sim.simx_opmode_blocking)
