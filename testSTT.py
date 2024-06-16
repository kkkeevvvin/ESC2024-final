from STT import VoiceControl



def ctrl(command:str):
    if ("de" in command):
        print("wait")
    return True


vc = VoiceControl(ctrl, "vosk-model-small-cn-0.22", "reconized.txt")
vc.startThread()