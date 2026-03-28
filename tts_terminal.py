#!/usr/bin/env python3
"""
IndicF5 TTS Terminal Runner
============================
A comprehensive command-line interface that replicates all functionalities
provided by the web frontend (temp_script.js), using the TTSProcessor class
from tts_utils.py directly — no HTTP server required.

Sub-commands
------------
  single        Generate speech for a single text snippet.
  batch         Generate speech for multiple requests from a JSON file.
  list-voices   List all available reference voices.
  add-voice     Register a new reference voice (WAV + transcript).
  remove-voice  Remove a reference voice from the registry.
  list-files    Show previously generated audio files.
  sysinfo       Print current CPU / RAM / GPU stats.

Usage examples
--------------
  python tts_terminal.py single --text "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" --voice PAN_F_HAPPY_00001
  python tts_terminal.py single --text "Hello" --voice PAN_F_HAPPY_00001 --seed 42 --format mp3
  python tts_terminal.py batch --input requests.json
  python tts_terminal.py list-voices
  python tts_terminal.py add-voice --file my.wav --name my_voice --content "transcript" --author "Me"
  python tts_terminal.py remove-voice --name my_voice --delete-file
  python tts_terminal.py list-files
  python tts_terminal.py sysinfo
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure the project root is importable regardless of the working directory.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import PATHS
from tts_utils import TTSProcessor


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------

def format_elapsed(seconds: float) -> str:
    """
    Format a duration given in fractional seconds to a human-readable string.

    The output shows minutes, seconds, and milliseconds together with the
    raw total in seconds so timings are easy to compare at a glance.

    Args:
        seconds: Elapsed time in seconds (float).

    Returns:
        A string of the form  '01m:23s.456ms  (83.456s total)'.

    Example:
        >>> format_elapsed(83.456)
        '01m:23s.456ms  (83.456s total)'
    """
    total_s = int(seconds)
    mins = total_s // 60
    secs = total_s % 60
    ms = int((seconds - total_s) * 1000)
    return f"{mins:02d}m:{secs:02d}s.{ms:03d}ms  ({seconds:.3f}s total)"


def _print_phase(label: str, elapsed: float) -> None:
    """
    Print a single timing phase line to stdout.

    Args:
        label:   Short description of the phase (e.g. 'Model load').
        elapsed: Duration of this phase in seconds.
    """
    print(f"  {label:<18}: {format_elapsed(elapsed)}")


# ---------------------------------------------------------------------------
# System monitoring
# ---------------------------------------------------------------------------

def print_system_stats() -> None:
    """
    Print a snapshot of CPU, RAM, and GPU utilisation to stdout.

    Mirrors the intent of the JS ``startSystemMonitoring`` function.

    Requires ``psutil`` for CPU/RAM metrics (optional) and ``torch`` for
    GPU metrics (optional).  Gracefully degrades when either library is
    absent, printing an install hint instead of crashing.
    """
    print("\n[SYSTEM STATS]")
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        print(f"  CPU usage  : {cpu:.1f}%")
        print(f"  RAM used   : {mem.used / 1e9:.2f} GB / {mem.total / 1e9:.2f} GB total")
    except ImportError:
        print("  (psutil not installed — run: pip install psutil)")

    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                alloc = torch.cuda.memory_allocated(i) / 1e9
                total_gpu = props.total_memory / 1e9
                print(
                    f"  GPU [{i}] {props.name}: "
                    f"{alloc:.2f} GB / {total_gpu:.2f} GB VRAM used"
                )
        else:
            print("  GPU        : not available — running on CPU")
    except ImportError:
        print("  (torch not installed)")
    print()


# ---------------------------------------------------------------------------
# Voice management helpers
# ---------------------------------------------------------------------------

def cmd_list_voices(processor: TTSProcessor) -> None:
    """
    Print a formatted table of all reference voices to stdout.

    Mirrors ``loadReferenceVoices`` / ``GET /api/referenceVoices`` from the
    web frontend.

    Args:
        processor: An initialised TTSProcessor whose voices are already loaded
                   via ``processor.load_reference_voices()``.
    """
    voices = processor.get_available_reference_voices()
    if not voices:
        print("No reference voices found.")
        return

    header = f"{'KEY':<32} {'AUTHOR':<28} {'SR':>6}  {'MODEL':<10}  FILE"
    print(f"\n{header}")
    print("-" * len(header))
    for key, meta in voices.items():
        print(
            f"{key:<32} {meta.get('author', ''):<28} "
            f"{meta.get('sample_rate', ''):>6}  "
            f"{meta.get('model', '')::<10}  "
            f"{meta.get('file', '')}"
        )
    print(f"\nTotal: {len(voices)} voice(s)\n")


def cmd_add_voice(
    wav_path: str,
    name: str,
    content: str,
    author: str = "User",
    voice_model: str = "IndicF5",
    voices_file: str = "",
    voices_dir: str = "",
) -> None:
    """
    Register a new reference voice: copy WAV to the voices directory and
    append an entry to the registry JSON file.

    Mirrors ``POST /api/referenceVoices/upload`` endpoint behaviour.

    The voice key is derived from ``name`` by lower-casing and replacing
    spaces with underscores (e.g. ``"My Voice"`` → ``"my_voice"``).

    Args:
        wav_path:    Absolute or relative path to the source WAV file.
        name:        Desired voice key/name.
        content:     Verbatim transcript of what the speaker says in the WAV.
                     This is used as ``ref_text`` during inference.
        author:      Human-readable label for the voice (default: 'User').
        voice_model: Model identifier tag stored in the registry
                     (default: 'IndicF5').
        voices_file: Path to reference_voices.json; empty → use project default.
        voices_dir:  Directory where voice WAV files are stored;
                     empty → use project default.

    Raises:
        FileNotFoundError: If ``wav_path`` does not point to an existing file.
        ValueError:        If the derived key already exists in the registry.
    """
    import shutil

    voices_file = voices_file or str(SCRIPT_DIR / "data" / "reference_voices" / "reference_voices.json")
    voices_dir  = voices_dir  or str(SCRIPT_DIR / "data" / "reference_voices")

    wav_path = os.path.abspath(wav_path)
    if not os.path.isfile(wav_path):
        raise FileNotFoundError(f"WAV file not found: {wav_path}")

    key = name.lower().replace(" ", "_")

    # Load existing registry
    registry: Dict[str, Any] = {}
    if os.path.isfile(voices_file):
        with open(voices_file, "r", encoding="utf-8") as f:
            registry = json.load(f)

    if key in registry:
        raise ValueError(
            f"Voice key '{key}' already exists. "
            "Delete it first (remove-voice) or choose a different --name."
        )

    # Copy WAV file to voices directory
    os.makedirs(voices_dir, exist_ok=True)
    dest_filename = os.path.basename(wav_path)
    dest_path = os.path.join(voices_dir, dest_filename)
    if os.path.abspath(wav_path) != os.path.abspath(dest_path):
        shutil.copy2(wav_path, dest_path)
        print(f"[INFO] Copied WAV to: {dest_path}")

    # Auto-detect sample rate (requires soundfile)
    sample_rate = 24000
    try:
        import soundfile as sf
        info = sf.info(dest_path)
        sample_rate = info.samplerate
    except ImportError:
        print("[INFO] soundfile not available — defaulting sample_rate to 24000 Hz")

    # Append to registry
    registry[key] = {
        "author": author,
        "file": dest_filename,
        "content": content,
        "sample_rate": sample_rate,
        "model": voice_model,
    }
    os.makedirs(os.path.dirname(voices_file), exist_ok=True)
    with open(voices_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Voice '{key}' registered successfully (sample_rate={sample_rate} Hz).")


def cmd_remove_voice(
    voice_key: str,
    delete_file: bool = False,
    voices_file: str = "",
    voices_dir: str = "",
) -> None:
    """
    Remove a reference voice from the registry and optionally delete its WAV.

    Mirrors ``DELETE /api/referenceVoices/{voice_key}`` endpoint behaviour.

    Args:
        voice_key:   Registry key to delete.
        delete_file: If True, also removes the WAV from the voices directory.
        voices_file: Path to reference_voices.json; empty → use project default.
        voices_dir:  Directory containing voice WAV files;
                     empty → use project default.

    Raises:
        FileNotFoundError: If reference_voices.json does not exist.
        KeyError:          If ``voice_key`` is not found in the registry.
    """
    voices_file = voices_file or str(SCRIPT_DIR / "data" / "reference_voices" / "reference_voices.json")
    voices_dir  = voices_dir  or str(SCRIPT_DIR / "data" / "reference_voices")

    if not os.path.isfile(voices_file):
        raise FileNotFoundError(f"Registry file not found: {voices_file}")

    with open(voices_file, "r", encoding="utf-8") as f:
        registry: Dict[str, Any] = json.load(f)

    if voice_key not in registry:
        raise KeyError(
            f"Voice key '{voice_key}' not found. "
            f"Available: {list(registry.keys())}"
        )

    meta = registry.pop(voice_key)

    with open(voices_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Voice '{voice_key}' removed from registry.")

    if delete_file:
        wav_path = os.path.join(voices_dir, meta["file"])
        if os.path.isfile(wav_path):
            os.remove(wav_path)
            print(f"[INFO] Deleted WAV file: {wav_path}")
        else:
            print(f"[WARNING] WAV file not found (skipping delete): {wav_path}")


# ---------------------------------------------------------------------------
# Generated-files helper
# ---------------------------------------------------------------------------

def cmd_list_files(output_dir: str = "") -> List[str]:
    """
    List all audio files previously generated and saved to the output directory.

    Mirrors the ``loadGeneratedFiles`` JS function and ``GET /api/files``
    endpoint behaviour.

    Args:
        output_dir: Path to the output directory; empty → use project default.

    Returns:
        Sorted list of filenames (not full paths) found in output_dir.
    """
    output_dir = output_dir or PATHS.get("output_dir", str(SCRIPT_DIR / "data" / "out"))

    if not os.path.isdir(output_dir):
        print(f"[INFO] Output directory does not exist yet: {output_dir}")
        return []

    files = sorted(
        f for f in os.listdir(output_dir)
        if f.lower().endswith((".wav", ".mp3"))
    )

    print(f"\n[FILES] {len(files)} file(s) in '{output_dir}':")
    for fname in files:
        size = os.path.getsize(os.path.join(output_dir, fname))
        print(f"  {fname}  ({size:,} bytes)")
    print()
    return files


# ---------------------------------------------------------------------------
# Single TTS generation
# ---------------------------------------------------------------------------

def cmd_single_tts(
    processor: TTSProcessor,
    text: str,
    reference_voice_key: str = "",
    voice_file: str = "",
    ref_text: str = "",
    output_format: str = "wav",
    sample_rate: int = 24000,
    normalize: bool = True,
    seed: int = -1,
    save_to_file: bool = True,
    output_dir: str = "",
) -> Dict[str, Any]:
    """
    Generate speech for a single text input using a chosen reference voice.

    Mirrors the ``generateSingleTTS`` JS function and ``POST /api/tts``
    endpoint.

    Voice source (exactly one must be provided):
      - ``reference_voice_key`` — key looked up in the loaded voice registry.
      - ``voice_file`` + optional ``ref_text`` — path to a WAV file used
        directly.  A temporary in-memory entry is injected into the processor's
        registry so the existing ``process_single_text`` path is reused.
        The entry is cleaned up after inference.

    The function delegates inference to ``TTSProcessor.process_single_text``
    which handles:
      - Seed setting (``seed_everything``).
      - Model forward pass (``model(text, ref_audio_path, ref_text)``).
      - Audio normalisation (if requested via TTSProcessor internals).
      - Automatic text chunking when text > 300 characters.

    Args:
        processor:           Initialised and model-loaded TTSProcessor.
        text:                Text to synthesize (may contain
                             ``<refvoice key='...'>`` tags for multi-voice).
        reference_voice_key: Key present in the reference voices registry.
                             Mutually exclusive with ``voice_file``.
        voice_file:          Path to a WAV file used as the reference voice
                             directly (bypasses the registry).
                             Mutually exclusive with ``reference_voice_key``.
        ref_text:            Verbatim transcript of ``voice_file``.
                             Used as ``ref_text`` during inference.
                             Ignored when ``reference_voice_key`` is used.
        output_format:       ``'wav'`` or ``'mp3'`` (default: ``'wav'``).
        sample_rate:         Output audio sample rate in Hz (default: 24000).
        normalize:           Whether to normalise audio amplitude to 0.95 peak.
        seed:                Random seed; ``-1`` selects a fresh random seed.
        save_to_file:        If True, persist the audio file to ``output_dir``.
        output_dir:          Directory to save generated files; empty → project
                             default (``data/out``).

    Returns:
        Dict with at minimum:
        - ``'success'``     : bool
        - ``'filename'``    : str or None — saved filename
        - ``'output_path'`` : str or None — full path
        - ``'used_seed'``   : int
        - ``'duration'``    : float — wall-clock inference time in seconds
        - ``'sample_rate'`` : int
        - ``'message'``     : str — error description on failure

    Raises:
        ValueError: If neither ``reference_voice_key`` nor ``voice_file`` is given.
    """
    if not reference_voice_key and not voice_file:
        raise ValueError("Provide either reference_voice_key or voice_file.")

    # ── Inject a temporary in-memory voice when a raw WAV path is given ──────
    _temp_key: Optional[str] = None
    if voice_file:
        abs_wav = os.path.abspath(voice_file)
        if not os.path.isfile(abs_wav):
            return {
                "success": False,
                "message": f"voice-file not found: {abs_wav}",
                "output_path": None,
                "filename": None,
            }
        _temp_key = "_tts_terminal_temp_voice_"
        # Storing the absolute path as "file" works because os.path.join(dir, abs)
        # returns abs when the second argument is absolute (Python behaviour).
        processor.reference_voices[_temp_key] = {
            "author":      "temporary (via --voice-file)",
            "file":        abs_wav,
            "content":     ref_text,
            "sample_rate": sample_rate,
            "model":       "IndicF5",
        }
        reference_voice_key = _temp_key
        print(f"  Voice  : {abs_wav}  (direct file, ref_text={repr(ref_text[:60])})")
    else:
        print(f"  Voice  : {reference_voice_key}")

    output_dir = output_dir or PATHS.get("output_dir", str(SCRIPT_DIR / "data" / "out"))

    if save_to_file:
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = os.path.splitext(os.path.basename(voice_file))[0] if voice_file else reference_voice_key
        output_path = os.path.join(output_dir, f"tts_{label}_{timestamp}.{output_format}")
    else:
        output_path = None

    print(f"  Text   : {text[:80]}{'...' if len(text) > 80 else ''}")
    print(f"  Seed   : {seed}  |  Format: {output_format} @ {sample_rate} Hz")
    if output_path:
        print(f"  Output : {output_path}")

    try:
        result = processor.process_single_text(
            text=text,
            reference_voice_key=reference_voice_key,
            output_path=output_path,
            sample_rate=sample_rate,
            seed=seed,
        )
    finally:
        # Always clean up temp registry entry to avoid polluting the processor state
        if _temp_key and _temp_key in processor.reference_voices:
            del processor.reference_voices[_temp_key]

    if output_path and result.get("success"):
        result["output_path"] = output_path
        result["filename"] = os.path.basename(output_path)
    else:
        result["output_path"] = None
        result["filename"] = None

    return result


def cmd_interactive_tts(
    processor: TTSProcessor,
    voice_file: str,
    text: str,
    ref_text: str = "",
    seed: int = -1,
    output_dir: str = "",
) -> Dict[str, Any]:
    """
    CLI-driven single-shot TTS generation.

    Uses direct model calls via TTSProcessor (no API server), with all
    parameters supplied via command-line flags.
    """
    print("\n[INTERACTIVE MODE]")
    print("This mode runs local inference directly (no API/server) via CLI flags.")

    voice_file = voice_file.strip().strip('"').strip("'")
    if not voice_file:
        return {
            "success": False,
            "message": "Reference WAV path cannot be empty.",
            "output_path": None,
            "filename": None,
        }
    if not os.path.isfile(voice_file):
        return {
            "success": False,
            "message": f"File not found: {voice_file}",
            "output_path": None,
            "filename": None,
        }

    text = text.strip()
    if not text:
        return {
            "success": False,
            "message": "Text cannot be empty.",
            "output_path": None,
            "filename": None,
        }

    return cmd_single_tts(
        processor=processor,
        text=text,
        voice_file=voice_file,
        ref_text=ref_text,
        output_format="wav",
        sample_rate=24000,
        normalize=True,
        seed=seed,
        save_to_file=True,
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# Batch TTS generation
# ---------------------------------------------------------------------------

def cmd_batch_tts(
    processor: TTSProcessor,
    requests: List[Dict[str, Any]],
    output_dir: str = "",
) -> Dict[str, Any]:
    """
    Generate speech for multiple text/voice pairs in sequence.

    Mirrors the ``processBatch`` JS function and ``POST /api/tts/batch``
    endpoint.

    Each item in ``requests`` must contain:
      - ``'text'``                : str  — text to synthesize
      - ``'reference_voice_key'`` : str  — key in the voice registry

    Optional per-item fields (fall back to defaults when absent):
      - ``'output_format'``  : str  (default: ``'wav'``)
      - ``'sample_rate'``    : int  (default: 24000)
      - ``'normalize'``      : bool (default: True)
      - ``'seed'``           : int  (default: -1 → random)

    Args:
        processor:  Initialised and model-loaded TTSProcessor.
        requests:   List of request dicts (see above).
        output_dir: Directory to save generated files; empty → project default.

    Returns:
        Dict with keys:
        - ``'total_requests'``      : int
        - ``'successful_requests'`` : int
        - ``'failed_requests'``     : int
        - ``'total_duration'``      : float — wall-clock seconds for the batch
        - ``'results'``             : List[Dict] — per-item result dicts
                                      (same shape as cmd_single_tts return,
                                      plus ``'index'`` and ``'text'`` fields)
    """
    total = len(requests)
    results: List[Dict[str, Any]] = []
    successful = 0
    failed = 0

    batch_start = time.time()
    print(f"\n[BATCH] Processing {total} request(s)...\n")

    for idx, req in enumerate(requests, start=1):
        text = req.get("text", "").strip()
        voice_key = req.get("reference_voice_key", "").strip()
        fmt = req.get("output_format", "wav")
        sr = req.get("sample_rate", 24000)
        norm = req.get("normalize", True)
        seed = req.get("seed", -1)

        print(f"--- Batch item {idx}/{total} ---")

        if not text or not voice_key:
            result: Dict[str, Any] = {
                "success": False,
                "index": idx,
                "text": text,
                "message": "Missing 'text' or 'reference_voice_key'.",
                "duration": 0.0,
            }
            failed += 1
        else:
            result = cmd_single_tts(
                processor=processor,
                text=text,
                reference_voice_key=voice_key,
                output_format=fmt,
                sample_rate=sr,
                normalize=norm,
                seed=seed,
                save_to_file=True,
                output_dir=output_dir,
            )
            result["index"] = idx
            result["text"] = text
            if result.get("success"):
                successful += 1
            else:
                failed += 1

        status = "OK" if result.get("success") else f"FAILED — {result.get('message')}"
        print(f"  Result : {status}  |  {format_elapsed(result.get('duration', 0.0))}\n")
        results.append(result)

    total_duration = time.time() - batch_start
    print(
        f"[BATCH] Done — {successful}/{total} succeeded, "
        f"{failed} failed, total: {format_elapsed(total_duration)}\n"
    )

    return {
        "total_requests": total,
        "successful_requests": successful,
        "failed_requests": failed,
        "total_duration": total_duration,
        "results": results,
    }


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the top-level ArgumentParser with all sub-commands.

    Global flags (before the sub-command) configure paths and credentials.
    Each sub-command adds its own flags via sub-parsers.

        Sub-commands registered:
            interactive, single, batch, list-voices, add-voice, remove-voice,
            list-files, sysinfo

    Returns:
        Configured ArgumentParser ready to call ``.parse_args()`` on.
    """
    default_output_dir  = PATHS.get("output_dir",  str(SCRIPT_DIR / "data" / "out"))
    default_voices_file = PATHS.get("reference_voices_file",
                                    str(SCRIPT_DIR / "data" / "reference_voices" / "reference_voices.json"))
    default_voices_dir  = PATHS.get("reference_voices_dir",
                                    str(SCRIPT_DIR / "data" / "reference_voices"))
    default_model       = os.getenv("MODEL_REPO_ID", "hareeshbabu82/TeluguIndicF5")

    parser = argparse.ArgumentParser(
        prog="tts_terminal.py",
        description="IndicF5 TTS Terminal Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Global options
    parser.add_argument(
        "--model", default=default_model,
        help=f"HuggingFace model repo ID (default: {default_model})",
    )
    parser.add_argument(
        "--cache-dir", default=os.getenv("MODEL_CACHE_DIR"),
        help="Local directory for caching downloaded model files",
    )
    parser.add_argument(
        "--hf-token", default=os.getenv("HF_TOKEN"),
        help="HuggingFace API token (for private/gated repos)",
    )
    parser.add_argument(
        "--output-dir", default=default_output_dir,
        help=f"Directory for generated audio (default: {default_output_dir})",
    )
    parser.add_argument(
        "--voices-file", default=default_voices_file,
        help="Path to reference_voices.json",
    )
    parser.add_argument(
        "--voices-dir", default=default_voices_dir,
        help="Directory containing reference voice WAV files",
    )
    parser.add_argument(
        "--no-sysinfo", action="store_true",
        help="Skip printing system stats at startup",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # ── interactive ───────────────────────────────────────────────────────
    p_interactive = sub.add_parser(
        "interactive",
        help="Generate one WAV using CLI flags (no runtime prompts).",
    )
    p_interactive.add_argument(
        "--voice-file",
        required=True,
        help="Path to the reference WAV file.",
    )
    p_interactive.add_argument(
        "--text", "-t",
        required=True,
        help="Text to synthesize.",
    )
    p_interactive.add_argument(
        "--ref-text",
        default="",
        help="Transcript of the reference WAV (recommended).",
    )
    p_interactive.add_argument(
        "--seed", "-s",
        type=int,
        default=-1,
        help="Random seed for reproducibility (-1 = random, default: -1)",
    )

    # ── single ─────────────────────────────────────────────────────────────
    p_single = sub.add_parser(
        "single",
        help="Generate speech for one text snippet.",
    )
    p_single.add_argument("--text", "-t", required=True, help="Text to synthesize.")
    # Voice source: either a registry key OR a direct WAV file path (mutually exclusive).
    voice_group = p_single.add_mutually_exclusive_group(required=True)
    voice_group.add_argument(
        "--voice", "-v",
        help="Reference voice key from the registry (use list-voices to see options).",
    )
    voice_group.add_argument(
        "--voice-file",
        help=(
            "Path to a reference WAV file used directly, bypassing the registry. "
            "Pair with --ref-text to supply the transcript (empty string is used otherwise)."
        ),
    )
    p_single.add_argument(
        "--ref-text",
        default="",
        help=(
            "Transcript of the --voice-file audio (used as ref_text during inference). "
            "Ignored when --voice (registry key) is used."
        ),
    )
    p_single.add_argument(
        "--format", "-f", default="wav", choices=["wav", "mp3"],
        help="Output audio format (default: wav)",
    )
    p_single.add_argument(
        "--sample-rate", "-r", type=int, default=24000,
        help="Audio sample rate in Hz (default: 24000)",
    )
    p_single.add_argument(
        "--no-normalize", action="store_true",
        help="Disable amplitude normalisation",
    )
    p_single.add_argument(
        "--seed", "-s", type=int, default=-1,
        help="Random seed for reproducibility (-1 = random, default: -1)",
    )
    p_single.add_argument(
        "--no-save", action="store_true",
        help="Do not save audio to disk (inference only / dry run)",
    )

    # ── batch ──────────────────────────────────────────────────────────────
    p_batch = sub.add_parser(
        "batch",
        help="Generate speech for multiple requests defined in a JSON file.",
    )
    p_batch.add_argument(
        "--input", "-i", required=True,
        help=(
            "JSON file with a list of request objects, each containing "
            "'text' and 'reference_voice_key'. Optional: 'output_format', "
            "'sample_rate', 'normalize', 'seed'. "
            "Top-level structure may be a bare list or {'requests': [...]}."
        ),
    )

    # ── list-voices ────────────────────────────────────────────────────────
    sub.add_parser("list-voices", help="Print all available reference voices.")

    # ── add-voice ──────────────────────────────────────────────────────────
    p_add = sub.add_parser("add-voice", help="Register a new reference voice.")
    p_add.add_argument("--file",    required=True, help="Path to the source WAV file.")
    p_add.add_argument("--name",    required=True, help="Voice key name (e.g. 'my_voice').")
    p_add.add_argument("--content", required=True, help="Verbatim transcript of the reference WAV.")
    p_add.add_argument("--author",  default="User", help="Human label for the voice (default: User).")
    p_add.add_argument(
        "--voice-model", default="IndicF5",
        help="Model identifier stored in the registry (default: IndicF5)",
    )

    # ── remove-voice ───────────────────────────────────────────────────────
    p_rm = sub.add_parser("remove-voice", help="Remove a reference voice from the registry.")
    p_rm.add_argument("--name", required=True, help="Voice key to remove.")
    p_rm.add_argument(
        "--delete-file", action="store_true",
        help="Also delete the WAV file from the voices directory",
    )

    # ── list-files ─────────────────────────────────────────────────────────
    sub.add_parser("list-files", help="List previously generated audio files.")

    # ── sysinfo ────────────────────────────────────────────────────────────
    sub.add_parser("sysinfo", help="Print CPU / RAM / GPU utilisation snapshot.")

    return parser


# ---------------------------------------------------------------------------
# Main (entry point)
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Main entry point for the IndicF5 TTS terminal runner.

    Orchestration
    -------------
    1. Parse CLI arguments.
    2. Run commands that do **not** require the model (list-voices, add-voice,
       remove-voice, list-files, sysinfo) immediately and exit.
    3. For inference commands (interactive, single, batch):
       a. Optionally print system stats (``--no-sysinfo`` suppresses this).
       b. Load reference voices via TTSProcessor.
       c. Load the TTS model via TTSProcessor.
       d. Run the requested inference command.
       e. Print a full timing breakdown:
            Voice load | Model load | Generation | TOTAL
          using ``time.time()`` checkpoints at each phase.

    All timing uses ``time.time()`` and is formatted via ``format_elapsed``.
    """
    t_start = time.time()

    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(2)

    print("=" * 62)
    print("  IndicF5 TTS Terminal Runner")
    print("=" * 62)

    # ── Commands that don't need the model ─────────────────────────────────

    if args.command == "sysinfo":
        print_system_stats()
        print(f"Done in {format_elapsed(time.time() - t_start)}")
        return

    if args.command == "list-voices":
        t0 = time.time()
        # Instantiate processor just to use its voice-loading logic
        processor = TTSProcessor()
        processor.load_reference_voices()
        cmd_list_voices(processor)
        print(f"Done in {format_elapsed(time.time() - t0)}")
        return

    if args.command == "add-voice":
        t0 = time.time()
        cmd_add_voice(
            wav_path=args.file,
            name=args.name,
            content=args.content,
            author=args.author,
            voice_model=args.voice_model,
            voices_file=args.voices_file,
            voices_dir=args.voices_dir,
        )
        print(f"Done in {format_elapsed(time.time() - t0)}")
        return

    if args.command == "remove-voice":
        t0 = time.time()
        cmd_remove_voice(
            voice_key=args.name,
            delete_file=args.delete_file,
            voices_file=args.voices_file,
            voices_dir=args.voices_dir,
        )
        print(f"Done in {format_elapsed(time.time() - t0)}")
        return

    if args.command == "list-files":
        t0 = time.time()
        cmd_list_files(output_dir=args.output_dir)
        print(f"Done in {format_elapsed(time.time() - t0)}")
        return

    # ── Inference commands: interactive / single / batch ───────────────────

    if not args.no_sysinfo:
        print_system_stats()

    # Phase 1 — load reference voices
    print("[1/3] Loading reference voices...")
    t_voices_start = time.time()
    processor = TTSProcessor()
    processor.load_reference_voices()
    t_voices_done = time.time()
    voices_count = len(processor.get_available_reference_voices())
    print(f"      {voices_count} voice(s) loaded in {format_elapsed(t_voices_done - t_voices_start)}\n")

    # Phase 2 — load model
    print(f"[2/3] Loading TTS model '{args.model}'...")
    t_model_start = time.time()
    processor.load_model()
    t_model_done = time.time()
    print(f"      Model ready in {format_elapsed(t_model_done - t_model_start)}\n")

    # Phase 3 — generate audio
    print("[3/3] Generating audio...")
    t_gen_start = time.time()

    if args.command == "interactive":
        result = cmd_interactive_tts(
            processor=processor,
            voice_file=args.voice_file,
            text=args.text,
            ref_text=args.ref_text,
            seed=args.seed,
            output_dir=args.output_dir,
        )
        t_gen_done = time.time()

        print("\n" + "=" * 62)
        if result.get("success"):
            print("  SUCCESS")
            print(f"  Seed used   : {result.get('used_seed', 'N/A')}")
            print(f"  Sample rate : {result.get('sample_rate', 'N/A')} Hz")
            if result.get("output_path"):
                print(f"  File saved  : {result['output_path']}")
        else:
            print(f"  FAILED: {result.get('message', 'Unknown error')}")
        print("=" * 62)

    elif args.command == "single":
        result = cmd_single_tts(
            processor=processor,
            text=args.text,
            reference_voice_key=args.voice or "",
            voice_file=args.voice_file or "",
            ref_text=getattr(args, "ref_text", ""),
            output_format=args.format,
            sample_rate=args.sample_rate,
            normalize=not args.no_normalize,
            seed=args.seed,
            save_to_file=not args.no_save,
            output_dir=args.output_dir,
        )
        t_gen_done = time.time()

        print("\n" + "=" * 62)
        if result.get("success"):
            print("  SUCCESS")
            print(f"  Seed used   : {result.get('used_seed', 'N/A')}")
            print(f"  Sample rate : {result.get('sample_rate', 'N/A')} Hz")
            if result.get("output_path"):
                print(f"  File saved  : {result['output_path']}")
        else:
            print(f"  FAILED: {result.get('message', 'Unknown error')}")
        print("=" * 62)

    elif args.command == "batch":
        # Load and validate batch JSON
        with open(args.input, "r", encoding="utf-8") as f:
            raw = json.load(f)

        if isinstance(raw, dict) and "requests" in raw:
            batch_requests = raw["requests"]
        elif isinstance(raw, list):
            batch_requests = raw
        else:
            print('[ERROR] Batch JSON must be a list or {"requests": [...]}.')
            sys.exit(1)

        summary = cmd_batch_tts(
            processor=processor,
            requests=batch_requests,
            output_dir=args.output_dir,
        )
        t_gen_done = time.time()

        print("=" * 62)
        print("  BATCH SUMMARY")
        print(f"  Total       : {summary['total_requests']}")
        print(f"  Succeeded   : {summary['successful_requests']}")
        print(f"  Failed      : {summary['failed_requests']}")
        print("=" * 62)

    else:
        # Should never reach here given the subparser setup
        t_gen_done = time.time()
        print(f"[ERROR] Unknown command: {args.command}")
        sys.exit(1)

    # ── Timing breakdown ───────────────────────────────────────────────────
    t_total = time.time()
    print("\n  TIMING BREAKDOWN")
    _print_phase("Voice load",  t_voices_done - t_voices_start)
    _print_phase("Model load",  t_model_done  - t_model_start)
    _print_phase("Generation",  t_gen_done    - t_gen_start)
    _print_phase("TOTAL",       t_total       - t_start)
    print("=" * 62 + "\n")


if __name__ == "__main__":
    main()
