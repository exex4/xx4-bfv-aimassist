from lib import BFV
import time
import math
from ctypes import *

debug = 1


class Aimer:
    tick = 0
    closestDistance = 9999
    closestSoldier = None
    closestSoldierMovementX = 0
    closestSoldierMovementY = 0
    lastSoldier = 0
    screensize = (0, 0)

    def __init__(self, screensize, trigger, distance_limit, fov):
        self.screensize = screensize
        self.trigger = trigger
        self.distance_limit = distance_limit
        self.fov = fov

    def DebugPrintMatrix(self, mat):
        print("[%.3f %.3f %.3f %.3f ]" % (mat[0][0], mat[0][1], mat[0][2], mat[0][3]))
        print("[%.3f %.3f %.3f %.3f ]" % (mat[1][0], mat[1][1], mat[1][2], mat[1][3]))
        print("[%.3f %.3f %.3f %.3f ]" % (mat[2][0], mat[2][1], mat[2][2], mat[2][3]))
        print("[%.3f %.3f %.3f %.3f ]\n" % (mat[3][0], mat[3][1], mat[3][2], mat[3][3]))

    def DebugPrintVec4(self, Vec4):
        print("[%.3f %.3f %.3f %.3f ]\n" % (Vec4[0], Vec4[1], Vec4[2], Vec4[3]))

    def accelDistance(self, distance):
        leftMin = 0
        rightMin = 0.5
        leftSpan = 100 - 0
        rightSpan = 1.2 - 0.5

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(distance - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

        # return 0.0 + (distance - 0) / 20 * 100

    def start(self):
        print("+ Searching for BFV.exe")
        phandle = BFV.get_handle()
        if phandle:
            time.sleep(1)
        else:
            print("- Error: Cannot find BFV.exe")
            exit(1)

        print("+ BFV.exe found, Handle 0x%x" % phandle)
        cnt = 0
        # mouse = Controller()
        self.lastSoldier = 0
        self.lastX = 0
        self.lastY = 0
        # m = Mouse()
        while 1:
            BFV.process(phandle, cnt)
            cnt += 1

            data = BFV.gamedata
            self.closestDistance = 9999
            self.closestSoldier = None
            self.closestSoldierMovementX = 0
            self.closestSoldierMovementY = 0

            if self.lastSoldier is not 0:
                if cdll.user32.GetAsyncKeyState(self.trigger) & 0x8000:
                    found = False
                    for Soldier in data.soldiers:
                        if self.lastSoldier == Soldier.ptr:
                            found = True
                            try:
                                dw, distance, delta_x, delta_y, Soldier.ptr, dfc = self.calcAim(data, Soldier)
                                self.closestDistance = dfc
                                self.closestSoldier = Soldier
                                # accel = self.accelDistance(distance)
                                # print(accel)
                                accel = 0  # this is WIP
                                self.closestSoldierMovementX = delta_x + (self.lastX * accel)
                                self.closestSoldierMovementY = delta_y + (self.lastY * accel)
                                self.lastX = delta_x
                                self.lastY = delta_y
                                # print("x: %s" % delta_x)
                            except Exception as e:
                                self.lastSoldier = 0
                                self.closestSoldier = None
                                print("Disengaging: soldier no longer meets criteria: %s" % e)
                    if not found:
                        self.lastSoldier = 0
                        self.closestSoldier = None
                        self.lastX = 0
                        self.lastY = 0
                        print("Disengaging: soldier no longer found")
                else:
                    self.lastSoldier = 0
                    self.closestSoldier = None
                    self.lastX = 0
                    self.lastY = 0
                    print("Disengaging: key released")
            else:
                for Soldier in data.soldiers:
                    try:
                        dw, distance, delta_x, delta_y, Soldier.ptr, dfc = self.calcAim(data, Soldier)
                        # if Soldier.ptr == 0x1d66c06f0 or Soldier.ptr == 0x183ba54b0:
                        #    print("Soldier: %s is dfc: %s, distance is %s" % (hex(Soldier.ptr), dfc, distance))
                        if dw > self.fov:
                            continue
                        if Soldier.occluded:
                            continue

                        if self.distance_limit is not None and distance > self.distance_limit:
                            continue

                        if dfc < self.closestDistance:  # is actually comparing dfc, not distance
                            if cdll.user32.GetAsyncKeyState(self.trigger) & 0x8000:
                                # print("COMPARE - Soldier: %s is dfc: %s, distance is %s" % (hex(Soldier.ptr), dfc, distance))
                                self.closestDistance = dfc
                                self.closestSoldier = Soldier
                                self.closestSoldierMovementX = delta_x
                                self.closestSoldierMovementY = delta_y
                                self.lastSoldier = Soldier.ptr
                                self.lastX = delta_x
                                self.lastY = delta_y

                    except:
                        # print("Exception", sys.exc_info()[0])
                        continue
                if self.lastSoldier != 0:
                    print("Locking onto soldier: 0x%x" % self.lastSoldier)

            if self.closestSoldier is not None:
                if cdll.user32.GetAsyncKeyState(self.trigger) & 0x8000:
                    if self.closestSoldierMovementX > self.screensize[0] / 2 or self.closestSoldierMovementY > \
                            self.screensize[1] / 2:
                        if debug: print("continue1")
                        continue
                    else:
                        if abs(self.closestSoldierMovementX) > self.screensize[0]:
                            if debug: print("continue2")
                            continue
                        if abs(self.closestSoldierMovementY) > self.screensize[1]:
                            if debug: print("continue3")
                            continue
                        if self.closestSoldierMovementX == 0 and self.closestSoldierMovementY == 0:
                            continue

                        self.move_mouse(int(self.closestSoldierMovementX), int(self.closestSoldierMovementY))

                        time.sleep(0.02)

    def calcAim(self, data, Soldier):

        transform = Soldier.head
        x, y, w = self.World2Screen(data.myviewmatrix, transform[0], transform[1], transform[2])
        distance = self.FindDistance(Soldier.transform[3][0], Soldier.transform[3][1], Soldier.transform[3][2],
                                     data.mytransform[3][0], data.mytransform[3][1], data.mytransform[3][2])

        dw = distance - w

        # if Soldier.occluded:
        #     raise Exception("Soldier is occluded")

        delta_x = (self.screensize[0] / 2 - x) * -1
        delta_y = (self.screensize[1] / 2 - y) * -1

        dfc = math.sqrt(delta_x ** 2 + delta_y ** 2)

        return dw, distance, delta_x / 2, delta_y / 2, Soldier.ptr, dfc

    def FindDistance(self, d_x, d_y, d_z, l_x, l_y, l_z):
        distance = math.sqrt((d_x - l_x) ** 2 + (d_y - l_y) ** 2 + (d_z - l_z) ** 2)
        return distance

    def World2Screen(self, MyViewMatrix, posX, posY, posZ):

        w = float(
            MyViewMatrix[0][3] * posX + MyViewMatrix[1][3] * posY + MyViewMatrix[2][3] * posZ + MyViewMatrix[3][3])

        x = float(
            MyViewMatrix[0][0] * posX + MyViewMatrix[1][0] * posY + MyViewMatrix[2][0] * posZ + MyViewMatrix[3][0])

        y = float(
            MyViewMatrix[0][1] * posX + MyViewMatrix[1][1] * posY + MyViewMatrix[2][1] * posZ + MyViewMatrix[3][1])

        mX = float(self.screensize[0] / 2)
        mY = float(self.screensize[1] / 2)

        x = float(mX + mX * x / w)
        y = float(mY - mY * y / w)

        return x, y, w

    def current_mouse_position(self):
        cursor = POINT()
        windll.user32.GetCursorPos(byref(cursor))
        return cursor.x, cursor.y

    def move_mouse(self, x, y):  # relative
        ii = Input_I()
        ii.mi = MouseInput(x, y, 0, 0x1, 0, pointer(c_ulong(0)))
        command = Input(c_ulong(0), ii)
        windll.user32.SendInput(1, pointer(command), sizeof(command))


PUL = POINTER(c_ulong)


class KeyBdInput(Structure):
    _fields_ = [("wVk", c_ushort),
                ("wScan", c_ushort),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(Structure):
    _fields_ = [("uMsg", c_ulong),
                ("wParamL", c_short),
                ("wParamH", c_ushort)]


class MouseInput(Structure):
    _fields_ = [("dx", c_long),
                ("dy", c_long),
                ("mouseData", c_ulong),
                ("dwFlags", c_ulong),
                ("time", c_ulong),
                ("dwExtraInfo", PUL)]


class POINT(Structure):
    _fields_ = [("x", c_long),
                ("y", c_long)]


class Input_I(Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(Structure):
    _fields_ = [("type", c_ulong),
                ("ii", Input_I)]
