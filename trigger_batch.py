import modal
import os
import sys
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Modal konfiqurasiyası
if "MODAL_TOKEN_ID" in os.environ:
    os.environ["MODAL_TOKEN_ID"] = os.environ["MODAL_TOKEN_ID"].strip()
if "MODAL_TOKEN_SECRET" in os.environ:
    os.environ["MODAL_TOKEN_SECRET"] = os.environ["MODAL_TOKEN_SECRET"].strip()

def send_to_n8n(project_name, file_links):
    # Authentication silindi (USER tələbi ilə)
    webhook_url = "https://n8n.alikhanli.site/webhook-test/cognitcentric/audio"
    payload = {
        "project_name": project_name,
        "links": file_links
    }
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 404:
            # Əgər test URL tapılmazsa, production URL-i yoxlayaq
            prod_url = "https://n8n.alikhanli.site/webhook/cognitcentric/audio"
            response = requests.post(prod_url, json=payload)
        
        print(f"📡 Webhook sent! Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Webhook error: {e}")

def process_batch(json_path):
    print(f"🚀 Processing batch: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    project_name = data.get("project_name", Path(json_path).stem)
    scenes = data.get("scenes", [])

    if len(scenes) > 40:
        print(f"❌ Error: Too many scenes ({len(scenes)}). Maximum allowed is 40.")
        return

    # Modal funksiyasını tapırıq
    try:
        f_modal = modal.Function.from_name("cognicentric-audio", "generate_f5_audio")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)

    ref_audio_path = Path("clone_source/universal_clon.mp3")
    if not ref_audio_path.exists():
        print(f"❌ Ref audio not found at {ref_audio_path}")
        sys.exit(1)

    with open(ref_audio_path, 'rb') as audio_f:
        audio_bytes = audio_f.read()

    output_dir = Path("batch_output") / project_name
    output_dir.mkdir(parents=True, exist_ok=True)

    def process_single_scene(scene):
        scene_id = scene.get("id", "unknown")
        text = scene.get("text", "")
        print(f"🎙️ Generating scene {scene_id}...")
        
        # Modal-a göndər
        result_bytes = f_modal.remote(text, audio_bytes)
        
        file_name = f"{scene_id}.wav"
        save_path = output_dir / file_name
        with open(save_path, "wb") as out_f:
            out_f.write(result_bytes)
        
        return file_name

    # Paralel emal (ThreadPoolExecutor modal .remote-ları eyni anda çağırır)
    print(f"⚡ Starting parallel processing for {len(scenes)} scenes...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_scene, scenes))

    # Linkləri hazırla (GitHub Raw linklərini təxmin edirik)
    repo = os.environ.get("GITHUB_REPOSITORY", "Rafo044/Voicemaker")
    branch = "main" # və ya master
    base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/batch_output/{project_name}/"
    
    file_links = [f"{base_url}{name}" for name in results]

    # n8n-ə göndər
    send_to_n8n(project_name, file_links)

    # Arxivlə
    proc_dir = Path("batch_processed")
    proc_dir.mkdir(exist_ok=True)
    import shutil
    shutil.move(json_path, str(proc_dir / Path(json_path).name))
    print(f"✅ Batch completed and archived.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python trigger_batch.py <json_file>")
        sys.exit(1)
    process_batch(sys.argv[1])
