import subprocess
import os
import gradio as gr
import requests
import json

OLLAMA_SERVER_URL = "http://localhost:11434"  # Replace this with your actual Ollama server URL if different
WHISPER_MODEL_DIR = "./whisper.cpp/models"  # Directory where whisper models are stored


def get_available_models() -> list[str]:
    """
    Retrieves a list of all available models from the Ollama server and extracts the model names.

    Returns:
        A list of model names available on the Ollama server.
    """
    response = requests.get(f"{OLLAMA_SERVER_URL}/api/tags")
    if response.status_code == 200:
        models = response.json()["models"]
        llm_model_names = [model["model"] for model in models]  # Extract model names
        return llm_model_names
    else:
        raise Exception(
            f"Failed to retrieve models from Ollama server: {response.text}"
        )


WHISPER_MODEL_CHOICES = ["base", "small", "medium", "large-v3"]


def get_available_whisper_models() -> list[str]:
    """
    Returns the fixed list of standard Whisper model sizes offered in the UI.
    Any model not yet downloaded gets fetched automatically the first time
    it's selected (see ensure_whisper_model_downloaded), so the dropdown
    doesn't need to scan the models folder to decide what to show.
    """
    return WHISPER_MODEL_CHOICES


def ensure_whisper_model_downloaded(whisper_model_name: str) -> None:
    """
    Downloads the requested ggml Whisper model into WHISPER_MODEL_DIR if it
    isn't already present on disk. Lets the user pick base/small/medium/large
    from the dropdown without having to manually download each one first.
    """
    os.makedirs(WHISPER_MODEL_DIR, exist_ok=True)
    model_path = os.path.join(WHISPER_MODEL_DIR, f"ggml-{whisper_model_name}.bin")
    if os.path.exists(model_path):
        return

    url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{whisper_model_name}.bin"
    print(f"Downloading Whisper model '{whisper_model_name}' (first use only)...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded {model_path}")


def summarize_with_model(llm_model_name: str, context: str, text: str) -> str:
    """
    Uses a specified model on the Ollama server to generate a summary.
    Handles streaming responses by processing each line of the response.
    """
    prompt = f"""You are given a transcript from a meeting, along with some optional context.

    Context: {context if context else 'No additional context provided.'}

    The transcript is as follows:

    {text}

    Please summarize the transcript."""

    headers = {"Content-Type": "application/json"}
    data = {"model": llm_model_name, "prompt": prompt}

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate", json=data, headers=headers, stream=True
    )

    if response.status_code == 200:
        full_response = ""
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    full_response += json_line.get("response", "")
                    if json_line.get("done", False):
                        break
            return full_response
        except json.JSONDecodeError:
            print("Error: Response contains invalid JSON data.")
            return f"Failed to parse the response from the server. Raw response: {response.text}"
    else:
        raise Exception(
            f"Failed to summarize with model {llm_model_name}: {response.text}"
        )


def preprocess_audio_file(audio_file_path: str) -> str:
    """
    Converts the input audio file to a WAV format with 16kHz sample rate and mono channel.
    """
    output_wav_file = f"{os.path.splitext(audio_file_path)[0]}_converted.wav"

    cmd = f'ffmpeg -y -i "{audio_file_path}" -ar 16000 -ac 1 "{output_wav_file}"'
    subprocess.run(cmd, shell=True, check=True)

    return output_wav_file


def translate_and_summarize(
    audio_file_path: str, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str]:
    """
    Translates the audio file into text using the whisper.cpp model and generates a
    summary using Ollama. Also provides the transcript file for download.
    """
    output_file = "output.txt"

    print("Processing audio file:", audio_file_path)

    audio_file_wav = preprocess_audio_file(audio_file_path)

    print("Audio preprocessed:", audio_file_wav)

    ensure_whisper_model_downloaded(whisper_model_name)

    # NOTE (Windows): newer whisper.cpp builds name the binary whisper-cli.exe
    # (older versions used main.exe), typically under
    # whisper.cpp/build/bin/Release/whisper-cli.exe after a CMake build.
    # Set the WHISPER_BINARY env var if your build output differs.
    whisper_binary = os.environ.get("WHISPER_BINARY", "./whisper.cpp/build/bin/Release/whisper-cli.exe")
    whisper_command = f'"{whisper_binary}" -m ./whisper.cpp/models/ggml-{whisper_model_name}.bin -f "{audio_file_wav}" > {output_file}'
    subprocess.run(whisper_command, shell=True, check=True)

    print("Whisper.cpp executed successfully")

    with open(output_file, "r") as f:
        transcript = f.read()

    transcript_file = "transcript.txt"
    with open(transcript_file, "w") as transcript_f:
        transcript_f.write(transcript)

    summary = summarize_with_model(llm_model_name, context, transcript)

    os.remove(audio_file_wav)
    os.remove(output_file)

    return summary, transcript_file


def gradio_app(
    audio, context: str, whisper_model_name: str, llm_model_name: str
) -> tuple[str, str]:
    return translate_and_summarize(audio, context, whisper_model_name, llm_model_name)


if __name__ == "__main__":
    ollama_models = get_available_models()
    whisper_models = get_available_whisper_models()

    iface = gr.Interface(
        fn=gradio_app,
        inputs=[
            gr.Audio(type="filepath", label="Upload an audio file"),
            gr.Textbox(
                label="Context (optional)",
                placeholder="Provide any additional context for the summary",
            ),
            gr.Dropdown(
                choices=whisper_models,
                label="Select a Whisper model for audio-to-text conversion",
                value="small",
                info="If not downloaded yet, it will be fetched automatically on first use.",
            ),
            gr.Dropdown(
                choices=ollama_models,
                label="Select a model for summarization",
                value=ollama_models[0] if ollama_models else None,
            ),
        ],
        outputs=[
            gr.Textbox(label="Summary"),
            gr.File(label="Download Transcript"),
        ],
        analytics_enabled=False,
        title="Meeting Summarizer",
        description="Upload an audio file of a meeting and get a summary of the key concepts discussed.",
    )

    iface.launch(debug=True, inbrowser=True)