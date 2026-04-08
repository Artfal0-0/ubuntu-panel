from flask import Flask, render_template, jsonify, request
import subprocess
import os
import json
import threading

app = Flask(__name__)

def ejecutar_comando(comando):
    try:
        mi_env = os.environ.copy()
        if 'DISPLAY' not in mi_env:
            mi_env['DISPLAY'] = ':0' 
        subprocess.Popen(comando, shell=True, env=mi_env)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system/brightness/<int:level>')
def set_brightness(level):
    level = max(5, min(100, level))
    ejecutar_comando(f"brightnessctl set {level}%")
    return jsonify({"status": "ok"})

@app.route('/api/spotify/current')
def current_track():
    try:
        cancion = subprocess.check_output(['playerctl', 'metadata', '--format', '{{ title }} - {{ artist }}']).decode('utf-8').strip()
    except:
        cancion = "Nada sonando"
    return jsonify({"cancion": cancion})

@app.route('/api/spotify/playpause')
def play_pause():
    ejecutar_comando("playerctl play-pause")
    return jsonify({"status": "ok"})

@app.route('/api/spotify/next')
def next_track():
    ejecutar_comando("playerctl next")
    return jsonify({"status": "ok"})

@app.route('/api/spotify/prev')
def prev_track():
    ejecutar_comando("playerctl previous")
    return jsonify({"status": "ok"})

@app.route('/api/system/volume/<int:vol_level>')
def set_volume(vol_level):
    vol = max(0, min(100, vol_level))
    ejecutar_comando(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {vol}%")
    return jsonify({"status": "ok", "volume": vol})

@app.route('/api/system/lock')
def lock_screen():
    ejecutar_comando("dbus-send --type=method_call --dest=org.gnome.ScreenSaver /org/gnome/ScreenSaver org.gnome.ScreenSaver.Lock")
    return jsonify({"status": "ok"})

@app.route('/api/apps/<app_name>')
def launch_app(app_name):
    comandos = {
        "spotify": "spotify",
        "terminal": "gnome-terminal",
        "calculadora": "gnome-calculator",
        "onlyoffice": "onlyoffice-desktopeditors",
        "configuracion": "gnome-control-center",
        "antigravity": "/usr/share/antigravity/antigravity",
        "navegador": "/opt/zen/zen",
        "archivos": "nautilus",
        "vscode": "code",
        "monitor": "gnome-system-monitor",
        "captura": "gnome-screenshot -i", 
        "gimp": "gimp",
        "vlc": "vlc",
        "discord": "discord"
    }
    
    comando = comandos.get(app_name)
    if comando:
        ejecutar_comando(comando)
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "App no encontrada"}), 404

@app.route('/manifest.json')
def manifest():
    manifest_data = {
        "name": "Ubuntu Panel",
        "short_name": "Panel",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#1a0b14",
        "theme_color": "#2c001e",
        "icons": [{
            "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='none' stroke='%23E95420' stroke-width='8'/><circle cx='50' cy='14' r='10' fill='%23E95420'/><circle cx='81' cy='67' r='10' fill='%23E95420'/><circle cx='19' cy='67' r='10' fill='%23E95420'/></svg>",
            "sizes": "any",
            "type": "image/svg+xml"
        }]
    }
    return jsonify(manifest_data)

@app.route('/sw.js')
def service_worker():
    sw_code = """
    self.addEventListener('install', (e) => { self.skipWaiting(); });
    self.addEventListener('activate', (e) => { e.waitUntil(clients.claim()); });
    self.addEventListener('fetch', (e) => { });
    """
    return app.response_class(sw_code, mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True, use_reloader=True)