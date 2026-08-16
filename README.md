# AI Meeting Summarizer (Local: Ollama + whisper.cpp)

## Overview

This is a fully local, offline-capable meeting summarizer. It converts
audio recordings of meetings into transcripts using `whisper.cpp`, then
summarizes them using a locally-running LLM served by `Ollama`. No API
keys, no billing, no data leaves your machine.

## How It Works

### Workflow

1. **Input**: Upload an audio recording of a meeting (`.wav`, `.mp3`, etc.).
2. **Preprocessing**: FFmpeg converts the audio to 16kHz mono WAV, the format `whisper.cpp` expects.
3. **Transcription**: `whisper.cpp` (compiled locally, via `whisper-cli.exe` on Windows) converts the audio to text using a selected Whisper model size.
4. **Summarization**: The transcript is sent to a locally-running Ollama model, which returns a summary.
5. **User Interface**: Gradio provides the web interface for uploading audio, selecting models, and viewing results.

### Benefits

- **Fully local**: transcription and summarization both run on your own machine — no data sent to any external API.
- **No billing**: no API keys, no usage costs, ever.
- **Model choice**: pick from `base`, `small`, `medium`, or `large-v3` Whisper models, and any model you have pulled into Ollama.

## Requirements

- Python 3.x
- [FFmpeg](https://www.ffmpeg.org/) (for audio preprocessing)
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) (compiled from source — see setup docs in this repo)
- [Ollama](https://ollama.com/) (running locally with at least one model pulled)
- [Gradio](https://www.gradio.app/) (for the web interface)
- [Requests](https://requests.readthedocs.io/) (for calling the Ollama API)

## Pre-Installation

Before running the app, make sure Ollama is installed and running with a model pulled:
```bash
ollama run llama3.2
```
Leave Ollama running in the background (or as a service) while using the app.

You'll also need `whisper.cpp` compiled locally. See `Installation_setup.md` in
this repo for a full step-by-step Windows setup (CMake, Visual Studio Build
Tools, compiling the binary, downloading models).

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/jeevitha-a-22/ai-meeting-notes-summarizer.git
cd ai-meeting-notes-summarizer
```

### Step 2: Set Up a Virtual Environment and Install Dependencies
```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Step 3: Set the Whisper Binary Path (Windows)
```powershell
$env:WHISPER_BINARY = ".\whisper.cpp\build\bin\Release\whisper-cli.exe"
```
(Set this in every new terminal window before running the app — it doesn't persist automatically.)

### Step 4: Run the Application
```bash
python main.py
```

### Step 5: Accessing the Application
Gradio will open automatically in your browser, typically at `http://127.0.0.1:7860`.

## Usage

1. **Upload an Audio File** — any common audio format (`.wav`, `.mp3`, etc.)
2. **Provide Context (Optional)** — e.g. "Weekly product sync"
3. **Select a Whisper Model** — `base`, `small`, `medium`, or `large-v3`. If not already downloaded, it's fetched automatically on first use.
4. **Select a Summarization Model** — any model currently pulled into your local Ollama server
5. **View Results** — get a summary in the interface, and download the full transcript as a text file

## License

This project is licensed under the MIT License.

