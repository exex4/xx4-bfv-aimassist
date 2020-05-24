from lib import BFV
import time
import math
from pynput.mouse import Controller
from ctypes import *


class Aimer:
    tick = 0
    closestDistance = 999
    closestSoldier = None
    closestSoldierMovementX = 0
    closestSoldierMovementY = 0
    lastSoldier = 0
    screensize = (0, 0)

    def __init__(self, screensize):
        self.screensize = screensize

    def DebugPrintMatrix(self, mat):
        print("[%.3f %.3f %.3f %.3f ]" % (mat[0][0], mat[0][1], mat[0][2], mat[0][3]))
        print("[%.3f %.3f %.3f %.3f ]" % (mat[1][0], mat[1][1], mat[1][2], mat[1][3]))
        print("[%.3f %.3f %.3f %.3f ]" % (mat[2][0], mat[2][1], mat[2][2], mat[2][3]))
        print("[%.3f %.3f %.3f %.3f ]\n" % (mat[3][0], mat[3][1], mat[3][2], mat[3][3]))

    def DebugPrintVec4(self, Vec4):
        print("[%.3f %.3f %.3f %.3f ]\n" % (Vec4[0], Vec4[1], Vec4[2], Vec4[3]))

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
        mouse = Controller()
        self.lastSoldier = 0
        while 1:
            BFV.process(phandle, cnt)
            cnt += 1

            data = BFV.gamedata
            self.closestDistance = 999
            self.closestSoldier = None
            self.closestSoldierMovementX = 0
            self.closestSoldierMovementY = 0

            if self.lastSoldier is not 0:
                if cdll.user32.GetAsyncKeyState(0xa4) & 0x8000:
                    found = False
                    for Soldier in data.soldiers:
                        if self.lastSoldier == Soldier.ptr:
                            found = True
                            try:
                                w, dw, distance, delta_x, delta_y, Soldier.ptr = self.calcAim(data, Soldier)
                                self.closestDistance = distance
                                self.closestSoldier = Soldier
                                self.closestSoldierMovementX = delta_x
                                self.closestSoldierMovementY = delta_y
                            except Exception as e:
                                self.lastSoldier = 0
                                self.closestSoldier = None
                                print("Disengaging: soldier no longer meets criteria: %s" % e)
                    if not found:
                        self.lastSoldier = 0
                        self.closestSoldier = None
                        print("Disengaging: soldier no longer found")
                else:
                    self.lastSoldier = 0
                    self.closestSoldier = None
                    print("Disengaging: key released")
            else:
                for Soldier in data.soldiers:
                    try:
                        w, dw, distance, delta_x, delta_y, Soldier.ptr = self.calcAim(data, Soldier)
                        if dw > 2:
                            continue
                        max_movement = 550 - (500 * distance / 75)
                        if abs(delta_x) > max_movement or abs(delta_y) > max_movement:
                            continue
                        if dw < self.closestDistance:
                            if cdll.user32.GetAsyncKeyState(0xa4) & 0x8000:
                                self.closestDistance = distance
                                self.closestSoldier = Soldier
                                self.closestSoldierMovementX = delta_x
                                self.closestSoldierMovementY = delta_y
                                self.lastSoldier = Soldier.ptr

                    except:
                        continue
                if self.lastSoldier != 0:
                    print("Locking onto soldier: 0x%x" % self.lastSoldier)

            if self.closestSoldier is not None:
                if cdll.user32.GetAsyncKeyState(0xa4) & 0x8000:
                    mouse.move(self.closestSoldierMovementX, self.closestSoldierMovementY)
                    time.sleep(0.02)

    def calcAim(self, data, Soldier):

        transform = Soldier.head
        x, y, w = self.World2Screen(data.myviewmatrix, transform[0], transform[1], transform[2])
        distance = self.FindDistance(Soldier.transform[3][0], Soldier.transform[3][1], Soldier.transform[3][2],
                                 data.mytransform[3][0], data.mytransform[3][1], data.mytransform[3][2])

        dw = distance - w
        # if dw > 2:
        #     raise Exception

        if distance > 75:
            raise Exception("distance exceeded")

        if Soldier.occluded:
            raise Exception("Soldier is occluded")

        delta_x = (1280 - x) * -1
        delta_y = (720 - y) * -1

        # max_movement = 550 - (500 * distance / 75)
        # if abs(delta_x) > max_movement or abs(delta_y) > max_movement:
        #     # print ("Skipping")
        #     raise Exception

        return w, dw, distance, delta_x / 2, delta_y / 2, Soldier.ptr


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


