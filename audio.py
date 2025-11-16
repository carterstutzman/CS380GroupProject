import sounddevice as sd
import wave
import os,math

def KEY(STEP): #Key Number
   return ((2**(1/12))**(STEP-49))#*440


def load(file):
    temp = wave.Wave_read(file)
    temp2 = temp.readframes(temp.getnframes())
    new = []
    for n in range(0, int(len(temp2)),2):

        #try:
            int_sample = int.from_bytes([temp2[n],temp2[n+1]], "little", signed=True)
            new.append(int_sample/32768)
        #except:
        #    pass

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
    def __init__(self, path):
        if path not in ["SINE", "SAW", "SQUARE", "TRIANGLE"]:
            self.type = "SAMPLE"
            self.data = load(path)[0]
            self.nsamples = len(self.data)
        else:
            self.type = self.path


    def GetData(self,i):
        i = int(i)
        if self.type == "SAMPLE":
            if (i >= 0):
                return self.data[i % self.nsamples]
            if (i < 0):
                return self.data[self.nsamples - (i%self.nsamples)]
        if self.type == "SINE":
            return math.sin(i)
        
        

class Channel:
    def __init__(self, ):

        self.playing = False

        self.data = [0 for n in range(0, 44100)]


        #changeable
        self.volume = 1.0
        self.pan = 0.0
        self.pitch = 1.0

        #internal
        self.sample = None
        self.pos = 0


    def Play(self, sample, pitch=1.0, vol=1.0, pan=0.0):
        self.sample = sample
        self.playing = True
        self.pos = 0
        self.volume = vol
        self.pitch = pitch
        self.pan  = pan

    def Stop(self):
        self.data = [0 for n in range(0,44100)]
        self.sample = None
        self.playing = False
        self.pos = 0
    def Update(self, frames):
        #print(frames, self.samples, self.playing)
        #double temp = GetData((i + pos) * pitch) / 32767.0;
        if self.sample != None and self.playing:
            for x in range(0, frames):
                S = self.sample.GetData((self.pos + x)*self.pitch)
                self.data[x] = S * self.volume
                #print(S)
            self.pos += x
            if self.pos > self.sample.nsamples*1.0/self.pitch:
                self.Stop()

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
        self.samples = []
        self.ReInit()

    def ReInit(self):
        self.samples = []
        self.channels = [Channel() for n in range(0, self.numChannels)]
        if self.stream != None:
            self.stream.close()

        self.stream = sd.OutputStream(samplerate=samplerate, channels=2, callback=self.OutputCallback, latency="low")
        self.stream.start()

        

    def PlaySample(self,alias,chan=-1, pitch=1.0, vol=1.0,pan=0.0):
        if chan == -1:
            for x in range(0, len(self.channels)):
                if not self.channels[x].playing:
                    self.channels[x].Play(self.samples[self.samples.index(alias)+1],pitch,vol,pan)
                    break
        else:
            if not self.channels[chan].playing:
                self.channels[chan].Play(self.samples[self.samples.index(alias)+1], pitch, vol, pan)
    
    def LoadSample(self,path,alias):
        self.samples.append(alias)
        S = Sample(path)
        self.samples.append(S)
        
    
    def OutputCallback(self,outdata,frames,time2,status):   
        L = []
        R = []
        dat = []
        for c in self.channels:
            c.Update(frames)
            dat.append(c.GetData())
            
        
        MAX = 0
        for y in range(0, frames):
            A = 0
            B = 0
            tot = 1.0
            for x in range(0, len(dat)):
                if self.channels[x].playing:
                    tot+=1.0
                pan = self.channels[x].pan
                panL = 0.5
                panR = 0.5
                if (pan < 0.0):
                    panL = abs(pan / 2.0) + 0.5
                    panR = 1.0 - panL
                
                elif (pan > 0.0):
                    panR = pan / 2.0 + 0.5
                    panL = 1.0 - panR
                
                
                
               
                A += dat[x][y] * panL
                B += dat[x][y] * panR
            
            tot = 1.0
            L += [A/math.sqrt(tot)]
            R += [B/math.sqrt(tot)]
            


        outdata[:] = [[L[n], R[n]] for n in range(0,frames)]
        
            


    def HandleMessage(self, msg):
        #print("Audio System :", msg)
        data = msg.split(" ")
        outMsg = ""
        if data[0] == "LOADPIANO":
            i = 0
            for a in os.listdir("./samples/piano"):
                try:
                    self.LoadSample("./samples/piano/"+a, str(i))
                    
                except:
                    pass
                i+=1
            outMsg = "LOADED PIANO SAMPLES"
        if data[0] == "PLAY":
            self.PlaySample(data[1], -1, float(data[2]), float(data[3]), float(data[4]))
        
        if data[0] == "PLAYEXPLICIT":
            self.PlaySample(data[1], int(data[2]), float(data[3]), float(data[4]), float(data[5]))
        
        if data[0] == "CHORD":
            self.PlaySample(str(int(data[1])+0), -1)
            self.PlaySample(str(int(data[1])+4), -1)
            self.PlaySample(str(int(data[1])+7), -1)
            self.PlaySample(str(int(data[1])+11), -1)
            


        if data[0] == "STOP":
            self.channels[int(data[1])].Stop()

        if data[0] == "LOAD":
            self.LoadSample(data[1], data[2])

    
        
        return outMsg
        
#################
