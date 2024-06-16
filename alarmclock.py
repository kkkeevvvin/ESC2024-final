import datetime


class AlarmClock:
    def __init__(self, timezone:int) -> None:
        self.on = False
        self.tz = datetime.timezone(datetime.timedelta(hours=timezone))
        self.sleepTime = datetime.time(0, 0)
        self.wakeTime = datetime.time(0, 0)
    
    def turnOn(self):
        self.on = True
        print("[info] [clock] turn on")

    def turnOff(self):
        self.on = False
        print("[info] [clock] turn off")

    def getState(self):
        return self.on

    def setSleepTime(self, strtime:str):
        try:
            self.sleepTime = datetime.time.fromisoformat(strtime)
            print("[info] [clock] set sleep time: ", self.getSleepTime())
        except:
            print("[warning] [clock] set sleep time fail")


    def setWakeTime(self, strtime:str):
        try:
            self.wakeTime = datetime.time.fromisoformat(strtime)
            print("[info] [clock] set wake time: ", self.getWakeTime())
        except:
            print("[warning] [clock] set wake time fail")

    def getSleepTime(self):
        return self.sleepTime.strftime("%H:%M")
    
    def getWakeTime(self):
        return self.wakeTime.strftime("%H:%M")
    
    # minutes until time to sleep
    def getTimeUntilSleep(self):
        n = datetime.datetime.now(self.tz).time()
        timeDelta = (self.sleepTime.minute + self.sleepTime.hour*60) - (n.minute + n.hour*60)
        if timeDelta < 0:
            timeDelta += 24*60
        return timeDelta

    # minutes after wake
    def getTimePassWake(self):
        n = datetime.datetime.now(self.tz).time()
        timeDelta = (n.minute + n.hour*60) - (self.wakeTime.minute + self.wakeTime.hour*60)
        if timeDelta < 0:
            timeDelta += 24*60
        return timeDelta
    
    def isSleeping(self) -> bool:
        sTime = self.sleepTime.minute + self.sleepTime.hour*60
        wTime = self.wakeTime.minute + self.wakeTime.hour*60
        n = datetime.datetime.now(self.tz).time()
        nTime = n.minute + n.hour*60
        if wTime < sTime:
            wTime += 24*60
        if nTime < sTime:
            nTime += 24*60
        if nTime >= wTime:
            return False
        else:
            return True
        

    def getLightFactor(self) -> float:
        if (self.on):
            if (self.isSleeping()):
                return 0.0
            elif (self.getTimeUntilSleep() <= 10):
                return self.getTimeUntilSleep()/10.0
            elif (self.getTimePassWake() <= 10):
                return self.getTimePassWake()/10.0
            else:
                return 1.0
        else:
            return 1.0
        


if __name__ == "__main__":
    tz = datetime.timezone(datetime.timedelta(hours=8))
    print(datetime.datetime.now(tz).time().strftime("%H:%M"))
    ac = AlarmClock(8)
    try:
        while True:
            ac.setSleepTime(input("set sleep time: "))
            ac.setWakeTime(input("set wake time: "))
            print(ac.getTimeUntilSleep(), "minutes until sleep")
            print(ac.getTimePassWake(), "minutes passed after wake")
            print("is sleeping: ", ac.isSleeping())
            print("light factor: ",ac.getLightFactor())
    except:
        pass