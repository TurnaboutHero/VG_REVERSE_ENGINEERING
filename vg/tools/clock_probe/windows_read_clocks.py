"""Read scalar clocks from one exact Windows client. No injection or memory writes."""
import argparse
import ctypes
import hashlib
import json
import struct
import time
from ctypes import wintypes
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--pid', type=int, required=True)
p.add_argument('--exe', required=True, help='Path to the exact analyzed Windows Vainglory.exe')
p.add_argument('--seconds', type=float, default=120)
p.add_argument('--output', required=True, help='New JSONL output; refuses overwrite')
a = p.parse_args()
if not 0 < a.pid <= 0xffffffff:
    p.error('pid must be a positive Windows DWORD')
if not 0 < a.seconds <= 600:
    p.error('seconds must be finite and within(0,600]')
exe = Path(a.exe)
if hashlib.sha256(exe.read_bytes()).hexdigest() != '659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642':
    raise RuntimeError('Wrong build')
k = ctypes.WinDLL('kernel32', use_last_error=True)
k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k.OpenProcess.restype = wintypes.HANDLE
k.CloseHandle.argtypes = [wintypes.HANDLE]
k.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k.ReadProcessMemory.restype = wintypes.BOOL
k.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
k.CreateToolhelp32Snapshot.restype = wintypes.HANDLE

class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [('dwSize', wintypes.DWORD), ('th32ModuleID', wintypes.DWORD), ('th32ProcessID', wintypes.DWORD), ('GlblcntUsage', wintypes.DWORD), ('ProccntUsage', wintypes.DWORD), ('modBaseAddr', ctypes.c_void_p), ('modBaseSize', wintypes.DWORD), ('hModule', wintypes.HMODULE), ('szModule', wintypes.WCHAR * 256), ('szExePath', wintypes.WCHAR * 260)]
k.Module32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MODULEENTRY32W)]
k.Module32FirstW.restype = wintypes.BOOL
k.Module32NextW.argtypes = k.Module32FirstW.argtypes
k.Module32NextW.restype = wintypes.BOOL
snap = k.CreateToolhelp32Snapshot(0x18, a.pid)
if snap == ctypes.c_void_p(-1).value:
    raise ctypes.WinError(ctypes.get_last_error())
base = None
try:
    entry = MODULEENTRY32W()
    entry.dwSize = ctypes.sizeof(entry)
    ok = k.Module32FirstW(snap, ctypes.byref(entry))
    while ok:
        if entry.szModule.lower() == 'vainglory.exe':
            if Path(entry.szExePath).resolve() != exe.resolve():
                raise RuntimeError('Unexpected module path')
            base = entry.modBaseAddr
            break
        ok = k.Module32NextW(snap, ctypes.byref(entry))
finally:
    k.CloseHandle(snap)
if base is None:
    raise RuntimeError('Game module absent')
h = k.OpenProcess(0x410, False, a.pid)
if not h:
    raise ctypes.WinError(ctypes.get_last_error())

def read(addr, n):
    buf = ctypes.create_string_buffer(n)
    done = ctypes.c_size_t()
    if not k.ReadProcessMemory(h, addr, buf, n, ctypes.byref(done)) or done.value != n:
        raise ctypes.WinError(ctypes.get_last_error())
    return buf.raw
try:
    guards = {0x148870: 'd98194010000c3', 0x149e20: 'a1241c0902c3', 0x149d20: '558becf30f104508f30f1181940100005dc20400'}
    # The loader rebases the singleton getter's absolute address operand.
    guards[0x149e20] = (b'\xa1' + struct.pack('<I', base + 0x1c91c24) + b'\xc3').hex()
    for rva, expected in guards.items():
        if read(base + rva, len(bytes.fromhex(expected))).hex() != expected:
            raise RuntimeError(f'Runtime guard mismatch at RVA{rva:x}')
    with open(a.output, 'x') as out:
        out.write(json.dumps({'tag': 'identity', 'pid': a.pid, 'base': hex(base), 'guards': 3, 'method': 'ReadProcessMemory only', 'sha256': '659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642'}) + '\n')
        out.flush()
        start = time.monotonic()
        samples = 0
        while time.monotonic() - start < a.seconds:
            try:
                obj = struct.unpack('<I', read(base + 0x1c91c24, 4))[0]
                record = struct.unpack('<f', read(base + 0x1af0b30, 4))[0]
                row = {'tag': 'sample', 'wall_ns': time.time_ns(), 'elapsed': time.monotonic() - start, 'record_clock': record, 'game_clock': None, 'clock_gate_bit': None}
                if obj:
                    field = read(obj + 0x194, 10)
                    row.update(game_clock=struct.unpack('<f', field[:4])[0], clock_gate_bit=field[9] & 1)
                out.write(json.dumps(row, allow_nan=False) + '\n')
                out.flush()
                samples += 1
            except OSError as e:
                out.write(json.dumps({'tag': 'read_error', 'error': type(e).__name__, 'elapsed': time.monotonic() - start}) + '\n')
                raise
            time.sleep(0.1)
        out.write(json.dumps({'tag': 'summary', 'samples': samples, 'elapsed': time.monotonic() - start, 'native_cause_confirmed': False}) + '\n')
finally:
    k.CloseHandle(h)
