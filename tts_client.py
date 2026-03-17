#!/usr/bin/env python3
"""
IndicF5 Local TTS (No API)

- Loads model directly
- Uses reference voice wav
- Generates speech
- Measures timing

Usage:
python indicf5_local.py \
  --text "Hello world" \
  --voice reference.wav
"""

import torch
import torchaudio
import time
import argparse
import os


# ==============================
# CONFIG
# ==============================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUTPUT_FILE = "output.wav"


# ==============================
# MODEL LOADING
# ==============================

def load_model():
    """
    Load IndicF5 model.

    Replace this with actual model loading code depending on your repo.
    """

    start = time.time()

    print("📦 Loading IndicF5 model...")

    # 🔥 IMPORTANT: Replace below with actual loading
    # Example placeholder (you must adapt):
    model = torch.hub.load(
        'snakers4/silero-models',
        'silero_tts',
        language='en',
        speaker='v3_en'
    )

    model.to(DEVICE)

    end = time.time()
    print(f"✅ Model loaded in {end - start:.2f}s")

    return model


# ==============================
# AUDIO HELPERS
# ==============================

def load_reference_audio(path):
    """
    Load reference voice file.

    Args:
        path (str): Path to wav file

    Returns:
        waveform, sample_rate
    """
    waveform, sr = torchaudio.load(path)
    return waveform.to(DEVICE), sr


def save_audio(waveform, sample_rate, path=OUTPUT_FILE):
    """
    Save generated waveform.

    Args:
        waveform: Tensor
        sample_rate: int
    """
    torchaudio.save(path, waveform.cpu(), sample_rate)
    print(f"💾 Saved to {path}")


# ==============================
# TTS GENERATION
# ==============================

def generate_speech(model, text, reference_audio):
    """
    Generate speech from text + reference.

    NOTE: Replace with IndicF5 inference logic.

    Args:
        model: loaded model
        text (str)
        reference_audio (Tensor)

    Returns:
        waveform
    """

    start = time.time()

    print("🚀 Generating speech...")

    # 🔥 PLACEHOLDER — replace with IndicF5 forward pass
    audio = model.apply_tts(
        text=text,
        speaker='random',
        sample_rate=24000
    )

    end = time.time()
    print(f"⏱ Inference time: {end - start:.2f}s")

    return audio.unsqueeze(0), 24000


# ==============================
# MAIN
# ==============================

def main():
    parser = argparse.ArgumentParser(description="IndicF5 Local TTS")

    parser.add_argument("--text", required=True, help="Input text")
    parser.add_argument("--voice", required=True, help="Reference wav file")

    args = parser.parse_args()

    # ------------------------------
    # Load model
    # ------------------------------
    model = load_model()

    # ------------------------------
    # Load reference audio
    # ------------------------------
    ref_audio, sr = load_reference_audio(args.voice)

    # ------------------------------
    # Generate speech
    # ------------------------------
    audio, out_sr = generate_speech(model, args.text, ref_audio)

    # ------------------------------
    # Save output
    # ------------------------------
    save_audio(audio, out_sr)


# ==============================
# ENTRY
# ==============================

if __name__ == "__main__":
    main()