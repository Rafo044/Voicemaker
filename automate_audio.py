import os
import torch
import torchaudio
import re
import numpy as np
import shutil
from pathlib import Path
from f5_tts.api import F5TTS

# Qovluq yolları (Colab və Lokal uyğunluğu üçün nisbi yollar)
BASE_DIR = Path(__file__).parent
CLONE_SOURCE_DIR = BASE_DIR / "clone_source"
INPUT_SCRIPTS_DIR = BASE_DIR / "input_scripts"
OUTPUT_DIR = BASE_DIR / "output_voiceovers"
PROCESSED_DIR = BASE_DIR / "processed_scripts"

# Qovluqların mövcudluğunu təmin et
for d in [INPUT_SCRIPTS_DIR, OUTPUT_DIR, PROCESSED_DIR, CLONE_SOURCE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

class AudioAutomator:
    def __init__(self):
        print("🚀 F5-TTS Modeli yüklənir...")
        self.model = F5TTS()
    
    def get_reference_audio(self):
        """Klon qovluğundakı səs faylını tapır."""
        valid_extensions = ('.wav', '.mp3', '.flac')
        for f in CLONE_SOURCE_DIR.iterdir():
            if f.suffix.lower() in valid_extensions:
                return f
        return None

    def clean_text(self, text):
        """[serious] kimi teqləri təmizləyir."""
        return re.sub(r'\[.*?\]', '', text).strip()

    def split_script(self, text, limit=200):
        """Mətni keyfiyyət və sabitlik üçün hissələrə bölür (generate_f5 məntiqi)."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) < limit:
                current += (" " if current else "") + s
            else:
                if current: chunks.append(current.strip())
                current = s
        if current: chunks.append(current.strip())
        return chunks

    def process_scripts(self):
        ref_file = self.get_reference_audio()
        if not ref_file:
            print(f"❌ XƏTA: '{CLONE_SOURCE_DIR}' qovluğunda heç bir audio fayl tapılmadı!")
            return

        # Referans mətni (əgər yoxdursa generic mətn istifadə olunur)
        ref_text_file = CLONE_SOURCE_DIR / "ref_text.txt"
        ref_text = ref_text_file.read_text().strip() if ref_text_file.exists() else "Experience is the mother of all knowledge."

        scripts = list(INPUT_SCRIPTS_DIR.glob("*.txt"))
        if not scripts:
            print("📭 'input_scripts' qovluğu boşdur. Yeni skript gözlənilir...")
            return

        for script_path in scripts:
            # Çıxış faylının adını giriş faylının adından alırıq
            output_filename = f"{script_path.stem}.wav"
            output_path = OUTPUT_DIR / output_filename
            
            print(f"📄 Emal edilir: {script_path.name} -> {output_filename}")
            
            try:
                full_text = script_path.read_text(encoding='utf-8')
                text_to_process = self.clean_text(full_text)
                chunks = self.split_script(text_to_process)
                
                print(f"📦 Mətn {len(chunks)} hissəyə bölündü.")
                
                all_wavs = []
                sr = 24000
                
                for i, chunk in enumerate(chunks):
                    print(f"  🎙️ ({i+1}/{len(chunks)}) Emal edilir: {chunk[:40]}...")
                    wav, sample_rate, _ = self.model.infer(
                        ref_file=str(ref_file),
                        ref_text=ref_text,
                        gen_text=chunk
                    )
                    
                    # NumPy-dan Torch-a çevrilmə (generate_f5 düsturu)
                    if isinstance(wav, np.ndarray):
                        wav_tensor = torch.from_numpy(wav)
                    else:
                        wav_tensor = wav.cpu()
                    
                    if wav_tensor.ndim == 1:
                        wav_tensor = wav_tensor.unsqueeze(0)
                    
                    all_wavs.append(wav_tensor)
                    sr = sample_rate
                
                if all_wavs:
                    final_audio = torch.cat(all_wavs, dim=-1)
                    torchaudio.save(str(output_path), final_audio, sr)
                    print(f"✅ Hazırdır: {output_path}")
                    
                    # Skripti 'processed' qovluğuna köçür
                    shutil.move(str(script_path), str(PROCESSED_DIR / script_path.name))
                else:
                    print(f"❌ Xəta: {script_path.name} üçün səs yaradıla bilmədi.")
            
            except Exception as e:
                print(f"⚠️ Kritik xəta baş verdi ({script_path.name}): {e}")

if __name__ == "__main__":
    automator = AudioAutomator()
    automator.process_scripts()
