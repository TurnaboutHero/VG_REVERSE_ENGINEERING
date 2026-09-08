// Windows VA 00819f30; image base 00400000

undefined4 * __thiscall FUN_00819f30(undefined4 *param_1,undefined4 param_2,undefined4 param_3)

{
  param_1[4] = param_2;
  param_1[5] = param_3;
  param_1[1] = 0;
  param_1[2] = 0;
  *(undefined1 *)(param_1 + 3) = 0;
  *param_1 = Nuo::Kindred::ActionActorDie::vftable;
  return param_1;
}
