import argparse

import numpy as np
import sounddevice as sd
import soundfile as sf
from tqdm import tqdm


class AudioFile:
    def __init__(self, filename, samplerate, channels) -> None:
        self.sound_file = sf.SoundFile(filename, mode='w', 
                                       samplerate=samplerate,
                                       channels=channels)

    def __call__(self, indata: np.ndarray, frames: int, time: "CData", 
                 status: sd.CallbackFlags):
        if status:
            print(status)
        else:
            self.sound_file.write(indata.copy())
    
    def close_stream(self):
        self.__del__()

    def __del__(self):
        self.sound_file.close()
            


parser = argparse.ArgumentParser()
parser.add_argument("--version", action="version", version="0.0.1")
parser.add_argument("--filename", "-f", default="recording.wav", 
                    help="name of the file to save the recording in")
parser.add_argument("--samplerate", "-s", type=int, default=44100,
                    help="samplerate of the recording")
parser.add_argument("--channels", "-c", type=int, default=1, 
                    help="number of channels")
parser.add_argument("--duration", "-d", type=int, required=True, 
                    help="duration of the recording, in seconds")
parser.add_argument("--blocksize", "-b", type=int, required=False, default=0,
                    help="blocksize of the recording data")

args = parser.parse_args()


audio_file_callback = AudioFile(args.filename, args.samplerate, args.channels)

print(f"Recording to file: {args.filename}")
with sd.InputStream(samplerate=args.samplerate,
                    blocksize=args.blocksize,
                    channels=args.channels,
                    callback=audio_file_callback,
                    finished_callback=audio_file_callback.close_stream):
    for i in tqdm(range(args.duration)):
        sd.sleep(1000)
print("Finished recording.")
