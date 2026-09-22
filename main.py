import os
import subprocess
import urllib.request
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# ساخت پوشه داده‌ها
os.makedirs('/data', exist_ok=True)

# دانلود خودکار فایل سرور در صورت عدم وجود (به دلیل دیسک Volume)
JAR_PATH = '/data/server.jar'
if not os.path.exists(JAR_PATH):
    print("در حال دانلود فایل سرور ماینکرافت...")
    url = "https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/497/downloads/paper-1.20.4-497.jar"
    urllib.request.urlretrieve(url, JAR_PATH)
    print("دانلود تکمیل شد.")

# تایید قوانین EULA
with open('/data/eula.txt', 'w') as f:
    f.write('eula=true\n')

# تنظیمات اولیه سرور
if not os.path.exists('/data/server.properties'):
    with open('/data/server.properties', 'w') as f:
        f.write('online-mode=false\nserver-port=25565\nmotd=My Railway Minecraft Server\n')

mc_process = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>پنل مدیریت ماینکرافت</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #121212; color: #fff; text-align: center; padding: 40px; }
        .card { background: #1e1e1e; padding: 30px; border-radius: 12px; display: inline-block; width: 350px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        button { padding: 12px 20px; font-size: 16px; border: none; border-radius: 6px; cursor: pointer; margin: 10px; font-weight: bold; }
        .btn-start { background: #4CAF50; color: white; }
        .btn-stop { background: #f44336; color: white; }
        .status { font-size: 20px; margin: 20px 0; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎮 داشبورد سرور ماینکرافت</h2>
        <div id="status" class="status">در حال دریافت وضعیت...</div>
        <button class="btn-start" onclick="sendAction('start')">▶ روشن کردن سرور</button>
        <button class="btn-stop" onclick="sendAction('stop')">⏹ خاموش کردن سرور</button>
    </div>

    <script>
        async function checkStatus() {
            try {
                let res = await fetch('/api/status');
                let data = await res.json();
                let el = document.getElementById('status');
                if (data.status === 'ONLINE') {
                    el.innerText = 'وضعیت: 🟢 آنلاین';
                    el.style.color = '#4CAF50';
                } else {
                    el.innerText = 'وضعیت: 🔴 خاموش';
                    el.style.color = '#f44336';
                }
            } catch (e) {}
        }

        async function sendAction(action) {
            let res = await fetch('/api/' + action, { method: 'POST' });
            let data = await res.json();
            alert(data.message);
            checkStatus();
        }

        setInterval(checkStatus, 3000);
        checkStatus();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def status():
    global mc_process
    running = mc_process is not None and mc_process.poll() is None
    return jsonify({"status": "ONLINE" if running else "OFFLINE"})

@app.route('/api/start', methods=['POST'])
def start_server():
    global mc_process
    if mc_process is None or mc_process.poll() is not None:
        if not os.path.exists(JAR_PATH):
            return jsonify({"message": "فایل server.jar یافت نشد. در حال دریافت..."})
        mc_process = subprocess.Popen(
            ['java', '-Xmx1024M', '-Xms512M', '-jar', 'server.jar', 'nogui'],
            cwd='/data'
        )
        return jsonify({"message": "سرور در حال روشن شدن است..."})
    return jsonify({"message": "سرور از قبل روشن است."})

@app.route('/api/stop', methods=['POST'])
def stop_server():
    global mc_process
    if mc_process and mc_process.poll() is None:
        mc_process.terminate()
        mc_process = None
        return jsonify({"message": "سرور خاموش شد."})
    return jsonify({"message": "سرور خاموش است."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
