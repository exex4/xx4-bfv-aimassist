OBFUS_MGR = 0
Dx11Secret = 0x598447EFD7A36912
Dx11EncBuffer = 0
CryptMode = 0
GPUMemPtr = 0


# 7.3 12/08/2020
GAMERENDERER = 0x1447F6FB8
CLIENT_GAME_CONTEXT = 0x1447522A8
OBJECTIVE_MANAGER = 0x14468B8B0  # FF 0D ? ? ? ? 48 8B 1D [? ? ? ?] 48 8B 43 10 48 8B 4B 08 48 3B C8 74 0E
CLIENTSHRINKINGPLAYAREA = 0x1446645A0  # ? 8B F2 48 8B D9 ? 8B 35 [? ? ? ?] ? 85 F6
ClientSoldierEntity = 0x144F2EF50
ClientVehicleEntity = 0x144E3A170
ClientSupplySphereEntity = 0x144C54550
ClientCombatAreaTriggerEntity = 0x144E3B870
ClientExplosionPackEntity = 0x144F346A0
ClientProxyGrenadeEntity = 0x144F34370
ClientGrenadeEntity = 0x144F34590
ClientInteractableGrenadeEntity = 0x144C5BCB0
ClientCapturePointEntity = 0x144C8DD30
ClientLootItemEntity = 0x144C473A0
ClientArmorVestLootItemEntity = 0x144C89090
ClientStaticModelEntity = 0x144E32F10
PROTECTED_THREAD = 0x144752654
OBFUS_MGR_PTR_1 = 0x1438B46D0
OBFUS_MGR_RET_1 = 0x147E38436
OBFUS_MGR_DEC_FUNC = 0x14161F880
OBJECTIVE_VTBL = 0x1437A7EF8



badobfus = 0


NDM_FRAMES = 0 #
NDM_BUSY = 4 #
NDM_LOCALPLAYER = 8 #
NDM_PLAYERLIST = 0x10 #
NDM_TYPEINFOLIST = 0x18 #
NDM_ENTITYKEYLIST = 0x20 #
ClientPlayer_TeamID = 0x1C48 #
ClientPlayer_Soldier = 0x1d50 #
ClientPlayer_Vehicle = 0x1d60 #
GameRenderer_RenderView = 0x60 #
RenderView_ViewMatrix = 0x4F0 #
HC_Health = 0x20
HC_MaxHealth = 0x24
#CVE_TeamID = 0x25c
CVE_TeamID = 0x234 #6.2
#CSE_HealthComponent = 0x310 #
CSE_HealthComponent = 0x2E8  # 6.2
CSE_Occluded = 0xA7B
#CCPE_Transform = 0x3c0
CCPE_Transform = 0x3A0  # 6.2
#CSE_Player = 0x3D0
CSE_Player = 0x3A8  # 6.2
CVE_VehicleEntityData = 0x38
VED_ControllableType = 0x1F8
CCAT_ActiveTrigger = 0xD84
CCAT_TriggerData = 0x28
CCAT_ppAreaBounds = 0x60
VVSD_PointsArray = 0x20
AOD_ObjectiveArray = 0x18
OD_Transform = 0x30
OD_ShortName = 0x20
OD_LongName = 0x80
OD_TeamState = 0x88
OD_ControlledState = 0x8C

CSE_ClientSoldierWeapon = 0xA48  # weakptr
CSW_SoldierWeaponData = 0x038
SWD_WeaponName = 0x190
CSW_WeaponFiring = 0x5F48
WF_ProjectilesLoaded = 0x250
WF_ProjectilesInMagazines = 0x254
WF_WeaponFiringData = 0x130
WFD_ShotConfigData = 0x18
SCD_MagazineCapacity = 0x328
SCD_NumberOfMagazines = 0x332


CSE_ClientSoldierPrediction = 0x810
CSP_Location = 0x20 # v3
CSP_Velocity = 0x30 # v3

#CSE_ClientSoldierWeaponsComponent = 0x8C8
CSE_ClientSoldierWeaponsComponent = 0xA08
CSWC_ClientActiveWeaponHandler = 0xB98
CAWH_ClientSoldierWeapon = 0x38
#CSW_SoldierWeaponData = 0x38
SWD_WeaponFiringData = 0x90
WFD_FiringFunctionData = 0x10
FFD_BulletEntityData = 0xF0
