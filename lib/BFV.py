from lib import MemAccess
from lib.MemAccess import *
from lib.PointerManager import PointerManager
from lib import offsets


class GameData:
    myplayer = 0
    mysoldier = 0
    myteamid = 0
    myvehicle = 0
    myviewmatrix = 0
    mytransform = 0

    def __init__(self):
        self.soldiers = []

    def AddSoldier(self, soldier):
        self.soldiers += [soldier]

    def ClearSoldiers(self):
        self.soldiers = []


class GameSoldierData:
    transform = None
    ptr = 0
    occluded = 0
    head = 0
    spine = 0
    neck = 0


gamedata = GameData()


def get_handle():
    def yes_or_no(question):
        while True:
            reply = str(input(question + ' (y/n): ')).lower().strip()
            if reply[:1] == 'y':
                return True
            if reply[:1] == 'n':
                return False

    pid = api.get_processid_by_name("bfv.exe")
    if type(pid) == type(None):
        return 0
    pHandle = HANDLE(api.OpenProcess(DWORD(0x1f0fff), False, DWORD(pid)))
    priv = api.is_elevated(pHandle)
    if priv == 2:
        ans = yes_or_no("[+] WARNING! BFV.exe is running as admin, do you still want to continue?")
        if ans == False:
            exit(0)
    return pHandle.value


def GetEntityTransform(pHandle, Entity):
    mem = MemAccess(pHandle)
    flags = mem[Entity](0x40).read_uint64(0x8)
    if flags == None:
        return 0
    _9 = (flags >> 8) & 0xFF
    _10 = (flags >> 16) & 0xFF
    # print((0x20*(_10+(2*_9)))+0x10, flush=True)
    transform = mem[Entity](0x40).read_mat4((0x20 * (_10 + (2 * _9))) + 0x10)
    return transform


def GetEntityVec4(pHandle, Entity):
    mem = MemAccess(pHandle)
    flags = mem[Entity](0x40).read_uint64(0x8)
    if flags == None:
        return 0
    _9 = (flags >> 8) & 0xFF
    _10 = (flags >> 16) & 0xFF
    _off = (0x20 * (_10 + (2 * _9))) + 0x10
    v4 = [mem[Entity](0x40).read_uint32(_off + 0x30),
          mem[Entity](0x40).read_uint32(_off + 0x34),
          mem[Entity](0x40).read_uint32(_off + 0x38),
          mem[Entity](0x40).read_uint32(_off + 0x40)]
    return v4


def GetEncKey(pHandle, typeinfo):
    global offsets
    cache_en = api._cache_en
    api._cache_en = False
    global keystore
    mem = MemAccess(pHandle)
    pm = PointerManager(pHandle)

    if (mem[typeinfo].read_uint64(0x88) == 0):
        api._cache_en = cache_en
        return 0
    try:
        keystore
    except NameError:
        keystore = {}
    if typeinfo in keystore:
        api._cache_en = cache_en
        #print ("[+] Typeinfo: 0x%x Encryption Key: 0x%x"% (typeinfo,keystore[typeinfo]))
        return keystore[typeinfo]

    pm = PointerManager(pHandle)
    key = pm.GetEntityKey(mem[typeinfo](0).me())

    if key == 0:
        return 0

    keystore[typeinfo] = key

    api._cache_en = cache_en
    print("+ Typeinfo: 0x%x Encryption Key: 0x%x" % (typeinfo, keystore[typeinfo]), flush=True)
    return keystore[typeinfo]


def GetEntityList(pHandle, typeinfo, flink_offset=0x80):
    elist = []
    mem = MemAccess(pHandle)
    flink = mem[typeinfo].read_uint64(0x88)
    key = GetEncKey(pHandle, typeinfo)

    while (flink):
        ent = PointerManager.decrypt_ptr(flink, key)
        if ent >= 0x100000000000:
            return []
        elist += [ent - flink_offset]
        flink = mem[ent].read_uint64(0x0)

    return elist


def DebugPrintMatrix(mat):
    print("[%.3f %.3f %.3f %.3f ]" % (mat[0][0], mat[0][1], mat[0][2], mat[0][3]))
    print("[%.3f %.3f %.3f %.3f ]" % (mat[1][0], mat[1][1], mat[1][2], mat[1][3]))
    print("[%.3f %.3f %.3f %.3f ]" % (mat[2][0], mat[2][1], mat[2][2], mat[2][3]))
    print("[%.3f %.3f %.3f %.3f ]\n" % (mat[3][0], mat[3][1], mat[3][2], mat[3][3]))


def process(pHandle, cnt):
    api._access = 0
    # api._cache_en = True
    del api._cache
    api._cache = {}

    mem = MemAccess(pHandle)
    pm = PointerManager(pHandle)

    global gamedata
    try:
        gamedata
    except NameError:
        gamedata = GameData()

    MyPlayer = pm.GetLocalPlayer()
    MySoldier = mem[MyPlayer].weakptr(offsets.ClientPlayer_Soldier).me()
    MyTeamId = mem[MyPlayer].read_uint32(offsets.ClientPlayer_TeamID)
    # MyVehicle = mem[MyPlayer].weakptr(offsets.ClientPlayer_Vehicle).me()
    MyViewmatrix = mem[offsets.GAMERENDERER]()(offsets.GameRenderer_RenderView).read_mat4(offsets.RenderView_ViewMatrix)
    MyTransform = GetEntityTransform(pHandle, MySoldier)
    # MyPos = GetEntityVec4(pHandle, MySoldier)

    gamedata.myviewmatrix = MyViewmatrix
    gamedata.mytransform = MyTransform

    gamedata.ClearSoldiers()

    for Soldier in GetEntityList(pHandle, offsets.ClientSoldierEntity, 0xF0):
        if Soldier == MySoldier:
            #print("Me: %x" % Soldier)
            continue
        #print("Soldier %x" % Soldier)
        if mem[Soldier](offsets.CSE_Player).me() == 0:
            continue
        if mem[Soldier](offsets.CSE_Player).read_uint32(offsets.ClientPlayer_TeamID) == MyTeamId:
            # Skip if on same team
            continue
        Transform = GetEntityTransform(pHandle, Soldier)
        #DebugPrintMatrix(Transform)
        if Transform == 0:
            continue
        occluded = mem[Soldier].read_uint8(offsets.CSE_Occluded)
        #if occluded == 1:
        #   continue
        Health = mem[Soldier](offsets.CSE_HealthComponent).read_float(offsets.HC_Health)
        if Health <= 0:
            # skip if dead
            continue

        #BoneCollisionComponent = mem[Soldier](0x6e0)
        #if Soldier == 0x1679b5900:
        #    print("BCC address: %x" % BoneCollisionComponent.me())
        #Head = BoneCollisionComponent(0x20).read_vec4(4*0x20) # spine?
        Head = mem[Soldier](0x6e0)(0x20).read_vec4(8 * 0x20)
        #Spine = mem[Soldier](0x6e0)(0x20).read_vec4(4 * 0x20)
        #Neck = mem[Soldier](0x6e0)(0x20).read_vec4(6 * 0x20)

        #if Soldier == 0x1679b5900:
            #print("Head address: %x" % Head.me())
            #DebugPrintMatrix(Head)

        SoldierData = GameSoldierData()
        SoldierData.ptr = Soldier
        SoldierData.transform = Transform
        SoldierData.occluded = occluded
        SoldierData.head = Head
        #SoldierData.spine = Spine
        #SoldierData.neck = Neck
        gamedata.AddSoldier(SoldierData)
