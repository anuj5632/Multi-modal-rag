def format_timestamp(seconds: float) -> str:
    """Converts seconds to mm:ss (or hh:mm:ss for long durations) format."""

    seconds = int(seconds)
    hours,remainder = divmod(seconds,3600)
    minutes,secs = divmod(remainder,60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def create_audio_chunks(segments,max_chars = 800,max_duration = 45.0):
    
    """
    Merges consecutive Whisper segments into larger chunks so retrieval
    operates on meaningful spans of conversation rather than single
    sentences. A chunk closes once it exceeds max_chars OR max_duration,
    whichever comes first (mirrors the role RecursiveCharacterTextSplitter
    plays for PDF text chunks, but time-aware).

    Each returned chunk keeps its start/end timestamps so answers can cite
    "at 04:12" the same way PDF answers cite "page 7".

    """

    chunks = []

    current_text = []
    current_start = None
    current_end = None
    current_len = 0

    def flush():
        if current_text:
            chunks.append({
                "start":current_start,
                "end":current_end,
                "text":" ".join(current_text),
            })

    
    def _duration(seg):
        return seg["end"] - seg["start"]
    
    def _max_duration(seg1,seg2):
        return max(_duration(seg1),_duration(seg2))

    for seg in segments:
        if current_start is None:
            current_start = seg["start"]
        
        would_be_duration = seg["end"] - current_start
        would_be_len = current_len + len(seg["text"])+1 # +1 for space

        if current_text and (would_be_len > max_chars or would_be_duration > max_duration):
            flush()
            current_text = []
            current_start = seg["start"]
            current_len = 0

        current_text.append(seg["text"])
        current_end = seg["end"]
        current_len += len(seg["text"])+1 # +1 for space

    flush()

    for index, xhunk in enumerate(chunks):
        chunk["chunk_index"] = index+1

    return chunks