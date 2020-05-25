from lib import MemAccess
from lib import offsets
from lib.MemAccess import *


class PointerManager():
    badobfus = 0
    def __init__(self, pHandle):
        self.mem = MemAccess(pHandle)
        self.pHandle = pHandle

        self.OBFUS_MGR = 0
        if offsets.OBFUS_MGR == 0:
            offsets.OBFUS_MGR = self.GetObfuscationMgr()
        else:
            self.OBFUS_MGR = offsets.OBFUS_MGR

    @staticmethod
    def decrypt_ptr(encptr, key):
        # Grab byte at location
        def GRAB_BYTE(x, n):
            return (x >> (n * 8)) & 0xFF

        ret = 0
        subkey = (key ^ ((5 * key) % (2 ** 64))) % (2 ** 64)
        for i in range(7):
            y = GRAB_BYTE(subkey, i)
            subkey += 8
            t1 = (y * 0x3B) % (2 ** 8)
            t2 = (y + GRAB_BYTE(encptr, i)) % (2 ** 8)
            ret |= (t2 ^ t1) << (i * 8)
        ret |= GRAB_BYTE(encptr, 7) << 56
        ret &= 0x7FFFFFFFFFFFFFFF
        return ret

    def GetObfuscationMgr(self):
        api._cache_en = False
        print("[+] Searching for ObfuscationMgr...", flush=True)
        addr = -1
        OM = 0
        ss = StackAccess(self.pHandle, self.mem[offsets.PROTECTED_THREAD].read_uint32(0))
        while (1):
            #print("finding obfus while ignoring %x" % offsets.badobfus)
            addr = -1
            time.sleep(0.1)
            buf = ss.read()
            addr = buf.find(b"\x12\x69\xa3\xd7\xef\x47\x84\x59")
            if (addr == -1):
                addr = buf.find(b"\xae\x15\x75\xa7\x6e\x35\xe4\x2c")
            if (addr > -1):
                for i in range(-160, 160, 8):
                    testptr = int.from_bytes(buf[addr + i:addr + 8 + i], "little")
                    if self.mem[testptr - 0x120].read_uint64(0x0) == offsets.OBFUS_MGR_PTR_1:
                        OM = testptr - 0x120
                        #if OM != offsets.badobfus:
                        self.OBFUS_MGR = OM
                        break
                        #else:
                        #    print("not accepting obfus1")
                    elif self.mem[testptr].read_uint64(0x0) == offsets.OBFUS_MGR_PTR_1:
                        OM = testptr
                        #if not OM == offsets.badobfus:
                        self.OBFUS_MGR = OM
                        break
                        #else:
                        #    print("not accepting obfus2")
                if (OM > 0):
                    #if OM == offsets.badobfus:
                    #    print("not accepting obfus3")
                    #else:
                    break


        ss.close()
        print("[+] Found ObfuscationMgr @ 0x%08x " % OM, flush=True)
        api._cache_en = True
        return OM

    def GetDx11Secret(self):
        api._cache_en = False
        ss = StackAccess(self.pHandle, self.mem[offsets.PROTECTED_THREAD].read_uint32(0))
        if self.mem[self.OBFUS_MGR].read_uint64(0x100) != 0:
            addr = -1
            OM = 0
            i = 0
            print("Doing Dx11 stuff", flush=True)
            xxx = 0
            final = ss.stack_size
            while (1):
                addr = -1
                time.sleep(0.1)
                buf = ss.read()
                if xxx >= final:
                    print("Resetting xxx to 0, greater than final")
                    xxx = 0

                addr = buf.find((offsets.OBFUS_MGR_RET_1).to_bytes(8, byteorder='little'), xxx)
                if (addr > -1):
                    print("Found OBFUS_MGR_RET_1 at 0x%08x" % addr, flush=True)
                    print("OBFUS_MGR: 0x%08x" % offsets.OBFUS_MGR)
                    i = -120
                    if (int.from_bytes(buf[addr + i:addr + i + 8], "little") == offsets.OBFUS_MGR):
                        i = -56
                        testptr = int.from_bytes(buf[addr + i:addr + 8 + i], "little")
                        # print("testptr 0x%16x" % testptr, flush=True)
                        if (testptr > 0x100000000000000):
                            if (testptr == offsets.Dx11Secret):
                                continue
                            offsets.Dx11Secret = testptr
                            api._cache_en = True
                            ss.close()
                            return offsets.Dx11Secret
                        else:
                            print("Incrementing xxx to 0x%8x" % xxx)
                            xxx = addr

        else:
            offsets.Dx11Secret = 0
            api._cache_en = True
            ss.close()
            return 0

    def CheckCryptMode(self):
        api._cache_en = False
        DecFunc = self.mem[self.OBFUS_MGR].read_uint64(0xE0) ^ self.mem[self.OBFUS_MGR].read_uint64(0xF8)
        Dx11EncBuffer = self.mem[self.OBFUS_MGR].read_uint64(0x100)

        if ((Dx11EncBuffer != 0) and (offsets.Dx11EncBuffer != Dx11EncBuffer)):
            self.GetDx11Secret()
            print("[+] Dynamic key loaded, root key set to 0x%x" % (offsets.Dx11Secret))
            offsets.Dx11EncBuffer = Dx11EncBuffer
            offsets.CryptMode = 1
        elif (offsets.CryptMode == 0):
            if ((DecFunc == offsets.OBFUS_MGR_DEC_FUNC) and (Dx11EncBuffer != 0)):
                self.GetDx11Secret()
                print("[+] Dynamic key loaded, retrieving key...")
                offsets.Dx11EncBuffer = Dx11EncBuffer
                offsets.CryptMode = 1
        elif (offsets.CryptMode == 1):
            if (DecFunc != offsets.OBFUS_MGR_DEC_FUNC):
                offsets.Dx11Secret = 0x598447EFD7A36912
                print("[+] Static key loaded, root key set to 0x%x" % (offsets.Dx11Secret))
                offsets.CryptMode = 0
        api._cache_en = True

    def hashtable_find(self, table, key):
        mem = self.mem
        bucketCount = mem[table].read_uint32(0x10)
        if (bucketCount == 0):
            #print("bucket zero")
            return 0
        elemCount = mem[table].read_uint32(0x14)
        startcount = key % bucketCount
        node = mem[table](0x8)(0x8 * startcount).me()


        if (node == 0):
            print ("node zero")
            return 0

        while 1:
            first = mem[node].read_uint64(0x0)
            second = mem[node].read_uint64(0x8)
            next = mem[node].read_uint64(0x16)

            if first == key:
                #print ("Key: 0x%016x Node: 0x%016x"%(key^ mem[self.OBFUS_MGR].read_uint64(0xE0),node))
                return second
            elif (next == 0):
                #print("next 0 for node 0x%16x" % node)
                return 0

            node = next
            if node > 0x1000000000000000:
                #something wrong?
                #print ("Bad obfus for node 0x%016x", node)
                offsets.badobfus = self.OBFUS_MGR
                self.OBFUS_MGR = 0
                offsets.OBFUS_MGR = 0
                print("badobfus: 0x%x" % offsets.badobfus)
                return 0


    def GetLocalPlayer(self):
        self.CheckCryptMode()
        mem = self.mem
        ClientPlayerManager = mem[offsets.CLIENT_GAME_CONTEXT](0).read_uint64(0x60)
        ObfManager = self.OBFUS_MGR
        LocalPlayerListXorValue = mem[ClientPlayerManager].read_uint64(0xF8)
        LocalPlayerListKey = LocalPlayerListXorValue ^ mem[ObfManager].read_uint64(0xE0)

        hashtable = ObfManager + 0x10
        EncryptedPlayerManager = self.hashtable_find(hashtable, LocalPlayerListKey)
        if (EncryptedPlayerManager == 0):
            return 0
        MaxPlayerCount = mem[EncryptedPlayerManager].read_uint32(0x18)

        if (MaxPlayerCount != 1):
            return 0

        XorValue1 = mem[EncryptedPlayerManager].read_uint64(0x20) ^ mem[EncryptedPlayerManager].read_uint64(0x8)
        XorValue2 = mem[EncryptedPlayerManager].read_uint64(0x10) ^ offsets.Dx11Secret

        LocalPlayer = mem[XorValue2].read_uint64(0) ^ XorValue1

        return LocalPlayer

    def GetPlayerById(self, id):
        self.CheckCryptMode()
        mem = self.mem
        ClientPlayerManager = mem[offsets.CLIENT_GAME_CONTEXT](0).read_uint64(0x60)
        ObfManager = self.OBFUS_MGR
        PlayerListXorValue = mem[ClientPlayerManager].read_uint64(0x100)
        PlayerListKey = PlayerListXorValue ^ mem[ObfManager].read_uint64(0xE0)

        hashtable = ObfManager + 0x10
        EncryptedPlayerManager = self.hashtable_find(hashtable, PlayerListKey)
        if (EncryptedPlayerManager == 0):
            return 0
        MaxPlayerCount = mem[EncryptedPlayerManager].read_uint32(0x18)

        if (MaxPlayerCount != 70):
            return 0

        XorValue1 = mem[EncryptedPlayerManager].read_uint64(0x20) ^ mem[EncryptedPlayerManager].read_uint64(0x8)
        XorValue2 = mem[EncryptedPlayerManager].read_uint64(0x10) ^ offsets.Dx11Secret

        ClientPlayer = mem[XorValue2].read_uint64(0x8 * id) ^ XorValue1

        return ClientPlayer

    def GetSpectatorById(self, id):
        self.CheckCryptMode()
        mem = self.mem
        ClientPlayerManager = mem[offsets.CLIENT_GAME_CONTEXT](0).read_uint64(0x60)
        ObfManager = self.OBFUS_MGR
        PlayerListXorValue = mem[ClientPlayerManager].read_uint64(0xF0)
        PlayerListKey = PlayerListXorValue ^ mem[ObfManager].read_uint64(0xE0)

        hashtable = ObfManager + 0x10
        EncryptedPlayerManager = self.hashtable_find(hashtable, PlayerListKey)
        if (EncryptedPlayerManager == 0):
            return 0
        MaxPlayerCount = mem[EncryptedPlayerManager].read_uint32(0x18)

        if (MaxPlayerCount == 0) or (id >= MaxPlayerCount):
            return 0

        XorValue1 = mem[EncryptedPlayerManager].read_uint64(0x20) ^ mem[EncryptedPlayerManager].read_uint64(0x8)
        XorValue2 = mem[EncryptedPlayerManager].read_uint64(0x10) ^ offsets.Dx11Secret

        ClientPlayer = mem[XorValue2].read_uint64(0x8 * id) ^ XorValue1

        return ClientPlayer

    def GetEntityKey(self, PointerKey):
        self.CheckCryptMode()
        mem = self.mem
        ObfManager = self.OBFUS_MGR
        HashTableKey = PointerKey ^ mem[ObfManager].read_uint64(0xE0)
        hashtable = ObfManager + 0x78
        EncryptionKey = self.hashtable_find(hashtable, HashTableKey)

        if (EncryptionKey == 0):
            print ("encryptionkey = 0")
            return 0

        EncryptionKey ^= offsets.Dx11Secret

        return EncryptionKey

    def DecryptPointer(self, EncPtr, PointerKey):
        self.CheckCryptMode()
        if not (EncPtr & 0x8000000000000000):
            return 0
        mem = self.mem
        ObfManager = self.OBFUS_MGR
        HashTableKey = PointerKey ^ mem[ObfManager].read_uint64(0xE0)
        hashtable = ObfManager + 0x78
        EncryptionKey = self.hashtable_find(hashtable, HashTableKey)

        if (EncryptionKey == 0):
            return 0

        EncryptionKey ^= offsets.Dx11Secret

        return PointerManager.decrypt_ptr(EncPtr, EncryptionKey)
