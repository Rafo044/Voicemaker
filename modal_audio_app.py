import modal
import os
from pathlib import Path

# Modal Image tərifi (Gərəkli kitabxanalarla)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg")
    .pip_install(
        "f5-tts",
        "torchaudio",
        "pydub",
        "numpy",
        "torch"
    )
)

app = modal.App("cognicentric-audio", image=image)

# GPU seçimi (T4 kifayət edər, lakin sürət üçün A100 də olar)
@app.function(gpu="T4", timeout=600, secrets=[modal.Secret.from_name("github-secret")])
def generate_f5_audio(text: str, ref_audio_bytes: bytes, ref_text: str = "Experience is the mother of all knowledge."):
    import torch
    import torchaudio
    import numpy as np
    import re
    from f5_tts.api import F5TTS
    import io

    # Model yüklənir
    model = F5TTS()
    
    # Referans audio faylını müvəqqəti saxlayaq
    ref_path = "temp_ref.wav"
    with open(ref_path, "wb") as f:
        f.write(ref_audio_bytes)

    # Mətni hissələrə bölmək (generate_f5 məntiqi)
    def clean_and_split(txt):
        txt = re.sub(r'\[.*?\]', '', txt).strip()
        sentences = re.split(r'(?<=[.!?])\s+', txt)
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) < 200:
                current += (" " if current else "") + s
            else:
                if current: chunks.append(current.strip())
                current = s
        if current: chunks.append(current.strip())
        return chunks

    chunks = clean_and_split(text)
    all_wavs = []
    sr = 24000

    for chunk in chunks:
        wav, sample_rate, _ = model.infer(
            ref_file=ref_path,
            ref_text=ref_text,
            gen_text=chunk
        )
        
        wav_tensor = torch.from_numpy(wav) if isinstance(wav, np.ndarray) else wav.cpu()
        if wav_tensor.ndim == 1:
            wav_tensor = wav_tensor.unsqueeze(0)
        
        all_wavs.append(wav_tensor)
        sr = sample_rate

    final_audio = torch.cat(all_wavs, dim=-1)
    
    # Nəticəni bayt olaraq qaytaraq
    buffer = io.BytesIO()
    torchaudio.save(buffer, final_audio, sr, format="wav")
    return buffer.getvalue()

@app.local_entrypoint()
def main():
    """Lokal terminaldan işlətmək üçün: modal run modal_audio_app.py"""
    # Bu hissə test üçündür
    input_text = "The quick brown fox jumps over the lazy dog."
    ref_path = "clone_source/universal_clon.mp3" # Lokal yol
    
    if os.path.exists(ref_path):
        with open(ref_path, "rb") as f:
            ref_bytes = f.read()
            
        print("🚀 Modal-da səs yaradılır...")
        result_bytes = generate_f5_audio.remote(input_text, ref_bytes)
        
        with open("modal_test_output.wav", "wb") as f:
            f.write(result_bytes)
        print("✅ Modal testi tamamlandı: modal_test_output.wav")
