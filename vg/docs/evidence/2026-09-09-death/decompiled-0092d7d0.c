// Windows VA 0092d7d0; image base 00400000

void __fastcall FUN_0092d7d0(int param_1)

{
  undefined4 *puVar1;

  puVar1 = (undefined4 *)FUN_00859670(0x18,4);
  *puVar1 = Nuo::Kindred::IGameAction::vftable;
  puVar1[1] = *(undefined4 *)(param_1 + 4);
  puVar1[2] = *(undefined4 *)(param_1 + 8);
  *(undefined1 *)(puVar1 + 3) = *(undefined1 *)(param_1 + 0xc);
  *puVar1 = Nuo::Kindred::ActionActorDie::vftable;
  puVar1[4] = *(undefined4 *)(param_1 + 0x10);
  puVar1[5] = *(undefined4 *)(param_1 + 0x14);
  FUN_0092f720(puVar1);
  return;
}
