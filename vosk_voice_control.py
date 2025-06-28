import vosk
import sounddevice as sd
import queue
import json

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

model = vosk.Model("vosk-model-small-en-us-0.15")
sample_rate = 16000
rec = vosk.KaldiRecognizer(model, sample_rate)

with sd.RawInputStream(samplerate=sample_rate, blocksize=4000, dtype='int16', channels=1, callback=callback):
    print("Say something:")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            res = rec.Result()
            text = json.loads(res).get('text', '')
            print(f"Recognized: {text}")
        else:
            partial = rec.PartialResult()
            print(f"Partial: {partial}")
