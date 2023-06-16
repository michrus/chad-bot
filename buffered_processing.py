"""
Records and processes audio, storing data in temporary files if
real time performance cannot be achieved.
"""
import sys
import queue
# from typing import Optional

import numpy as np
import sounddevice as sd
# import soundfile as sf
import whisper


def main():
    # audio_queue = queue.Queue()

    samplerate = 44100
    min_duration_to_process = 5
    blocksize = int(min_duration_to_process * samplerate)
    duration = 6
    channels = 1
    # recording: np.ndarray = sd.rec(
    #     int(duration * samplerate),
    #     samplerate=samplerate,
    #     channels=channels
    # )
    recording_buffer = RecordingBuffer()
    model = whisper.load_model("tiny")
    processing = True
    with sd.InputStream(samplerate=samplerate,
                        blocksize=blocksize,
                        channels=channels,
                        callback=recording_buffer,
                        finished_callback=recording_buffer.mark_finished):
        sd.sleep(duration * 1000)
        while recording_buffer.recording:
        # while recording_buffer.total_samples < duration * samplerate:
        # while processing:
            try:
                chunk: np.ndarray = recording_buffer.queue.get(block=False)
                chunk = chunk.reshape((-1,))
                # chunk = whisper.pad_or_trim(chunk)
                # mel = whisper.log_mel_spectrogram(chunk).to(model.device)
                # options = whisper.DecodingOptions(language="pl")
                # result = whisper.decode(model, mel, options)
                result = model.transcribe(chunk, language="pl")
                print(result)
                recording_buffer.queue.task_done()
            except queue.Empty:
                processing = False
                # pass

    return 0


class RecordingBuffer:
    def __init__(self) -> None:
        self.queue = queue.Queue()
        self.total_samples = 0
        self.recording = True

    def __call__(self, indata: np.ndarray, frames: int, time: "CData", 
                 status: sd.CallbackFlags):
        if status:
            print(status)
        else:
            self.queue.put(indata)
            self.total_samples += len(indata)
    
    def mark_finished(self):
        self.recording = False
        

if __name__ == "__main__":
    result = main()
    sys.exit(result)
