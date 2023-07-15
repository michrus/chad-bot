import argparse
import os
import pprint
import time

import ffmpeg
import numpy as np
import soundfile as sf
import whisper


def convert_samplerate(filename: str, new_rate: int):
    print(f"Converting original file to new samplerate: {new_rate}")
    stream = ffmpeg.input(filename)
    *name_segments, format_suffix = filename.split(".")
    new_filename = ".".join(name_segments) + f"_sr{new_rate}." + format_suffix
    stream = ffmpeg.output(stream, new_filename, ar=f"{new_rate}")
    ffmpeg.run(stream)
    if os.path.exists(new_filename):
        print("Samplerate conversion successful.")
        return new_filename
    else:
        raise Exception("Failed to convert file to new samplerate.")


parser = argparse.ArgumentParser()
parser.add_argument("--version", action="version", version="0.0.1")
parser.add_argument("--filename", "-f", default="recording.wav", 
                    help="name of the file to load the recording from")
parser.add_argument("--samplerate", "-s", type=int, default=44100,
                    help="samplerate of the recording")
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
print("=" * 80)
print(f"Opening file: {args.filename}")
print(f"Samplerate: {args.samplerate}")
if args.whisper_load:
    print("Using method from Whisper to load and transcribe the file.")
    data = whisper.load_audio(args.filename, sr=args.samplerate)
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
    f = sf.SoundFile(args.filename)
    if f.samplerate != args.samplerate:
        filename = convert_samplerate(args.filename, args.samplerate)
    else:
        filename = args.filename
    f.close()
    f = sf.SoundFile(filename)
    processing = True
    print(f"Reading: {filename}")
    while processing:
        print("-" * 100)
        data = f.read(args.blocksize, 
                      dtype=np.float32)
        if not len(data):
            processing = False
        else:
            then = time.time()
            result = model.transcribe(data, language="pl")
            now = time.time()
            processing_time = now - then
            for segment in result.get("segments", []):
                print(segment.get("text", ""))
                print(f"Average logprob: {segment.get('avg_logprob', '')}")
            print(f"Processing block of size {args.blocksize} "
                  f"took: {processing_time} seconds.")
    f.close()
    # Cleanup
    if filename != args.filename:
        print("Remove file with altered samplerate.")
        os.remove(filename)

print(f"Finished.")
