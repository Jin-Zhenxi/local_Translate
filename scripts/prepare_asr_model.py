"""Download a faster-whisper model into the project for offline use."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_REPOSITORIES = {
    "base.en": "Systran/faster-whisper-base.en",
    "small.en": "Systran/faster-whisper-small.en",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a local faster-whisper model.")
    parser.add_argument("model", choices=MODEL_REPOSITORIES, nargs="?", default="base.en")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / "models" / f"faster-whisper-{args.model}"
    print(f"[ASR Model] Downloading {MODEL_REPOSITORIES[args.model]}...")
    snapshot_download(
        repo_id=MODEL_REPOSITORIES[args.model],
        local_dir=str(output_dir),
    )

    required_files = ("config.json", "model.bin", "tokenizer.json")
    missing = [name for name in required_files if not (output_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"Downloaded ASR model is incomplete; missing: {missing}")

    print(f"[ASR Model] Ready: {output_dir}")


if __name__ == "__main__":
    main()
