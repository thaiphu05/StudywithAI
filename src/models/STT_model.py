from io import BytesIO


class STTModel:
    def __init__(self, model_size: str = "base") -> None:
        self.model_size = model_size
        self.model = None

    def load_model(self) -> None:
        from faster_whisper import WhisperModel

        self.model = WhisperModel(
            self.model_size,
            device="cpu",
            compute_type="int8",
        )

    def transcribe(self, audio_bytes: bytes) -> dict:
        import av
        import numpy as np

        container = av.open(BytesIO(audio_bytes))
        out_frames: list[np.ndarray] = []
        for frame in container.decode(audio=0):
            out_frames.append(frame.to_ndarray())
        audio = np.concatenate(out_frames, axis=1)
        audio = audio.mean(axis=0).astype(np.float32)

        segments, info = self.model.transcribe(audio, beam_size=5)

        text_parts: list[str] = []
        segment_list: list[dict] = []
        for seg in segments:
            text_parts.append(seg.text)
            segment_list.append({
                "start": seg.start,
                "end": seg.end,
                "text": seg.text.strip(),
            })

        return {
            "text": " ".join(text_parts).strip(),
            "segments": segment_list,
            "duration": info.duration,
            "language": info.language,
        }
