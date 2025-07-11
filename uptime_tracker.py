import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)
STATE_FILE = LOG_DIR / 'uptime.json'
HEARTBEAT_FILE = LOG_DIR / 'heartbeat.json'

_state = {
    'time_started': None,
    'time_restarted': None,
    'last_commit_hash': None,
}

def _current_commit():
    import subprocess
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    except Exception:
        return 'unknown'

def record_start():
    now = datetime.now(timezone.utc).isoformat()
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        data.setdefault('time_started', now)
        data['time_restarted'] = now
    else:
        data = {
            'time_started': now,
            'time_restarted': None,
        }
    data['last_commit_hash'] = _current_commit()
    STATE_FILE.write_text(json.dumps(data))
    _state.update(data)


def load_state():
    if STATE_FILE.exists():
        _state.update(json.loads(STATE_FILE.read_text()))


def get_uptime():
    if not _state['time_started']:
        return 0
    start = datetime.fromisoformat(_state['time_started'])
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - start).total_seconds()


def heartbeat(verbose=False):
    data = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime': get_uptime(),
        'version': os.getenv('APP_VERSION', '4.0.0'),
    }
    if verbose:
        data['last_restart'] = _state.get('time_restarted')
        data['commit'] = _state.get('last_commit_hash')
        data['memory_sync'] = os.path.exists('addons/sterling_os/memory_timeline.json')
    return data


def log_heartbeat():
    data = heartbeat()
    HEARTBEAT_FILE.write_text(json.dumps(data))
    print(json.dumps(data))


def start_heartbeat_logger(interval=60):
    if interval <= 0:
        return
    def loop():
        while True:
            log_heartbeat()
            time.sleep(interval)
    t = threading.Thread(target=loop, daemon=True)
    t.start()

load_state()
record_start()
start_heartbeat_logger(float(os.getenv('HEARTBEAT_INTERVAL', '60')))
