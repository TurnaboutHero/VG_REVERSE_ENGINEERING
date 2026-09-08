'use strict';
const manifest = __PROBE_MANIFEST__;
let observer = null, hooks = [], installed = false, base = null;
let last = {}, counts = {};
function emit(tag, fields) { counts[tag] = (counts[tag] || 0) + 1; send(Object.assign({tag: tag, wall_ms: Date.now()}, fields || {})); }
function sampled(tag) { const now = Date.now(); if (now - (last[tag] || 0) < 500) return false; last[tag] = now; return true; }
function record() { return base.add(manifest.record_va).readFloat(); }
function state(p) { return {game: p.add(0x2bc).readFloat(), pause_bit: p.add(0x2c5).readU8() & 1}; }
function safeError(error) {
  const allowed = ['Error', 'TypeError', 'RangeError', 'ReferenceError', 'SyntaxError'];
  const name = allowed.includes(error.name) ? error.name : 'Error';
  // Native exception text can include addresses or application content.
  return {error_name: name, error_message: 'Observer operation failed; native details omitted'};
}
function guarded(fn) { try { fn(); } catch (error) { emit('read_error', safeError(error)); } }
function install(module) {
  if (installed || module.name !== manifest.module) return;
  if (Process.arch !== manifest.arch) { emit('rejected_arch'); return; }
  base = module.base;
  // Check every entry before Interceptor patches any entry.
  for (const name of Object.keys(manifest.hooks)) {
    const h = manifest.hooks[name];
    const bytes = new Uint8Array(base.add(h.va).readByteArray(h.hex.length / 2));
    const actual = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
    if (actual !== h.hex) { emit('rejected_bytes', {hook: name}); return; }
  }
  installed = true;
  function attach(name, callbacks) { hooks.push(Interceptor.attach(base.add(manifest.hooks[name].va), callbacks)); }
  try {
    attach('timer', {onEnter(args) { this.p = args[0]; }, onLeave() { guarded(() => {
      const raw = this.p.add(0x20).readDouble();
      if (raw > 1 || sampled('timer')) emit('timer', {raw: raw, capped_scaled: this.p.add(0x18).readDouble(), scale: this.p.add(0x28).readDouble(), record: record()});
    }); }});
    attach('game_get', {onEnter(args) { guarded(() => { if (sampled('game')) emit('game', Object.assign(state(args[0]), {record: record()})); }); }});
    for (const name of ['clock_0451', 'clock_046f']) attach(name, {
      onEnter(args) { this.p = args[0]; guarded(() => { this.before = state(this.p); }); },
      onLeave() { guarded(() => { emit(name, {before: this.before, after: state(this.p), record: record()}); }); }
    });
    attach('writer', {onEnter(args) { guarded(() => {
      const p = args[0], op = (p.readU8() << 8) | p.add(1).readU8();
      if (op !== 0x451 && op !== 0x46f) return;
      const fields = {opcode: op, record: record()};
      if (op === 0x46f && args[1].toUInt32() >= 71) fields.snapshot_game = new DataView(p.add(66).readByteArray(4)).getFloat32(0, false);
      emit('writer', fields);
    }); }});
    attach('record_start', {onEnter() { guarded(() => { emit('record_start_before', {record: record()}); }); }, onLeave() { guarded(() => { emit('record_start_after', {record: record()}); }); }});
    attach('record_tick', {onEnter() { this.log = sampled('record_tick'); if (this.log) guarded(() => { this.before = record(); }); }, onLeave() { if (this.log) guarded(() => { emit('record_tick', {before: this.before, after: record()}); }); }});
    emit('hooks_installed', {count: hooks.length});
  } catch (error) { hooks.forEach(h => h.detach()); hooks = []; emit('attach_error', safeError(error)); }
}
rpc.exports = { stop() { if (observer) observer.detach(); hooks.forEach(h => h.detach()); hooks = []; return {counts: counts}; } };
if (Process.arch !== manifest.arch) emit('rejected_arch');
else observer = Process.attachModuleObserver({onAdded(module) { guarded(() => install(module)); }});
