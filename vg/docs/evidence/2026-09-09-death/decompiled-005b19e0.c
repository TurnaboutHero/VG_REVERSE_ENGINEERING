// Windows VA 005b19e0; image base 00400000

void __thiscall FUN_005b19e0(int param_1,int param_2,int param_3)

{
  byte bVar1;
  char cVar2;
  uint uVar3;
  char *pcVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 ****ppppuVar8;
  int *piVar9;
  int *piVar10;
  undefined4 uVar11;
  undefined4 uVar12;
  undefined4 ****ppppuVar13;
  char *pcVar14;
  undefined1 local_cc [4];
  uint local_c8;
  int local_c4;
  undefined4 ***local_c0;
  int local_bc;
  int local_b8;
  uint local_b4;
  int local_b0;
  char local_ab;
  byte local_aa;
  byte local_a9;
  undefined4 ***local_74 [4];
  undefined4 local_64;
  uint local_60;
  undefined4 ***local_5c [4];
  undefined4 local_4c;
  uint local_48;
  undefined4 ***local_44 [4];
  undefined4 local_34;
  uint local_30;
  basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_> local_2c [16];
  int local_1c;
  undefined4 local_18;
  uint local_14;
  void *local_10;
  undefined1 *puStack_c;
  undefined4 local_8;

  uVar12 = DAT_01ab9cec;
  local_8._0_1_ = 0xff;
  local_8._1_3_ = 0xffffff;
  puStack_c = &LAB_011d29ab;
  local_10 = ExceptionList;
  uVar3 = DAT_01e44f28 ^ (uint)&stack0xfffffffc;
  ExceptionList = &local_10;
  local_b0 = param_3;
  local_c4 = param_2;
  local_a9 = 0;
  local_c0 = (undefined4 ***)((uint)local_c0 & 0xffffff00);
  local_c8 = local_c8 & 0xffffff00;
  local_bc = param_1;
  local_14 = uVar3;
  if ((*(byte *)(param_2 + 0x1e0) & 1) != 0) {
    local_64 = 0;
    local_60 = 0xf;
    local_74[0] = (undefined4 ***)((uint)local_74[0] & 0xffffff00);
    local_8 = 0;
    local_4c = 0;
    local_48 = 0xf;
    local_5c[0] = (undefined4 ***)((uint)local_5c[0] & 0xffffff00);
    FUN_00457390("icon_hero_",10);
    local_8._0_1_ = 1;
    pcVar4 = (char *)FUN_00939130(uVar3);
    pcVar14 = pcVar4;
    do {
      cVar2 = *pcVar14;
      pcVar14 = pcVar14 + 1;
    } while (cVar2 != '\0');
    FUN_004574c0(pcVar4,(int)pcVar14 - (int)(pcVar4 + 1));
    cVar2 = FUN_0093c830();
    local_c4 = CONCAT31(local_c4._1_3_,cVar2 == *(char *)(local_bc + 0x148));
    iVar5 = FUN_009396f0();
    iVar7 = local_b0;
    if (iVar5 != DAT_01265f20) {
      iVar7 = iVar5;
    }
    uVar3 = FUN_00857970(iVar7);
    uVar11 = uVar12;
    local_b4 = uVar3;
    if (uVar3 == 0) {
LAB_005b1ed1:
      uVar3 = (uint)local_a9 << 8;
LAB_005b1ed7:
      local_c0 = (undefined4 ****)0x0;
    }
    else {
      uVar6 = FUN_00939e40();
      iVar7 = FUN_00857970(uVar6);
      if (iVar7 == 0) {
        if ((*(byte *)(uVar3 + 0x1e0) & 1) == 0) {
          cVar2 = FUN_0093c830();
          if ((cVar2 != '\0') &&
             (cVar2 = FUN_0093c830(), uVar11 = DAT_01a41b58, cVar2 == *(char *)(local_bc + 0x148)))
          {
            uVar11 = DAT_01a41b54;
          }
          uVar3 = *(uint *)(uVar3 + 0x1e0);
          if ((uVar3 >> 0xd & 1) == 0) {
            if ((uVar3 >> 2 & 1) == 0) {
              if ((uVar3 >> 0xb & 1) == 0) {
                if ((uVar3 >> 10 & 1) == 0) {
                  if ((uVar3 & 0x110) == 0) goto LAB_005b1ed1;
                  local_34 = 0;
                  local_30 = 0xf;
                  local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
                  FUN_00457390("hud_pingicon_action_minion",0x1a);
                  local_8._0_1_ = 0xb;
                }
                else {
                  local_34 = 0;
                  local_30 = 0xf;
                  local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
                  FUN_00457390("hud_pingicon_action_minion_miner",0x20);
                  local_8._0_1_ = 10;
                }
              }
              else {
                local_34 = 0;
                local_30 = 0xf;
                local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
                FUN_00457390("hud_pingicon_action_gold_miner",0x1e);
                local_8._0_1_ = 9;
              }
            }
            else {
              piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Uncaptured");
              piVar10 = (int *)FUN_0093c1a0(&local_c0);
              if (*piVar10 == *piVar9) {
                local_34 = 0;
                local_30 = 0xf;
                local_44[0] = (undefined4 ***)((uint)local_44[0] & 0xffffff00);
                FUN_00457390("hud_battlelog_blackclaw",0x17);
                local_8._0_1_ = 5;
              }
              else {
                piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Captured");
                piVar10 = (int *)FUN_0093c1a0(&local_c0);
                if (*piVar10 == *piVar9) {
                  local_34 = 0;
                  local_30 = 0xf;
                  local_44[0] = (undefined4 ***)((uint)local_44[0] & 0xffffff00);
                  FUN_00457390("hud_battlelog_blackclaw",0x17);
                  local_8._0_1_ = 6;
                }
                else {
                  piVar9 = (int *)FUN_0081e810("5v5_Ghostwing");
                  piVar10 = (int *)FUN_0093c1a0(&local_c0);
                  if (*piVar10 == *piVar9) {
                    local_34 = 0;
                    local_30 = 0xf;
                    local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
                    FUN_00457390("hud_battlelog_ghostwing",0x17);
                    local_8._0_1_ = 7;
                  }
                  else {
                    if ((*(uint *)(local_b4 + 0x1e0) >> 0x1e & 1) == 0) goto LAB_005b1eb8;
                    local_34 = 0;
                    local_30 = 0xf;
                    local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
                    FUN_00457390("hud_pingicon_action_kraken",0x1a);
                    local_8._0_1_ = 8;
                  }
                }
              }
            }
          }
          else {
            local_34 = 0;
            local_30 = 0xf;
            local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
            FUN_00457390("hud_pingicon_action_turret",0x1a);
            local_8._0_1_ = 4;
          }
          std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                    ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_74,
                     (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_> *
                     )local_44);
          local_8._0_1_ = 1;
          FUN_00456d80();
        }
        else {
          local_34 = 0;
          local_30 = 0xf;
          local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
          FUN_00457390("icon_hero_",10);
          ppppuVar8 = local_44;
          if (0xf < local_30) {
            ppppuVar8 = (undefined4 ****)local_44[0];
          }
          local_8._0_1_ = 3;
          FUN_00457390(ppppuVar8,local_34);
          local_8._0_1_ = 1;
          FUN_00456d80();
          pcVar4 = (char *)FUN_00939130();
          pcVar14 = pcVar4;
          do {
            cVar2 = *pcVar14;
            pcVar14 = pcVar14 + 1;
          } while (cVar2 != '\0');
          FUN_004574c0(pcVar4,(int)pcVar14 - (int)(pcVar4 + 1));
          local_a9 = 1;
          cVar2 = FUN_0093c830();
          local_c8 = CONCAT31(local_c8._1_3_,cVar2 == *(char *)(local_bc + 0x148));
        }
LAB_005b1eb8:
        local_c0 = local_74;
        uVar3 = (uint)local_a9 << 8;
        if (0xf < local_60) {
          local_c0 = local_74[0];
        }
      }
      else {
        if ((*(byte *)(iVar7 + 0x1e0) & 1) == 0) {
          uVar3 = (uint)local_a9 << 8;
        }
        else {
          local_34 = 0;
          local_30 = 0xf;
          local_44[0] = (undefined4 ***)((uint)local_44[0]._1_3_ << 8);
          FUN_00457390("icon_hero_",10);
          ppppuVar8 = local_44;
          if (0xf < local_30) {
            ppppuVar8 = (undefined4 ****)local_44[0];
          }
          local_8._0_1_ = 2;
          FUN_00457390(ppppuVar8,local_34);
          local_8._0_1_ = 1;
          FUN_00456d80();
          pcVar4 = (char *)FUN_00939130();
          pcVar14 = pcVar4;
          do {
            cVar2 = *pcVar14;
            pcVar14 = pcVar14 + 1;
          } while (cVar2 != '\0');
          FUN_004574c0(pcVar4,(int)pcVar14 - (int)(pcVar4 + 1));
          uVar3 = 0x100;
          cVar2 = FUN_0093c830();
          local_c8 = CONCAT31(local_c8._1_3_,cVar2 == *(char *)(local_bc + 0x148));
        }
        if ((char)(uVar3 >> 8) == '\0') goto LAB_005b1ed7;
        local_c0 = local_74;
        if (0xf < local_60) {
          local_c0 = local_74[0];
        }
      }
    }
    ppppuVar8 = local_5c;
    if (0xf < local_48) {
      ppppuVar8 = (undefined4 ****)local_5c[0];
    }
    uVar6 = FUN_005b0150(PTR_s_build___HUDPartsCommon_atlas_01a40ab0,ppppuVar8,0);
    iVar7 = local_bc;
    local_8._0_1_ = 0xc;
    cVar2 = FUN_005b07c0(local_c0,"hud_stats_kills",&DAT_020e9d30,uVar6,1,1,local_c8,local_c4,uVar11
                         ,uVar12,0);
    FUN_00458550();
    if (cVar2 != '\0') {
      iVar7 = *(int *)(*(int *)(iVar7 + 0x144) + -4 + *(int *)(iVar7 + 0x13c) * 4);
      *(uint *)(iVar7 + 0x780) = (uVar3 >> 8) << 2 | *(uint *)(iVar7 + 0x780) & 0xfffffffb;
      *(uint *)(iVar7 + 0x9b4) = *(uint *)(iVar7 + 0x9b4) | 4;
    }
    if (0xf < local_48) {
      uVar3 = local_48 + 1;
      ppppuVar8 = (undefined4 ****)local_5c[0];
      if (0xfff < uVar3) {
        ppppuVar8 = (undefined4 ****)local_5c[0][-1];
        uVar3 = local_48 + 0x24;
        if (0x1f < (uint)((int)local_5c[0] + (-4 - (int)ppppuVar8))) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
      }
      FUN_011b8432(ppppuVar8,uVar3);
    }
    if (0xf < local_60) {
      uVar3 = local_60 + 1;
      ppppuVar8 = (undefined4 ****)local_74[0];
      if (0xfff < uVar3) {
        ppppuVar8 = (undefined4 ****)local_74[0][-1];
        uVar3 = local_60 + 0x24;
        if (0x1f < (uint)((int)local_74[0] + (-4 - (int)ppppuVar8))) {
                    /* WARNING: Subroutine does not return */
          _invalid_parameter_noinfo_noreturn();
        }
      }
      FUN_011b8432(ppppuVar8,uVar3);
    }
    goto LAB_005b2818;
  }
  if ((*(byte *)(param_2 + 0x1e2) & 1) == 0) goto LAB_005b2818;
  local_34 = 0;
  local_30 = 0xf;
  local_44[0] = (undefined4 ***)((uint)local_44[0] & 0xffffff00);
  FUN_00457390("white_background",0x10);
  local_4c = 0;
  local_48 = 0xf;
  local_5c[0] = (undefined4 ***)((uint)local_5c[0] & 0xffffff00);
  local_8._0_1_ = 0xe;
  local_8._1_3_ = 0;
  local_b4 = local_b4 & 0xffffff00;
  local_b0 = FUN_00857970(local_b0);
  if (local_b0 != 0) {
    cVar2 = FUN_0093c830();
    local_ab = cVar2 == *(char *)(local_bc + 0x148);
    uVar11 = FUN_00939e40();
    local_b8 = FUN_00857970(uVar11);
    uVar11 = uVar12;
    if (local_b8 == 0) {
      local_aa = 1;
      if (local_b0 == param_2) {
        pcVar4 = "GoldMine";
        pcVar14 = (char *)FUN_00939130();
        iVar7 = _strcoll(pcVar14,pcVar4);
        if (iVar7 == 0) {
          local_18 = 0xf;
          local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                         )0x0;
          local_1c = iVar7;
          FUN_00457390("hud_pingicon_action_kraken",0x1a);
          local_8._0_1_ = 0x10;
          std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                    ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_44,
                     local_2c);
          local_8._0_1_ = 0xe;
          FUN_00456d80();
          uVar11 = DAT_01ab9cec;
        }
        else {
          local_aa = 0;
        }
        goto LAB_005b23d8;
      }
      if ((*(byte *)(local_b0 + 0x1e0) & 1) == 0) {
        cVar2 = FUN_0093c830();
        if ((cVar2 != '\0') && (uVar11 = DAT_01a41b58, local_ab != '\0')) {
          uVar11 = DAT_01a41b54;
        }
        if ((*(byte *)(local_b0 + 0x1e0) & 1) != 0) goto LAB_005b21f1;
        uVar3 = *(uint *)(local_b0 + 0x1e0);
        if ((uVar3 >> 0xd & 1) == 0) {
          if ((uVar3 >> 0xb & 1) != 0) {
            local_1c = 0;
            local_18 = 0xf;
            local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                           )0x0;
            FUN_00457390("hud_pingicon_action_gold_miner",0x1e);
            local_8._0_1_ = 0x13;
            goto LAB_005b2341;
          }
          if ((uVar3 >> 10 & 1) != 0) {
            local_1c = 0;
            local_18 = 0xf;
            local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                           )0x0;
            FUN_00457390("hud_pingicon_action_minion_miner",0x20);
            local_8._0_1_ = 0x14;
            goto LAB_005b2341;
          }
          if ((uVar3 & 0x110) != 0) {
            local_1c = 0;
            local_18 = 0xf;
            local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                           )0x0;
            FUN_00457390("hud_pingicon_action_minion",0x1a);
            local_8._0_1_ = 0x15;
            goto LAB_005b2341;
          }
          if ((uVar3 >> 2 & 1) == 0) {
            local_aa = 0;
          }
          else {
            piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Uncaptured");
            piVar10 = (int *)FUN_0093c1a0(local_cc);
            if (*piVar10 == *piVar9) {
              local_1c = 0;
              local_18 = 0xf;
              local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                             )0x0;
              FUN_00457390("hud_battlelog_blackclaw",0x17);
              local_8._0_1_ = 0x16;
            }
            else {
              piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Captured");
              piVar10 = (int *)FUN_0093c1a0(&local_b8);
              if (*piVar10 == *piVar9) {
                local_1c = 0;
                local_18 = 0xf;
                local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                               )0x0;
                FUN_00457390("hud_battlelog_blackclaw",0x17);
                local_8._0_1_ = 0x17;
              }
              else {
                piVar9 = (int *)FUN_0081e810("5v5_Ghostwing");
                piVar10 = (int *)FUN_0093c1a0(&local_b8);
                if (*piVar10 == *piVar9) {
                  local_1c = 0;
                  local_18 = 0xf;
                  local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                                 )0x0;
                  FUN_00457390("hud_battlelog_ghostwing",0x17);
                  local_8._0_1_ = 0x18;
                }
                else {
                  param_2 = local_c4;
                  if ((*(uint *)(local_b0 + 0x1e0) >> 0x1e & 1) == 0) goto LAB_005b23d8;
                  local_1c = 0;
                  local_18 = 0xf;
                  local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                                 )0x0;
                  FUN_00457390("hud_pingicon_action_kraken",0x1a);
                  local_8._0_1_ = 0x19;
                }
              }
            }
            std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                      ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_44,
                       local_2c);
            local_8._0_1_ = 0xe;
            FUN_00456d80();
            param_2 = local_c4;
          }
        }
        else {
          local_1c = 0;
          local_18 = 0xf;
          local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                         )0x0;
          FUN_00457390("hud_pingicon_action_turret",0x1a);
          local_8._0_1_ = 0x12;
LAB_005b2341:
          std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                    ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_44,
                     local_2c);
          local_8._0_1_ = 0xe;
          FUN_00456d80();
        }
      }
      else {
LAB_005b21f1:
        cVar2 = FUN_009448b0();
        if ((cVar2 == '\0') && ((*(uint *)(param_2 + 0x1e0) >> 0xc & 1) == 0)) goto LAB_005b2128;
        local_1c = 0;
        local_18 = 0xf;
        local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>)
                      0x0;
        FUN_00457390("icon_hero_",10);
        local_8._0_1_ = 0x11;
        std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                  ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_44,
                   local_2c);
        local_8._0_1_ = 0xe;
        FUN_00456d80();
        uVar6 = FUN_00939130();
        FUN_00456d40(uVar6);
        local_c0 = (undefined4 ***)CONCAT31(local_c0._1_3_,1);
        local_c8 = CONCAT31(local_c8._1_3_,local_ab);
        local_aa = 1;
      }
    }
    else {
      if ((*(byte *)(local_b8 + 0x1e0) & 1) != 0) {
        local_1c = 0;
        local_18 = 0xf;
        local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>)
                      0x0;
        FUN_00457390("icon_hero_",10);
        local_8._0_1_ = 0xf;
        std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                  ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_44,
                   local_2c);
        local_8._0_1_ = 0xe;
        FUN_00456d80();
        uVar12 = FUN_00939130();
        FUN_00456d40(uVar12);
        local_a9 = 1;
        local_c0 = (undefined4 ***)CONCAT31(local_c0._1_3_,1);
        cVar2 = FUN_0093c830();
        local_c8 = CONCAT31(local_c8._1_3_,cVar2 == *(char *)(local_bc + 0x148));
        FUN_0093c830();
        uVar12 = DAT_01a41b58;
      }
LAB_005b2128:
      local_aa = local_a9;
    }
LAB_005b23d8:
    cVar2 = FUN_0093c830();
    local_a9 = cVar2 == *(char *)(local_bc + 0x148);
    uVar3 = *(uint *)(param_2 + 0x1e0);
    if ((uVar3 >> 2 & 1) == 0) {
      local_1c = 0;
      local_18 = 0xf;
      local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>)
                    0x0;
      if ((uVar3 >> 0xf & 1) == 0) {
        if ((uVar3 >> 0xd & 1) != 0) {
          FUN_00457390("hud_pingicon_action_turret",0x1a);
          local_8._0_1_ = 0x1f;
          goto LAB_005b2683;
        }
        if ((uVar3 >> 0xe & 1) != 0) {
          FUN_00457390("hud_battlelog_armory",0x14);
          local_8._0_1_ = 0x20;
          goto LAB_005b2683;
        }
        if ((uVar3 >> 0xb & 1) == 0) {
          FUN_00457390("hud_pingicon_action_minion_miner",0x20);
          local_8._0_1_ = 0x22;
        }
        else {
          FUN_00457390("hud_pingicon_action_gold_miner",0x1e);
          local_8._0_1_ = 0x21;
        }
        std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                  ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_5c,
                   local_2c);
        local_8._0_1_ = 0xe;
        FUN_00456d80();
        bVar1 = local_a9 ^ 1;
        if (local_ab == '\0') {
          bVar1 = local_a9;
        }
        local_b4 = (uint)bVar1;
        if (local_b0 == param_2) goto LAB_005b275c;
LAB_005b276d:
        if ((char)local_b4 == '\0') goto LAB_005b2787;
        uVar12 = DAT_01a41b54;
        if (local_a9 != 0) {
          uVar12 = DAT_01a41b58;
        }
      }
      else {
        FUN_00457390("hud_pingicon_action_vain_crystal",0x20);
        local_8._0_1_ = 0x1e;
LAB_005b2683:
        std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                  ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_5c,
                   local_2c);
        local_8._0_1_ = 0xe;
        FUN_00456d80();
LAB_005b275c:
        cVar2 = FUN_0093c830();
        if (cVar2 != '\0') goto LAB_005b276d;
      }
    }
    else {
      piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Uncaptured");
      piVar10 = (int *)FUN_0093c1a0(&local_b8);
      if (*piVar10 == *piVar9) {
        local_1c = 0;
        local_18 = 0xf;
        local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>)
                      0x0;
        FUN_00457390("hud_battlelog_blackclaw",0x17);
        local_8._0_1_ = 0x1a;
LAB_005b261d:
        std::basic_string<char,std::char_traits<char>,std::allocator<char>_>::operator=
                  ((basic_string<char,std::char_traits<char>,std::allocator<char>_> *)local_5c,
                   local_2c);
        local_8._0_1_ = 0xe;
        FUN_00456d80();
      }
      else {
        piVar9 = (int *)FUN_0081e810("5v5_Blackclaw_Captured");
        piVar10 = (int *)FUN_0093c1a0(&local_b8);
        if (*piVar10 == *piVar9) {
          local_1c = 0;
          local_18 = 0xf;
          local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                         )0x0;
          FUN_00457390("hud_battlelog_blackclaw",0x17);
          local_8._0_1_ = 0x1b;
          goto LAB_005b261d;
        }
        piVar9 = (int *)FUN_0081e810("5v5_Ghostwing");
        piVar10 = (int *)FUN_0093c1a0(&local_b8);
        if (*piVar10 == *piVar9) {
          local_1c = 0;
          local_18 = 0xf;
          local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                         )0x0;
          FUN_00457390("hud_battlelog_ghostwing",0x17);
          local_8._0_1_ = 0x1c;
          goto LAB_005b261d;
        }
        if ((*(uint *)(param_2 + 0x1e0) >> 0x1e & 1) != 0) {
          local_1c = 0;
          local_18 = 0xf;
          local_2c[0] = (basic_string<char,struct_std::char_traits<char>,class_std::allocator<char>_>
                         )0x0;
          FUN_00457390("hud_pingicon_action_kraken",0x1a);
          local_8._0_1_ = 0x1d;
          goto LAB_005b261d;
        }
      }
      cVar2 = FUN_0093c830();
      if (cVar2 == '\0') {
        local_b4 = CONCAT31(local_b4._1_3_,local_ab);
        goto LAB_005b276d;
      }
LAB_005b2787:
      uVar12 = DAT_01a41b58;
      if (local_a9 != 0) {
        uVar12 = DAT_01a41b54;
      }
    }
    if (local_aa == 0) {
      ppppuVar8 = (undefined4 ****)0x0;
    }
    else {
      ppppuVar8 = local_44;
      if (0xf < local_30) {
        ppppuVar8 = (undefined4 ****)local_44[0];
      }
    }
    ppppuVar13 = local_5c;
    if (0xf < local_48) {
      ppppuVar13 = (undefined4 ****)local_5c[0];
    }
    cVar2 = FUN_005b0710(ppppuVar8,"hud_stats_kills",&DAT_020e9d30,ppppuVar13,1,1,local_c8,0,uVar11,
                         uVar12,0);
    if (cVar2 != '\0') {
      FUN_005b38e0(local_c0,0);
    }
  }
  FUN_00456d80();
  FUN_00456d80();
LAB_005b2818:
  ExceptionList = local_10;
  __security_check_cookie(local_14 ^ (uint)&stack0xfffffffc);
  return;
}
