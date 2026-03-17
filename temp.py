#!/usr/bin/env python3

import time
import argparse
import torch

# Import from your repo
from f5_tts.infer.utils_infer import load_model, load_vocoder, convert_char_to_pinyin
from f5_tts.model import DiT
from omegaconf import OmegaConf
from importlib.resources import files


def load_everything(model_name="F5TTS_v1_Base", device="cuda"):
    print("🔄 Loading model...")

    # Load config
    model_cfg = OmegaConf.load(
        str(files("f5_tts").joinpath(f"configs/{model_name}.yaml"))
    )

    model_cls = DiT
    model_arc = model_cfg.model.arch
    mel_spec_type = model_cfg.model.mel_spec.mel_spec_type
    vocab_file = "emilia_zh_en"   # or whatever dataset name in config

    # Load checkpoint (auto from HF)
    from huggingface_hub import hf_hub_download
    repo = "SWivid/F5-TTS"
    ckpt_file = hf_hub_download(
        repo_id=repo,
        filename=f"{model_name}/model_1250000.safetensors"
    )

    # Load model
    model = load_model(
        model_cls,
        model_arc,
        ckpt_file,
        mel_spec_type=mel_spec_type,
        vocab_file=vocab_file,
        device=device,
    )

    # Load vocoder
    vocoder = load_vocoder(device=device)

    print("✅ Model loaded\n")

    return model, vocoder, model_cfg


def prepare_inputs(text, ref_text):
    # Combine reference + generation text
    text_list = [ref_text + text]

    # Convert to phoneme/pinyin
    final_text = convert_char_to_pinyin(text_list)

    return final_text


def run_inference(model, vocoder, text, ref_audio, ref_text, steps=32):
    # Load reference audio
    import torchaudio

    audio, sr = torchaudio.load(ref_audio)
    audio = audio.to(model.device)

    hop_length = 256  # typical (can be read from config if needed)
    ref_audio_len = audio.shape[-1] // hop_length

    # Prepare text
    final_text = prepare_inputs(text, ref_text)

    # Estimate duration
    ref_text_len = len(ref_text.encode("utf-8"))
    gen_text_len = len(text.encode("utf-8"))

    duration = ref_audio_len + int(ref_audio_len / ref_text_len * gen_text_len)

    # 🚀 START TIMER
    start = time.time()

    with torch.inference_mode():
        generated, _ = model.sample(
            cond=audio,
            text=final_text,
            duration=duration,
            steps=steps,
        )

        # Remove reference portion
        generated = generated[:, ref_audio_len:, :]
        generated = generated.permute(0, 2, 1)

        # Decode
        generated_wave = vocoder.decode(generated)

    # 🚀 END TIMER
    end = time.time()

    print("\n✅ Done")
    print(f"Reference Audio : {ref_audio}")
    print(f"Time Taken      : {end - start:.2f} sec")


def main():
    parser = argparse.ArgumentParser(description="Minimal CLI TTS")

    parser.add_argument("--text", default="ಉದ್ಯೋಗ ಹೊರ್ತುಪಡ್ಸಿ ನನಗೆ ಒಂದು ಹವ್ಯಾಸ ಎದ್ರಾಗ ಆಸಕ್ತಿ ಜಾಸ್ತಿ ಅದ ಅಂತಂದು ಹೇಳಿದ್ರೆ ಡಾನ್ಸ್", help="Text to generate")
    parser.add_argument("--ref_audio", default="ref.wav", help="Reference audio path")
    parser.add_argument("--ref_text", default="ಇಂಡಿಯಾ ಶ್ರೀಲಂಕಾ ನೇಪಾಲ್ ಬಾಂಗ್ಲಾದೇಶ್ ಆಫ್ಘಾನಿಸ್ತಾನ್", help="Reference audio transcript")
    parser.add_argument("--steps", type=int, default=32, help="Sampling steps")
    parser.add_argument("--device", default="cuda", help="cuda or cpu")

    args = parser.parse_args()

    model, vocoder, _ = load_everything(device=args.device)

    run_inference(
        model,
        vocoder,
        args.text,
        args.ref_audio,
        args.ref_text,
        steps=args.steps,
    )


if __name__ == "__main__":
    main()