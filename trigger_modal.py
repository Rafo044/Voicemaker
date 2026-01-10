import modal
import os
import sys
from pathlib import Path

# GitHub Secret-lərdən gələn təsadüfi yeni sətirləri (\n) təmizləyirik (strip)
if "MODAL_TOKEN_ID" in os.environ:
    os.environ["MODAL_TOKEN_ID"] = os.environ["MODAL_TOKEN_ID"].strip()
if "MODAL_TOKEN_SECRET" in os.environ:
    os.environ["MODAL_TOKEN_SECRET"] = os.environ["MODAL_TOKEN_SECRET"].strip()

def run_modal_task(file_path):
    print(f"🚀 Processing {file_path} on Modal...")
    
    # Modal-da yerləşən funksiyanı tapırıq
    try:
        f = modal.Function.from_name("cognicentric-audio", "generate_f5_audio")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

    script_file = Path(file_path)
    ref_audio = Path("clone_source/universal_clon.mp3")

    if not ref_audio.exists():
        print(f"❌ Ref audio not found at {ref_audio}")
        sys.exit(1)

    text = script_file.read_text(encoding='utf-8')
    with open(ref_audio, 'rb') as audio_f:
        audio_bytes = audio_f.read()

    # Modal-a göndər
    result_bytes = f.remote(text, audio_bytes)

    # Nəticəni yadda saxla
    output_path = Path("output_voiceovers") / (script_file.stem + ".wav")
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "wb") as out_f:
        out_f.write(result_bytes)

    print(f"✅ Saved to {output_path}")

    # Faylı arxivlə (Processed scripts qovluğuna köçür)
    proc_dir = Path("processed_scripts")
    proc_dir.mkdir(exist_ok=True)
    import shutil
    shutil.move(str(script_file), str(proc_dir / script_file.name))
    print(f"📦 Archived {script_file.name} to processed_scripts/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_modal.py <script_file>")
        sys.exit(1)
    run_modal_task(sys.argv[1])
