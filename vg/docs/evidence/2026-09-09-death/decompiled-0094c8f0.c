// Windows VA 0094c8f0; image base 00400000

void __fastcall FUN_0094c8f0(int param_1)

{
  char cVar1;
  int iVar2;

  if (((DAT_0209e204 == '\0') && (iVar2 = FUN_00857970(*(undefined4 *)(param_1 + 0x10)), iVar2 != 0)
      ) && (cVar1 = FUN_00558e40(), cVar1 != '\0')) {
    FUN_0092c110();
    FUN_00540c30(iVar2,*(undefined4 *)(param_1 + 0x14));
    if (DAT_0209e205 != '\0') {
      FUN_00566400();
      return;
    }
    FUN_0054fa00(iVar2,*(undefined4 *)(param_1 + 0x14));
  }
  return;
}
