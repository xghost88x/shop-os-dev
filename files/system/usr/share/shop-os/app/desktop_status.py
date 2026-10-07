#!/usr/bin/env python3
"""Local desktop telemetry and an allowlisted launcher for Dad's Garage."""
import json
import os
import shutil
import subprocess
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


PORT = 17381
LOCK = threading.Lock()
WEATHER = {'available': False, 'label': 'Weather unavailable', 'updated': 0}
CACHE = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'dads-garage/weather.json'
ACTIONS = {
    'manuals': ['dolphin', str(Path.home()/'Documents/Shop Manuals')],
    'videos': ['python3', '/usr/share/shop-os/app/shop_os.py', '--page=videos'],
    'parts': ['python3', '/usr/share/shop-os/app/shop_os.py', '--page=parts'],
    'files': ['dolphin'],
    'firefox': ['flatpak', 'run', 'org.mozilla.firefox'],
    'chromium': ['flatpak', 'run', 'org.chromium.Chromium'],
    'support': ['flatpak', 'run', 'com.rustdesk.RustDesk'],
    'settings': ['systemsettings'],
    'apps': ['krunner'],
    'lock': ['loginctl', 'lock-session'],
    'restart': ['systemctl', 'reboot'],
    'shutdown': ['systemctl', 'poweroff'],
}


def get_json(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'DadsGarageOS/1.0'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def weather_label(code):
    if code == 0: return 'Clear'
    if code in (1, 2): return 'Partly cloudy'
    if code == 3: return 'Overcast'
    if code in (45, 48): return 'Fog'
    if code in (51, 53, 55, 56, 57): return 'Drizzle'
    if code in (61, 63, 65, 66, 67, 80, 81, 82): return 'Rain'
    if code in (71, 73, 75, 77, 85, 86): return 'Snow'
    if code in (95, 96, 99): return 'Thunderstorms'
    return 'Conditions unavailable'


def weather_loop():
    global WEATHER
    coordinates = None
    while True:
        try:
            if coordinates is None:
                data = get_json('https://geocoding-api.open-meteo.com/v1/search?' +
                                urllib.parse.urlencode({'name': 'Machesney Park', 'count': 10, 'countryCode': 'US'}))
                city = next(c for c in data.get('results', [])
                            if c.get('admin1') == 'Illinois' and c.get('country_code') == 'US')
                coordinates = (city['latitude'], city['longitude'])
            data = get_json('https://api.open-meteo.com/v1/forecast?' + urllib.parse.urlencode({
                'latitude': coordinates[0], 'longitude': coordinates[1],
                'current': 'temperature_2m,weather_code', 'temperature_unit': 'fahrenheit',
                'timezone': 'America/Chicago', 'forecast_days': 1}))
            current = data['current']
            weather = {'available': True, 'temperature': round(current['temperature_2m']),
                       'label': weather_label(current['weather_code']), 'updated': time.time()}
            with LOCK:
                WEATHER = weather
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            temporary = CACHE.with_suffix('.tmp')
            temporary.write_text(json.dumps(weather))
            temporary.replace(CACHE)
            delay = 900
        except (OSError, ValueError, KeyError, StopIteration, TypeError):
            delay = 120
        time.sleep(delay)


CPU_PREVIOUS = None


def snapshot():
    global CPU_PREVIOUS
    fields = Path('/proc/stat').read_text().splitlines()[0].split()[1:]
    ticks = [int(x) for x in fields[:8]]
    total, idle = sum(ticks), ticks[3] + (ticks[4] if len(ticks)>4 else 0)
    with LOCK:
        previous = CPU_PREVIOUS
        CPU_PREVIOUS = (total, idle)
        weather = dict(WEATHER)
    cpu = 0
    if previous and total>previous[0]:
        cpu = round(100*(1-(idle-previous[1])/(total-previous[0])))
    memory = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':',1)
        memory[key] = int(value.split()[0])*1024
    ram_total = memory['MemTotal']
    ram_used = ram_total-memory.get('MemAvailable',memory.get('MemFree',0))
    disk = shutil.disk_usage(str(Path.home()))
    battery, charging = None, False
    for supply in sorted(Path('/sys/class/power_supply').glob('*')):
        try:
            if (supply/'type').read_text().strip() == 'Battery':
                battery = int((supply/'capacity').read_text().strip())
                charging = (supply/'status').read_text().strip() in ('Charging','Full')
                break
        except (OSError, ValueError): pass
    network = False
    for interface in Path('/sys/class/net').glob('*'):
        if interface.name=='lo' or interface.name.startswith(('veth','docker','virbr','br-')): continue
        try:
            if (interface/'operstate').read_text().strip()=='up': network=True
        except OSError: pass
    age = max(0, time.time() - weather.get('updated', 0))
    weather['stale'] = age > 1800
    weather['ageMinutes'] = round(age/60) if weather.get('updated') else None
    uptime = float(Path('/proc/uptime').read_text().split()[0])
    return {'cpu': max(0,min(100,cpu)), 'ram': round(100*ram_used/ram_total),
            'ramUsed': round(ram_used/2**30, 1), 'ramTotal': round(ram_total/2**30, 1),
            'diskFree': round(disk.free/2**30, 1), 'diskUsed': round(100*disk.used/disk.total),
            'battery': battery, 'charging': charging,
            'network': 'Connected' if network else 'Disconnected',
            'uptimeMinutes': int(uptime/60), 'weather': weather}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass

    def permitted(self):
        # Block remote origins and DNS rebinding; Qt requests have no Origin.
        return (self.headers.get('Host') == '127.0.0.1:' + str(PORT)
                and self.headers.get('Origin') is None)

    def reply(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.permitted(): return self.reply(403, {'error': 'Local desktop requests only'})
        if self.path != '/status': return self.reply(404, {'error': 'Unknown request'})
        try: self.reply(200, snapshot())
        except OSError: self.reply(503, {'error': 'System information unavailable'})

    def do_POST(self):
        if not self.permitted(): return self.reply(403, {'error': 'Local desktop requests only'})
        if self.path != '/launch' or self.headers.get('Content-Type') != 'application/json':
            return self.reply(400, {'error': 'Invalid request'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 1024: raise ValueError()
            action = json.loads(self.rfile.read(length))['action']
            command = ACTIONS[action]
            if action == 'manuals': (Path.home()/'Documents/Shop Manuals').mkdir(parents=True,exist_ok=True)
            if not shutil.which(command[0]): return self.reply(503, {'error': 'Application is unavailable'})
            subprocess.Popen(command, start_new_session=True, stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.reply(200, {'ok': True})
        except (KeyError, ValueError, TypeError):
            self.reply(400, {'error': 'Unknown action'})
        except OSError:
            self.reply(503, {'error': 'Could not start application'})


def main():
    global WEATHER
    try:
        cached = json.loads(CACHE.read_text())
        if isinstance(cached, dict) and isinstance(cached.get('updated'), (int, float)):
            WEATHER = cached
    except (OSError, ValueError): pass
    try:
        server = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError:
        return  # Another instance already owns the desktop endpoint.
    threading.Thread(target=weather_loop, daemon=True).start()
    snapshot()
    server.serve_forever()


if __name__ == '__main__': main()
