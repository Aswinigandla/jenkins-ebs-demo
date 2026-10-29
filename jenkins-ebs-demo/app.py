from flask import Flask, request, redirect, render_template_string
from pathlib import Path
import os

app = Flask(__name__)
DATA_DIR = Path(os.environ.get("EBS_DATA_DIR", "/mnt/ebs-data"))
DATA_FILE = DATA_DIR / "notes.txt"

PAGE = '''
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jenkins + EBS Demo</title>
<style>
body{font-family:Arial,sans-serif;max-width:760px;margin:40px auto;padding:0 18px;background:#f5f7fb;color:#172033}
main{background:white;padding:28px;border-radius:14px;box-shadow:0 4px 18px #0001}
h1{color:#174ea6}input{width:70%;padding:11px}button{padding:11px 16px;cursor:pointer}
li{margin:9px 0;overflow-wrap:anywhere}.small{color:#5a6475;font-size:.92rem}
</style></head><body><main>
<h1>Jenkins + AWS EBS Demo</h1>
<p>Deployed by Jenkins. Notes are saved on a separate EBS-mounted volume.</p>
<form method="post" action="/add"><input name="note" placeholder="Type a note to save on EBS" maxlength="300" required><button>Save note</button></form>
<h2>Saved notes</h2>
{% if notes %}<ul>{% for note in notes %}<li>{{ note }}</li>{% endfor %}</ul>
{% else %}<p>No notes yet. Add one above.</p>{% endif %}
<p class="small">Storage path: {{ data_file }}</p>
</main></body></html>
'''

def read_notes():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.touch()
    return DATA_FILE.read_text(encoding="utf-8").splitlines()

@app.get("/")
def home():
    return render_template_string(PAGE, notes=read_notes(), data_file=str(DATA_FILE))

@app.post("/add")
def add_note():
    note = request.form.get("note", "").strip()
    if note:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with DATA_FILE.open("a", encoding="utf-8") as f:
            f.write(note.replace("\n", " ") + "\n")
    return redirect("/")

if __name__ == "__main__":
    # Learning demo only; use a production WSGI server and HTTPS for real workloads.
    app.run(host="0.0.0.0", port=5000)
