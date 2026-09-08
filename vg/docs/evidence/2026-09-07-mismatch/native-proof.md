# Android 4.13.4 snapshot baseline native proof

Static analysis of existing `work/official-apk-comparison/libGameKindred-arm64.so`; no download, install, execution of APK, or production edits. Disassembly generated using existing elf_probe.py and Capstone. Addresses below are Android virtual addresses; payload offsets are decimal unless hex-prefixed.

## Snapshot stat dataflow

Receiver 0x828a10 uses its incoming pointer as x19. At 0x828a54..58 it tests uint32 payload+0x146: nonzero skips baseline decoding. For zero:

| Payload float offset | Receiver instruction | Temporary stat offset from SP+0x6c8 | Stat meaning |
|---|---|---|---|
| 298 / 0x12a | 0x828c30 loads 64 bits from payload+0x126; 0x828c38 stores at SP+0x768, so second float is SP+0x76c | +0xa4 = 41*4 | attribute 41, kills |
| 302 / 0x12e | 0x828c3c loads; 0x828c44 stores SP+0x770 | +0xa8 = 42*4 | attribute 42, deaths |
| 306 / 0x132 | 0x828cd0 loads; 0x828cd4 stores SP+0x9c4 | +0x2fc = 0x2d0+11*4 | resource 11, assists |
| 310 / 0x136 | 0x828cdc loads; 0x828ce0 stores SP+0x9d0 | +0x308 = 0x2d0+14*4 | resource 14; CS label not independently proven here |

0x828c64..78 ORs 0x1f81e2049ff5 into stat valid mask SP+0x9d8 (temp+0x310); bits 41 and 42 are set. This matters because application of attributes is mask-conditional.

0x828e74 passes temporary stat pointer on stack+0x10. Constructor 0xc03320 has FP = caller SP-0x10, so its 0xc033ec load `[FP+0x20]` receives exactly that pointer. At 0xc03488..98 it calls 0xc4d208 with destination event+0x50 and source temp. 0xc4d208 branches to 0xc4d20c, which copies all three 45-float attribute arrays, remaining stat fields, resources, and mask.

The event vtable installed is 0x2711600. Relocation slots: +0x10→0xc03768; +0x18→0xc038d0; +0x20→0xc03e50. Receiver 0x828ee0 calls 0xbe20fc, which dispatches vtable+0x20. 0xc03e50 allocates event storage, copies event+0x50 with the same copy function, and calls 0xbe2364 to insert the copy. This proves the baseline survives queue cloning.

Application method 0xc038d0 obtains actor through 0x18887c4 at 0xc0392c and stores it in x19. At 0xc03a40..50, unless event+0x368 flag is nonzero, it calls 0xc5ba64(actor,event+0x50). That method loads actor+0x40 then tail-calls 0xc5f94c. The latter assigns baseline attribute arrays when corresponding mask bits are set, and unconditionally copies all 16 resources:

- attribute base arrays: source +0/+0xb4/+0x168 → actor-stat +0x38/+0xec/+0x1a0;
- resources: source +0x2d0 → actor-stat +0x308.

Therefore kills baseline reaches actor-stat+0xdc; deaths +0xe0; assists +0x334; resource14 +0x340. This is assignment, not addition.

Existing independent native label proof in `android-stat-export.txt` binds the effective attribute41/42 calculations to literal `myKills` (0x81cbc4 onward) and `myDeaths` (0x81cbfc onward); resource11 at actor-stat+0x334 is loaded into s15 at 0x81cb88 and exported as literal `myAssists` at 0x81cc88..b4. Thus the snapshot fields feed the same actual stat storage used for named KDA export. This is stronger than correlation with result screenshots.

## Clock evidence and limit

0x82b4c8 receiver loads float payload+0x40 at 0x82b504, passes s0 into 0x8bd430, and 0x8bd488 stores it at game-object+0x2bc. Proven network-to-state assignment. This bounded audit did NOT trace +0x2bc to displayed clock rendering; avoid claiming that additional proof.

## Implication

A replay beginning with nonzero snapshot stats cannot be calculated correctly by starting at zero and summing only later ADD records. Each segment snapshot is a baseline, not another increment. Separate capture states must not be merged simply because numbered files appear adjacent. This static proof itself does not validate any particular reconstructed final score or determine why files came to be mixed.

## Evidence files

- snapshot-disassembly.txt: receiver and constructor
- snapshot-copy-queue.txt: copy thunk and vtable dispatch
- snapshot-copy-details.txt: queue clone and actual copy loop
- snapshot-apply.txt: event virtual methods and actor application
- stat-assignment.txt: actor baseline assignment
- actor-stat-clock.txt: clock receiving and actor stat forwarding
