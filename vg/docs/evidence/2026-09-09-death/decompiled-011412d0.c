// Windows VA 011412d0; image base 00400000

void FUN_011412d0(uint *param_1,uint param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  bool bVar6;

  uVar5 = param_4;
  uVar2 = FUN_004c4450(&param_3,4,param_4);
  uVar3 = 0;
  uVar4 = param_2 >> 2;
  if ((uint *)((param_2 & 0xfffffffc) + (int)param_1) < param_1) {
    uVar4 = 0;
  }
  if (uVar4 != 0) {
    do {
      bVar6 = (int)uVar5 < 0;
      uVar1 = uVar5 << 1;
      uVar3 = uVar3 + 1;
      uVar5 = *param_1;
      *param_1 = uVar2 ^ (uVar1 | bVar6) ^ *param_1;
      param_1 = param_1 + 1;
    } while (uVar3 < uVar4);
  }
  return;
}
