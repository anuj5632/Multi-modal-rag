from faster_whisper import WhisperModel

MODEL_SIZE = "base"

_model = None

def _load_model():
    global _model
    if _model is None:
        print("Loading Whisper model...")
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        print("Whisper model loaded successfully")
    return _model

def transcribe_audio(audio_path:str):
    """
    Transcribes an audio file and returns (segments, language, duration).

    segments: list of {"start": float_seconds, "end": float_seconds, "text": str}
    language: detected language code, e.g. "en"
    duration: total audio duration in seconds
    """

    model = _load_model()
    
    segments_iter, info = model.transcribe(audio_path, beam_size = 5)

    segments = []

    for segment in segments_iter:
        text = segment.text.strip()
        if not text:
            continue

        segments.append({
            "start":segment.start,
            "end":segment.end,
            "text":text
        })
    return segments, info.language, info.duration