import vosk
import pyaudio
import json
from pypinyin import lazy_pinyin
from threading import Thread
import os
import time

# voice control
#   regulateFunc: funcion that has 1 str argument for keyword processing, return bool whether to keep voice control alive
class VoiceControl:

    def __init__(self, regulateFunc, modelPath:str="vosk-model-small-cn-0.22", outputPath:str="recognized.txt") -> None:
        self.model = vosk.Model(modelPath)
        self.reconizer = vosk.KaldiRecognizer(self.model, 16000)
        self.pAudio = pyaudio.PyAudio()
        self.stream = self.pAudio.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=8192)
        self.outputPath = outputPath
        self.regulate = regulateFunc

    def startThread(self):
        thread = Thread(target=self.start)
        thread.start()
        
    def start(self) -> None:
        with open(self.outputPath, "w") as outputFile:
            #print("Listening for speech. Say \"離開\" to stop.")
            # Start streaming and recognize speech
            try:
                keep = True
                while True:
                    data = self.stream.read(4096)#read in chunks of 4096 bytes
                    if self.reconizer.AcceptWaveform(data):#accept waveform of input voice
                # Parse the JSON result and get the recognized text
                        result = json.loads(self.reconizer.Result())
                        recognizedText = result["text"]

                # Write recognized text to the file
                        outputFile.write(recognizedText + "\n")
                        pinyin = "".join(lazy_pinyin(recognizedText)).replace(" ", "")
                        if (pinyin != ""):
                            print("[info] [voice control] recognized:  %s (%s)"%(recognizedText, pinyin))
                            keep = self.regulate(pinyin)

                # Check for the termination keyword
                    if not keep:
                        print("Termination keyword detected. Stopping...")
                        break
            finally:
                self.stream.stop_stream()
                self.stream.close()
                self.pAudio.terminate()

            outputFile.close()
                
def ctrl(command:str):
    if ("de" in command):
        print("keyword \"de\" detected")
    return True

if __name__ =="__main__":
    vc = VoiceControl(ctrl, "vosk-model-small-cn-0.22", "reconized.txt")
    vc.startThread()
    print("OK")
    try:
        while True:
            time.sleep(5)
            pass
    except KeyboardInterrupt:
        os._exit(0)

