"""Download and convert OPUS-MT English-to-Chinese for offline inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MODEL_ID = "Helsinki-NLP/opus-mt-en-zh"
LANGUAGE_TOKEN = ">>cmn_Hans<<"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOWNLOAD_DIR = PROJECT_ROOT / "models" / ".downloads" / "opus-mt-en-zh"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "models" / "opus-mt-en-zh-int8"


def find_sentencepiece_file(model_dir: Path, role: str) -> Path:
    """Find a source or target SentencePiece model without guessing its role."""
    preferred_names = {
        "source": ("source.spm", "src.spm", "source.model", "src.model"),
        "target": ("target.spm", "tgt.spm", "target.model", "tgt.model"),
    }
    for name in preferred_names[role]:
        path = model_dir / name
        if path.is_file():
            return path

    markers = ("source", "src") if role == "source" else ("target", "tgt")
    candidates = [
        path
        for path in model_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".spm", ".model"}
        and any(marker in path.stem.lower() for marker in markers)
    ]
    if len(candidates) == 1:
        return candidates[0]

    discovered = sorted(
        path.name
        for path in model_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".spm", ".model"}
    )
    raise FileNotFoundError(
        f"Could not identify the {role} SentencePiece model in {model_dir}. "
        f"Discovered: {discovered or 'none'}"
    )


def prepare_model(download_dir: Path, output_dir: Path, force: bool) -> None:
    try:
        import ctranslate2
        import sentencepiece as spm
        import torch  # noqa: F401 - required by the Transformers converter
        from ctranslate2.converters import TransformersConverter
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "Missing model-preparation dependencies. Run:\n"
            "  python -m pip install -r scripts/requirements-model.txt"
        ) from exc

    if ctranslate2.contains_model(str(output_dir)) and not force:
        print(f"[Model] Ready: {output_dir}")
        return

    download_dir.mkdir(parents=True, exist_ok=True)
    output_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"[Model] Downloading {MODEL_ID}...")
    snapshot_path = Path(
        snapshot_download(
            repo_id=MODEL_ID,
            local_dir=str(download_dir),
            allow_patterns=[
                "config.json",
                "generation_config.json",
                "pytorch_model.bin",
                "model.safetensors",
                "source.spm",
                "target.spm",
                "tokenizer_config.json",
                "vocab.json",
            ],
        )
    )

    source_spm = find_sentencepiece_file(snapshot_path, "source")
    target_spm = find_sentencepiece_file(snapshot_path, "target")
    print(f"[Model] Source tokenizer: {source_spm.name}")
    print(f"[Model] Target tokenizer: {target_spm.name}")

    copy_files = [source_spm.name, target_spm.name]
    for optional_name in ("tokenizer_config.json", "generation_config.json"):
        if (snapshot_path / optional_name).is_file():
            copy_files.append(optional_name)

    print(f"[Model] Converting to CTranslate2 INT8: {output_dir}")
    converter = TransformersConverter(str(snapshot_path), copy_files=copy_files)
    converter.convert(str(output_dir), quantization="int8", force=force)

    metadata = {
        "model_id": MODEL_ID,
        "quantization": "int8",
        "source_sentencepiece": source_spm.name,
        "target_sentencepiece": target_spm.name,
        "target_language": "Simplified Chinese",
        "target_language_token": LANGUAGE_TOKEN,
    }
    (output_dir / "translation_model.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not ctranslate2.contains_model(str(output_dir)):
        raise RuntimeError(f"Conversion did not produce a valid CTranslate2 model: {output_dir}")

    vocabulary_path = output_dir / "source_vocabulary.json"
    if not vocabulary_path.is_file():
        vocabulary_path = output_dir / "shared_vocabulary.json"
    vocabulary = json.loads(vocabulary_path.read_text(encoding="utf-8"))
    vocabulary_tokens = vocabulary.keys() if isinstance(vocabulary, dict) else vocabulary
    if LANGUAGE_TOKEN not in vocabulary_tokens:
        raise RuntimeError(
            f"Required Simplified Chinese token {LANGUAGE_TOKEN!r} is not in {vocabulary_path}"
        )

    print(f"[Model] Conversion complete: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare the local OPUS-MT English-to-Simplified-Chinese model."
    )
    parser.add_argument("--download-dir", type=Path, default=DEFAULT_DOWNLOAD_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    prepare_model(
        args.download_dir.expanduser().resolve(),
        args.output_dir.expanduser().resolve(),
        args.force,
    )


if __name__ == "__main__":
    main()
