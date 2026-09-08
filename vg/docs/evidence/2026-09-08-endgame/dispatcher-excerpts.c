// Original Ghidra dispatcher FUN_004cfec0, preferred base00400000
// source line 609
  case 0x3f1:
// source line 610
    bStack_e40 = 0;
// source line 611
    bStack_e3f = 0;
// source line 612
    bStack_e3e = 0;
// source line 613
    bStack_e3d = 0;
// source line 614
    bStack_e3c = 0;
// source line 615
    memmove(&bStack_e40,param_1,5);
// source line 616
    uVar11 = Ordinal_14(CONCAT13(bStack_e3d,CONCAT12(bStack_e3e,CONCAT11(bStack_e3f,bStack_e40))));
// source line 617
    FUN_0081a680(uVar11,bStack_e3c);
// source line 618
    local_8 = 0x22;
// source line 619
    goto LAB_004d030c;
// source line 4372
  case 0x48d:
// source line 4373
    memset(local_a60,0,0x64c);
// source line 4374
    puVar13 = local_760;
// source line 4375
    local_e30 = 0.0;
// source line 4376
    do {
// source line 4377
      fVar10 = local_e30;
// source line 4378
      uVar11 = Ordinal_8(DAT_01265f20);
// source line 4379
      local_a60[(int)fVar10] = uVar11;
// source line 4380
      auStack_a20[(int)fVar10] = DAT_01265f1a;
// source line 4381
      iVar8 = 10;
// source line 4382
      do {
// source line 4383
        uVar11 = Ordinal_8(DAT_01265f28);
// source line 4384
        *puVar13 = uVar11;
// source line 4385
        puVar13 = puVar13 + 1;
// source line 4386
        iVar8 = iVar8 + -1;
// source line 4387
      } while (iVar8 != 0);
// source line 4388
      local_e30 = (float)((int)local_e30 + 1);
// source line 4389
    } while ((int)local_e30 < 0x10);
// source line 4390
    local_434 = CONCAT11(DAT_01265f1a,DAT_01265f1a);
// source line 4391
    memmove(local_a60,
// source line 4392
            (void *)CONCAT13(bStack_e39,CONCAT12(bStack_e3a,CONCAT11(bStack_e3b,bStack_e3c))),0x64c)
// source line 4393
    ;
// source line 4394
    FUN_004c3a70(local_a60);
// source line 4395
    goto LAB_004d4fe0;
// source line 4396
  case 0x48f:
// source line 4433
    FUN_0081a230(uVar11,uVar12);
// source line 4434
    local_8 = 3;
// source line 4435
LAB_004d030c:
// source line 4436
    bStack_20 = 1;
// source line 4437
    FUN_0092c240(&uStack_2c);
// source line 4438
    local_3d6 = (float)CONCAT22(local_3d6._2_2_,(undefined2)local_3d6);
// source line 4439
    local_3ce = (float)CONCAT22(local_3ce._2_2_,(undefined2)local_3ce);
// source line 4440
    local_3ca = (float)CONCAT22(local_3ca._2_2_,(undefined2)local_3ca);
// source line 4441
    local_396 = (float)CONCAT22(local_396._2_2_,(undefined2)local_396);
// source line 4442
    local_392 = (float)CONCAT22(local_392._2_2_,(undefined2)local_392);
// source line 4443
    local_376 = (float)CONCAT22(local_376._2_2_,(undefined2)local_376);
// source line 4444
    local_372 = (float)CONCAT22(local_372._2_2_,(undefined2)local_372);
// source line 4445
    local_362 = (float)CONCAT22(local_362._2_2_,(undefined2)local_362);
