#!/usr/bin/env python3
"""Observe exact-build ARM64 startup clocks, then stop only the new test process this runner creates."""
import argparse
import hashlib
import json
import threading
import time
from pathlib import Path

EXPECTED_SHA = 'cd1b8831f82c469274613fc30f1f1f6e78c788102cdad7db5db2c04b96580a47'


def seconds(value):
    result = float(value)
    if not 1 <= result <= 60:
        raise argparse.ArgumentTypeError('seconds must be between 1 and 60')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', required=True, help='Frida device ID, normally adb serial')
    parser.add_argument('--package', default='com.superevilmegacorp.game')
    parser.add_argument('--elf', type=Path, required=True, help='Exact extracted ARM64 ELF, SHA256 validated before connection')
    parser.add_argument('--seconds', type=seconds, default=45)
    parser.add_argument('--output', type=Path, required=True, help='New JSONL file; refuses overwrite')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'probe-manifest.json').read_text())
    if hashlib.sha256(args.elf.read_bytes()).hexdigest() != EXPECTED_SHA or manifest['sha256'] != EXPECTED_SHA:
        parser.error('ELF SHA256 mismatch; only the exact analyzed build is accepted')
    # No Frida dependency required for help or argument/ELF rejection.
    import frida
    args.output.parent.mkdir(parents=True, exist_ok=True)
    error_tags = {'script_error', 'read_error', 'attach_error', 'rejected_arch', 'rejected_bytes',
                  'cleanup_script_unavailable', 'cleanup_detach_failed', 'cleanup_resume_failed', 'cleanup_kill_failed'}
    counts = {}
    lock = threading.Lock()
    detached = threading.Event()
    device = session = script = None
    pid = None
    resumed = False
    failure = None
    started = time.monotonic()
    with args.output.open('x', encoding='utf-8') as log:
        def write(row):
            with lock:
                log.write(json.dumps(row, ensure_ascii=True) + '\n')
                log.flush()
        def message(row, _data):
            if row.get('type') == 'send':
                payload = row.get('payload', {})
                tag = payload.get('tag', 'unknown')
                with lock:
                    counts[tag] = counts.get(tag, 0) + 1
                write(payload)
            elif row.get('type') == 'error':
                write({'tag': 'script_error', 'error_name': 'ScriptError', 'error_message': 'Injected script failed; native details omitted'})
                with lock:
                    counts['script_error'] = counts.get('script_error', 0) + 1
        try:
            device = frida.get_device(args.device, timeout=10)
            # Avoid replacing an already-running user game instance.
            if any(app.identifier == args.package and app.pid for app in device.enumerate_applications()):
                raise RuntimeError('Package already running; no process was replaced')
            pid = device.spawn([args.package])
            session = device.attach(pid)
            session.on('detached', lambda *_: detached.set())
            source = (root / 'clock_probe.js').read_text().replace('__PROBE_MANIFEST__', json.dumps(manifest))
            script = session.create_script(source)
            script.on('message', message)
            script.load()
            device.resume(pid)
            resumed = True
            deadline = time.monotonic() + args.seconds
            while time.monotonic() < deadline and not detached.is_set():
                detached.wait(min(0.25, max(0, deadline - time.monotonic())))
        except Exception as exc:
            failure = type(exc).__name__
            write({'tag': 'runner_error', 'error_type': failure, 'error_message': 'Runner operation failed; device details omitted'})
        finally:
            detached_before_cleanup = detached.is_set()
            def bounded_cleanup(operation, timeout):
                cancellable = frida.Cancellable()
                alarm = threading.Timer(timeout, cancellable.cancel)
                alarm.daemon = True
                alarm.start()
                try:
                    with cancellable:
                        operation()
                finally:
                    alarm.cancel()

            # The PID is assigned only after our own spawn succeeds. Existing
            # application instances are refused above and never reach this kill.
            spawn_terminated = False
            if device is not None and pid is not None:
                try:
                    bounded_cleanup(lambda: device.kill(pid), 5)
                    spawn_terminated = True
                    detached.wait(2)
                except frida.ProcessNotFoundError:
                    spawn_terminated = True
                except Exception as exc:
                    counts['cleanup_kill_failed'] = counts.get('cleanup_kill_failed', 0) + 1
                    write({'tag': 'cleanup_kill_failed', 'error_type': type(exc).__name__,
                           'error_message': 'Owned test process termination failed'})
            # A frozen target cannot service script RPCs. Kill the owned test
            # instance first; bound detach if the session has not yet closed.
            cleanup_confirmed = session is None or detached.is_set()
            if session is not None and not detached.is_set():
                try:
                    bounded_cleanup(session.detach, 8)
                    cleanup_confirmed = True
                except Exception as exc:
                    counts['cleanup_detach_failed'] = counts.get('cleanup_detach_failed', 0) + 1
                    write({'tag': 'cleanup_detach_failed', 'error_type': type(exc).__name__,
                           'error_message': 'Bounded session detach failed; hook removal unconfirmed'})
            if pid is not None and not spawn_terminated:
                cleanup_confirmed = False
            # Never label this experiment complete solely because boot/hooks succeeded.
            clock_evidence = bool(counts.get('writer') and counts.get('game') and counts.get('timer'))
            summary = {'tag': 'summary', 'elapsed_seconds': round(time.monotonic() - started, 3),
                       'counts': counts, 'failure': failure, 'detached_early': detached_before_cleanup,
                       'observation': 'clock_events_observed_needs_analysis' if clock_evidence else 'boot_only_or_insufficient_clock_evidence',
                       'native_cause_confirmed': False, 'spawn_resumed': resumed,
                       'cleanup_confirmed': cleanup_confirmed, 'spawn_terminated': spawn_terminated,
                       'probe_errors': sorted(tag for tag in error_tags if counts.get(tag)),
                       'identity': 'host ELF exact SHA plus all runtime hook-entry byte checks; deployment identity must be independently verified'}
            write(summary)
    print(json.dumps(summary))
    return 1 if failure or not counts.get('hooks_installed') or any(counts.get(tag) for tag in error_tags) else 0


if __name__ == '__main__':
    raise SystemExit(main())
