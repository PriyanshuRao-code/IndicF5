#!/usr/bin/env python3
"""
Command-line interface for IndicF5 TTS
Usage examples:
  python tts_cli.py --list-voices
  python tts_cli.py --voice PAN_F_HAPPY_00001 --text "ਸਤ ਸ੍ਰੀ ਅਕਾਲ"
  python tts_cli.py --voice PAN_F_HAPPY_00001 --text "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" --output out.wav
  echo "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" | python tts_cli.py --voice PAN_F_HAPPY_00001
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Make sure project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from tts_utils import TTSProcessor
from config import PATHS


def list_voices(processor: TTSProcessor):
    voices = processor.get_available_reference_voices()
    if not voices:
        print("No reference voices found.")
        return
    print(f"Available voices ({len(voices)}):\n")
    for key, info in voices.items():
        print(f"  {key}")
        print(f"    Author : {info.get('author', 'unknown')}")
        print(f"    Model  : {info.get('model', 'IndicF5')}")
        print(f"    Content: {info.get('content', '')[:60]}...")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="IndicF5 TTS - Terminal Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--voice", "-v", help="Reference voice key (use --list-voices to see options)")
    parser.add_argument("--text", "-t", help="Text to synthesize (or pipe via stdin)")
    parser.add_argument("--output", "-o", help="Output WAV file path (default: data/out/<timestamp>.wav)")
    parser.add_argument("--seed", type=int, default=-1, help="Random seed for reproducibility (default: random)")
    parser.add_argument("--sample-rate", type=int, default=24000, help="Output sample rate (default: 24000)")
    parser.add_argument("--list-voices", "-l", action="store_true", help="List available reference voices and exit")

    args = parser.parse_args()

    processor = TTSProcessor()
    processor.load_reference_voices()

    if args.list_voices:
        list_voices(processor)
        return

    if not args.voice:
        parser.error("--voice is required. Use --list-voices to see available options.")

    # Get text from --text flag or stdin
    text = args.text
    if not text:
        if sys.stdin.isatty():
            parser.error("Provide text via --text or pipe it via stdin.")
        text = sys.stdin.read().strip()
    if not text:
        parser.error("No text provided.")

    if not processor.validate_reference_voice_key(args.voice):
        available = list(processor.get_available_reference_voices().keys())
        print(f"Error: voice '{args.voice}' not found. Available: {available}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    output_path = args.output
    if not output_path:
        out_dir = PATHS.get("output_dir", "./data/out")
        os.makedirs(out_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(out_dir, f"tts_{args.voice}_{timestamp}.wav")

    print(f"Loading model...")
    processor.load_model()

    print(f"Synthesizing: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
    print(f"Voice        : {args.voice}")
    print(f"Output       : {output_path}")

    result = processor.process_single_text(
        text=text,
        reference_voice_key=args.voice,
        output_path=output_path,
        sample_rate=args.sample_rate,
        seed=args.seed,
    )

    if result["success"]:
        print(f"\nDone in {result['duration']:.2f}s -> {output_path}")
    else:
        print(f"\nFailed: {result['message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
