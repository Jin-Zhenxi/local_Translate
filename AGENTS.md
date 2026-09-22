# Codex repository instructions

This repository is a local, offline English-speech-to-Simplified-Chinese subtitle application. The validated Windows path uses `faster-whisper base.en` and a local OPUS-MT CTranslate2 INT8 model.

## First actions after clone

1. Read `README.md` before changing code.
2. Run `git lfs install` and `git lfs pull` from the repository root.
3. Confirm these files are real model binaries, not small Git LFS pointer files:
   - `models/faster-whisper-base.en/model.bin`
   - `models/opus-mt-en-zh-int8/model.bin`
4. If `config.ini` is missing, copy `config.ini.example` to `config.ini`. Do not commit `config.ini` because audio-device selection is machine-specific.
5. On Windows, run `install_windows.bat`, then `start_windows.bat`.

## Required runtime configuration

- ASR backend: `whisper`
- Whisper model: `base.en`
- ASR device: `cpu`
- ASR compute type: `int8`
- Source language: `en`
- Translation model: `models/opus-mt-en-zh-int8`
- Translation device: `cpu`
- Translation compute type: `int8`

Do not download or switch to `small.en`. Do not run the model-preparation scripts when both tracked runtime model directories are complete.

## Files that intentionally stay local

- `.venv/`: platform- and Python-version-specific environment
- `config.ini`: machine-specific settings such as the selected microphone
- `models/.downloads/`: temporary model conversion/download cache
- `__pycache__/`: generated Python bytecode

Do not add these paths to Git. The two runtime model directories are already tracked through Git LFS.

## Platform scope

The Windows CPU/INT8 path is the current validated checkpoint. Apple Silicon support is a separate verification phase described in `README.md`; preserve the Windows path while making any Mac-specific compatibility changes.
