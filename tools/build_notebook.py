"""Génère le notebook Colab du clipper (jour 1 : téléchargement + transcription)."""
import json, sys

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")}

def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": text.strip("\n")}

cells = [
md("""
# 🎬 Clipper — jour 1 : vidéo → transcription

**Mode d'emploi**
1. Menu **Exécution → Modifier le type d'exécution → GPU T4** → Enregistrer (une seule fois).
2. Colle ton lien YouTube dans la cellule ② (entre les guillemets).
3. Menu **Exécution → Tout exécuter**.
4. À la fin, la transcription s'affiche avec les minutages.

⚠️ Usage personnel uniquement : ne republie pas les extraits d'une vidéo d'un autre créateur sans son accord.
"""),
md("## ① Installation des outils (≈ 1 minute)"),
code("""
# Installe le téléchargeur YouTube et le moteur de transcription (ffmpeg est déjà présent dans Colab)
!pip install -q -U yt-dlp faster-whisper
import shutil
print("✅ Outils installés" if shutil.which("ffmpeg") else "❌ ffmpeg introuvable")
"""),
md("## ② Ton lien YouTube"),
code("""
YOUTUBE_URL = ""  # ← colle ton lien ici, ex. "https://www.youtube.com/watch?v=..."

# Laisse vide le lien ci-dessus pour déposer toi-même un fichier vidéo (solution de secours)
"""),
md("## ③ Téléchargement de la vidéo"),
code("""
import glob, os, subprocess

WORK_DIR = "/content/clipper"
os.makedirs(WORK_DIR, exist_ok=True)
VIDEO_PATH = f"{WORK_DIR}/video.mp4"
if os.path.exists(VIDEO_PATH):
    os.remove(VIDEO_PATH)

def download_youtube(url: str) -> bool:
    # Meilleure qualité jusqu'à 1080p, en MP4
    result = subprocess.run([
        "yt-dlp", "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b",
        "--merge-output-format", "mp4", "-o", VIDEO_PATH, url,
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-1500:])
    return os.path.exists(VIDEO_PATH)

def upload_manually() -> bool:
    from google.colab import files
    print("📂 Choisis ton fichier vidéo (MP4, MOV…)")
    uploaded = files.upload()
    if not uploaded:
        return False
    name = next(iter(uploaded))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", name, "-c", "copy", VIDEO_PATH])
    os.remove(name)
    return os.path.exists(VIDEO_PATH)

ok = download_youtube(YOUTUBE_URL.strip()) if YOUTUBE_URL.strip() else False
if not ok:
    if YOUTUBE_URL.strip():
        print("⚠️ YouTube a bloqué le téléchargement. Solution : télécharge la vidéo toi-même, puis dépose-la ci-dessous.")
    ok = upload_manually()

if ok:
    duration = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", VIDEO_PATH],
        capture_output=True, text=True).stdout.strip() or 0)
    print(f"✅ Vidéo prête : {duration/60:.1f} minutes")
else:
    raise SystemExit("❌ Aucune vidéo récupérée.")
"""),
md("## ④ Transcription (≈ 1 à 3 minutes pour 10 minutes de vidéo avec le GPU)"),
code("""
import json, torch
from faster_whisper import WhisperModel

# Avec le GPU : modèle le plus précis. Sans GPU : modèle plus léger (plus lent et moins précis).
if torch.cuda.is_available():
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
else:
    print("⚠️ Pas de GPU : active-le (Exécution → Modifier le type d'exécution → GPU T4) pour aller beaucoup plus vite.")
    model = WhisperModel("small", device="cpu", compute_type="int8")

segments_iter, info = model.transcribe(VIDEO_PATH, word_timestamps=True, vad_filter=True)
print(f"Langue détectée : {info.language}")

segments = []
for seg in segments_iter:
    segments.append({
        "start": round(seg.start, 2),
        "end": round(seg.end, 2),
        "text": seg.text.strip(),
        "words": [{"start": round(w.start, 2), "end": round(w.end, 2), "word": w.word} for w in (seg.words or [])],
    })

with open(f"{WORK_DIR}/transcript.json", "w", encoding="utf-8") as f:
    json.dump({"language": info.language, "segments": segments}, f, ensure_ascii=False)
print(f"✅ Transcription terminée : {len(segments)} phrases")
"""),
md("## ⑤ Transcription avec minutages"),
code("""
def fmt(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"

lines = [f"[{fmt(s['start'])}-{fmt(s['end'])}] {s['text']}" for s in segments]
transcript_text = "\\n".join(lines)
with open(f"{WORK_DIR}/transcript.txt", "w", encoding="utf-8") as f:
    f.write(transcript_text)
print(transcript_text)
"""),
]

notebook = {"cells": cells, "metadata": {
    "accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}

with open(sys.argv[1], "w", encoding="utf-8") as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
