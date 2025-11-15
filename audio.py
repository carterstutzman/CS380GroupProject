import sounddevice as sd
import wave

def KEY(STEP): #Key Number
   return ((2**(1/12))**(STEP-49))#*440


def load(file):
    temp = wave.Wave_read(file)
    temp2 = temp.readframes(temp.getnframes())
    new = []
    for n in range(0, int(len(temp2)),2):

        try:
            int_sample = int.from_bytes([temp2[n],temp2[n+1]], "little", signed=True)
            new.append(int_sample/32768)
        except:
            pass

    return new, temp.getframerate(), temp.getnframes(), temp
def save(path,data,framerate=44100):
    import struct
    with wave.open(path,"w") as f:
          
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(framerate)
        for samples in data:
            #for sample in samples:
            samples = int(samples * (2**15-1))
            f.writeframes(struct.pack("<h",samples))
    
class Sample:
    def __init__(self):
        self.data = []
        self.nsamples = 1

    def Load(self,path):
        self.data = load(path)
        self.nsamples = len(self.data)

    def GetData(self,i):
        if (i >= 0):
            return self.data[i % self.nsamples]
        if (i < 0):
            return self.data[self.nsamples - (i%self.nsamples)]
        
class Channel:
    def __init__(self, ):
        self.source = None
        self.playing = False

        self.data = [0 for n in range(0, 44100)]


        #changeable
        self.volume = 1.0
        self.pan = 0.0
        self.pitch = 1.0

    def Update(self, frames):
        pass

    def GetData(self):
        return self.data


# Parameters
samplerate = 44100                    
class Drippy:
    def __init__(self,samplerate=44100,channels=16):
        self.samplerate = samplerate
        self.numChannels = channels
        self.channels = []
        self.stream = None
        self.ReInit()

    def ReInit(self):
        self.samples = {}
        self.channels = [Channel() for n in range(0, self.numChannels)]
        if self.stream != None:
            self.stream.close()

        self.stream = sd.OutputStream(samplerate=samplerate, channels=2, callback=self.OutputCallback, latency="low")
        self.stream.start()

        

    
    def LoadSample(self,path,alias):
        self.samples[alias] = path

    
    def OutputCallback(self,outdata,frames,time2,status):   
        L = []
        R = []
        dat = []
        for c in self.channels:
            dat.append(c.GetData())

        outdata[:] = [[0, 0] for n in range(0,frames)]
        
            


    def HandleMessage(self, msg):
        #print("Audio System :", msg)
        data = msg.split(" ")
        outMsg = ""
        if data[0] == "PLAY":
            outMsg = self.samples[data[1]]
        if data[0] == "STOP":
            outMsg = "CHANNEL #"+data[1]+" STOPPED"

        if data[0] == "LOAD":
            self.LoadSample(data[1], data[2])

    
        
        return outMsg
        
#################
