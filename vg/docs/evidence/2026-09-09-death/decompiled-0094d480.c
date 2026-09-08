// Windows VA 0094d480; image base 00400000

void __fastcall FUN_0094d480(int param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  undefined1 *puVar10;
  uint uVar11;
  uint uVar12;
  int *piVar13;
  undefined **local_18c;
  undefined4 local_188;
  byte local_184;
  byte local_180;
  undefined1 local_17f;
  int local_17c;
  int local_178;
  uint local_174;
  uint local_170;
  int local_16c [70];
  int local_54 [16];
  uint local_14;
  void *local_10;
  undefined1 *puStack_c;
  undefined4 local_8;

  local_8 = 0xffffffff;
  puStack_c = &LAB_011f9e3b;
  local_10 = ExceptionList;
  uVar2 = DAT_01e44f28 ^ (uint)&stack0xfffffffc;
  ExceptionList = &local_10;
  local_14 = uVar2;
  iVar3 = FUN_00857970(*(undefined4 *)(param_1 + 0x18),uVar2);
  if (iVar3 == 0) {
    local_178 = iVar3;
    FUN_01129ea0(**(undefined4 **)(**(int **)(DAT_0209e200 + 0x20) + *(int *)(param_1 + 0x10) * 4),
                 &local_178,1,0);
    iVar3 = local_178;
    local_17c = local_178;
    *(undefined4 *)(local_178 + 0x178) = *(undefined4 *)(param_1 + 0x18);
    *(undefined1 *)(local_178 + 0x1f0) = *(undefined1 *)(param_1 + 0x1c);
    *(undefined1 *)(local_178 + 0x17c) = *(undefined1 *)(param_1 + 0x1d);
    FUN_0095d140(*(undefined4 *)(param_1 + 0x10));
    *(uint *)(iVar3 + 500) =
         *(uint *)(iVar3 + 500) ^ (*(uint *)(iVar3 + 500) ^ *(uint *)(param_1 + 0x35c)) & 0x3ff;
    iVar4 = FUN_00857970(*(undefined4 *)(param_1 + 0x37c),uVar2);
    if (iVar4 == 0) {
      *(undefined4 *)(iVar3 + 0x1c8) = 0;
      uVar6 = DAT_020ec6fc;
    }
    else {
      *(int *)(iVar3 + 0x1c8) = iVar4 + 0x14;
      uVar6 = *(undefined4 *)(iVar4 + 0x18);
    }
    *(undefined4 *)(iVar3 + 0x1cc) = uVar6;
    *(undefined4 *)(iVar3 + 0x1b0) = *(undefined4 *)(param_1 + 0x350);
    FUN_0093fba0(*(undefined4 *)(param_1 + 0x358),param_1 + 0x14,0,param_1 + 0x20,param_1 + 0x2c);
    FUN_009419d0();
    FUN_00941ac0();
    if (*(char *)(param_1 + 0x354) == '\0') {
      FUN_0095c940(param_1 + 0x38);
    }
    if (1 < *(uint *)(param_1 + 0x360)) {
      uVar2 = 1;
      do {
        FUN_00944de0(1);
        uVar2 = uVar2 + 1;
      } while (uVar2 < *(uint *)(param_1 + 0x360));
    }
    FUN_0095eb50(param_1 + 0x20,param_1 + 0x2c);
    if ((DAT_0209e204 != '\0') ||
       (FUN_004a8f80(iVar3,*(undefined1 *)(param_1 + 0x1c)), DAT_0209e204 != '\0')) {
      iVar5 = FUN_00937950();
      iVar4 = *(int *)(*(int *)(iVar3 + 0x1c) + 4);
      if (iVar5 != 0) {
        iVar4 = iVar5;
      }
      guard_check_icall(iVar3,iVar4,*(undefined4 *)(param_1 + 0x35c));
      if (DAT_0209e204 != '\0') {
        FUN_01129d20(DAT_020e9c28);
      }
    }
    iVar4 = *(int *)(iVar3 + 0xc);
    if (iVar4 != 0) {
LAB_0094d648:
      if (*(int *)(*(int *)(iVar4 + 4) + 0x54) != DAT_02091598) goto code_r0x0094d650;
      puVar10 = (undefined1 *)(param_1 + 0x36c);
      local_170 = -param_1 - 0x36c;
      do {
        FUN_00945dd0((uint)(puVar10 + local_170) & 0xff,puVar10[-8],*puVar10,puVar10[8]);
        puVar10 = puVar10 + 1;
        iVar3 = local_17c;
      } while (puVar10 + local_170 < &DAT_00000008);
    }
LAB_0094d6a3:
    if (DAT_0209e204 != '\0') {
      (**(code **)(param_1 + 0x388))
                (iVar3,*(undefined1 *)(param_1 + 0x38c),*(undefined1 *)(param_1 + 0x38d));
    }
    if (*(code **)(param_1 + 0x380) != (code *)0x0) {
      (**(code **)(param_1 + 0x380))(iVar3,*(undefined4 *)(param_1 + 900));
    }
    iVar4 = *(int *)(*(int *)(iVar3 + 0x1c) + 0x44);
    if ((iVar4 != 0) && (iVar4 = FUN_0096c7a0(iVar4), iVar4 != 0)) {
      iVar4 = *(int *)(*(int *)(iVar3 + 0x1c) + 0x44);
      if (iVar4 == 0) {
        uVar6 = 0;
      }
      else {
        uVar6 = FUN_0096c7a0(iVar4,0x12345678);
        uVar6 = FUN_004c4450(iVar4,uVar6);
      }
      iVar4 = FUN_00936bd0(uVar6);
      FUN_009432c0(*(undefined4 *)(*(int *)(iVar3 + 0x2c) + 0x28 + iVar4 * 4));
    }
    uVar2 = FUN_0112ac50(local_16c,0x46,DAT_01ef3360,0);
    local_170 = 0;
    local_174 = uVar2;
    if (uVar2 != 0) {
      do {
        uVar1 = local_170;
        iVar4 = local_17c;
        if (local_16c[local_170] != 0) {
          uVar12 = 0;
          uVar2 = 1;
          uVar11 = 0;
          do {
            uVar7 = ((int)"onEntitySpawned"[uVar11] + uVar2) % 0xfff1;
            uVar8 = ((int)"onEntitySpawned"[uVar11 + 1] + uVar7) % 0xfff1;
            uVar9 = ((int)"onEntitySpawned"[uVar11 + 2] + uVar8) % 0xfff1;
            iVar3 = uVar11 + 3;
            uVar11 = uVar11 + 4;
            uVar2 = ((int)"onEntitySpawned"[iVar3] + uVar9) % 0xfff1;
            uVar12 = ((((uVar12 + uVar7) % 0xfff1 + uVar8) % 0xfff1 + uVar9) % 0xfff1 + uVar2) %
                     0xfff1;
          } while (uVar11 < 0x10);
          FUN_00536dd0(0,1,uVar12 << 0x10 | uVar2,local_17c);
          uVar2 = local_174;
          iVar3 = iVar4;
        }
        local_170 = uVar1 + 1;
      } while (local_170 < uVar2);
    }
    local_184 = local_184 | 3;
    local_180 = local_180 & 0xfe;
    local_188 = 0;
    local_18c = Nuo::Kindred::ActorFilterPlayers::vftable;
    local_17f = 0xff;
    local_8 = 0;
    local_174 = FUN_00858bd0(&local_18c,local_54,0x10,0);
    local_170 = 0;
    if (local_174 != 0) {
      do {
        if (*(int *)(local_54[local_170] + 0x30) != 0) {
          for (iVar4 = *(int *)(*(int *)(local_54[local_170] + 0x30) + 0x14); iVar4 != 0;
              iVar4 = *(int *)(iVar4 + 0x260)) {
            for (piVar13 = (int *)(-(uint)(*(int *)(iVar4 + 0x28) != 0) &
                                  *(int *)(iVar4 + 0x28) - 4U); piVar13 != (int *)0x0;
                piVar13 = (int *)(-(uint)(piVar13[1] != 0) & piVar13[1] - 4U)) {
              (**(code **)(*piVar13 + 0x24))(iVar4,iVar3);
            }
          }
        }
        local_170 = local_170 + 1;
      } while (local_170 < local_174);
    }
    FUN_007c4340(iVar3);
    if ((DAT_0209e204 != '\0') && ((*(uint *)(iVar3 + 0x1e0) & 0x20002111) != 0)) {
      piVar13 = (int *)FUN_01129d20(DAT_020e9c2c);
      (**(code **)(*piVar13 + 0xc))();
    }
  }
  ExceptionList = local_10;
  __security_check_cookie(local_14 ^ (uint)&stack0xfffffffc);
  return;
code_r0x0094d650:
  iVar4 = *(int *)(iVar4 + 0x10);
  if (iVar4 == 0) goto LAB_0094d6a3;
  goto LAB_0094d648;
}
