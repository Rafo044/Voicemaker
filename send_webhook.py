import os
import sys
import json
import requests
from pathlib import Path

def send_to_n8n(project_name, file_links):
    webhook_url = "https://n8n.alikhanli.site/webhook-test/cognitcentric/audio"
    payload = {
        "project_name": project_name,
        "links": file_links
    }
    try:
        response = requests.post(webhook_url, json=payload)
        print(f"📡 Webhook sent! Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Webhook error: {e}")

def run_webhook(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    project_name = data.get("project_name", Path(json_path).stem)
    scenes = data.get("scenes", [])
    
    repo = os.environ.get("GITHUB_REPOSITORY", "Rafo044/Voicemaker")
    branch = "main"
    base_url = f"https://raw.githubusercontent.com/{repo}/{branch}/batch_output/{project_name}/"
    
    file_links = []
    for scene in scenes:
        scene_id = scene.get("id", "unknown")
        file_links.append(f"{base_url}{scene_id}.wav")

    send_to_n8n(project_name, file_links)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_webhook.py <json_file>")
        sys.exit(1)
    run_webhook(sys.argv[1])
