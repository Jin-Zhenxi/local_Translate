"""Offline English-to-Simplified-Chinese translation with CTranslate2."""

from __future__ import annotations

import json
import re
import threading
from pathlib import Path

import ctranslate2
import sentencepiece as spm


DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "opus-mt-en-zh-int8"
SUPPORTED_TARGETS = {"chinese", "simplified chinese", "zh", "zh-cn", "zh-hans"}


class Translator:
    def __init__(
        self,
        api_key=None,
        base_url=None,
        model=None,
        target_lang="Chinese",
        model_path=None,
        device="cpu",
        compute_type="int8",
        inter_threads=1,
    ):
        """Load the local OPUS-MT model while preserving the original API shape."""
        del api_key, base_url, model  # Legacy API arguments are intentionally unused.

        if target_lang.strip().lower() not in SUPPORTED_TARGETS:
            raise ValueError(
                f"Only English to Simplified Chinese is supported, got: {target_lang!r}"
            )

        self.target_lang = "Simplified Chinese"
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH).expanduser().resolve()
        if not ctranslate2.contains_model(str(self.model_path)):
            raise FileNotFoundError(
                f"Local translation model not found at {self.model_path}. "
                "Run: python scripts/prepare_translation_model.py"
            )

        metadata_path = self.model_path / "translation_model.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Translation model metadata not found: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        source_spm = self.model_path / metadata["source_sentencepiece"]
        target_spm = self.model_path / metadata["target_sentencepiece"]
        if not source_spm.is_file() or not target_spm.is_file():
            raise FileNotFoundError(
                f"SentencePiece files are missing from {self.model_path}"
            )

        self.source_tokenizer = spm.SentencePieceProcessor(model_file=str(source_spm))
        self.target_tokenizer = spm.SentencePieceProcessor(model_file=str(target_spm))
        self.target_language_token = metadata["target_language_token"]
        self._lock = threading.Lock()

        self.translator = ctranslate2.Translator(
            str(self.model_path),
            device=device,
            compute_type=compute_type,
            inter_threads=max(1, int(inter_threads)),
        )

        # Kept for compatibility with code that inspects the old context fields.
        self.previous_text = ""
        self.previous_translation = ""

        print("[Translator] Initialized local OPUS-MT:")
        print(f"  - Model path: {self.model_path}")
        print(f"  - Device: {device}")
        print(f"  - Compute type: {compute_type}")
        print(f"  - Target language: {self.target_lang}")

    def translate(self, text, use_context=True):
        """Translate one English utterance; ``use_context`` is API-compatible."""
        del use_context
        text = text.strip() if text else ""
        if not text:
            return ""

        source_tokens = [self.target_language_token]
        source_tokens.extend(self.source_tokenizer.encode(text, out_type=str))

        with self._lock:
            results = self.translator.translate_batch(
                [source_tokens],
                beam_size=4,
                max_decoding_length=256,
            )

        target_tokens = results[0].hypotheses[0]
        translated = self.target_tokenizer.decode(target_tokens).strip()
        translated = self._normalize_chinese_punctuation(translated)
        self.previous_text = text
        self.previous_translation = translated
        return translated

    @staticmethod
    def _normalize_chinese_punctuation(text):
        text = text.translate(str.maketrans({",": "，", "?": "？", "!": "！"}))
        text = re.sub(r"\.{2,}\s*$", "。", text)
        text = re.sub(r"\.\s*$", "。", text)
        return text


if __name__ == "__main__":
    translator = Translator()
    for sample in (
        "Hello, how are you?",
        "Today we're going to talk about artificial intelligence.",
    ):
        print(sample)
        print(translator.translate(sample))
