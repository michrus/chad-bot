"""
Records and processes audio, storing data in temporary files if
real time performance cannot be achieved.
"""
import sys
import queue
# from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper


def main():
    # audio_queue = queue.Queue()

    samplerate = 44100
    min_duration_to_record = 1
    blocksize = int(min_duration_to_record * samplerate)
    transcribe_buffer = np.ndarray(shape=(0,), dtype=np.float32)
    min_frames_to_process = samplerate * 30
    duration = 30
    channels = 1
    # recording: np.ndarray = sd.rec(
    #     int(duration * samplerate),
    #     samplerate=samplerate,
    #     channels=channels
    # )
    recording_buffer = RecordingBuffer()
    model = whisper.load_model("medium")
    processing = True
    rec_stream = sd.InputStream(samplerate=samplerate,
                        blocksize=blocksize,
                        channels=channels,
                        callback=recording_buffer,
                        finished_callback=recording_buffer.mark_finished)
    print("Recording.")
    rec_stream.start()
    sd.sleep(duration * 1000)
    rec_stream.stop()
    print("Done recording.")
    i = 0
    print(f"qsize: {recording_buffer.queue.qsize()}")
    with sf.SoundFile("recording.wav", mode='w', samplerate=samplerate,
                          channels=channels) as file:
        while recording_buffer.queue.qsize() > 0:
            try:
                if i % 50 == 0:
                    print(f"qsize: {recording_buffer.queue.qsize()}")
                processing_chunk: np.ndarray = recording_buffer.queue.get(block=False)
                file.write(processing_chunk)
                processing_chunk = processing_chunk.reshape((-1,))
                
                chunk_copy = processing_chunk.copy()
                transcribe_buffer = np.append(transcribe_buffer, 
                                            chunk_copy, 
                                            axis=0)
                if len(transcribe_buffer) >= min_frames_to_process:
                    result = model.transcribe(transcribe_buffer, language="pl")
                    # Expand the data if transcription yields nothing
                    if len(result.get("text", "")) > 0:
                        # If transcription was successful and the buffer is not
                        # empty - clear it
                        print(f"qsize: {recording_buffer.queue.qsize()}")
                        print(f"transcribe_buffer length: {len(transcribe_buffer)}")
                        print(f"result: {result}")
                        print("Clearing transcribe_buffer")
                        print("=" * 80)
                        del transcribe_buffer
                        transcribe_buffer = np.ndarray(shape=(0,), dtype=np.float32)
                recording_buffer.queue.task_done()
                i += 1
            except queue.Empty:
                processing = False
                # pass
    print("Closing recording stream")
    rec_stream.close()
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
            self.queue.put(indata.copy())
            self.total_samples += len(indata)
    
    def mark_finished(self):
        self.recording = False
        

if __name__ == "__main__":
    result = main()
    sys.exit(result)
