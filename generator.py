import random 
import pyglet
from pyglet import shapes
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
        

circleFifths = [["C maj","G maj","D maj","A maj","E maj","B maj","F# maj","Db maj","G# maj","Eb maj","Bb maj","F maj"],
                ["A min","E min","B min","F# min","Db min","G# min","Eb min","Bb min","F min","C min","G min","D min"],
                ["C maj 7","G maj 7","D maj 7","A maj 7","E maj 7","B maj 7","F# maj 7","Db maj 7","G# maj 7","Eb maj 7","Bb maj 7","F maj 7"],
                ["A min 7","E min 7","B min 7","F# min 7","Db min 7","G# min 7","Eb min 7","Bb min 7","F min 7","C min 7","G min 7","D min 7"],
                
                
]

class Generator:
    def __init__(self, audioLiaison):
        self.liaison = audioLiaison

        self.pause = False
        
        self.chordMap = circleFifths[0]
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
        

        self.chordTimer = 0.0

        self.melodyMap = [ #Offsets from root note of key
            
        ]

        # self.melodyMap += [
        #     [0, 2, 4, 5],
        #     [7, 9, 11, 12],
        #     [12, 9, 11, 7],
        #     [9, 5, 7, 4],
        # ]

        self.melodyTimer = 0.0
        self.melodyIndex = 0
        self.barIndex = 0
        #TEMP
        self.startedPlaying = False

        self.octave = 3 #3



        #SLIDERS
        self.jazziness = 0.0  #Chances to do a 7th chord
        self.suspense  = 0.0  #Chances to do sus chord
        self.chaos     = 0.0  #Chances to not resolve/revisit past patterns
        self.sadness   = 0.0  #Chances to do minor sounding things



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
        currentChord = self.decodeChordNotation(self.chordMap[self.chordIndex])
        nextChord = self.decodeChordNotation((self.chordMap[(self.chordIndex + 1) % len(self.chordMap)])) 
        bar = [currentChord[0], currentChord[0], currentChord[0], currentChord[0], currentChord[0], currentChord[0], currentChord[0], currentChord[0]]
        peakFirst = random.randint(0, 1)

        peakIndex = 2 * (1 - peakFirst) + 5 * peakFirst
        valleyIndex = 2 * peakFirst + 5 * (1 - peakFirst)

        peakVal = currentChord[2] + 2
        valleyVal = currentChord[0] - 2

        bar[peakIndex] = peakVal
        bar[valleyIndex] = valleyVal

        bar[0] = currentChord[0]
        bar[7] = nextChord[0]

        #bar[1] = currentChord[random.randint(0, 2)]
        #bar[4] = currentChord[random.randint(0, 2)]
        #bar[6] = currentChord[random.randint(0, 2)]

        for n in range(1, 6):
            bar[n] = bar[n - 1] + random.randint(-1, 1) * 2

        return bar
        

        

    def MakeMelody(self):
        # currForm = self.decodeChordNotation(self.chordMap[self.chordIndex])
        # nextForm = self.decodeChordNotation((self.chordMap[(self.chordIndex + 1) % len(self.chordMap)])) 

        # diff = nextForm[0] - currForm[0]

        # rootStart = 0
        # rootEnd = nextForm[0] + random.randint(-1, 1)

        # mid1 = rootEnd / 4.0
        # mid2 = mid1 * 2
        # self.melodyMap.append([currForm[0], currForm[0], currForm[1], currForm[0], currForm[2], currForm[0], currForm[0], rootEnd])

        self.melodyMap.append(self.StandardBar())

        #self.liaison.PushMessage("PLAY "+str(rootStart)+" 1.0 1.0 0.0")

    def Update(self, dt):
        if not self.pause:
            #print(self.chordTimer)
            if (dt > 0.5):
                dt = 0.0
            self.chordTimer += dt
            if (self.startedPlaying == True):
                self.melodyTimer += dt
            while self.chordTimer >= 2.0:
                self.liaison.Print(self.chordMap[self.chordIndex].upper())
                #self.StopChord()
                self.PlayChord()

                self.chordTimer -= 2.0
                self.chordIndex = (self.chordIndex + 1) % len(self.chordMap)
                if (self.startedPlaying == True):
                  self.barIndex = (self.barIndex + 1) % len(self.melodyMap)

                self.MakeMelody()
                
                print(random.randint(0,1))
            
                #TEMP
                if (self.startedPlaying == False): self.melodyTimer = 0.25
                self.startedPlaying = True
            while self.melodyTimer >= 0.25:
                #self.liaison.Print(str(self.melodyMap[self.barIndex][self.melodyIndex]))
                #self.StopChord()
                #self.PlayChord()

                #MARKUS
                #self.MakeMelody()
                currForm = self.decodeChordNotation(self.chordMap[self.chordIndex])
                #self.liaison.PushMessage("PLAY "+str(self.melodyMap[self.barIndex][self.melodyIndex])+" 1.0 1.0 0.0")
                #MARKUS
                
                self.melodyTimer -= 0.25
                self.melodyIndex = (self.melodyIndex + 1) % len(self.melodyMap[self.barIndex])
                
                #print(random.randint(0,1))
                
    
    def Render(self, camera=None):
        pyglet.shapes.Rectangle(360-50,360+50,100,100,color=(255,0,0)).draw()
        


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
        