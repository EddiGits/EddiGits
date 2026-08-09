# Deep Research: Useful Open-Source Android Apps to Modify

**Research date:** 2026-08-09. All licenses, star counts, and last-push dates were verified against the live GitHub API on this date (last push = code activity, not the stars-inflated "updated" field).

**Context:** This research targets our work on the HeliBoard-Voice-Keyboard fork (privacy-focused keyboard + voice input) and the EddiGits Whisper transcription/RAG pipeline. Candidates were scored on four things:

1. **License** — can we legally fork, modify, and redistribute? (Apache/MIT/ISC = anything goes; GPL-3.0 = fork must stay GPL; AGPL = network copyleft; "source-first" = NOT open source)
2. **Activity** — real commits in 2025–2026, not a zombie repo
3. **Stack** — Kotlin/Compose is easiest to modify; Java/Views is fine; C++/NDK and cross-platform stacks (React Native, Flutter, Haskell) raise the bar
4. **Fit** — how naturally our voice/AI/transcription expertise plugs in

---

## TL;DR — Top 10 recommendations

| # | App | License | Why it's the best use of our time |
|---|-----|---------|-----------------------------------|
| 1 | [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) | Apache-2.0 | The fastest-moving on-device speech toolkit (streaming ASR, TTS, VAD, diarization) with ~10 ready Android demo apps. Could replace batch Whisper in our keyboard with true streaming dictation. |
| 2 | [AntennaPod](https://github.com/AntennaPod/AntennaPod) | GPL-3.0 | Podcast manager; per-episode Whisper transcription + tap-to-seek transcripts + cross-show search is the single highest-value mod on this list, and it already supports the Podcasting 2.0 `podcast:transcript` tag. |
| 3 | [RTranslator](https://github.com/niedev/RTranslator) | Apache-2.0 | Production-grade on-device Whisper + NLLB (ONNX) that runs on 2–3 GB RAM phones. Permissive license — we can lift its optimized Whisper pipeline directly. |
| 4 | [Transcribro](https://github.com/soupslurpr/Transcribro) | ISC | The only permissively-licensed modern Compose voice keyboard (whisper.cpp + Silero VAD, works as system `RecognitionService`). Code can be lifted into any project without copyleft friction. Slowing (last push 2025-08) but complete. |
| 5 | [Next Player](https://github.com/anilbeesetti/nextplayer) | GPL-3.0 | Modern Compose/Media3 video player that already builds FFmpeg via JNI — adding a whisper.cpp "Generate subtitles" button is a natural extension. |
| 6 | [whisperIME](https://github.com/woheller69/whisperIME) | MIT | Small, active, readable Whisper IME + transcription app; ideal for benchmarking TFLite vs ONNX vs whisper.cpp backends. |
| 7 | [Dicio](https://github.com/DicioTeam/dicio-android) | GPL-3.0 | Offline voice assistant with a clean STT ↔ skills ↔ TTS abstraction — the plumbing for adding voice *commands* (not just dictation) to a keyboard. |
| 8 | [Fossify Voice Recorder / suite](https://github.com/FossifyOrg) | GPL-3.0 | Small per-app codebases + shared commons lib. Fork Voice Recorder, add on-device Whisper transcription + speaker-labeled export → instant useful product. |
| 9 | [Thunderbird for Android](https://github.com/thunderbird/thunderbird-android) | Apache-2.0 | Mozilla-backed email client; most permissive major app found. Voice-dictated composer + on-device thread summarization is a strong accessibility angle. |
| 10 | [Seal](https://github.com/JunkFood02/Seal) | GPL-3.0 | yt-dlp downloader in clean Compose; a post-download auto-transcribe hook (write `.srt`/`.txt` next to the media) = "download + transcript" in one tap. |

---

## Category 1 — Voice keyboards & speech-to-text (closest to our HeliBoard work)

### FUTO Keyboard & FUTO Voice Input ⚠️ study, don't fork
- https://github.com/futo-org/android-keyboard (~3.0k★, push 2026-08-04) and https://github.com/futo-org/voice-input (~310★, semi-frozen since voice merged into the keyboard)
- **License: FUTO Source First 1.1 — NOT open source.** Personal-use forks OK; redistribution/commercial use restricted.
- Kotlin + Compose + C++/JNI (AOSP LatinIME lineage + whisper.cpp/ggml, on-device transformer autocorrect).
- **Value to us:** the best reference implementation of "Whisper inside an IME" — mic pipeline, VAD, streaming decode into `InputConnection`, model download manager. Since FUTO Keyboard and HeliBoard share AOSP LatinIME ancestry, we can port its voice UX/threading patterns into our fork (clean-room reimplementation, given the license) rather than fork FUTO itself.

### Transcribro — ISC (permissive)
- https://github.com/soupslurpr/Transcribro — ~730★, last push 2025-08-29 (⚠️ slowing, ~1 yr quiet)
- Kotlin, Compose, Material 3; whisper.cpp JNI + Silero VAD. Voice keyboard **and** system-wide `RecognitionService`.
- **Ideas:** use its `RecognitionService` as the backend our HeliBoard mic key calls; swap in our own quantized/fine-tuned Whisper models. ISC means code can be reused anywhere, including in GPL projects.

### whisperIME (+ whisperIMEplus) — MIT, active
- https://github.com/woheller69/whisperIME (~615★, push 2026-08-04) · https://github.com/woheller69/whisperIMEplus (~380★, push 2026-08-09)
- Java; TFLite Whisper (IME) and ONNX Whisper borrowed from RTranslator (plus). Registers as IME and `RecognitionService`; also transcribes files.
- **Ideas:** A/B its TFLite pipeline vs our whisper.cpp pipeline for battery/latency; borrow the translate mode (Whisper task-token switching).

### Sayboard — GPL-3.0
- https://github.com/ElishaAz/Sayboard — ~580★, last push 2025-07-01 (⚠️ ~13 months quiet)
- Kotlin + Vosk. **The best reference for *streaming* STT in a keyboard** — Vosk emits partial results as you speak, a UX batch-Whisper can't do natively.
- **Idea:** hybrid dictation mode for our fork — Vosk/sherpa streaming for live feedback, Whisper re-scoring on utterance end. Its model-manager UI is also reusable.

### Kõnele (K6nele) — Apache-2.0
- https://github.com/Kaljurand/K6nele — ~290★, push 2025-06-15 (mature, slow-moving since 2011)
- The most complete open implementation of Android's `SpeechRecognizer` provider contract, plus a unique **rewrite-rules engine** (regex voice commands → text/actions).
- **Idea:** steal the rewrites system for voice-command/punctuation macros in our keyboard.

### WhisperInput — MIT ⚠️ dormant
- https://github.com/alex-vt/WhisperInput — ~115★, last push 2024-06. Abandoned; use only as an MIT parts bin (auto-punctuation post-processing, panel-overlay UI).

---

## Category 2 — Speech engines, TTS, assistants, on-device AI

### sherpa-onnx (k2-fsa) — Apache-2.0 ⭐ top engine pick
- https://github.com/k2-fsa/sherpa-onnx — ~14.1k★, pushed 2026-08-09, extremely active
- C++ core over ONNX Runtime; first-class Android demos (Kotlin/Java) under `android/`: streaming zipformer/Paraformer/Parakeet/Moonshine/Whisper ASR, VITS/Piper/Kokoro/Matcha TTS, VAD, speaker diarization, keyword spotting. Ships prebuilt AARs.
- **Ideas:** replace our keyboard's batch Whisper with streaming zipformer + endpointing for dictation-grade UX; the `SherpaOnnxTtsEngine` demo is a template for shipping a system TTS engine.

### whisper.cpp Android examples — MIT
- https://github.com/ggml-org/whisper.cpp (`examples/whisper.android`) — ~52.7k★, pushed 2026-08-09
- The upstream we should track anyway. Vulkan/GPU + Q5/Q8 quantization improvements landed through 2025–2026 — worth rebasing our JNI layer. **Idea:** wrap the example in a `RecognitionService` for a minimal MIT-licensed FUTO-Voice-Input replacement.

### Vosk / vosk-android-demo — Apache-2.0
- https://github.com/alphacep/vosk-android-demo — ~1.05k★, push 2025-12-08. Mature/slow vs sherpa-onnx. Lowest-effort streaming multilingual STT with ~50 MB models; good low-end-device fallback engine.

### RTranslator — Apache-2.0, very active
- https://github.com/niedev/RTranslator — ~10.3k★, pushed 2026-08-08
- Real-time offline conversation translator: Whisper + NLLB-200 via ONNX Runtime, aggressive memory optimization (2–3 GB RAM phones), Bluetooth LE conversation mode.
- **Ideas:** benchmark its ONNX Whisper against our whisper.cpp builds; lift the NLLB pipeline for "dictate in language A, type in language B" in the keyboard.

### Dicio — GPL-3.0
- https://github.com/DicioTeam/dicio-android (⚠️ moved from Stypox/dicio-android) — ~1.4k★, push 2026-07-25
- Fully offline voice assistant: Kotlin/Compose, Vosk STT, pluggable TTS, wake word, typed skills API.
- **Ideas:** swap its Vosk input for our Whisper/sherpa engine; embed a Dicio-style command grammar behind long-press-mic in the keyboard.

### Google AI Edge Gallery — Apache-2.0
- https://github.com/google-ai-edge/gallery — ~24.4k★, created 2025-03, pushed 2026-08-07
- The flagship 2025–2026 on-device GenAI reference app (Kotlin, Compose, MediaPipe/LiteRT, Gemma 3n incl. audio input).
- **Idea:** bolt a small on-device LLM onto transcription output for punctuation/formatting/summarization — an offline "AI cleanup" pass. Reuse its model-download + benchmark UI.

### TTS: SherpaTTS / ttsEngine — GPL-3.0
- https://github.com/woheller69/ttsEngine — ~750★, push 2026-07-20. Ready-made scaffold for shipping any ONNX voice (Piper/VITS/Kokoro) as a system Android TTS engine. **Idea:** "read back what I dictated" proofreading paired with the keyboard.
- Also: RHVoice (https://github.com/RHVoice/RHVoice, ~1.8k★, active) — lightweight non-neural TTS, but ⚠️ mixed licensing (LGPL core, GPL when linked with MAGE, some voices non-commercial) and a heavy C++/SCons build. Study/integration target, not a fork base.

### Watching list (small/new, 2025–2026)
- **WonderWhisper** (https://github.com/dkapo88/WonderWhisper) — system-wide dictation + LLM cleanup + command mode; tiny (~9★, created 2026-04) but exactly the 2026 trend; license unverified.
- **moonshine** (https://github.com/moonshine-ai/moonshine) — tiny low-latency STT models with Android support; easiest path is running Moonshine models through sherpa-onnx.

---

## Category 3 — Media & content (natural transcription targets)

### AntennaPod — GPL-3.0 ⭐ highest-value mod target
- https://github.com/AntennaPod/AntennaPod — ~8.1k★, pushed 2026-08-02, healthy org-run project
- Java (gradual Kotlin adoption), Media3/ExoPlayer, well-modularized (`playback`, `model`, `net`) so the audio pipeline is isolated.
- **Mod:** per-episode Whisper transcription with tap-to-seek transcript view, full-text search across all subscribed shows, AI chapter/summary generation. The Podcasting 2.0 `podcast:transcript` support already provides the data model.

### Next Player — GPL-3.0
- https://github.com/anilbeesetti/nextplayer — ~4.2k★, pushed 2026-08-09
- Kotlin + Compose + Media3 with a custom FFmpeg decoder module (NDK/JNI) — arguably the best modern-stack media codebase to learn or fork. Adding whisper.cpp to the existing native build is a natural extension.
- **Mod:** per-video "Generate subtitles" button producing SRT, reusing its subtitle rendering path.

### Seal — GPL-3.0
- https://github.com/JunkFood02/Seal — ~28.1k★, push 2026-07-25 (maintained, slower in 2025–26)
- yt-dlp downloader in clean Compose/M3. **Mod:** post-download hook that auto-transcribes audio and writes `.srt`/`.txt` next to the file.

### NewPipe & LibreTube — GPL-3.0
- https://github.com/TeamNewPipe/NewPipe — ~39.3k★, pushed 2026-08-04. Java-majority; extraction isolated in NewPipeExtractor; enormous fork ecosystem (Tubular, BraveNewPipe) proves forkability.
- https://github.com/libre-tube/LibreTube — ~12.4k★, pushed 2026-08-08. Pure Kotlin, much smaller — easier solo fork. **Mod:** "AI subtitles" toggle running Whisper on streams lacking captions.

### Music/video players
- **Auxio** (https://github.com/OxygenCobalt/Auxio, GPL-3.0, ~4.1k★, push 2026-08-04) — 100% Kotlin, disciplined single-maintainer architecture, fully understandable in days. Mod: voice-controlled playback.
- **Retro Music Player** (https://github.com/RetroMusicPlayer/RetroMusicPlayer, GPL-3.0, ~5.2k★) — feature-maximal; lots of UI surface (lyrics screen, tag editor) to hang AI features on. Mod: Whisper-aligned synced lyrics.
- **mpv-android** (https://github.com/mpv-android/mpv-android, ~3.5k★, push 2026-08-09) — app code MIT, ⚠️ but binaries are GPL once libmpv/FFmpeg are linked. Thin Kotlin UI over an extremely capable engine with raw audio taps. Mod: "transcribe what I'm watching" HUD.
- **VLC for Android** (https://github.com/videolan/vlc-android, GPL-2.0 app / LGPL libVLC, very active) — ⚠️ GitHub is a mirror (canonical: code.videolan.org); heaviest NDK build here. Fork only if codec breadth is essential.

---

## Category 4 — Messaging & email

### Thunderbird for Android (fka K-9 Mail) — Apache-2.0 ⭐ most permissive major app
- https://github.com/thunderbird/thunderbird-android — ~13.8k★, pushed 2026-08-06, Mozilla/MZLA-backed
- Kotlin-majority, multi-module, Compose in newer modules. ⚠️ Rebrand away from Thunderbird/K-9 trademarks when forking.
- **Mod:** voice-dictated composer + on-device thread summarization ("read my inbox aloud / reply by voice" — strong accessibility story).

### Element X Android — AGPL-3.0
- https://github.com/element-hq/element-x-android — ~2.3k★, pushed 2026-08-07
- 100% Compose over the Matrix Rust SDK — probably the best large-scale Compose architecture study on GitHub. Matrix federation is fork-friendly (no server restrictions). ⚠️ AGPL + CLA for upstream contributions.
- **Mod:** voice-message transcription + "meeting notes" summarizer for rooms.

### Signal for Android — AGPL-3.0 ⚠️ heavy restrictions
- https://github.com/signalapp/Signal-Android — ~29.2k★, very active
- Forks may NOT use Signal's production servers or trademark (see LibreSignal shutdown; Molly proves rebranded forks are viable). **Client-side-only mods avoid the server problem** — e.g., on-device Whisper transcription of received voice notes rendered under the audio bubble.

### SimpleX Chat — AGPL-3.0
- https://github.com/simplex-chat/simplex-chat — ~19.2k★, pushed 2026-08-09
- ⚠️ Core is Haskell compiled to a native lib; only the Compose Multiplatform UI (`/apps/multiplatform`) is Kotlin. Fine for client-side additions (e.g., local voice-message transcription), hard if protocol internals need touching.

### Fediverse: Pachli (not Tusky)
- https://github.com/pachli/pachli-android — GPL-3.0, ~245★, pushed 2026-08-07, nonprofit governance
- ⚠️ **Tusky's GitHub repo was archived 2025-05-23** (moved to Codeberg at reduced pace). Pachli is the actively-maintained Tusky lineage on GitHub.
- **Mod:** auto-transcribe audio/video attachments and post transcripts as media descriptions — an accessibility feature the fediverse actively wants.

---

## Category 5 — Productivity, notes, and utilities

### Notes
- **Markor** (https://github.com/gsantner/markor) — **Apache-2.0**, ~6.0k★, push 2026-08-05. Java/Views. File-based Markdown/todo.txt editor; zero backend. Mod: voice capture appending transcribed text to a daily note; LLM "summarize/rewrite selection" toolbar action.
- **Quillpad** (https://github.com/quillpad/quillpad) — GPL-3.0, ~1.4k★, push 2026-06-27. Small clean Kotlin/Room codebase, easiest full comprehension in the category. ⚠️ Repo is itself a GitHub fork (of msoultanidis/quillnote), so `fork:false` searches miss it.
- **Notesnook** (https://github.com/streetwriters/notesnook) — GPL-3.0, ~14.4k★, very active. ⚠️ React Native — best-in-class E2EE architecture to study, poor fit for native Kotlin work.

### Tasks
- **Tasks.org** (https://github.com/tasks/tasks) — GPL-3.0, ~5.5k★, pushed 2026-08-09. The reference for CalDAV task sync in Kotlin, migrating to Compose Multiplatform. Mod: natural-language quick-add parsed by an on-device LLM.
- **Super Productivity** (https://github.com/super-productivity/super-productivity) — MIT, ~21.2k★, very active. ⚠️ TypeScript/Angular via Capacitor; the dedicated Kotlin wrapper repo is archived. Mod: voice time-tracking commands via a Capacitor plugin.

### Fossify suite — GPL-3.0 ⭐ best "replace a system app" base
- https://github.com/FossifyOrg (Gallery ~3.6k★, pushed 2026-08-09; also Messages, Contacts, Phone, Calendar, Voice Recorder, File Manager, Keyboard) — community fork after Simple Mobile Tools was sold to ZipoApps (Dec 2023).
- Kotlin/Views, small per-app codebases sharing one commons library.
- **Mods:** Voice Recorder + on-device Whisper transcription with speaker-labeled Markdown export; Messages + local-ML spam/OTP classification.

### Other utilities
- **Material Files** (https://github.com/zhanghai/MaterialFiles) — GPL-3.0, ~8.7k★, push 2026-04-06 (⚠️ single maintainer, slowing). Very high code quality; the `java.nio.file` provider abstraction makes new storage backends clean. Mod: semantic file-search index.
- **Kvaesitso launcher** (https://github.com/MM2-0/Kvaesitso) — GPL-3.0, ~5.0k★, push 2026-08-05. Pure-Compose search-centric launcher **with an existing plugin SDK**. Mod: on-device LLM answer/intent provider in the search pipeline.
- **Lawnchair** (https://github.com/LawnchairLauncher/lawnchair) — Apache-2.0, ~13.3k★, active. ⚠️ AOSP Launcher3 rebases are painful; heavyweight fork base.
- **Loop Habit Tracker** (https://github.com/iSoron/uhabits) — GPL-3.0, ~10.1k★, push 2026-07-21 (near maintenance-mode). Clean core/UI split; ideal first serious fork. Mod: voice check-ins; Health Connect correlations.
- **Gadgetbridge** — AGPL-3.0, very active. ⚠️ **Develop from https://codeberg.org/Freeyourgadget/Gadgetbridge — the GitHub mirror is archived.** Only realistic OSS base for cloudless wearable data. Mod: on-device AI weekly health summary from its SQLite activity DB.
- **Feeder** (https://github.com/spacecowboy/Feeder) — GPL-3.0, ~3.0k★, pushed 2026-08-09. Offline-first RSS, mature Compose. Mod: on-device article summarization.
- **ReadYou** (https://github.com/ReadYouApp/ReadYou — ⚠️ moved from Ashinch/ReadYou) — GPL-3.0, ~7.4k★, push 2026-07-03. Prettiest MD3/Compose reference. Mod: AI read-aloud "podcast mode" for the article queue.
- **Simple OCR / android-ocr** (https://github.com/SubhamTyagi/android-ocr) — **Apache-2.0**, ~580★, push 2026-08-06. Offline Tesseract, 120+ languages. Fastest path to any "scan → text → do something" product.
- **Ivy Wallet** (https://github.com/Ivy-Apps/ivy-wallet) — GPL-3.0, ⚠️ **archived April 2026**, README explicitly invites forks. A polished, frozen Kotlin/Compose/Hilt/MVI codebase with no upstream conflicts — you own the roadmap. Active alternative: MoneyManagerEx Android (GPL-3.0, Java, alive).
- **GrapheneOS Camera** (https://github.com/GrapheneOS/Camera) — **MIT**, ~1.3k★, push 2026-08-07. Small, clean CameraX codebase — fastest camera base to bend. Mod: voice-command shutter; live-transcribed video captions sidecar.
- **Maps:** prefer **CoMaps** (https://github.com/comaps/comaps, Apache-2.0, community fork, active) over Organic Maps (ownership/governance dispute since late 2024). Heavy C++ core. Mod: fully-offline voice navigation ("navigate to the nearest pharmacy") — zero-network voice-in/voice-out is a real differentiator.

---

## License cheat-sheet

| License | What it means for us | Apps |
|---------|----------------------|------|
| **MIT / ISC / Apache-2.0** (permissive — can go closed-source, mix anywhere) | whisper.cpp, whisperIME, Transcribro, sherpa-onnx, RTranslator, AI Edge Gallery, Vosk, Kõnele, Thunderbird, Markor, Super Productivity, android-ocr, GrapheneOS Camera, Lawnchair, CoMaps, mpv-android (⚠️ app code only) |
| **GPL-3.0** (fork must stay GPL — same as HeliBoard, so fully compatible with our keyboard work) | AntennaPod, Next Player, Seal, NewPipe, LibreTube, Auxio, Dicio, Sayboard, Fossify, Tasks.org, Feeder, ReadYou, Kvaesitso, Material Files, Quillpad, Pachli, uhabits, Ivy Wallet, ttsEngine |
| **AGPL-3.0** (network copyleft) | Signal (+ server/trademark restrictions), Element X (+ CLA), SimpleX, Gadgetbridge |
| **⚠️ NOT open source** (source-first; study only, no redistribution of forks) | FUTO Keyboard, FUTO Voice Input |

## Traps found during verification

- **FUTO Keyboard / Voice Input** — source-available, not OSI open source. Study the architecture; don't redistribute forks.
- **Archived repos:** Tusky on GitHub (2025-05, → Codeberg/Pachli), Ivy Wallet (2026-04), Record You, Gadgetbridge's *GitHub mirror* (real dev on Codeberg), super-productivity-android Kotlin wrapper, WhisperInput (dormant since 2024).
- **Moved repos:** Dicio → DicioTeam org; ReadYou → ReadYouApp org.
- **Mirrors, not canon:** VLC and Briar develop on GitLab/self-hosted; their GitHub repos lag.
- **License subtleties:** mpv-android's MIT app code produces GPL binaries once linked with FFmpeg/libmpv; RHVoice has per-voice non-commercial data packs; Signal forks can't touch Signal's servers or name; Organic Maps has governance problems → use CoMaps.
- **Slowing but usable:** Transcribro, Sayboard, Kõnele, Material Files, Loop Habit Tracker (all 6–14 months quiet; fine as code sources, riskier as upstreams).

## Suggested next steps

1. **Keyboard track:** prototype sherpa-onnx streaming ASR (zipformer + endpointing) as an alternative voice engine in HeliBoard-Voice-Keyboard; keep whisper.cpp for final-pass accuracy. Borrow Transcribro's (ISC) `RecognitionService` pattern and Kõnele's rewrite rules for voice punctuation commands.
2. **Transcription-product track:** fork AntennaPod or Fossify Voice Recorder and wire in the EddiGits Whisper pipeline — both give an immediately useful app with a clear audience.
3. **Quick win:** whisperIME (MIT) and RTranslator (Apache) are the two codebases worth reading end-to-end first; together they cover the TFLite, ONNX, and whisper.cpp backends.
