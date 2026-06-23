# Voicemaker

Avtomatlaşdırılmış mətn-səs (Text-to-Speech) sintezatoru və klonlama layihəsi. Bu layihə **F5-TTS** modelindən istifadə edərək səs klonlama və böyük həcmli səs generasiyasını həm lokal, həm də **Modal** (serverless GPU) üzərindən yerinə yetirir. Eyni zamanda nəticələri avtomatik olaraq **n8n** webhook-una göndərməyi dəstəkləyir.

## Layihənin Əsas Xüsusiyyətləri

- **F5-TTS İnteqrasiyası:** Yüksək keyfiyyətli, emosional və təbii səs klonlama.
- **Bulud & Lokal Dəstək:** Tək və ya çoxlu səhnələri Modal platforması vasitəsilə buludda emal etmək mümkündür. 
- **Batch Processing (Kütləvi Emal):** `.json` faylları vasitəsilə birdən çox səhnəni eyni anda generasiya edə bilərsiniz.
- **Avtomatlaşdırma:** `n8n` kimi alətlərə asan inteqrasiya üçün xüsusi webhook skripti daxildir.

## Qovluq Strukturu

- `clone_source/`: Klonlama üçün əsas səs faylını (`universal_clon.mp3`) burada saxlayın.
- `input_scripts/`: Lokal skriptlər vasitəsilə səs generasiya etmək üçün mətn fayllarını bura əlavə edin.
- `output_voiceovers/`: Hazır səs faylları burada saxlanılır.
- `processed_scripts/`: Emal edilmiş mətn faylları bura arxivlənir.
- `batch_inputs/` & `batch_output/`: Kütləvi emal (JSON faylları) üçün giriş və çıxış qovluqları.

## Əsas Skriptlər

- `modal_audio_app.py`: Modal tətbiqinin konfiqurasiyası və F5-TTS inference məntiqi.
- `automate_audio.py`: Lokal mühitdə mətnləri avtomatik səsə çevirən skript.
- `trigger_modal.py`: Tək mətn skriptini Modal-a göndərib səsi generasiya edir.
- `trigger_batch.py`: Birdən çox mətn səhnəsini Modal-da paralel generasiya edir.
- `send_webhook.py`: Nəticələri webhook (n8n) vasitəsilə göndərir.

## İstifadə (Kütləvi Emal Nümunəsi)

1. `batch_inputs` qovluğunda `template.json.example` formatına uyğun json hazırlayın.
2. `python trigger_batch.py batch_inputs/your_file.json` əmrini işlədin.
3. Tamamlandıqdan sonra `python send_webhook.py batch_inputs/your_file.json` əmri ilə nəticələri göndərin.

---
*Qeyd: Bu layihədə emosional səsləndirmə üçün ElevenLabs V3 kalibrasiya faylı (`PERFECT_CLONE_SCRIPT.md`) istinad kimi saxlanılmışdır.*
