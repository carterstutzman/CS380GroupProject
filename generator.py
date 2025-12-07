import random 
import pyglet
import math
from pyglet import shapes


screenSize = [720,720]
centerX = int(screenSize[0]/2)
centerY = int(screenSize[1]/2)
"""
chord notation brainstorming

real music uses :
C  -> major chord
c  -> minor chord
C+ -> augmented chord
c0 -> diminished chord
C7 -> dominant seventh chord

or

Cmaj  -> major
Cmin  -> minor
Caug  -> augmented
Cdim  -> diminished
C7    -> dom seventh
Cmin7 -> minor seventh

"""

chordForms = [
"maj",
[0, 4, 7,   11],
"min",
[0, 3, 7,   10],
"dim",
[0, 3, 6,    9],
"aug",
[0, 4, 8,   10],
"sus2",
[0, 2, 7,    0],#don't know the seventh
"sus4",
[0, 5, 7,    0],#ditto

]
notes = ["A","Bb","B","C","Db","D","Eb","E","F","F#","G","G#"]
        

circleFifths = [["C maj",  "G maj",  "D maj",  "A maj",   "E maj",   "B maj",    "F# maj",  "Db maj",  "G# maj",   "Eb maj",  "Bb maj",  "F maj"],
                ["A min",  "E min",  "B min",  "F# min",  "Db min",  "G# min",   "Eb min",  "Bb min",  "F min",    "C min",   "G min",   "D min"],
                ["C maj 7","G maj 7","D maj 7","A maj 7", "E maj 7", "B maj 7",  "F# maj 7","Db maj 7","G# maj 7", "Eb maj 7","Bb maj 7","F maj 7"],
                ["A min 7","E min 7","B min 7","F# min 7","Db min 7","G# min 7", "Eb min 7","Bb min 7","F min 7",  "C min 7", "G min 7", "D min 7"],
                
                
]

class Generator:
    def __init__(self, audioLiaison):
        self.liaison = audioLiaison
        self.Reset()
        
    def Reset(self):
        self.pause = False
        self.scene = None
        self.chordMap = ["C maj"]
        self.chordToAdd = "C maj"
        # for i in range(0, 12):
        #     self.chordMap += [
        #     notes[i] + " maj",
        #     notes[i] + " min",
        #     notes[i] + " dim",
        #     notes[i] + " aug",
        #     notes[i] + " sus2",
        #     notes[i] + " sus4",

        #     notes[i] + " maj 7",
        #     notes[i] + " min 7",
        #     notes[i] + " dim 7",
        #     notes[i] + " aug 7",
        #     ]
            
        self.chordIndex = 0
        self.chordOffsets = []

        self.chordTimer = 0.0
        self.chordRepeats = 0

        self.melodyMap = [ #Offsets from root note of scale
            
        ]

        self.melodyTimer = 0.0
        self.melodyIndex = 0
        self.barIndex = 0
        self.circleIndex = 0
        #TEMP
        self.startedPlaying = False

        self.octave = 3 #3
        self.bpm = 1.5 # 1.5 for fast, 3.0 for slow

        self.key = self.GetKey("C")
        self.scale = self.MakeMajorScale()

        #SLIDERS
        self.spaceSlider = 0.0
        self.emotionSlider = 0.0


        self.moodTimer = 0.0

    def GetKey(self, Note): #Takes key string
        return (notes.index(Note) + 1) + (12 * self.octave)

    def MakeMajorScale(self):
        nextKey = self.key + 12
        scale = [self.key, self.key + 2, self.key + 4, self.key + 5, self.key + 7, self.key + 9, self.key + 11, self.key + 12 , nextKey + 2, nextKey + 4, nextKey + 5, nextKey + 7, nextKey + 9, nextKey + 11, nextKey + 12]
        #                 W             W             H             W             W             W              H             ||| Next key for bleed over
        return scale
    
    def MakeMinorScale(self):
        scale = [self.key, self.key + 2, self.key + 3, self.key + 5, self.key + 7, self.key + 8, self.key + 10, self.key + 12]
        #                 W             H             W             W             H             W              W
        return scale

    def GetChordOffsets(self,STR):
        dat = STR.split(" ")
        offsets = chordForms[chordForms.index(dat[1])+1]

        return offsets

    def decodeChordNotation(self,STR):
        dat = STR.split(" ")
        note = notes.index(dat[0])
        note += self.octave*12
        
        form = chordForms[chordForms.index(dat[1])+1][0: 3+(len(dat) > 2 and dat[2] == "7")]
        for n in range(0, len(form)):
            form[n] += note
        #print(form)
        return form
    def StopChord(self):
        for n in range(0, 4):
            self.liaison.PushMessage("STOP "+str(n))
    def PlayChord(self):
        form = self.decodeChordNotation(self.chordMap[self.chordIndex])
        for f in range(0, len(form)):
            self.liaison.PushMessage("PLAY "+str(form[f])+" 1.0 0.25 0.0")
            #self.liaison.PushMessage("PLAYKEY S0 "+str(form[f] + 24)+" 1.0 0.0")

    def StandardBar(self):
        rootIndex = self.rootNote
        if (rootIndex < 0): rootIndex = (7 - rootIndex) - 1 
        print(rootIndex)

        currentChord = self.GetChordOffsets(self.chordMap[self.chordIndex]) # REMEMBER... ISSUE IS THAT CHORD OFFSETS ARE IN KEYS, NOT STEPS IN SCALE
        nextChord = self.decodeChordNotation((self.chordMap[(self.chordIndex + 1) % len(self.chordMap)])) 
        bar = [None, None, None, None, None, None, None, None]
        peakFirst = random.randint(0, 1)

        peakIndex = 2 * (1 - peakFirst) + 5 * peakFirst
        valleyIndex = 2 * peakFirst + 5 * (1 - peakFirst)

        peakVal = (currentChord[2] + rootIndex)
        valleyVal = (currentChord[0] + rootIndex)

        bar[peakIndex] = peakVal
        bar[valleyIndex] = valleyVal

        bar[0] = (currentChord[1] + rootIndex)
        bar[7] = nextChord[0] + random.randint(-1, 1) * 2

        #bar[1] = currentChord[random.randint(0, 2)]
        #bar[4] = currentChord[random.randint(0, 2)]
        #bar[6] = currentChord[random.randint(0, 2)]

        # for n in range(1, 6):
        #     bar[n] = bar[n - 1] + random.randint(-1, 1) * 2

        #print(bar)
        return bar
        
    def Arpeggio(self):
        rootIndex = self.rootNote
        if (rootIndex < 0): rootIndex = (7 - rootIndex) - 1
        print(rootIndex)

        currentChord = self.GetChordOffsets(self.chordMap[self.chordIndex])
        bar = [None, None, None, None, None, None, None, None]

        startPoint = min((random.randint(0, 2) * 2), 4)


        direction = random.randint(0, 1)
        if (direction == 1):
            bar[startPoint] = (currentChord[0] + rootIndex)
            bar[startPoint + 1] = (currentChord[1] + rootIndex)
            bar[startPoint + 2] = (currentChord[2] + rootIndex)
        else:
            bar[startPoint + 2] = (currentChord[0] + rootIndex)
            bar[startPoint + 1] = (currentChord[1] + rootIndex)
            bar[startPoint] = (currentChord[2] + rootIndex)

        #print(bar)
        return bar
    
    def EmptyBar(self):
        return [None, None, None, None, None, None, None, None]

    def MakeMelody(self, STR, space, emotion):
        s = (space + 1.0) / 2.0
        e = (emotion + 1.0) / 2.0

        dat = STR.split(" ")
        self.rootNote = (notes.index(dat[0])) + (12 * self.octave)
        print("NOTE:",self.rootNote)
        ran = random.randint(0, 10)
        if (space > 0.0):           
            if (ran <= 1): 
                self.melodyMap.append(self.EmptyBar())
            elif (ran <= 7 * space): 
                self.melodyMap.append(self.StandardBar())
            else:
                self.melodyMap.append(self.Arpeggio())
        else:
            if (ran <= 4 * (1.0+space)): 
                self.melodyMap.append(self.Arpeggio())
            elif (ran <= 8 * (1.0+(space * space * space))):
                self.melodyMap.append(self.StandardBar())
            else: 
                self.melodyMap.append(self.EmptyBar())
                if (random.randint(0,100) > 50):
                    self.AddNoteToBar(self.melodyMap[len(self.melodyMap) - 1])
        
        numToAdd = 0
        if (space >= 0.0):
            numToAdd = int(space * 7.0 * (random.randint(25, 100) / 100.0)) + 1
            for n in range(0, numToAdd):
                self.AddNoteToBar(self.melodyMap[len(self.melodyMap) - 1])

        print(self.melodyMap[len(self.melodyMap) - 1])

        #self.melodyMap.append([self.rootNote, self.rootNote, self.rootNote, self.rootNote, self.rootNote, self.rootNote, self.rootNote, self.rootNote])
        
        # if len(self.melodyMap) % 2 == 0:
        #     self.melodyMap.append(self.MakeMajorScale())
        # else:
        #     self.melodyMap.append(self.MakeMinorScale())

    def AddNoteToBar(self, bar):
        rootIndex = self.rootNote
        currentChord = self.GetChordOffsets(self.chordMap[self.chordIndex])
        indices = []
        for n in range(0, 8):
            if (bar[n] == None): indices.append(n)
        
        if (len(indices) == 0): return

        index = indices[random.randint(0, len(indices) - 1)]
        bar[index] = 0
        num = 0
        if (index > 0):
            left = bar[index - 1]
            if (left != None): 
                bar[index] += left
                num += 1
        if (index < 7):
            right = bar[index - 1]
            if (right != None):
                bar[index] += right
                num += 1
        
        if (bar[index] == 0): bar[index] = currentChord[random.randint(0, 2)] + rootIndex
        elif (num == 1): bar[index] += random.choice([-2, 2])
        else: bar[index] //= num  

    def MakeChordSegment(self, val):
        print(val)
        normVal = (val + 1.0) / 2.0
        numBars = 0
        if(random.randint(0,100) / 100.0 > normVal):
            if(random.randint(0,100) / 100.0 > 0.5):
                numBars = 1
            else:
                numBars = 2
        else:
            if(random.randint(0,100) / 100.0 > 0.5):
                numBars = 4
            else:
                numBars = 8

        prevChord = self.chordMap[len(self.chordMap) - 1]
        try:
            position = circleFifths[self.circleIndex].index(prevChord)
            newPosition = (position + random.randint(-2, 2)) % len(circleFifths[self.circleIndex])
        
        except:
            for i in range(0, len(circleFifths)):
                try:
                    position = circleFifths[i].index(prevChord)
                    newPosition = position
                except:
                    pass
        if (newPosition < 0): newPosition += len(circleFifths[self.circleIndex])

        numBars = 1

        self.chordRepeats = numBars
        self.chordToAdd = circleFifths[self.circleIndex][newPosition]

    def Update(self, dt):

        if not self.pause:
            ##emotion stuff
            self.moodTimer += dt
            moodSwing = math.sin(self.moodTimer)+self.emotionSlider
            self.octave = int(3 + moodSwing//2)
            if moodSwing > 0.0:
                self.circleIndex = 0
            if moodSwing > 1.0:
                self.circleIndex = 2
            
            if moodSwing < 0.0:
                self.circleIndex = 1
            if moodSwing < -1.0:
                self.circleIndex = 3
            
            
            s = (self.spaceSlider + 1.0) / 2.0
            if (self.spaceSlider < 0): self.bpm = -(self.spaceSlider) * (3.5 - 2.0) + 2.0
            else: self.bpm = (self.spaceSlider) * (1.0 - 2.0) + 2.0
            #print(self.chordTimer)
            if (dt > 0.5):
                dt = 0.0
            self.chordTimer += dt
            if (self.startedPlaying == True):
                self.melodyTimer += dt
            while self.chordTimer >= self.bpm:
                #if (self.chordRepeats <= 0): self.chordMap += self.MakeChordSegment(self.spaceSlider)
                self.chordMap.append(self.chordToAdd)
                self.chordRepeats -= 1
                if (self.chordRepeats <= 0): self.MakeChordSegment(-self.spaceSlider)

                print("INDEX:",self.chordIndex)
                self.liaison.Print(self.chordMap[self.chordIndex].upper())
                #self.StopChord()
                self.PlayChord()

                #Make minor
                # randVal = random.randint(0, 100)
                # if (randVal > 75):
                #     self.chordMap = circleFifths[1]
                # elif (randVal < 25):
                #     self.chordMap = circleFifths[0]

                if (self.startedPlaying == True):
                  self.barIndex = (self.barIndex + 1) % len(self.melodyMap)

                self.MakeMelody(self.chordMap[self.chordIndex], self.spaceSlider, self.emotionSlider)

                self.chordTimer -= self.bpm
                self.chordIndex = (self.chordIndex + 1)
                
                #TEMP
                if (self.startedPlaying == False): self.melodyTimer = (self.bpm / 8)
                self.startedPlaying = True
            while self.melodyTimer >= (self.bpm / 8):
                #self.liaison.Print(str(self.melodyMap[self.barIndex][self.melodyIndex]))
                #self.StopChord()
                #self.PlayChord()

                #MARKUS
                #self.MakeMelody()
                currForm = self.decodeChordNotation(self.chordMap[self.chordIndex])
                if (self.melodyMap[self.barIndex][self.melodyIndex] != None): self.liaison.PushMessage("PLAY "+str(self.melodyMap[self.barIndex][self.melodyIndex])+" 1.0 1.0 0.0")
                #self.liaison.PushMessage("PLAY "+str(self.melodyMap[self.melodyIndex])+" 1.0 1.0 0.0")
                #MARKUS
                
                self.melodyTimer -= (self.bpm / 8)
                self.melodyIndex = (self.melodyIndex + 1) % len(self.melodyMap[self.barIndex])
                
                #print(random.randint(0,1))
                
    
    def Render(self, camera=None):
        pyglet.shapes.Rectangle(360-32 + self.spaceSlider*360,360-32+self.emotionSlider*360,64,64,color=(255,0,0)).draw()
        


    def HandleMessage(self,msg):
        data = msg.split(" ")
        if data[0] == "MIN":
            self.chordMap = circleFifths[1]
        if data[0] == "MAJ":
            self.chordMap = circleFifths[0]
        
        if data[0] == "MIN7":
            self.chordMap = circleFifths[3]
        if data[0] == "MAJ7":
            self.chordMap = circleFifths[2]
        

        if data[0] == "DRAG":
            self.spaceSlider = int(data[1]) / centerX - 1.0
            self.emotionSlider = int(data[2]) / centerY - 1.0
            
            if self.spaceSlider > 1.0: self.spaceSlider = 1.0
            if self.spaceSlider < -1.0: self.spaceSlider = -1.0
            
            if self.emotionSlider > 1.0: self.emotionSlider = 1.0
            if self.emotionSlider < -1.0: self.emotionSlider = -1.0
            
            self.scene.PushMessage("SET_GEL_R "+str(int((self.emotionSlider*0.5 + 0.5)*255)))
            self.scene.PushMessage("SET_GEL_G "+str(int(((-self.spaceSlider)*0.5 + 0.5)*255)))
            
            print(int((self.emotionSlider*0.5 + 0.5)*255), int(((-self.spaceSlider)*0.5 + 0.5)*255))
        
        if data[0] == "RESET":
            self.Reset()