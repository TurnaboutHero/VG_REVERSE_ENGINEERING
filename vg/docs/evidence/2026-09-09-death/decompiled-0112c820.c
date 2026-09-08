// Windows VA 0112c820; image base 00400000

void FUN_0112c820(uint param_1,uint param_2,undefined4 param_3)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  undefined4 local_ac;
  int local_a8;
  int local_a4;
  undefined1 local_a0 [4];
  int *local_9c;
  undefined4 local_98;
  int *local_94;
  uint local_90;
  uint local_8c;
  uint auStack_88 [32];
  uint local_8;

  local_8 = DAT_01e44f28 ^ (uint)&stack0xfffffffc;
  local_98 = param_3;
  uVar7 = 0;
  local_8c = param_1;
  local_9c = (int *)0x0;
  piVar4 = (int *)(param_1 + param_2);
  local_94 = (int *)0x0;
  uVar6 = *(uint *)(param_1 + 4);
  piVar3 = (int *)(param_1 + uVar6);
  if ((((7 < uVar6) && (uVar6 <= param_2)) && (piVar3 < piVar4)) &&
     ((int *)(piVar3[1] + (int)piVar3) <= piVar4)) {
    do {
      iVar8 = *piVar3;
      piVar1 = local_9c;
      if (iVar8 == 0x424d5953) {
        if (uVar7 < 0x20) {
          auStack_88[uVar7] = (uint)piVar3;
          uVar7 = uVar7 + 1;
        }
      }
      else {
        piVar1 = piVar3;
        if ((iVar8 != 0x48435450) && (piVar1 = local_9c, iVar8 == 0x54534e49)) {
          local_94 = piVar3;
        }
      }
      local_9c = piVar1;
      piVar2 = local_94;
      uVar6 = piVar3[1];
      piVar1 = (int *)(uVar6 + (int)piVar3);
    } while (((7 < uVar6) && (uVar6 <= (uint)((int)piVar4 - (int)piVar3))) &&
            ((piVar1 < piVar4 && (piVar3 = piVar1, (int *)(piVar1[1] + (int)piVar1) <= piVar4))));
    local_90 = uVar7;
    if ((local_94 != (int *)0x0) && (local_9c != (int *)0x0)) {
      piVar4 = (int *)FUN_0112bf40(local_94[1] + -8,0x10);
      local_94 = piVar4;
      memmove(piVar4,piVar2 + 2,piVar2[1] - 8);
      uVar6 = (uint)*(byte *)(local_8c + 9);
      if ((uVar6 != 0) && (uVar6 - 1 < 0xf)) {
        FUN_011412d0(piVar4,piVar2[1] + -8,*(undefined4 *)(&DAT_01e3f978 + uVar6 * 4),piVar2[1] + -8
                    );
      }
      iVar8 = local_9c[2];
      if (iVar8 != 0) {
        piVar3 = local_9c + 4;
        do {
          if ((*piVar3 != 0) || (piVar3[1] != 0)) {
            *(int *)(*piVar3 + (int)piVar4) = piVar3[1] + (int)piVar4;
          }
          piVar3 = piVar3 + 2;
          iVar8 = iVar8 + -1;
        } while (iVar8 != 0);
      }
      local_8c = 0;
      uVar6 = local_90;
      if (uVar7 != 0) {
        do {
          if (DAT_020ec99c != 0) {
            uVar7 = auStack_88[local_8c];
            iVar8 = DAT_020ec99c;
            do {
              if (*(int *)(iVar8 + 4) == *(int *)(uVar7 + 0xc)) {
                iVar9 = *(int *)(uVar7 + 8) + (int)local_94;
                uVar5 = FUN_0096c7a0(uVar7 + 0x10,0x12345678);
                local_ac = FUN_004c4450(uVar7 + 0x10,uVar5);
                local_a8 = iVar9;
                local_a4 = iVar8;
                FUN_0112bcb0(local_a0,0,&local_ac,local_98);
                uVar6 = local_90;
                break;
              }
              iVar8 = *(int *)(iVar8 + 8);
              uVar6 = local_90;
            } while (iVar8 != 0);
          }
          local_8c = local_8c + 1;
        } while (local_8c < uVar6);
      }
    }
  }
  __security_check_cookie(local_8 ^ (uint)&stack0xfffffffc);
  return;
}
