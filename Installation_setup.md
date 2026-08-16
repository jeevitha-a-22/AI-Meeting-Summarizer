# Installation Steps — Meeting Summarizer (Ollama + whisper.cpp)

## 1. Install Ollama
Download from [ollama.com/download](https://ollama.com/download) and run the installer.
```powershell
ollama run llama3.2
```

## 2. Install FFmpeg
```powershell
winget install ffmpeg
```

## 3. Install CMake and Build Tools
```powershell
winget install Kitware.CMake
```
Also install **Visual Studio Build Tools** with the **"Desktop development with C++"** workload:
[visualstudio.microsoft.com/downloads](https://visualstudio.microsoft.com/downloads/)

## 4. Clone and Build whisper.cpp
```powershell
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
cmake -B build
cmake --build build --config Release
```

## 5. Download a Whisper Model
```powershell
.\models\download-ggml-model.cmd small
```

## 6. Place whisper.cpp Inside Your Project Folder
```
AI Meeting Notes Summarizer/
├── main.py
├── requirements.txt
└── whisper.cpp/
```

## 7. Set the Whisper Binary Path
```powershell
cd "C:\Users\jeevitha\OneDrive\Desktop\AI Meeting Notes Summarizer"
$env:WHISPER_BINARY = ".\whisper.cpp\build\bin\Release\whisper-cli.exe"
```

## 8. Install Python Dependencies
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 9. Run
```powershell
python main.py
```
