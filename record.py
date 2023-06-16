import os
import sys
import queue

import numpy as np
import sounddevice as sd
import soundfile as sf
import whisper


q = queue.Queue()


def main():
    model = whisper.load_model("tiny")
    exit_status = 0

    sample_rate = 48000
    channels = 1
    tmp_filename = "delete_me.wav"
    try:
        with sf.SoundFile(tmp_filename,
                          mode="x",
                          samplerate=sample_rate,
                          channels=channels) as sound_file:
            with sd.InputStream(samplerate=sample_rate,
                                channels=channels,
                                callback=callback):
                print("Press Ctrl+C to stop the recording.")
                while True:
                    data = q.get()
                    # data_pad = whisper.pad_or_trim(data)
                    # mel = whisper.log_mel_spectrogram(data_pad).to(model.device)
                    # result = whisper.decode(model, mel, options)
                    # whisper_result.append(result)
                    sound_file.write(data)
    except KeyboardInterrupt:
        # print(whisper_result)
        print("Transcribing")
        result = model.transcribe(tmp_filename, language="pl")
        # result = model.transcribe(tmp_filename)
        print("Done transcribing")
        print(result)
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        exit_status = -1
    finally:
        os.remove(tmp_filename)
        sys.exit(exit_status)


def callback(in_data: np.ndarray, frames, time, status):
    """Callback function executed in separate thread."""
    if status:
        print(status, file=sys.stderr)
    q.put(in_data.copy())


if __name__ == "__main__":
    main()