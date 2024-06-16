import vosk
import pyaudio
import json
from pypinyin import lazy_pinyin
from threading import Thread
import os
import requests
import time


def lightRegulate(command:str) -> bool:
        #開燈
        if "kaideng" in command:
            try:
                rq = requests.get("http://127.0.0.1:8080/open")
                if (rq.status_code == 200):
                    print("\033[1;32;40mPi: open the light\033[0m")
                else:
                    print("\033[1;31;40mPi: open light fail\033[0m")
            except:
                print("\033[1;31;40mPi: open light fail\033[0m")

        #關燈
        elif "guandeng" in command:
            try:
                rq = requests.get("http://127.0.0.1:8080/close")
                if (rq.status_code == 200):
                    print("\033[1;31;40mPi: close the light\033[0m")
                else:
                    print("\033[1;31;40mPi: close light fail\033[0m")
            except:
                print("\033[1;31;40mPi: close light fail\033[0m")

        #日光
        elif "riguang" in command:
            try:
                rq = requests.get("http://127.0.0.1:8080/enviroment")
                if (rq.status_code == 200):
                    print("\033[1;33;40mPi: adjust the enviroment light\033[0m")
                else:
                    print("\033[1;31;40mPi: switch mode fail\033[0m")
            except:
                print("\033[1;31;40mPi: switch mode fail\033[0m")

        #升高
        elif "shengao" in command:
            try:
                rq = requests.get("http://127.0.0.1:8080/up")
                if (rq.status_code == 200):
                    print("\033[1;36;40mPi: increase brightness\033[0m")
                else:
                    print("\033[1;31;40mPi: increase brightness fail\033[0m")
            except:
                print("\033[1;31;40mPi: increase brightness fail\033[0m")

        #降低
        elif "jiangdi" in command:
            try:
                rq = requests.get("http://127.0.0.1:8080/down")
                if (rq.status_code == 200):
                    print("\033[1;34;40mPi: decrease brightness\033[0m")
                else:
                    print("\033[1;31;40mPi: decrease brightness fail\033[0m")
            except:
                print("\033[1;31;40mPi: decrease brightness fail\033[0m")

        #離開
        elif "likai" in command:
            print("\033[1;35;40mPi: stop\033[0m")
            return False
        else:
            pass
        return True



class VoiceControl:

    def __init__(self, regulateFunc, modelPath:str="", outputPath:str="recognized.txt") -> None:
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
            os._exit(0)
                


if __name__ =="__main__":
    vc = VoiceControl(lightRegulate, "vosk-model-small-cn-0.22", "reconized.txt")
    vc.startThread()
    print("OK")
    try:
        while True:
            time.sleep(5)
            pass
    except KeyboardInterrupt:
        os._exit(0)

