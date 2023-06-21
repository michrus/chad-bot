import argparse
import pprint
import time

import numpy as np
import soundfile as sf
import whisper


parser = argparse.ArgumentParser()
parser.add_argument("--version", action="version", version="0.0.1")
parser.add_argument("--filename", "-f", default="recording.wav", 
                    help="name of the file to load the recording from")
parser.add_argument("--blocksize", "-b", type=int, required=False, default=0,
                    help="blocksize of the recording data")
parser.add_argument("--model", "-m", type=str, required=False, 
                    default="medium", help="Whisper model size")
parser.add_argument("--language", "-l", type=str, required=False, 
                    default="en", help="Language of the recording")
parser.add_argument("--whisper_load", action="store_true",
                    help="Load audio file using Whisper function")

args = parser.parse_args()


print(f"Using Whisper model: {args.model}")
model = whisper.load_model(args.model)
print(f"Opening file: {args.filename}")

if args.whisper_load:
    print("Using method from Whisper to load and transcribe the file.")
    data = whisper.load_audio(args.filename)
    print(data.shape)
    print(data[:5])
    then = time.time()
    result = whisper.transcribe(model=model,
                                audio=data,
                                language=args.language)
    now = time.time()
    processing_time = now - then
    pprint.pprint(result)
    print(f"Load and transcribe took {processing_time} seconds.")
else:
    print("Loading blocks from file using soundfile and transcribing.")
    with sf.SoundFile(args.filename) as f:
        processing = True
        while processing:
            data = f.read(args.blocksize).astype(dtype=np.float32)
            print(data.shape)
            print(data[:5])
            if not len(data):
                processing = False
            else:
                then = time.time()
                result = model.transcribe(data, language="pl")
                now = time.time()
                processing_time = now - then
                pprint.pprint(result)
                print(f"Processing block of size {args.blocksize} "
                    f"took: {processing_time} seconds.")
print(f"Finished.")
