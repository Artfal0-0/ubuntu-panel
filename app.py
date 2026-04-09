from flask import Flask, render_template, jsonify, request, send_file, redirect
import subprocess
import os
import json
import threading
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Descargas')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def ejecutar_comando(comando):
    try:
        mi_env = os.environ.copy()
        if 'DISPLAY' not in mi_env:
            mi_env['DISPLAY'] = ':0' 
        if 'WAYLAND_DISPLAY' not in mi_env:
            mi_env['WAYLAND_DISPLAY'] = 'wayland-0'
        subprocess.Popen(comando, shell=True, env=mi_env)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clipboard', methods=['POST', 'GET'])
def manage_clipboard():
    mi_env = os.environ.copy()
    if 'WAYLAND_DISPLAY' not in mi_env:
        mi_env['WAYLAND_DISPLAY'] = 'wayland-0'

    if request.method == 'POST':
        texto = request.json.get('texto', '')
        if texto:
            try:
                proceso = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE, env=mi_env)
                proceso.communicate(input=texto.encode('utf-8'))
                return jsonify({"status": "ok"})
            except:
                return jsonify({"status": "error"}), 500
        return jsonify({"status": "empty"})
        
    elif request.method == 'GET':
        try:
            salida = subprocess.check_output(['wl-paste'], env=mi_env, text=True)
            return jsonify({"status": "ok", "texto": salida.strip()})
        except:
            return jsonify({"status": "error"}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error"}), 400
    file = request.files['file']
    if file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        ejecutar_comando(f'notify-send "Archivo Recibido" "{filename} guardado en Descargas"')
        return jsonify({"status": "ok", "filename": filename})
    return jsonify({"status": "error"}), 400

@app.route('/api/spotify/current')
def current_track():
    try:
        try:
            metadata = subprocess.check_output(['playerctl', 'metadata', '--format', '{{ title }}|||{{ artist }}']).decode('utf-8').strip()
            partes = metadata.split('|||')
            title = partes[0] if partes[0] else "Desconocido"
            artist = partes[1] if len(partes) > 1 else ""
        except:
            title = "Nada sonando"
            artist = ""

        try: pos = float(subprocess.check_output(['playerctl', 'position']).decode('utf-8').strip())
        except: pos = 0
        try: length = float(subprocess.check_output(['playerctl', 'metadata', 'mpris:length']).decode('utf-8').strip()) / 1000000.0
        except: length = 1
        try: shuffle = subprocess.check_output(['playerctl', 'shuffle']).decode('utf-8').strip()
        except: shuffle = "Off"
        try: loop = subprocess.check_output(['playerctl', 'loop']).decode('utf-8').strip()
        except: loop = "None"
        
        return jsonify({"title": title, "artist": artist, "pos": pos, "length": length, "shuffle": shuffle, "loop": loop})
    except:
        return jsonify({"title": "Nada sonando", "artist": "", "pos": 0, "length": 1, "shuffle": "Off", "loop": "None"})

@app.route('/api/spotify/art')
def spotify_art():
    try:
        art_url = subprocess.check_output(['playerctl', 'metadata', 'mpris:artUrl']).decode('utf-8').strip()
        if art_url.startswith('file://'):
            return send_file(art_url.replace('file://', ''))
        return redirect(art_url)
    except:
        return "", 404

@app.route('/api/spotify/seek/<float:position>')
def seek_track(position):
    ejecutar_comando(f"playerctl position {position}")
    return jsonify({"status": "ok"})

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

@app.route('/api/spotify/shuffle')
def toggle_shuffle():
    ejecutar_comando("playerctl shuffle Toggle")
    return jsonify({"status": "ok"})

@app.route('/api/spotify/repeat')
def toggle_repeat():
    try:
        current = subprocess.check_output(['playerctl', 'loop']).decode('utf-8').strip()
        if current == "None": nxt = "Playlist"
        elif current == "Playlist": nxt = "Track"
        else: nxt = "None"
        ejecutar_comando(f"playerctl loop {nxt}")
    except:
        ejecutar_comando("playerctl loop Playlist")
    return jsonify({"status": "ok"})

@app.route('/api/system/brightness/<int:level>')
def set_brightness(level):
    ejecutar_comando(f"brightnessctl set {max(1, min(100, level))}%")
    return jsonify({"status": "ok"})

@app.route('/api/system/volume/<int:vol_level>')
def set_volume(vol_level):
    ejecutar_comando(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {max(0, min(100, vol_level))}%")
    return jsonify({"status": "ok"})

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
        "discord": "discord",
        "github": "/opt/zen/zen https://github.com/Artfal0-0",
        "whatsapp": "/opt/zen/zen https://web.whatsapp.com/",
        "gemini": "/opt/zen/zen https://gemini.google.com/"
    }
    if app_name in comandos:
        ejecutar_comando(comandos[app_name])
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True, use_reloader=True)