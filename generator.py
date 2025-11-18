import random #temp
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
        
class Generator:
    def __init__(self, audioLiaison):
        self.liaison = audioLiaison

        self.pause = False
        
        self.chordMap = [
            
            
        ]
        for i in range(0, 12):
            self.chordMap += [
            notes[i] + " maj",
            notes[i] + " min",
            notes[i] + " dim",
            notes[i] + " aug",
            notes[i] + " sus2",
            notes[i] + " sus4",

            notes[i] + " maj 7",
            notes[i] + " min 7",
            notes[i] + " dim 7",
            notes[i] + " aug 7",
            ]
            
        self.chordIndex = 0
        

        self.chordTimer = 0.0


        self.octave = 3
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
            #self.liaison.PushMessage("PLAYKEY S0 "+str(form[f])+" 1.0 0.0")



    def Update(self, dt):
        if not self.pause:
            #print(self.chordTimer)
            if (dt > 0.5):
                dt = 0.0
            self.chordTimer += dt
            while self.chordTimer >= 2.0:
                self.liaison.Print(self.chordMap[self.chordIndex].upper())
                #self.StopChord()
                self.PlayChord()
                
                self.chordTimer -= 2.0
                self.chordIndex = (self.chordIndex + 1) % len(self.chordMap)
                
                print(random.randint(0,1))
                
    
    def Render(self, camera=None):
        pass