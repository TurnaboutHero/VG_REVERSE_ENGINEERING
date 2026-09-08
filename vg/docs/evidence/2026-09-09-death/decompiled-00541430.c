// Windows VA 00541430; image base 00400000

void FUN_00541430(undefined4 *param_1,undefined4 param_2)

{
  int iVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 uVar8;
  float10 fVar9;
  undefined4 uVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined *puVar13;
  undefined4 uVar14;

  iVar1 = (int)param_1;
  if ((*(byte *)((int)param_1 + 0x1e0) & 1) == 0) {
    if ((*(uint *)((int)param_1 + 0x1e0) >> 0xd & 1) == 0) {
      return;
    }
    FUN_00549e20();
    fVar9 = (float10)FUN_00548870();
    if ((float)fVar9 <= DAT_0121cba8) {
      return;
    }
    uVar5 = FUN_00938fb0();
    cVar2 = FUN_00936080(uVar5);
    if (cVar2 == '\0') {
      return;
    }
    puVar7 = (undefined4 *)FUN_005412a0("TurretDestroyed");
    cVar2 = FUN_009448b0();
    if (cVar2 != '\0') {
      uVar5 = puVar7[0x13];
      uVar8 = 0xffffffff;
      uVar14 = FUN_00937a80(0xffffffff);
      uVar10 = FUN_011b8a40(uVar14);
      uVar11 = uVar5;
      uVar12 = FUN_00541320(puVar7[0x10],uVar5,uVar5,uVar10);
      FUN_00540c80(*puVar7,puVar7[0x11],puVar7[0x12],uVar12,uVar5,uVar11,uVar10,uVar14,uVar8);
      return;
    }
    uVar5 = FUN_00939790(param_1);
    cVar2 = FUN_009446e0(uVar5);
    if (cVar2 != '\0') {
      uVar14 = 0xffffffff;
      uVar11 = 0xffffffff;
      uVar5 = FUN_00937a80(0xffffffff,0xffffffff);
      goto LAB_00541770;
    }
    uVar5 = FUN_00939790(param_1);
    cVar2 = FUN_009445b0(uVar5);
    if (cVar2 == '\0') {
      return;
    }
    uVar14 = 0xffffffff;
    uVar11 = 0xffffffff;
    uVar5 = FUN_00937a80(0xffffffff,0xffffffff);
    goto LAB_005418a4;
  }
  iVar4 = FUN_00857970(param_2);
  if (iVar4 == 0) goto LAB_00541618;
  uVar5 = FUN_00939e40();
  iVar4 = FUN_00857970(uVar5);
  if ((iVar4 != 0) && ((*(byte *)(iVar4 + 0x1e0) & 1) != 0)) {
    param_2 = *(undefined4 *)(iVar4 + 0x178);
  }
  cVar2 = FUN_009448b0();
  if (cVar2 == '\0') {
    uVar5 = FUN_00939790(param_1);
    cVar2 = FUN_009445b0(uVar5);
    if (cVar2 == '\0') goto LAB_00541618;
  }
  FUN_00571a00();
  iVar4 = FUN_00537bc0();
  switch(iVar4) {
  case 2:
    puVar13 = PTR_s_HeroKills_Double_Kill_01a3b190;
    break;
  case 3:
    puVar13 = PTR_s_HeroKills_Triple_Kill_01a3b194;
    break;
  case 4:
    param_1 = (undefined4 *)FUN_005412a0(PTR_s_HeroKills_Triple_Kill_01a3b194);
    uVar3 = FUN_0093c830();
    uVar5 = FUN_00938fb0(uVar3);
    iVar6 = FUN_00936250(uVar5);
    if (3 < iVar6) {
      param_1 = (undefined4 *)FUN_005412a0(PTR_s_HeroKills_Quadra_Kill_01a3b198);
    }
    goto LAB_005415b6;
  case 5:
    param_1 = (undefined4 *)FUN_005412a0(PTR_s_HeroKills_Triple_Kill_01a3b194);
    uVar3 = FUN_0093c830();
    uVar5 = FUN_00938fb0(uVar3);
    iVar6 = FUN_00936250(uVar5);
    if (4 < iVar6) {
      param_1 = (undefined4 *)FUN_005412a0(PTR_s_HeroKills_Penta_Kill_01a3b19c);
    }
LAB_005415b6:
    uVar5 = param_1[0xf];
    uVar8 = 0xffffffff;
    uVar12 = 0xffffffff;
    uVar10 = 0xffffffff;
    uVar11 = param_1[0xe];
    uVar14 = FUN_00541320(param_1[0xb],uVar11,uVar5,0xffffffff,0xffffffff,0xffffffff);
    FUN_00540c80(*param_1,param_1[0xc],param_1[0xd],uVar14,uVar11,uVar5,uVar10,uVar12,uVar8);
  default:
    goto switchD_005414d4_default;
  }
  puVar7 = (undefined4 *)FUN_005412a0(puVar13);
  uVar8 = 0xffffffff;
  uVar12 = 0xffffffff;
  uVar10 = 0xffffffff;
  uVar5 = puVar7[0xf];
  uVar11 = puVar7[0xe];
  uVar14 = FUN_00541320(puVar7[0xb],uVar11,uVar5,0xffffffff,0xffffffff,0xffffffff);
  FUN_00540c80(*puVar7,puVar7[0xc],puVar7[0xd],uVar14,uVar11,uVar5,uVar10,uVar12,uVar8);
switchD_005414d4_default:
  uVar3 = FUN_0093c830();
  uVar5 = FUN_00938fb0(uVar3);
  iVar6 = FUN_00936250(uVar5);
  if (iVar6 <= iVar4) {
    FUN_0053b030();
  }
LAB_00541618:
  cVar2 = FUN_00944350(param_2);
  if (cVar2 != '\0') {
    uVar5 = FUN_00939790(iVar1);
    cVar2 = FUN_009446e0(uVar5);
    if (cVar2 == '\0') {
      cVar2 = FUN_00541390();
      if (cVar2 != '\0') {
        return;
      }
      puVar7 = (undefined4 *)FUN_005412a0(PTR_s_YourKill_0121cce2_2_01a3b188);
      uVar14 = 0xffffffff;
      uVar11 = 0xffffffff;
      uVar5 = FUN_00937a80(0xffffffff,0xffffffff);
      goto LAB_00541664;
    }
  }
  puVar7 = (undefined4 *)FUN_005412a0(PTR_s_HeroKilled_01a3b18c);
  cVar2 = FUN_009448b0();
  if (cVar2 == '\0') {
    uVar5 = FUN_00939790(iVar1);
    cVar2 = FUN_009445b0(uVar5);
    if (cVar2 == '\0') {
      cVar2 = FUN_00944350(*(undefined4 *)(iVar1 + 0x178));
      if (cVar2 != '\0') {
        uVar14 = 0xffffffff;
        uVar11 = 0xffffffff;
        uVar5 = 0xffffffff;
LAB_00541664:
        uVar10 = puVar7[0xf];
        uVar12 = puVar7[0xe];
        uVar8 = FUN_00541320(puVar7[0xb],uVar12,uVar10,uVar5,uVar11,uVar14);
        FUN_00540c80(*puVar7,puVar7[0xc],puVar7[0xd],uVar8,uVar12,uVar10,uVar5,uVar11,uVar14);
        return;
      }
      uVar5 = FUN_00939790(iVar1);
      cVar2 = FUN_009446e0(uVar5);
      if (cVar2 != '\0') {
        uVar14 = 0xffffffff;
        uVar11 = 0xffffffff;
        uVar5 = 0xffffffff;
LAB_00541770:
        uVar10 = puVar7[5];
        uVar12 = puVar7[4];
        uVar8 = FUN_00541320(puVar7[1],uVar12,uVar10,uVar5,uVar11,uVar14);
        FUN_00540c80(*puVar7,puVar7[2],puVar7[3],uVar8,uVar12,uVar10,uVar5,uVar11,uVar14);
        return;
      }
    }
    else {
      cVar2 = FUN_00541390();
      if (cVar2 == '\0') {
        uVar14 = 0xffffffff;
        uVar11 = 0xffffffff;
        uVar5 = 0xffffffff;
LAB_005418a4:
        uVar10 = puVar7[10];
        uVar12 = puVar7[9];
        uVar8 = FUN_00541320(puVar7[6],uVar12,uVar10,uVar5,uVar11,uVar14);
        FUN_00540c80(*puVar7,puVar7[7],puVar7[8],uVar8,uVar12,uVar10,uVar5,uVar11,uVar14);
      }
    }
  }
  else {
    cVar2 = FUN_00541390();
    if (cVar2 == '\0') {
      uVar5 = puVar7[0x14];
      uVar8 = 0xffffffff;
      uVar12 = 0xffffffff;
      uVar10 = 0xffffffff;
      uVar11 = puVar7[0x13];
      uVar14 = FUN_00541320(puVar7[0x10],uVar11,uVar5,0xffffffff,0xffffffff,0xffffffff);
      FUN_00540c80(*puVar7,puVar7[0x11],puVar7[0x12],uVar14,uVar11,uVar5,uVar10,uVar12,uVar8);
      return;
    }
  }
  return;
}
