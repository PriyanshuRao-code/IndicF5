## api_client_example.md

📄 TTS IndicF5 API Client – Quick README

This script acts as a client tester for a Text-to-Speech (TTS) REST API. It demonstrates how to interact with a locally running TTS server to generate speech from text.

📌 File reference:

🚀 What it does
Sends HTTP requests to a TTS API (http://localhost:8000/api)
Converts text → speech using API endpoints
Supports single requests, batch processing, chunking, and file saving
Handles audio in base64 format → saves as .wav files
⚙️ Key Functionalities
🔹 1. Health Check
Endpoint: /health
Verifies if API server is running properly
🔹 2. Get Available Voices
Endpoint: /referenceVoices
Fetches all available reference voices
Returns voice keys + metadata
🔹 3. Single TTS Request
Endpoint: /tts
Converts one text → audio
Automatically:
Handles long text via chunking
Combines audio chunks into one file
🔹 4. Batch TTS Request
Endpoint: /tts/batch
Processes multiple texts in one request
Returns:
Success/failure count
Individual audio outputs
🔹 5. Server-side Save
Endpoint: /tts/save
Generates audio and stores it directly on server
Client only gets filename (no audio transfer)
🔹 6. Chunking Demo
Endpoint: /tts/chunk-demo
Shows how text will be split before TTS
Helps debug long-text processing
📂 Output

Client-side audio saved in:

client_output/
client_output/batch/
Audio is received as base64 → decoded → saved as .wav
🧠 Key Concepts Used
REST API communication (requests)
JSON request/response handling
Base64 encoding/decoding for audio
Automatic text chunking for long inputs
Multi-language support (Telugu, Hindi, Punjabi examples)
⚠️ Requirements
API server must be running locally

Reference voices must exist in:

data/reference_voices/
Python packages:
requests
json, base64, etc.
🧩 Overall Idea

This script is a testing + demonstration client for your TTS backend:

Backend = TTS engine
This script = API consumer

---

## config.md

All the configurations including server configurations, model configurations, audio configuration (sample rate, format, normalize, max audio len), paths (ref file and dir, output dir etc.), api configuration, logging configuration (file, log level) and security configurations (including api_key)

---

## example_bulk_tts.md

TTS Utils – Quick README

This script demonstrates how to use a Text-to-Speech (TTS) utility module (tts_utils.py) for generating speech from text in different ways.

🚀 What it does
Converts text → speech audio
Supports single input, batch processing, and advanced configurations
Allows saving audio files or returning audio as base64 (for APIs)
⚙️ Key Components
1. Core Utilities Used
generate_speech() → simple one-line TTS
generate_speech_batch() → batch processing
TTSProcessor → full control over TTS workflow
create_tts_processor() → quick processor setup
🧪 Examples Covered
🔹 Example 1: Simple Generation
Convert one text string to audio
Automatically loads model and reference voices
🔹 Example 2: Processor Instance
Reuse a single processor for multiple texts
More efficient for repeated operations
🔹 Example 3: Batch Processing
Convert multiple texts at once
Each text → separate audio file
🔹 Example 4: Advanced Usage
Custom processor configuration
Handles long text via chunking
Splits text intelligently (sentences → punctuation → words)
🔹 Example 5: Base64 Output
Generates audio without saving to file
Converts output to base64 string (useful for APIs/web apps)
📂 Output

All generated audio files are stored in:

tts_examples_output/

Batch outputs go into:

batch_output/
⚠️ Requirements

To run successfully, you need:

reference_voices.json with valid voice keys
Corresponding audio files for those voices
Required Python dependencies installed
🧠 Overall Idea

This script acts as a demo + testing playground for a TTS system:

Beginner → use simple functions
Intermediate → use processor instance
Advanced → customize pipeline, chunking, and output format

---

## test.md

TTS Model Inference Script – Quick README

This script demonstrates how to perform Text-to-Speech (TTS) inference using two approaches:

A custom Hugging Face IndicF5 model
The F5TTS API wrapper
🚀 What it does
Loads a pretrained TTS model from Hugging Face
Uses reference voices for speaker/style conditioning
Generates speech from input text
Saves output audio as .wav
Compares two TTS pipelines:
Direct model inference
F5TTS API-based inference
⚙️ Workflow Overview
🔹 1. Model Loading

Loads model from:

hareeshbabu82/TeluguIndicF5
Uses trust_remote_code=True for custom architecture
Measures loading time
🔹 2. Reference Voices Setup

Reads:

data/reference_voices/reference_voices.json
Each voice contains:
Audio file path (file)
Reference text (content)
🔹 3. Speech Generation (IndicF5 Model)
Input:
Telugu text
Reference voice key

Model call:

audio = model(
    text,
    ref_audio_path=...,
    ref_text=...
)
Features:
Voice cloning / style transfer using reference audio
Measures generation time
🔹 4. Audio Processing & Saving
Converts audio to float32 if needed
Saves output using soundfile

Output path:

data/out/gen_<timestamp>.wav
🔹 5. F5TTS API-Based Inference

Uses:

f5tts = F5TTS(model="F5TTS_Base")
Generates speech with:
Reference audio + text
New generation text (German example)

Saves output:

data/out/gen_f5tts_<timestamp>.wav
🧠 Key Concepts
🎤 Voice Cloning → using reference audio + text
🌍 Multilingual TTS → Telugu + German examples
⏱️ Performance Tracking → measures inference time
🔊 Audio Normalization → ensures correct format
🔁 Two Pipelines Comparison:
Direct model (flexible, raw)
F5TTS wrapper (structured, API-like)
📂 Outputs

Generated audio files:

data/out/
├── gen_<timestamp>.wav
├── gen_f5tts_<timestamp>.wav
⚠️ Requirements
Hugging Face model access
reference_voices.json + audio files
Python libraries:
transformers
numpy
soundfile
f5_tts
🧩 Overall Idea

This script is basically:
👉 “Load model → give reference voice → generate speech → save audio”

And then:
👉 “Compare with a higher-level API (F5TTS)”

⚖️ Pros & Cons
✅ Pros
Supports voice cloning
Works with multilingual text
Flexible (direct model usage)
Performance measurement included
❌ Cons
Requires proper reference data setup
Heavy model (slow loading time)
GPU not explicitly used (commented out)
Hardcoded paths → not production-ready

---

## tts_api.md

IndicF5 TTS API Server – Quick README

This script implements a production-ready FastAPI backend for a Text-to-Speech (TTS) system using the IndicF5 model.

📌 File reference:

🚀 What it does
Provides a REST API for Text-to-Speech
Supports:
Single & batch TTS
Voice cloning (reference voices)
Prompt-tag based multi-voice synthesis
Handles:
Audio generation
File storage
System monitoring
Voice management
🏗️ Architecture Overview
🔹 Core Components
FastAPI App → API server
TTSProcessor → handles model + inference
ThreadPoolExecutor → runs heavy tasks asynchronously
Config System → centralized settings
⚙️ Startup Flow
App starts (lifespan)
Loads Hugging Face model
Loads reference voices
Validates configuration
Creates required directories
🧠 Key Features
🎤 1. Text-to-Speech (Main Feature)
Endpoint: /api/tts
Converts text → speech
Supports:
Normal text
Long text (auto chunking)
Tagged text (multi-voice)
🧩 2. Intelligent Routing

Automatically decides how to process input:

If <refvoice> tags → multi-voice processing
If long text → chunking
Else → direct inference
🔁 3. Batch Processing
Endpoint: /api/tts/batch
Processes multiple requests together
Returns success/failure per request
🏷️ 4. Prompt Tagging (🔥 Advanced Feature)

Example:

<refvoice key="voice1">Hello</refvoice>
<refvoice key="voice2">World</refvoice>
Enables multi-speaker audio in one request
🎧 5. Reference Voice Management
Get all voices → /api/referenceVoices
Get audio → /api/referenceVoices/{key}/audio
Upload voice → /api/referenceVoices/upload
Delete voice → /api/referenceVoices/{key}
📂 6. File Management
List files → /api/files
Download → /api/files/{filename}
Delete → /api/files/{filename}
Clear all → /api/files
📊 7. System Monitoring
Endpoint: /api/system/monitor
Tracks:
CPU usage
Memory usage
GPU usage
🧪 8. Chunking Debug Tool
Endpoint: /api/tts/chunk-demo
Shows how text will be split
📦 API Endpoints Summary
Endpoint	Purpose
/api/tts	Single TTS
/api/tts/batch	Batch TTS
/api/tts/prompt-tagged	Multi-voice TTS
/api/referenceVoices	List voices
/api/files	Manage output files
/api/system/monitor	System stats
/api/health	Health check
📂 Output

Audio files stored in:

PATHS["output_dir"]
Formats supported:
WAV
MP3
FLAC
⚙️ Advanced Concepts Used
⚡ Async + ThreadPool (non-blocking API)
🧠 Intelligent request routing
🔊 Audio normalization & encoding (base64)
🔐 Secure file handling (path validation)
📊 System monitoring (psutil, GPUtil)
🌐 CORS support (frontend integration)
⚠️ Requirements
Hugging Face model access
Proper config (config.py)
Reference voices + audio files
Python packages:
fastapi, uvicorn
numpy, soundfile
psutil, GPUtil
🧩 Overall Idea

This is your full backend system:

Client (script / frontend)
        ↓
   FastAPI Server
        ↓
   TTSProcessor
        ↓
   IndicF5 Model
        ↓
   Audio Output
⚖️ Pros & Cons
✅ Pros
Production-ready architecture
Scalable (async + batching)
Supports multi-voice synthesis
File + voice management built-in
Monitoring included
❌ Cons
Complex (many moving parts)
CPU-heavy if no GPU
Needs proper config setup
Limited concurrency (executor=2)

---

## tts_cli.md

# TTS CLI - Command-Line Interface

A simple command-line interface for IndicF5 Text-to-Speech synthesis. This tool allows you to generate speech from text using predefined reference voices directly from the terminal.

## Features

- ✅ **List available voices** - View all registered reference voices
- ✅ **Single text synthesis** - Convert text to speech with a selected voice
- ✅ **Stdin support** - Pipe text directly to the script
- ✅ **Audio output control** - Specify custom output paths and sample rates
- ✅ **Reproducible results** - Use seeds for consistent audio generation
- ✅ **Automatic timestamped outputs** - Generated files are automatically named with timestamps

## Installation

Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Syntax

```bash
python tts_cli.py [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--voice` | `-v` | string | required | Reference voice key (use `--list-voices` to see options) |
| `--text` | `-t` | string | optional | Text to synthesize (or pipe via stdin) |
| `--output` | `-o` | string | auto-generated | Output WAV file path |
| `--seed` | - | integer | -1 (random) | Random seed for reproducibility |
| `--sample-rate` | - | integer | 24000 | Output sample rate in Hz |
| `--list-voices` | `-l` | flag | - | List available reference voices and exit |

## Examples

### List Available Voices

```bash
python tts_cli.py --list-voices
```

Output:
```
Available voices (5):

  PAN_F_HAPPY_00001
    Author : User
    Model  : IndicF5
    Content: ਸਤ ਸ੍ਰੀ ਅਕਾਲ...

  KAN_F_NEUTRAL_00001
    Author : Admin
    Model  : IndicF5
    Content: ನಮಸ್ತೆ ಕನ್ನಡ...
    
  ...
```

### Synthesize Text with Voice

```bash
python tts_cli.py --voice PAN_F_HAPPY_00001 --text "ਸਤ ਸ੍ਰੀ ਅਕਾਲ"
```

Output will be saved to: `./data/out/tts_PAN_F_HAPPY_00001_20240324_143021.wav`

### Specify Custom Output Path

```bash
python tts_cli.py --voice PAN_F_HAPPY_00001 --text "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" --output my_output.wav
```

### Pipe Text via Stdin

```bash
echo "ਸਤ ਸ੍ਰੀ ਅਕਾਲ" | python tts_cli.py --voice PAN_F_HAPPY_00001
```

Or from a file:

```bash
cat text_file.txt | python tts_cli.py --voice PAN_F_HAPPY_00001
```

### Set a Fixed Seed for Reproducibility

```bash
python tts_cli.py --voice PAN_F_HAPPY_00001 --text "Hello world" --seed 42
```

This will generate the same audio every time it's run with the same seed.

### Adjust Sample Rate

```bash
python tts_cli.py --voice PAN_F_HAPPY_00001 --text "Hello" --sample-rate 48000
```

### Combine Options

```bash
python tts_cli.py \
  --voice KAN_F_NEUTRAL_00001 \
  --text "ಉದ್ಯೋಗ ಹೊರ್ತುಪಡ್ಸಿ ನನಗೆ ಒಂದು ಹವ್ಯಾಸ" \
  --output kannada_speech.wav \
  --seed 123 \
  --sample-rate 24000
```

## Output

The script generates WAV files by default. Output files are saved to:

- **Auto-generated path**: `./data/out/tts_{VOICE_KEY}_{TIMESTAMP}.wav`
- **Custom path**: Specified via `--output` flag

Each output contains:
- Generated speech audio
- Specified sample rate (default: 24000 Hz)
- Mono or stereo format depending on model output

## Error Handling

### Missing Voice

```
Error: voice 'INVALID_VOICE' not found. Available: [...]
```

**Solution**: Use `--list-voices` to see valid voice keys.

### Missing Text

```
Error: No text provided.
```

**Solution**: Provide text via `--text` or pipe via stdin.

### Missing Voice Argument

```
Error: --voice is required. Use --list-voices to see available options.
```

**Solution**: Specify a voice with `-v` or `--voice`.

## Configuration

The script uses configuration from `config.py`:

```python
# Default output directory
PATHS["output_dir"] = "./data/out"

# Model and reference voices settings
MODEL_CONFIG["repo_id"]  # Hugging Face model ID
PATHS["reference_voices_file"]  # Location of voice registry
```

To modify these, edit `config.py` before running the script.

## Performance Notes

- **Model loading**: First run loads the model into memory (~5-15 seconds)
- **Synthesis time**: Depends on text length (typically 1-5 seconds per request)
- **GPU acceleration**: Automatically uses CUDA if available, falls back to CPU

## Related Files

- [tts_utils.md](tts_utils.md) - Core TTS processing functions
- [tts_terminal.md](tts_terminal.md) - Advanced terminal interface with batch processing
- [tts_api.md](tts_api.md) - REST API for programmatic access

## Troubleshooting

### Script not found
```bash
cd /path/to/TTSIndicF5
python tts_cli.py --list-voices
```

### Model not loading
Ensure you have sufficient disk space and internet connection for initial model download (~500MB - 2GB depending on model).

### Permission denied
```bash
chmod +x tts_cli.py
```

## License

See repository LICENSE file.


---

## tts_client.md

# TTS Client - Local TTS Template

A template/starter script demonstrating how to perform local Text-to-Speech synthesis using the IndicF5 model with reference voice prompts. This script loads the model directly without requiring an API server.

## Overview

The `tts_client.py` script shows a basic workflow for:
1. Loading the IndicF5 TTS model
2. Loading reference voice audio files
3. Generating speech from text with voice cloning
4. Saving the output to a WAV file

This is primarily intended as a **reference implementation** and **learning resource** for integrating IndicF5 into custom applications.

## Features

- 📦 **Direct model loading** - Load IndicF5 from Hugging Face Hub
- 🎙️ **Reference voice support** - Use speaker cloning with WAV files
- 🔧 **Minimal dependencies** - Only torch and torchaudio required
- ⏱️ **Timing measurements** - Track model loading and inference times
- 💾 **Audio I/O** - Load and save WAV files easily

## Installation

### Requirements

```bash
pip install torch torchaudio
```

Optional but recommended:
```bash
pip install transformers  # For easier model loading
```

## Usage

### Basic Syntax

```bash
python tts_client.py --text "Your text here" --voice reference.wav
```

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `--text` | string | ✅ Yes | Input text to convert to speech |
| `--voice` | string | ✅ Yes | Path to reference WAV file |

## Example

```bash
python tts_client.py \
  --text "Hello world" \
  --voice ./reference_speakers/speaker1.wav
```

## How It Works

### 1. Model Loading

```python
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_model():
    """Load IndicF5 model from Hugging Face"""
    print("📦 Loading IndicF5 model...")
    model = torch.hub.load(...)
    model.to(DEVICE)
    return model
```

The script automatically detects and uses GPU if available, otherwise falls back to CPU.

### 2. Audio Loading

```python
def load_reference_audio(path):
    """Load reference voice file"""
    waveform, sr = torchaudio.load(path)
    return waveform.to(DEVICE), sr
```

Accepts WAV files with various sample rates. Automatically moves to the selected device.

### 3. Speech Generation

```python
def generate_speech(model, text, reference_audio):
    """Generate speech from text + reference"""
    # Model inference
    audio = model.apply_tts(
        text=text,
        speaker='random',
        sample_rate=24000
    )
    return audio.unsqueeze(0), 24000
```

Uses the reference audio to condition voice cloning.

### 4. Audio Saving

```python
def save_audio(waveform, sample_rate, path="output.wav"):
    """Save generated waveform to WAV file"""
    torchaudio.save(path, waveform.cpu(), sample_rate)
    print(f"💾 Saved to {path}")
```

Saves the output as a WAV file in the specified location.

## Customization Guide

### Change Model Source

Modify the model loading in `load_model()`:

```python
def load_model():
    # Use different Hugging Face model
    from transformers import AutoModel
    model = AutoModel.from_pretrained(
        "ai4bharat/IndicF5",
        trust_remote_code=True
    )
    return model
```

### Modify Output Sample Rate

```python
def generate_speech(model, text, reference_audio):
    audio, _ = model.apply_tts(
        text=text,
        sample_rate=48000  # Change here
    )
    return audio.unsqueeze(0), 48000
```

### Process Multiple Files

Wrap the main function in a loop:

```python
text_files = ["text1.txt", "text2.txt", "text3.txt"]
reference_voice = "speaker.wav"

for text_file in text_files:
    with open(text_file, 'r') as f:
        text = f.read().strip()
    
    model = load_model()
    ref_audio, sr = load_reference_audio(reference_voice)
    audio, out_sr = generate_speech(model, text, ref_audio)
    
    output_name = text_file.replace('.txt', '.wav')
    save_audio(audio, out_sr, output_name)
```

### Add Batch Processing

```python
def batch_process(texts, voice_file, output_dir="outputs"):
    """Process multiple texts with the same voice"""
    os.makedirs(output_dir, exist_ok=True)
    model = load_model()
    ref_audio, sr = load_reference_audio(voice_file)
    
    for i, text in enumerate(texts):
        audio, out_sr = generate_speech(model, text, ref_audio)
        save_audio(audio, out_sr, f"{output_dir}/output_{i}.wav")
```

## Performance Notes

- **Model loading**: ~5-15 seconds (first time only if cached)
- **Inference time**: 1-5 seconds depending on text length
- **GPU memory**: ~2-4 GB (VRAM)
- **CPU memory**: ~4-8 GB (RAM)

## Configuration

### Device Selection

```python
# Auto-detect (recommended)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Or force CPU
DEVICE = "cpu"

# Or force GPU
DEVICE = "cuda:0"
```

### Output File

```python
OUTPUT_FILE = "output.wav"  # Change this line
```

## Common Issues and Solutions

### Model Loading Fails

```
RuntimeError: Model not found on Hugging Face
```

**Solution**: Check internet connection and ensure the model ID is correct.

### Out of Memory Error

```
RuntimeError: CUDA out of memory
```

**Solution**: 
- Reduce batch size or use CPU instead
- Close other GPU applications
- Use a smaller model variant if available

### Audio File Not Found

```
FileNotFoundError: [Errno 2] No such file or directory: 'reference.wav'
```

**Solution**: Ensure the reference WAV file path is correct and the file exists.

### No Audio Output

```
The script runs but produces silent audio
```

**Solution**: Check that the reference voice file is valid and the text is not empty.

## Advanced Usage

### Using with Different Languages

```python
# For Telugu
text = "మీ టెక్్ట్ ఇక"

# For Kannada  
text = "ನಿಮ್ಮ ಪಠ್ಯ ಇಲ್ಲಿ"

# For mixed scripts
text = "Hello ನಮಸ್ತೆ Hola"

# Run normally
audio, sr = generate_speech(model, text, ref_audio)
```

### Recording Custom Reference Voices

```bash
# Record a 5-10 second WAV file
ffmpeg -f alsa -i default -d 10 -q:a 9 -acodec libmp3lame my_voice.wav

# Then use it
python tts_client.py --text "Hello" --voice my_voice.wav
```

### Batch Processing Script

```python
#!/bin/bash
# process_batch.sh

for text_file in *.txt; do
    output="${text_file%.txt}.wav"
    python tts_client.py \
      --text "$(cat $text_file)" \
      --voice reference.wav > /dev/null
    mv output.wav "$output"
done
```

## Integration Examples

### With a Web Framework

```python
from flask import Flask, request, send_file
import tts_client

app = Flask(__name__)
model = load_model()
ref_audio, sr = load_reference_audio("voice.wav")

@app.route('/synthesize', methods=['POST'])
def synthesize():
    text = request.json['text']
    audio, sr = generate_speech(model, text, ref_audio)
    
    # Return audio
    torchaudio.save("temp.wav", audio, sr)
    return send_file("temp.wav", mimetype="audio/wav")
```

### With a Chat Interface

```python
def chat_tts(user_message, voice_file):
    """Generate speech response for chat"""
    model = load_model()
    ref_audio, sr = load_reference_audio(voice_file)
    audio, out_sr = generate_speech(model, user_message, ref_audio)
    return audio, out_sr
```

## Related Files

- [tts_cli.md](tts_cli.md) - Simple command-line interface
- [tts_terminal.md](tts_terminal.md) - Advanced terminal interface
- [tts_utils.md](tts_utils.md) - Core TTS processing utilities
- [tts_api.md](tts_api.md) - REST API implementation

## Performance Optimization

### Caching the Model

```python
MODEL_CACHE = None

def load_model():
    global MODEL_CACHE
    if MODEL_CACHE is None:
        MODEL_CACHE = torch.hub.load(...)
    return MODEL_CACHE
```

### Batching Multiple Requests

```python
def batch_generate(texts, reference_audio, model):
    """Generate multiple audio outputs efficiently"""
    results = []
    for text in texts:
        audio, sr = generate_speech(model, text, reference_audio)
        results.append(audio)
    return results
```

## License

See repository LICENSE file.

## References

- [IndicF5 Repository](https://huggingface.co/ai4bharat/IndicF5)
- [PyTorch Audio Documentation](https://pytorch.org/audio/)
- [Hugging Face Hub Guide](https://huggingface.co/docs/hub/)


---

## tts_terminal.md

IndicF5 TTS Terminal Runner – Quick README

This script provides a command-line interface (CLI) for your TTS system, allowing you to use all features without running the FastAPI server.

📌 File reference:

🚀 What it does
Runs TTS directly from terminal
Uses TTSProcessor internally (no HTTP calls)
Supports:
Single TTS
Batch TTS
Voice management
File management
System monitoring
🧠 Key Idea

👉 This is basically a “local client + controller” for your TTS engine

Instead of:

Client → API → TTSProcessor

You directly do:

CLI → TTSProcessor → Model → Audio
⚙️ Main Features
🔹 1. Single TTS
python tts_terminal.py single --text "Hello" --voice PAN_F_HAPPY_00001
Converts one text → audio
Supports:
custom seed
format (wav/mp3)
direct voice file
🔹 2. Batch TTS
python tts_terminal.py batch --input requests.json
Processes multiple texts
Reads JSON input
Outputs multiple audio files
🔹 3. Interactive Mode
python tts_terminal.py interactive --voice-file sample.wav --text "Hello"
Direct voice file usage (no registry needed)
🔹 4. Voice Management
List voices
list-voices
Add voice
add-voice --file my.wav --name my_voice
Remove voice
remove-voice --name my_voice
🔹 5. File Management
list-files
Lists generated audio files
🔹 6. System Monitoring
sysinfo
Shows:
CPU usage
RAM usage
GPU usage
⚙️ Internal Flow
🔹 Startup Steps
Parse CLI arguments
Load reference voices
Load model
Execute command
🔹 Processing Flow
Command Input
     ↓
Argument Parser (argparse)
     ↓
TTSProcessor
     ↓
Model Inference
     ↓
Audio Output (file)
⏱️ Performance Tracking
Shows timing for:
Voice loading
Model loading
Generation
Total runtime
📂 Outputs

Audio saved in:

data/out/
Supported formats:
WAV
MP3
⚠️ Requirements
Same as backend:
transformers, torch
numpy, soundfile
pydub
Reference voices setup
⚖️ Pros & Cons
✅ Pros
No server required (lightweight usage)
Great for testing & debugging
Full feature parity with API
Easy automation via scripts
❌ Cons
Not scalable like API
No UI (only terminal)
Sequential execution (no async batching)
🧩 Overall Role in Your System

You now have 3 layers:

1. CLI Tool (this file)
2. API Server (FastAPI)
3. Core Engine (TTSProcessor)

---

## tts_utils.md

TTS Utility Module (tts_utils.py) – Quick README

This module contains the core logic of the TTS system, separated from the API layer. It provides reusable functions for text-to-speech generation, batching, chunking, and multi-voice processing.

📌 File reference:

🚀 What it does
Handles all TTS processing logic
Interfaces with IndicF5 model (Hugging Face)
Supports:
Single text → speech
Batch processing
Multi-voice (tag-based) synthesis
Manages:
Audio generation
Chunking
Combining audio
Base64 encoding
🧠 Core Component
🔹 TTSProcessor (Main Class)

Central class that handles everything:

Model loading
Reference voice management
Audio generation
Processing pipelines
⚙️ Key Functionalities
🎤 1. Model & Voice Handling
load_model() → loads IndicF5 model
load_reference_voices() → loads voice metadata
Validates voice keys before inference
🔊 2. Audio Generation
generate_audio()
Input: text + reference voice
Output: numpy audio array
Supports:
Voice cloning
Seed-based reproducibility
✂️ 3. Text Chunking (VERY IMPORTANT)
split_text_into_chunks()
Strategy:
Sentence split
Punctuation split
Word split

👉 Ensures natural speech for long text

🔗 4. Audio Combining
combine_audio_files()
combine_audio_files_with_pauses()

Features:

Merge multiple audio chunks
Add pauses between segments
🔁 5. Single Text Processing
process_single_text()

Handles:

Short text → direct inference
Long text → chunk → generate → combine
🔄 6. Batch Processing
process_batch_texts()

Features:

Multiple texts + voices
Tracks success/failure
Generates separate files
🏷️ 7. Prompt Tag Processing (🔥 Advanced)
parse_reference_voice_tags()
process_reference_voice_tagged_text()

Example:

<refvoice key="voice1">Hello</refvoice>
<refvoice key="voice2">World</refvoice>

👉 Output = multi-speaker audio

🔄 8. Audio Utilities
audio_to_base64() → API-friendly output
save_audio_file() → save .wav
convert_wav_and_remove_silence() → clean audio
🧰 9. Convenience Functions
generate_speech() → quick single call
generate_speech_batch() → batch wrapper
generate_speech_from_reference_voice_tags() → multi-voice wrapper
📂 Data Flow
Text Input
   ↓
TTSProcessor
   ↓
Chunking (if needed)
   ↓
Model Inference
   ↓
Audio Processing
   ↓
Combine / Encode
   ↓
Final Output (WAV / Base64)
⚠️ Requirements
Hugging Face model
reference_voices.json
Python libraries:
transformers
numpy, soundfile
pydub
torch
⚖️ Pros & Cons
✅ Pros
Clean separation from API (modular design)
Handles complex cases (chunking + multi-voice)
Reusable across scripts, APIs, notebooks
Supports batch + scalable workflows
❌ Cons
Heavy dependency on reference voices
Temp file handling → slightly complex
Chunking logic can be optimized further
Limited GPU optimization (not explicit)
🧩 Overall Idea

This is the “engine” of your entire system:

API / Script / Client
        ↓
   TTSProcessor
        ↓
   Model (IndicF5)
        ↓
   Audio Output

---

## f5_tts/api.md

F5TTS Inference Module – Quick README

This file implements the core F5TTS model wrapper, used for high-quality text-to-speech generation with voice cloning.

📌 File reference:

🚀 What it does
Loads F5-TTS / E2-TTS models
Converts text → speech using:
Reference audio
Reference text
Generates:
Audio waveform (wav)
Spectrogram (spec)
Supports saving outputs to files
🧠 Key Idea

👉 This is a low-level inference engine (more raw than your TTSProcessor)

Reference Audio + Text
        ↓
   F5TTS Model
        ↓
 Generated Speech + Spectrogram
⚙️ Core Class
🔹 F5TTS

Main class that:

Loads model + vocoder
Handles inference
Manages device (CPU/GPU/MPS)
⚙️ Initialization Flow
🔹 1. Load Config
Reads .yaml config using OmegaConf
🔹 2. Load Model
Uses:
load_model()
load_vocoder()
🔹 3. Load Checkpoint
Downloads from Hugging Face using cached_path
🔊 Key Methods
🔹 infer() (Main Function)
wav, sr, spec = f5tts.infer(...)
Inputs:
ref_file → reference audio
ref_text → transcript of reference
gen_text → text to generate
Features:
Voice cloning
Speed control
CFG strength (generation quality)
Cross-fade smoothing
Silence removal
🔹 export_wav()
Saves generated audio
Optional silence removal
🔹 export_spectrogram()
Saves spectrogram image
🔹 transcribe()
Converts audio → text
⚙️ Advanced Controls (VERY IMPORTANT)

Inside infer():

Parameter	Purpose
target_rms	Loudness control
cross_fade_duration	Smooth transitions
cfg_strength	Quality vs diversity
nfe_step	Inference steps
speed	Speech speed
seed	Reproducibility
🧠 Internal Pipeline
Preprocess Reference Audio
        ↓
Model Inference (EMA Model)
        ↓
Mel Spectrogram
        ↓
Vocoder
        ↓
Final Audio (wav)
📂 Outputs
wav → generated audio
sr → sample rate
spec → spectrogram

Optional:

.wav file
.png spectrogram
⚠️ Requirements
torch
omegaconf
cached_path
soundfile
F5-TTS repo structure
⚖️ Pros & Cons
✅ Pros
High-quality speech synthesis
Fine-grained control over generation
Supports multiple model types
GPU acceleration support
❌ Cons
Complex setup (configs + checkpoints)
Slower than lightweight models
Requires tuning for best output
Less beginner-friendly
🧩 Role in Your System

Now your full system looks like:

CLI / API / Script
        ↓
TTSProcessor
        ↓
(IndicF5 OR F5TTS)
        ↓
Audio Output

👉 This file = alternative / advanced backend model

---

## f5_tts/configs.md

ls f5_tts/configs/
E2TTS_Base_train.yaml  E2TTS_Small_train.yaml  F5TTS_Base_train.yaml  F5TTS_Small_train.yaml  F5TTS_v1_Base.yaml
E2TTS_Base.yaml        E2TTS_Small.yaml        F5TTS_Base.yaml        F5TTS_Small.yaml

---

## f5_tts/socket_client.md

F5TTS Streaming Client – Quick README

This script implements a real-time audio streaming client for a TTS server. It sends text to a server and plays generated speech live as it is received.

🚀 What it does
Connects to a TTS streaming server (TCP socket)
Sends text input
Receives audio chunk-by-chunk
Plays audio in real-time using PyAudio
🧠 Key Idea

👉 Instead of waiting for full audio generation:

Traditional:
Text → Generate → Return full audio → Play

👉 This script does:

Streaming:
Text → Server → Audio chunks → Play instantly

🔥 This is low-latency TTS (very advanced)

⚙️ Workflow
🔹 1. Connect to Server

Uses TCP socket:

socket.connect((server_ip, port))

Default:

localhost:9998
🔹 2. Send Text

Encodes text → sends to server:

client_socket.sendall(text.encode("utf-8"))
🔹 3. Receive Audio Stream

Receives chunks:

data = socket.recv(8192)
Stops when:
No data
"END" signal received
🔹 4. Real-Time Playback

Converts bytes → numpy array:

np.frombuffer(data, dtype=np.float32)
Plays using PyAudio stream
🔹 5. Timing Metrics
Tracks:
Total time
Time to first audio chunk
🔊 Audio Configuration
Format: float32
Channels: 1 (mono)
Sample rate: 24000 Hz
⚙️ Async Design
Uses asyncio + run_in_executor
Keeps:
Network I/O non-blocking
Audio playback smooth
📂 Inputs / Outputs
Input:
Text string
Output:
Real-time audio playback (no file saving)
⚠️ Requirements

Running TTS streaming server on:

localhost:9998
Python libraries:
pyaudio
numpy
asyncio
⚖️ Pros & Cons
✅ Pros
Ultra low latency (instant playback)
Real-time experience (like voice assistant)
Efficient (no large file transfer)
Good for interactive systems
❌ Cons
Requires streaming server implementation
More complex than file-based TTS
Network dependency
Debugging harder
🧩 Role in Your System

Now your system becomes next-level architecture:

User Input
    ↓
Streaming Client (this script)
    ↓
TTS Server (socket-based)
    ↓
Model (F5TTS / IndicF5)
    ↓
Audio chunks
    ↓
Live Playback

---

## f5_tts/socket_file_client.md

F5TTS Streaming Client (Save Mode) – Quick README

This script is a TCP-based streaming client for a TTS server that:

Sends text
Receives audio in chunks
Reconstructs full audio
(Optionally) saves it to a file
🚀 What it does
Connects to TTS streaming server (localhost:9998)
Sends input text
Receives audio chunks continuously
Combines chunks into a full audio waveform
Can save output as .wav
🧠 Key Idea

👉 Compared to previous version (real-time playback):

Version	Behavior
Previous	Plays audio live
This one	Buffers → reconstructs → saves
⚙️ Workflow
🔹 1. Connect to Server
socket.connect((server_ip, port))
🔹 2. Send Text
client_socket.sendall(text.encode("utf-8"))
🔹 3. Receive Audio Chunks

Loop:

data = socket.recv(8192)
Stop when:
"END" received
Connection closed
🔹 4. Convert & Store
audio_array = np.frombuffer(data, dtype=np.float32)
audio_chunks.append(audio_array)
🔹 5. Combine Audio
full_audio = np.concatenate(audio_chunks)
🔹 6. (Optional) Save File
sf.write(filename, full_audio, 24000)

(Currently commented out in your code)

⏱️ Performance Tracking
Measures:
Total time
Time to first chunk
⚙️ Async Design
Uses:
asyncio
run_in_executor for blocking socket calls
📂 Input / Output
Input:
Text (via CLI argument)
Output:
Full audio array (in memory)
Optional .wav file
🧩 Difference from Previous Script
Feature	Playback Version	This Version
Audio handling	Real-time play	Buffer + save
Use case	Voice assistant	File generation
Latency	Low	Full wait
Output	Speaker	File
⚠️ Requirements

Running TTS server on:

localhost:9998
Libraries:
numpy
soundfile
asyncio
⚖️ Pros & Cons
✅ Pros
Clean full audio output
Easy file saving
No playback dependency (PyAudio not needed)
Good for batch / offline use
❌ Cons
No real-time feedback
Requires full stream completion
Higher perceived latency
🧩 Role in Your System

Now you have two streaming clients:

1. Real-time client → plays audio
2. Save-mode client → stores audio

👉 Both connect to same streaming backend

---

## f5_tts/socket_server.md

F5TTS Streaming Socket Server – Quick README

This script implements a real-time streaming TTS server using sockets. It generates speech chunk-by-chunk and streams it to clients while also saving it to disk.

📌 File reference:

🚀 What it does
Runs a TCP server
Accepts text from clients
Generates TTS audio incrementally (streaming)
Sends audio chunks in real-time
Saves full audio to file in parallel
🧠 Key Idea

👉 This is the backend counterpart to your streaming clients

Client → Socket Server → Model → Audio chunks → Client (real-time)
                                      ↓
                                   File save

🔥 This enables low-latency + persistent output simultaneously

⚙️ Core Components
🔹 1. TTSStreamingProcessor

Main engine:

Loads model + vocoder
Handles streaming inference
Manages chunking strategy
🔹 2. AudioFileWriterThread
Separate thread for file writing
Prevents blocking streaming
Writes chunks asynchronously
🔹 3. Socket Server

Listens on:

0.0.0.0:9998
Handles multiple clients sequentially
⚙️ Workflow
🔹 1. Server Start
python socket_server.py --model F5TTS_Base
🔹 2. Client Connection
Accepts socket connection
Receives text
🔹 3. Text Processing

Splits text:

chunk_text(text, max_chars)
Special handling for first chunk → lower latency
🔹 4. Streaming Inference
infer_batch_process(..., streaming=True)
Generates audio chunks progressively
🔹 5. Send + Save

For each chunk:

Send to client:

conn.sendall(...)

Save asynchronously:

file_writer_thread.add_chunk(...)
🔹 6. End Signal
conn.sendall(b"END")
⚡ Special Optimizations
🔥 1. Dynamic Chunking Strategy
First chunk → very small
Later chunks → larger
👉 Faster initial response
🔥 2. Warm-up Phase
Runs dummy inference at startup
👉 Reduces first-request latency
🔥 3. Non-blocking File Writing
Uses thread + queue
👉 Streaming unaffected
📂 Output

Audio files saved to:

data/out/tts_output_<timestamp>.wav
⚙️ Configurable Parameters
Parameter	Purpose
model	F5TTS model
ckpt_file	checkpoint
ref_audio	reference voice
ref_text	transcript
device	CPU/GPU
dtype	precision
⚠️ Requirements
torch, torchaudio
f5_tts modules
numpy
socket, threading
⚖️ Pros & Cons
✅ Pros
Real-time streaming (low latency)
Simultaneous file saving
Efficient chunk-based inference
Optimized first response
❌ Cons
Single-threaded client handling
TCP-based (not web-friendly)
Complex debugging
No authentication/security
🧩 Final System Architecture (Complete 🚀)

Now your full system looks like:

          ┌──────────────┐
          │   CLI / UI   │
          └──────┬───────┘
                 │
        ┌────────▼────────┐
        │ Streaming Client │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Socket Server    │  ← (THIS FILE)
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ TTSStreamingProc │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │  F5TTS Model     │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Audio Chunks     │
        └────────┬────────┘
                 │
     ┌───────────▼───────────┐
     │ Client Playback + Save │
     └───────────────────────┘

---

## f5_tts/train/train_all_files.md

# Training

Check your FFmpeg installation:
```bash
ffmpeg -version
```
If not found, install it first (or skip assuming you know of other backends available).

## Prepare Dataset

Example data processing scripts, and you may tailor your own one along with a Dataset class in `src/f5_tts/model/dataset.py`.

### 1. Some specific Datasets preparing scripts
Download corresponding dataset first, and fill in the path in scripts.

```bash
# Prepare the Emilia dataset
python src/f5_tts/train/datasets/prepare_emilia.py

# Prepare the Wenetspeech4TTS dataset
python src/f5_tts/train/datasets/prepare_wenetspeech4tts.py

# Prepare the LibriTTS dataset
python src/f5_tts/train/datasets/prepare_libritts.py

# Prepare the LJSpeech dataset
python src/f5_tts/train/datasets/prepare_ljspeech.py
```

### 2. Create custom dataset with metadata.csv
Use guidance see [#57 here](https://github.com/SWivid/F5-TTS/discussions/57#discussioncomment-10959029).

```bash
python src/f5_tts/train/datasets/prepare_csv_wavs.py
```

## Training & Finetuning

Once your datasets are prepared, you can start the training process.

### 1. Training script used for pretrained model

```bash
# setup accelerate config, e.g. use multi-gpu ddp, fp16
# will be to: ~/.cache/huggingface/accelerate/default_config.yaml     
accelerate config

# .yaml files are under src/f5_tts/configs directory
accelerate launch src/f5_tts/train/train.py --config-name F5TTS_v1_Base.yaml

# possible to overwrite accelerate and hydra config
accelerate launch --mixed_precision=fp16 src/f5_tts/train/train.py --config-name F5TTS_v1_Base.yaml ++datasets.batch_size_per_gpu=19200
```

### 2. Finetuning practice
Discussion board for Finetuning [#57](https://github.com/SWivid/F5-TTS/discussions/57).

Gradio UI training/finetuning with `src/f5_tts/train/finetune_gradio.py` see [#143](https://github.com/SWivid/F5-TTS/discussions/143).

If want to finetune with a variant version e.g. *F5TTS_v1_Base_no_zero_init*, manually download pretrained checkpoint from model weight repository and fill in the path correspondingly on web interface.

If use tensorboard as logger, install it first with `pip install tensorboard`.

<ins>The `use_ema = True` might be harmful for early-stage finetuned checkpoints</ins> (which goes just few updates, thus ema weights still dominated by pretrained ones), try turn it off with finetune gradio option or `load_model(..., use_ema=False)`, see if offer better results.

### 3. W&B Logging

The `wandb/` dir will be created under path you run training/finetuning scripts.

By default, the training script does NOT use logging (assuming you didn't manually log in using `wandb login`).

To turn on wandb logging, you can either:

1. Manually login with `wandb login`: Learn more [here](https://docs.wandb.ai/ref/cli/wandb-login)
2. Automatically login programmatically by setting an environment variable: Get an API KEY at https://wandb.ai/authorize and set the environment variable as follows:

On Mac & Linux:

```
export WANDB_API_KEY=<YOUR WANDB API KEY>
```

On Windows:

```
set WANDB_API_KEY=<YOUR WANDB API KEY>
```
Moreover, if you couldn't access W&B and want to log metrics offline, you can set the environment variable as follows:

```
export WANDB_MODE=offline
```


---

## f5_tts/eval/ecapa_tdnn.md



---

## f5_tts/eval/eval_all_files.md


# Evaluation

Install packages for evaluation:

```bash
pip install -e .[eval]
```

## Generating Samples for Evaluation

### Prepare Test Datasets

1. *Seed-TTS testset*: Download from [seed-tts-eval](https://github.com/BytedanceSpeech/seed-tts-eval).
2. *LibriSpeech test-clean*: Download from [OpenSLR](http://www.openslr.org/12/).
3. Unzip the downloaded datasets and place them in the `data/` directory.
4. Update the path for *LibriSpeech test-clean* data in `src/f5_tts/eval/eval_infer_batch.py`
5. Our filtered LibriSpeech-PC 4-10s subset: `data/librispeech_pc_test_clean_cross_sentence.lst`

### Batch Inference for Test Set

To run batch inference for evaluations, execute the following commands:

```bash
# batch inference for evaluations
accelerate config  # if not set before
bash src/f5_tts/eval/eval_infer_batch.sh
```

## Objective Evaluation on Generated Results

### Download Evaluation Model Checkpoints

1. Chinese ASR Model: [Paraformer-zh](https://huggingface.co/funasr/paraformer-zh)
2. English ASR Model: [Faster-Whisper](https://huggingface.co/Systran/faster-whisper-large-v3)
3. WavLM Model: Download from [Google Drive](https://drive.google.com/file/d/1-aE1NfzpRCLxA4GUxX9ITI3F9LlbtEGP/view).

Then update in the following scripts with the paths you put evaluation model ckpts to.

### Objective Evaluation

Update the path with your batch-inferenced results, and carry out WER / SIM / UTMOS evaluations:
```bash
# Evaluation [WER] for Seed-TTS test [ZH] set
python src/f5_tts/eval/eval_seedtts_testset.py --eval_task wer --lang zh --gen_wav_dir <GEN_WAV_DIR> --gpu_nums 8

# Evaluation [SIM] for LibriSpeech-PC test-clean (cross-sentence)
python src/f5_tts/eval/eval_librispeech_test_clean.py --eval_task sim --gen_wav_dir <GEN_WAV_DIR> --librispeech_test_clean_path <TEST_CLEAN_PATH>

# Evaluation [UTMOS]. --ext: Audio extension
python src/f5_tts/eval/eval_utmos.py --audio_dir <WAV_DIR> --ext wav
```


---

## f5_tts/eval/eval_infer_batch.md



---

## f5_tts/eval/eval_librispeech_test_clean.md



---

## f5_tts/eval/eval_seedtts_testset.md



---

## f5_tts/eval/eval_utmos.md



---

## f5_tts/eval/utils_eval.md



---

## f5_tts/scripts/count_max_epoch.md

📄 Adaptive Batch Size Calculator – Quick README

This script computes training configuration parameters for large-scale TTS (or audio) models using an adaptive batch size strategy based on frames instead of samples.

🚀 What it does
Estimates:
Number of epochs
Updates per epoch
Steps per epoch
Uses:
Dataset size (in hours)
Audio frame settings
GPU configuration
🧠 Key Idea

👉 Instead of fixed batch size (samples), this uses:

Frames-based batching (grouping sampler)

✔️ Minimizes padding
✔️ Improves GPU utilization
✔️ More efficient for variable-length audio

⚙️ Inputs
🔹 Dataset
total_hours = 95282 → total audio dataset size
🔹 Audio Parameters
mel_hop_length = 256
mel_sampling_rate = 24000

👉 Used to convert frames → seconds → hours

🔹 Training Target
wanted_max_updates = 1,000,000
🔹 Hardware Setup
gpus = 8
frames_per_gpu = 38400
grad_accum = 1
⚙️ Calculations
🔹 1. Mini-batch Size (Frames)
mini_batch_frames = frames_per_gpu × gpus × grad_accum
🔹 2. Convert Frames → Hours
mini_batch_hours = (frames × hop_length) / sampling_rate / 3600
🔹 3. Updates per Epoch
updates_per_epoch = total_hours / mini_batch_hours
🔹 4. Steps per Epoch
steps_per_epoch = updates_per_epoch × grad_accum
🔹 5. Required Epochs
epochs = wanted_max_updates / updates_per_epoch
📊 Output

The script prints:

Recommended number of epochs
Progress bar scale:
updates
steps
Batch size in:
frames
hours
🧩 Example Interpretation
Large dataset (~95K hours)
Huge effective batch size
Very few epochs needed

👉 Because:

Each batch already covers significant data
⚖️ Pros & Cons
✅ Pros
Efficient GPU usage
Less padding overhead
Scales well for large datasets
More stable training
❌ Cons
Harder to reason vs standard batch size
Requires careful tuning
Less intuitive for beginners


---

## f5_tts/scripts/count_params_gflops.md

📄 TTS Model FLOPs & Parameters Profiler – Quick README

This script is used to analyze the computational complexity of your TTS model by calculating:

FLOPs (Floating Point Operations)
Number of parameters
🚀 What it does
Builds a TTS model architecture (CFM + Transformer)
Simulates input data
Uses thop to compute:
FLOPs → computation cost
Parameters → model size
🧠 Key Idea

👉 Before training or deploying a model, you want to know:

How heavy is this model?
Can my GPU handle it?
Is it efficient enough?
⚙️ Model Architecture
🔹 Core Model
model = CFM(transformer=transformer)
CFM → main TTS framework
transformer → backbone (DiT here)
🔹 Transformer Used
DiT(dim=1024, depth=22, heads=16, ff_mult=2, ...)

👉 This is a large model (~335M parameters)

⚙️ Input Simulation
🔹 Audio Input
torch.randn(1, frame_length, n_mel_channels)
Simulates mel spectrogram
🔹 Text Input
torch.zeros(1, text_length)
Simulates tokenized text
⚙️ Key Parameters
Parameter	Meaning
duration = 20	seconds of audio
sample_rate = 24000	audio frequency
hop_length = 256	frame step
frame_length	computed audio frames
text_length = 150	token length
⚙️ FLOPs Calculation
flops, params = thop.profile(model, inputs=(...))
📊 Output

Example:

FLOPs: 363.4 G
Params: 335.8 M
🧩 Interpretation
🔹 FLOPs (~363 GFLOPs)
High compute cost
Slower inference/training
🔹 Params (~335M)
Large memory requirement
High capacity model

---

## f5_tts/model/cfm.md

📄 CFM (Conditional Flow Matching) Model – Quick README

This file implements the core generative model used in your TTS system, based on Conditional Flow Matching (CFM) — a modern approach for generating audio from text + reference speech.

📌 File reference:

🚀 What it does
Trains a model to transform noise → speech
Uses:
Reference audio (conditioning)
Text input
Supports:
Training (forward)
Inference (sample)
🧠 Key Idea

👉 Instead of directly generating audio:

Noise → Gradually transformed → Speech

Using:
👉 Neural ODE (continuous transformation over time)

⚙️ Core Components
🔹 1. CFM Class

Main model wrapper:

Handles:
Training logic
Sampling (generation)
Uses:
Transformer backbone (e.g., DiT)
🔹 2. Mel Spectrogram Module

Converts:

Raw audio → Mel spectrogram
Used as model input
🔹 3. Transformer

Predicts flow direction:

How to move noise → real audio
⚙️ Training (forward())
🔹 Steps:
Convert audio → mel

Sample:

x0 = noise
x1 = real audio

Interpolate:

φ_t = (1−t)x0 + t x1

Model predicts:

flow = x1 − x0

Compute loss:

MSE(predicted_flow, actual_flow)
🔥 Special Techniques
Random span masking
Model learns to fill missing parts
Classifier-Free Guidance (CFG)
Drops conditioning randomly
Conditional dropout
Improves generalization
⚙️ Inference (sample())
🔹 Steps:
Start from random noise

Define time steps:

t ∈ [0 → 1]

Solve ODE:

odeint(fn, y0, t)
Generate final audio
🔥 Advanced Features
Feature	Purpose
cfg_strength	control quality vs diversity
steps	number of ODE steps
sway_sampling_coef	modify time schedule
no_ref_audio	unconditional generation
edit_mask	partial editing
🧠 Key Concept: Neural ODE

👉 Instead of discrete steps:

x₀ → x₁ → x₂ → ...

👉 Continuous transformation:

dx/dt = f(x, t)
📂 Inputs / Outputs
Input:
cond → reference audio
text → tokenized text
Output:
Generated mel / waveform

---

## f5_tts/model/dataset.md

📄 TTS Dataset & Dynamic Batching Module – Quick README

This file handles data loading, preprocessing, and batching for training your TTS model. It is responsible for converting raw audio + text into model-ready inputs.

📌 File reference:

🚀 What it does
Loads datasets (custom / Hugging Face)
Converts audio → mel spectrograms
Filters invalid samples
Implements dynamic batching (frame-based)
Prepares padded batches for training
🧠 Key Idea

👉 Instead of fixed batch size:

Batch = fixed number of samples ❌

👉 This uses:

Batch = fixed number of audio frames ✅

✔️ Efficient for variable-length audio
✔️ Reduces padding waste
✔️ Prevents GPU OOM

⚙️ Core Components
🔹 1. HFDataset
Loads Hugging Face datasets

Converts:

audio → mel spectrogram
Handles:
resampling
duration filtering (0.3s–30s)
🔹 2. CustomDataset
Loads local datasets
Supports:
raw audio OR preprocessed mel
Handles:
path fixes
resampling
mono conversion
🔹 3. DynamicBatchSampler (🔥 Important)
DynamicBatchSampler(...)

👉 Groups samples based on total frames per batch

How it works:
Sort samples by length

Accumulate samples until:

total_frames ≤ threshold
Create batch
🔹 Benefits
Minimal padding
Balanced GPU usage
Faster training
⚙️ Dataset Loader
🔹 load_dataset()

Supports:

CustomDataset
CustomDatasetPath
HFDataset

Also loads:

duration.json → used for batching
⚙️ Collation Function
🔹 collate_fn()

Handles:

Padding mel spectrograms
Preparing:
mel
mel_lengths
text
text_lengths
🧩 Data Flow
Raw Audio + Text
        ↓
Dataset Loader
        ↓
Mel Spectrogram
        ↓
Dynamic Batch Sampler
        ↓
Collate Function
        ↓
Model Input
⚠️ Requirements
torch, torchaudio
datasets (Hugging Face)
Preprocessed dataset files:
.arrow
duration.json

---

## f5_tts/model/modules.md

📄 TTS Model Building Blocks (Modules) – Quick README

This file contains the core neural network components used to build your TTS model (CFM + DiT). It defines everything from mel spectrogram extraction to attention layers and transformer blocks.

📌 File reference:

🚀 What it does
Converts raw audio → mel spectrogram
Defines positional embeddings
Implements:
Attention mechanisms
Transformer blocks (DiT, MMDiT)
Provides building blocks for the full TTS model
🧠 Key Idea

👉 This file is like:

“LEGO pieces of your TTS model”

👉 Other files (like CFM, DiT) use these components to build the full model

⚙️ Core Components
🔊 1. Mel Spectrogram (MelSpec)

Converts:

Raw waveform → Mel spectrogram
Supports:
vocos (torchaudio-based)
bigvgan (custom optimized)

👉 This is the input representation for the model

📍 2. Positional Embeddings
🔹 Sinusoidal
Standard transformer positional encoding
🔹 Convolutional
Uses Conv1D for local positional awareness
🔹 Rotary (RoPE)
Advanced embedding for long sequences
🧠 3. Attention Mechanisms
🔹 Attention
Multi-head self-attention
🔹 AttnProcessor
Standard attention
🔹 JointAttnProcessor (🔥 Important)

Combines:

Audio + Text attention

👉 Enables multimodal learning

⚡ 4. Transformer Blocks
🔹 DiTBlock
Diffusion-style transformer block
Uses:
attention
feedforward
🔹 MMDiTBlock (🔥 Advanced)
Multi-modal transformer
Processes:
audio + text together
🧩 5. Normalization Layers
🔹 AdaLayerNormZero
Adaptive normalization using time embedding
🔹 GRN (Global Response Norm)
Stabilizes training
🔥 6. ConvNeXt Block
Modern convolution block
Captures local patterns
⏱️ 7. Time Embedding
🔹 TimestepEmbedding

Encodes:

time step (for diffusion / flow models)
🧩 Data Flow (Inside Model)
Raw Audio → MelSpec
        ↓
Add Positional Embeddings
        ↓
Transformer Blocks (DiT / MMDiT)
        ↓
Attention (Audio + Text)
        ↓
Output Representation
⚠️ Requirements
torch, torchaudio
librosa
x_transformers

---

## f5_tts/model/trainer.md

TTS Training Engine (Trainer) – Quick README

This file implements the full training pipeline for your TTS model (CFM), including:

Data loading
Optimization
Distributed training
Logging & checkpointing

📌 File reference:

🚀 What it does
Trains the CFM model end-to-end
Supports:
Multi-GPU training (via accelerate)
Dynamic batching
Logging (WandB / TensorBoard)
Checkpointing + resume
🧠 Key Idea

👉 This is the “training controller” of your entire system:

Dataset → DataLoader → Model → Loss → Optimizer → Update → Repeat
⚙️ Core Components
🔹 1. Accelerator (Multi-GPU Training)

Uses:

Accelerator(...)
Handles:
Distributed training
Gradient accumulation
Device management
🔹 2. Optimizer

Default:

AdamW
Optional:
bitsandbytes (8-bit optimizer → memory efficient)
🔹 3. EMA (Exponential Moving Average)
Maintains a smoothed version of model weights
Improves inference quality
🔹 4. Scheduler
Warmup → Decay
Warmup: gradually increase LR
Decay: reduce LR over time
⚙️ Training Flow
🔹 1. Load Dataset
Supports:
sample-based batching
frame-based batching (DynamicBatchSampler)
🔹 2. Forward Pass
loss, cond, pred = model(...)
🔹 3. Backpropagation
accelerator.backward(loss)
🔹 4. Optimization
Gradient clipping
Optimizer step
Scheduler step
🔹 5. EMA Update
ema_model.update()
🔹 6. Logging
Logs:
loss
learning rate
Tools:
WandB
TensorBoard
🔹 7. Checkpointing
Saves:
model weights
optimizer state
scheduler state
🔹 8. Sample Generation (Optional 🔥)
Generates audio during training

Saves:

step_X_gen.wav
step_X_ref.wav
⚙️ Special Features
🔥 1. Dynamic Batching Support
Works with your earlier sampler
👉 efficient GPU usage
🔥 2. Resume Training
Loads last checkpoint automatically
🔥 3. Multi-GPU Scaling
Automatically adjusts:
batch size
warmup steps
🔥 4. Memory Debugging
torch.cuda.memory_allocated()
📂 Outputs

Checkpoints:

ckpts/

Sample audio:

ckpts/.../samples/
⚠️ Requirements
torch, torchaudio
accelerate
wandb (optional)
ema_pytorch

---

## f5_tts/model/utils.md

TTS Utility & Tokenization Module – Quick README

This file provides helper functions for preprocessing, tokenization, masking, and reproducibility in your TTS pipeline.

📌 File reference:

🚀 What it does
Handles text → token conversion
Provides masking utilities for training
Supports Chinese → pinyin conversion
Ensures reproducibility (seed control)
Includes data cleaning utilities
🧠 Key Idea

👉 This file acts as:

“Support system for model + dataset pipeline”

It doesn’t train or infer — it prepares and cleans data properly

⚙️ Core Components
🔹 1. Reproducibility
seed_everything()
Fixes randomness across:
Python
PyTorch
CUDA

👉 Ensures same results every run

🔹 2. Helper Functions
exists() → checks if value exists
default() → fallback value

👉 Clean code utilities

🔹 3. Masking Utilities (🔥 Important)
lens_to_mask()
Converts sequence lengths → masks
mask_from_frac_lengths()
Creates random span masks
👉 Used in training (CFM infilling)
🔹 4. Tokenization
🧩 Byte-level Tokenizer
list_str_to_tensor()
Converts text → UTF-8 byte tokens
🔤 Character Tokenizer
list_str_to_idx()
Uses custom vocab mapping
⚙️ get_tokenizer()
Loads vocab file
Supports:
"pinyin"
"char"
"byte"
"custom"
🔹 5. Chinese → Pinyin Conversion (🔥 Advanced)
convert_char_to_pinyin()
Uses:
jieba → word segmentation
pypinyin → phonetic conversion

👉 Converts:

中文 → zhong1 wen2

✔️ Improves pronunciation
✔️ Handles polyphonic characters

🔹 6. Data Cleaning
repetition_found()
Detects repeated patterns in text
Helps filter noisy / corrupted data
🧩 Data Flow Role
Raw Text
   ↓
Tokenization (char / byte / pinyin)
   ↓
Masking (for training)
   ↓
Model Input
⚠️ Requirements
torch
jieba
pypinyin

---

## f5_tts/model/backbones/backbone_all_files.md

## Backbones quick introduction


### unett.py
- flat unet transformer
- structure same as in e2-tts & voicebox paper except using rotary pos emb
- update: allow possible abs pos emb & convnextv2 blocks for embedded text before concat

### dit.py
- adaln-zero dit
- embedded timestep as condition
- concatted noised_input + masked_cond + embedded_text, linear proj in
- possible abs pos emb & convnextv2 blocks for embedded text before concat
- possible long skip connection (first layer to last layer)

### mmdit.py
- sd3 structure
- timestep as condition
- left stream: text embedded and applied a abs pos emb
- right stream: masked_cond & noised_input concatted and with same conv pos emb as unett


---

## f5_tts/infer/inference_all_files.md

# Inference

The pretrained model checkpoints can be reached at [🤗 Hugging Face](https://huggingface.co/SWivid/F5-TTS) and [🤖 Model Scope](https://www.modelscope.cn/models/SWivid/F5-TTS_Emilia-ZH-EN), or will be automatically downloaded when running inference scripts.

**More checkpoints with whole community efforts can be found in [SHARED.md](SHARED.md), supporting more languages.**

Currently support **30s for a single** generation, which is the **total length** (same logic if `fix_duration`) including both prompt and output audio. However, `infer_cli` and `infer_gradio` will automatically do chunk generation for longer text. Long reference audio will be **clip short to ~12s**.

To avoid possible inference failures, make sure you have seen through the following instructions.

- Use reference audio <12s and leave proper silence space (e.g. 1s) at the end. Otherwise there is a risk of truncating in the middle of word, leading to suboptimal generation.
- <ins>Uppercased letters</ins> (best with form like K.F.C.) will be uttered letter by letter, and lowercased letters used for common words. 
- Add some spaces (blank: " ") or punctuations (e.g. "," ".") <ins>to explicitly introduce some pauses</ins>.
- If English punctuation marks the end of a sentence, make sure there is a space " " after it. Otherwise not regarded as when chunk.
- <ins>Preprocess numbers</ins> to Chinese letters if you want to have them read in Chinese, otherwise in English.
- If the generation output is blank (pure silence), <ins>check for FFmpeg installation</ins>.
- Try <ins>turn off `use_ema` if using an early-stage</ins> finetuned checkpoint (which goes just few updates).


## Gradio App

Currently supported features:

- Basic TTS with Chunk Inference
- Multi-Style / Multi-Speaker Generation
- Voice Chat powered by Qwen2.5-3B-Instruct
- [Custom inference with more language support](SHARED.md)

The cli command `f5-tts_infer-gradio` equals to `python src/f5_tts/infer/infer_gradio.py`, which launches a Gradio APP (web interface) for inference.

The script will load model checkpoints from Huggingface. You can also manually download files and update the path to `load_model()` in `infer_gradio.py`. Currently only load TTS models first, will load ASR model to do transcription if `ref_text` not provided, will load LLM model if use Voice Chat.

More flags options:

```bash
# Automatically launch the interface in the default web browser
f5-tts_infer-gradio --inbrowser

# Set the root path of the application, if it's not served from the root ("/") of the domain
# For example, if the application is served at "https://example.com/myapp"
f5-tts_infer-gradio --root_path "/myapp"
```

Could also be used as a component for larger application:
```python
import gradio as gr
from f5_tts.infer.infer_gradio import app

with gr.Blocks() as main_app:
    gr.Markdown("# This is an example of using F5-TTS within a bigger Gradio app")

    # ... other Gradio components

    app.render()

main_app.launch()
```


## CLI Inference

The cli command `f5-tts_infer-cli` equals to `python src/f5_tts/infer/infer_cli.py`, which is a command line tool for inference.

The script will load model checkpoints from Huggingface. You can also manually download files and use `--ckpt_file` to specify the model you want to load, or directly update in `infer_cli.py`.

For change vocab.txt use `--vocab_file` to provide your `vocab.txt` file.

Basically you can inference with flags:
```bash
# Leave --ref_text "" will have ASR model transcribe (extra GPU memory usage)
f5-tts_infer-cli \
--model F5TTS_v1_Base \
--ref_audio "ref_audio.wav" \
--ref_text "The content, subtitle or transcription of reference audio." \
--gen_text "Some text you want TTS model generate for you."

# Use BigVGAN as vocoder. Currently only support F5TTS_Base. 
f5-tts_infer-cli --model F5TTS_Base --vocoder_name bigvgan --load_vocoder_from_local

# Use custom path checkpoint, e.g.
f5-tts_infer-cli --ckpt_file ckpts/F5TTS_v1_Base/model_1250000.safetensors

# More instructions
f5-tts_infer-cli --help
```

And a `.toml` file would help with more flexible usage.

```bash
f5-tts_infer-cli -c custom.toml
```

For example, you can use `.toml` to pass in variables, refer to `src/f5_tts/infer/examples/basic/basic.toml`:

```toml
# F5TTS_v1_Base | E2TTS_Base
model = "F5TTS_v1_Base"
ref_audio = "infer/examples/basic/basic_ref_en.wav"
# If an empty "", transcribes the reference audio automatically.
ref_text = "Some call me nature, others call me mother nature."
gen_text = "I don't really care what you call me. I've been a silent spectator, watching species evolve, empires rise and fall. But always remember, I am mighty and enduring."
# File with text to generate. Ignores the text above.
gen_file = ""
remove_silence = false
output_dir = "tests"
```

You can also leverage `.toml` file to do multi-style generation, refer to `src/f5_tts/infer/examples/multi/story.toml`.

```toml
# F5TTS_v1_Base | E2TTS_Base
model = "F5TTS_v1_Base"
ref_audio = "infer/examples/multi/main.flac"
# If an empty "", transcribes the reference audio automatically.
ref_text = ""
gen_text = ""
# File with text to generate. Ignores the text above.
gen_file = "infer/examples/multi/story.txt"
remove_silence = true
output_dir = "tests"

[voices.town]
ref_audio = "infer/examples/multi/town.flac"
ref_text = ""

[voices.country]
ref_audio = "infer/examples/multi/country.flac"
ref_text = ""
```
You should mark the voice with `[main]` `[town]` `[country]` whenever you want to change voice, refer to `src/f5_tts/infer/examples/multi/story.txt`.

## API Usage

```python
from importlib.resources import files
from f5_tts.api import F5TTS

f5tts = F5TTS()
wav, sr, spec = f5tts.infer(
    ref_file=str(files("f5_tts").joinpath("infer/examples/basic/basic_ref_en.wav")),
    ref_text="some call me nature, others call me mother nature.",
    gen_text="""I don't really care what you call me. I've been a silent spectator, watching species evolve, empires rise and fall. But always remember, I am mighty and enduring. Respect me and I'll nurture you; ignore me and you shall face the consequences.""",
    file_wave=str(files("f5_tts").joinpath("../../tests/api_out.wav")),
    file_spec=str(files("f5_tts").joinpath("../../tests/api_out.png")),
    seed=None,
)
```
Check [api.py](../api.py) for more details.

## TensorRT-LLM Deployment

See [detailed instructions](../runtime/triton_trtllm/README.md) for more information.

## Socket Real-time Service

Real-time voice output with chunk stream:

```bash
# Start socket server
python src/f5_tts/socket_server.py

# If PyAudio not installed
sudo apt-get install portaudio19-dev
pip install pyaudio

# Communicate with socket client
python src/f5_tts/socket_client.py
```

## Speech Editing

To test speech editing capabilities, use the following command:

```bash
python src/f5_tts/infer/speech_edit.py
```


