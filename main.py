import pyglet
from pyglet.window import key
from pyglet import shapes
import math,random,time,sys,os
from pyglet.gl import *

from pyglet.graphics import *

##our imports
from audio import *
from generator import *

pyglet.image.Texture.default_mag_filter = pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST

pyglet.gl.glEnable(pyglet.gl.GL_TEXTURE_2D)

#░░▓▓█.▄▌▐▀╚╩╦╠═╬╧░▄╛┐└┴┬├.┼╞╟╚║╝╗║╔└─┘─ ┼├┌─┐│┬┴┤☺☻♥♦♣♠•◘○◙←↑→↓♡╱╲╳


screenSize = [1080,720]
centerX = int(screenSize[0]/2)
centerY = int(screenSize[1]/2)
window = pyglet.window.Window(screenSize[0], screenSize[1])
keys = key.KeyStateHandler()
window.push_handlers(keys)
##glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST) 
glClearColor(0.0,0.0,0.0,1)

PAL = [[255,255,255,255],
       [192,192,192,255],
       [128,128,128,255],
       [ 64,64,64,255],
       
       [255,  0,  0,255],
       [  0,255,  0,255],
       [  0,  0,255,255],
       [255,255,  0,255],
       [255,  0,255,255],
       [  0,255,255,255],
       [  0,  0,  0,255],
       ]

def BASE(STR):
    return '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$'.index(STR)

def MAKE(LIST,A=1,B=1,BLEND=0,MIR=0,SPR=0):
    global PAL
    OUT = []
    for x in range(0, len(LIST)):
        for n in range(0, B):
            for y in range(0, len(LIST[x])):
                try:
                    if MIR == 0:OUT+= PAL[BASE(LIST[len(LIST)-x-1][y])]*A
                    if MIR == 1:OUT+= PAL[BASE(LIST[len(LIST)-x-1][len(LIST[x])-y-1])]*A
                except:OUT += [0,0,0,0]*A
    for x in range(0, BLEND):
        for n in range(0, len(OUT)):
            if (n+1) % 4 != 0:
                try:OUT[n] = int((OUT[n+4]+OUT[n])/2)
                except:OUT[n] = OUT[n-4]
        for n in range(0, len(OUT)):
            if (len(OUT)-n) % 4 != 0:
                try:OUT[len(OUT)-1-n] = int((OUT[len(OUT)-1-n-4]+OUT[len(OUT)-1-n])/2)
                except:OUT[len(OUT)-1-n] = OUT[len(OUT)-1-n+4]
    A = pyglet.image.ImageData(len(LIST[0])*A, len(LIST)*B, 'RGBA', bytes(OUT))
    if SPR:
        A = pyglet.sprite.Sprite(A,x=0,y=0)
    return A

def Dist2D(p1,p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
def SignedDist2D(p1,p2):
    return (p1[0]-p2[0]) + (p1[1]-p2[1])
def Lerp(a,b,t):
    return (a + (b-a)*t)

def Lerp2D(a,b,t):
    return [Lerp(a[0],b[0],t),
            Lerp(a[1],b[1],t),
            0.0]
def Lerp3D(a,b,t):
    return [Lerp(a[0],b[0],t),
            Lerp(a[1],b[1],t),
            Lerp(a[2],b[2],t),
            ]


def CloseEnough2D(a,b,d):
    A = abs(a[0]-b[0]) <= d
    B = abs(a[1]-b[1]) <= d
    return A and B

class Camera:
    def __init__(self):
        self.scl = 4.0
        self.pos = [0,0,0]
        self.tgt = None

    def GetScreenCoords(self, pos):
        if (len(pos) < 3):
            pos.append(0.0)
        Z = 1.0/(pos[2]+1.0)
        return [centerX+Z*(pos[0]-self.pos[0])*self.scl, centerY + Z*(pos[1]-self.pos[1])*self.scl * Z, 0]
    def SetTarget(self, tgt):
        self.tgt = tgt
    def Update(self, dt):
        if keys[key.Z]:
            self.scl = 10.0
        else:
            self.scl = 1.0
        pass
    def Render(self,camera=None):
        pass

class Scene:
    def __init__(self, stuff=[]):
        self.stuff = stuff
        self.gel = pyglet.shapes.Rectangle(0,0, screenSize[0],screenSize[1], color=(64,128,255))
        self.gel.opacity = 128
    def MouseMotion(self, x,y,dx,dy):
        pass
    def PushMessage(self, msg):
        for thing in self.stuff:
            try:
                thing.HandleMessage(msg)
            except:
                pass
    def GetAll(self, t):
        temp = []
        for thing in self.stuff:
            if isinstance(thing, t):
                temp.append(thing)
        
        return temp
    def Remove(self,thing):
        try:
            del self.stuff[self.stuff.index(thing)]
            #print(len(self.stuff))
        except:
            print("not exist")
    def RemoveAllType(self, TYPE):
        i = 0
        while i < len(self.stuff):
            thing = self.stuff[i]
            if (isinstance(thing,TYPE)):
                self.Remove(thing)
            else:
                i+=1
        
    def RemoveAll(self):
        self.stuff = []
    def Add(self, thing, end=True):
        if end:
            self.stuff.append(thing)
        else:
            self.stuff = [thing] + self.stuff
    def Update(self,dt):
        for thing in self.stuff:
            thing.Update(dt)
    
    def Render(self):
        global camera
        for thing in self.stuff:
            thing.Render(camera)      

        self.gel.draw()





FNT = [ "A", MAKE([".11111.", ".11..1.", ".11..1.", "1111111", "11....1", "11....1", "11....1", ]), 
       "B", MAKE(["11111..", "11..1..", "11..1..", "1111111", "11....1", "11....1", "1111111", ]), 
       "C", MAKE(["1111111", "11.....", "11.....", "111....", "111....", "111....", "1111111", ]), 
       "D", MAKE(["111111.", "11...11", "11....1", "111...1", "111...1", "111..11", "111111.", ]), 
       "E", MAKE(["1111111", "11.....", "11.....", "11111..", "111....", "111....", "1111111", ]), 
       "F", MAKE(["1111111", "11.....", "11.....", "11111..", "111....", "111....", "111....", ]), 
       "G", MAKE(["1111111", "11....1", "11.....", "11.....", "11..111", "11...11", "1111111", ]), 
       "H", MAKE(["11....1", "11....1", "11....1", "1111111", "111...1", "111...1", "111...1", ]), 
       "I", MAKE(["1111111", "..11...", "..11...", "..111..", "..111..", "..111..", "1111111", ]), 
       "J", MAKE([".....11", ".....11", ".....11", ".....11", "1....11", "1....11", "1111111", ]), 
       "K", MAKE(["11...1.", "11...1.", "11...1.", "1111111", "111...1", "111...1", "111...1", ]), 
       "L", MAKE(["11.....", "11.....", "11.....", "111....", "111....", "111....", "1111111", ]), 
       "M", MAKE(["1111111", "11.11.1", "11.11.1", "11....1", "111...1", "111...1", "111...1", ]), 
       "N", MAKE(["1111111", "11....1", "11....1", "111...1", "111...1", "111...1", "111...1", ]), 
       "O", MAKE(["1111111", "11....1", "11....1", "11....1", "11....1", "11....1", "1111111", ]), 
       "P", MAKE(["1111111", "11....1", "11....1", "1111111", "111....", "111....", "111....", ]), 
       "Q", MAKE(["111111.", "11...1.", "11...1.", "111..1.", "111..1.", "111..1.", "1111111", ]), 
       "R", MAKE(["1111111", "11....1", "11....1", "1111111", "111..1.", "111..1.", "111..1.", ]), 
       "S", MAKE(["1111111", "11.....", "11.....", "1111111", "....111", "....111", "1111111", ]), 
       "T", MAKE(["1111111", "..11...", "..11...", "..11...", "..111..", "..111..", "..111..", ]), 
       "U", MAKE(["11....1", "11....1", "11....1", "111...1", "111...1", "111...1", "1111111", ]), 
       "V", MAKE(["11....1", "11....1", "11....1", "11...11", ".11..1.", ".11..1.", ".11111.", ]), 
       "W", MAKE(["11....1", "11....1", "11....1", "111...1", "111.1.1", "111.1.1", "1111111", ]), 
       "X", MAKE(["11....1", "11....1", "11...11", ".11111.", "1111111", "111...1", "111...1", ]), 
       "Y", MAKE(["11....1", "11....1", "11....1", "1111111", "...11..", "...11..", "...11.", ]), 
       "Z", MAKE(["1111111", "....111", "...111.", ".1111..", "1111...", "111....", "1111111", ]), 
       
       "a", MAKE([".......", 
                  ".......", 
                  ".......", 
                  ".111.1.", 
                  "11.111.", 
                  "11.111.", 
                  ".111.1."]), 

       "b", MAKE(["11.....", 
                  "11.....", 
                  "11.....", 
                  "11111..", 
                  "111.11.", 
                  "11..11.", 
                  "11111..", ]), 

       "c", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "111111.", 
                  "11.....", 
                  "11.....", 
                  "111111.", ]), 

       "d", MAKE(["....11.", 
                  "....11.", 
                  "....11.", 
                  ".11111.", 
                  "111.11.", 
                  "11..11.", 
                  ".11111.", ]),

       "e", MAKE([".......", 
                  ".......", 
                  ".1111..", 
                  "11...1.", 
                  "11111..", 
                  "11.....", 
                  ".1111..", ]), 

       "f", MAKE([".1111..", 
                  ".11.11.", 
                  ".11....", 
                  "1111...", 
                  ".11....", 
                  ".11....", 
                  ".11....", ]), 

       "g", MAKE([".......", 
                  "111111.", 
                  "1...11.", 
                  "1...11.", 
                  "111111.", 
                  "....11.", 
                  "111111.", ]), 

       "h", MAKE(["11.....", 
                  "11.....", 
                  "11.....", 
                  "11111..", 
                  "111.11.", 
                  "11...1.", 
                  "11...1.", ]), 

       "i", MAKE([".......", 
                  ".......", 
                  "..11...", 
                  ".......", 
                  "..11...", 
                  "..11...", 
                  "..11...", ]), 

       "j", MAKE([".......", 
                  "...11..", 
                  ".......", 
                  "...11..", 
                  "...11..", 
                  "1..11..", 
                  "11111..", ]), 

       "k", MAKE(["11.....", 
                  "11.....", 
                  "11.11..", 
                  "1111...", 
                  "111....", 
                  "1111...", 
                  "11.11..", ]), 

       "l", MAKE(["..11...", 
                  "..11...", 
                  "..11...", 
                  "..11...", 
                  "..11...", 
                  "..11...", 
                  "...11..", ]), 

       "m", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "1.1.1..", 
                  "111111.", 
                  "11.1.1.", 
                  "11...1.", ]), 

       "n", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "1.111..", 
                  "111.11.", 
                  "11...1.", 
                  "11...1.", ]), 

       "o", MAKE([".......", 
                  ".......", 
                  ".......", 
                  ".1111..", 
                  "11..11.", 
                  "11..11.", 
                  ".1111..", ]), 

       "p", MAKE([".......", 
                  ".......", 
                  ".1111..", 
                  "11..11.", 
                  "11..11.", 
                  "11111..", 
                  "11.....", ]), 

       "q", MAKE([".......", 
                  ".......", 
                  ".1111..", 
                  "11..11.", 
                  "11..11.", 
                  ".11111.", 
                  "....11.", ]), 

       "r", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "11.11..", 
                  "111111.", 
                  "11...1.", 
                  "11.....", ]), 

       "s", MAKE([".......", 
                  ".......", 
                  ".1111..", 
                  "11.....", 
                  ".1111..", 
                  "....11.", 
                  ".1111..", ]), 

       "t", MAKE(["..11...", 
                  "..11...", 
                  "..11...", 
                  ".1111..", 
                  "..11...", 
                  "..11...", 
                  "...11..", ]), 

       "u", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "11..11.", 
                  "11..11.", 
                  "111111.", 
                  ".1111..", ]),

       "v", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "11..11.", 
                  "11..11.", 
                  ".1111..", 
                  "..11...", ]), 

       "w", MAKE([".......", 
                  ".......", 
                  ".......", 
                  "11...1.", 
                  "11.1.1.", 
                  "111111.", 
                  ".11.1..", ]), 

       "x", MAKE([".......", 
                  ".......", 
                  "11..11.", 
                  "11..11.", 
                  ".1111..", 
                  "11..11.", 
                  "11..11.", ]), 

       "y", MAKE([".......", 
                  ".......", 
                  "11..11.", 
                  "11..11.", 
                  "111111.", 
                  "....11.", 
                  ".11111.", ]), 

       "z", MAKE([".......", 
                  ".......", 
                  "111111.", 
                  "....11.", 
                  "..111..", 
                  ".11....", 
                  "111111.", ]), 


        
       "~", MAKE([".......", ".......", ".11....", "1..1..1", "....11.", ".......", ".......", ]), 
       
       ".", MAKE([".......", ".......", ".......", ".......", "..111..", "..111..", "..111..", ]), 
       "!", MAKE(["11.....", "11.....", "11.....", "11.....", ".......", "11.....", "11.....", ]), 
       "@", MAKE(["1111111", "1.....1", "1.111.1", "1.1.1.1", "1.11111", "1......", "1111111", ]), 
       "#", MAKE([".......", ".......", ".1.1...", "11111..", ".1.1...", "11111..", ".1.1...", ]), 
       "$",##MUSICNOTE 
       MAKE([".......", "..1111.", "..1111.", "..1..1.", ".11.11.", ".11.11.", ".......", ]), 
       "%",##SPEAKER (VOLUME) 
       MAKE([".....11", "...1111", "1111111", "1111111", "1111111", "...1111", ".....11", ]), 
       

       ">", MAKE([".1.....", ".11....", ".111...", ".1111..", ".111...", ".11....", ".1.....", ]), 
       "<", MAKE(["....1..", "...11..", "..111..", ".1111..", "..111..", "...11..", "....1..", ]), 
       "?", MAKE(["1111111", ".....11", ".....11", "1111111", "11.....", ".......", "11.....", ]), 
       "}", MAKE(["1.1.1.1", "1.1.1.1", "1.1.1.1", "1.1.1.1", "1.1.1.1", "1.1.1.1", "1.1.1.1", ]), 
       "{", MAKE(["1.1.1..", "1.1.1..", "1.1.1..", "1.1.1..", "1.1.1..", "1.1.1..", "1.1.1..", ]), 
       "]", MAKE(["1.1....", "1.1....", "1.1....", "1.1....", "1.1....", "1.1....", "1.1....", ]), 
       "[", MAKE(["1......", "1......", "1......", "1......", "1......", "1......", "1......", ]), 
       "0", MAKE(["1111111", "11...11", "11..111", "11.11.1", "1111..1", "111...1", "1111111", ]), 
       "1", MAKE(["11111..", "..111..", "..111..", "..111..", "..111..", "..111..", "1111111", ]), 
       "2", MAKE(["1111111", ".....11", ".....11", "1111111", "11.....", "11.....", "1111111", ]), 
       "3", MAKE(["1111111", ".....11", ".....11", "..11111", ".....11", ".....11", "1111111", ]), 
       "4", MAKE(["1....11", "1....11", "1....11", "1111111", ".....11", ".....11", ".....11", ]), 
       "5", MAKE(["1111111", "11.....", "11.....", "1111111", ".....11", ".....11", "1111111", ]), 
       "6", MAKE(["1111111", "11.....", "11.....", "1111111", "11....1", "11....1", "1111111", ]), 
       "7", MAKE(["1111111", ".....11", ".....11", ".....11", ".....11", ".....11", ".....11", ]), 
       "8", MAKE(["1111111", "11....1", "11....1", "1111111", "11....1", "11....1", "1111111", ]), 
       "9", MAKE(["1111111", "1....11", "1....11", "1111111", ".....11", ".....11", ".....11", ]), 
       "+", MAKE([".......", "...1...", "...1...", ".11111.", "...1...", "...1...", ".......", ]), 
       "-", MAKE([".......", ".......", ".......", ".11111.", ".......", ".......", ".......", ]), 
       "|", MAKE(["...1...", "...1...", "...1...", "...1...", "...1...", "...1...", "...1...", ]), 
       "_", MAKE([".......", ".......", ".......", ".......", ".......", ".......", "1111111", ]), 
       "", MAKE(["1111111", "1111111", "111.111", "11...11", "1.....1", "1111111", "1111111", ]), 
       "", MAKE(["1111111", "1111111", "1.....1", "11...11", "111.111", "1111111", "1111111", ]), 
       "", MAKE(["1111111", "1111.11", "111..11", "11...11", "111..11", "1111.11", "1111111", ]), 
       "", MAKE(["1111111", "11.1111", "11..111", "11...11", "11..111", "11.1111", "1111111", ]), 
       ]

PLAYER = [
    MAKE([".000000.",
          "0000000.",
          ".0....0.",
          "..0000..",
          ".00000..",
          "0000000.",
          "0.00000.",
          "0000.000",
          ]),
    MAKE([".000000.",
          "0000000.",
          ".0....0.",
          "..0000..",
          ".00000..",
          ".0000000",
          ".00000.0",
          "0000.000",
          ]),
    
]

class AudioLiaison:
    def __init__(self, sysPtr):
        self.sysPtr = sysPtr

        self.memstr = ""
        self.outstrs = []

        
        self.prev = [0 for n in range(0,100)]
        self.prev2 = []
        self.pressed = False
        self.pressed2 = False
        self.pressed3 = False
        
        self.ptimer = 0.0

        self.active = True
        self.activatePress = True

        self.echo = False
    def Update(self,dt=0.0):
        if keys[key.GRAVE] and self.activatePress == False:
            self.active = not self.active
            self.activatePress = True

        if not keys[key.GRAVE]:
            self.activatePress = False        
        
        if not self.active:
            self.keys = [key.Q, key._2, key.W, key._3, key.E, key.R, key._5, key.T, key._6, key.Y, key._7, key.U, key.I, key._9, key.O, key._0, key.P, key.BRACKETLEFT, key.EQUAL, key.BRACKETRIGHT]
            i = 0
            for k in self.keys:
                if keys[k]:    
                    self.PushMessage("PLAYEXPLICIT "+str(39+i)+" "+str(i)+" 1.0 0.25 0.0")
                else:
                    self.PushMessage("STOP "+str(i))
                i+=1
        if self.active:
            i = 0
            prs = False
            self.alphanum = [key.A,key.B, key.C, key.D, key.E, key.F, key.G, key.H, key.I, key.J, key.K, key.L, key.M, key.N, key.O, key.P, key.Q, key.R, key.S, key.T, key.U, key.V, key.W, key.X, key.Y, key.Z, key._0, key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9, 
                            key.SPACE, key.PERIOD, key.MINUS]
            self.alphanum = [keys[a] for a in self.alphanum]

            if keys[key.ENTER] and not self.pressed2:
                self.PushMessage(self.memstr)
                
                self.memstr = ""
                self.pressed2 = True
                
            elif keys[key.BACKSPACE] and not self.pressed3:
                self.memstr = self.memstr[0:len(self.memstr)-1]
                self.pressed3 = True
                self.ptimer = 0.15
            elif keys[key.UP]:
                self.memstr = self.outstrs[len(self.outstrs)-1][1:]
            else:
                if self.alphanum.count(True) != 0:
                    K = self.alphanum.index(True)
                    if self.prev[K] == False:
                        self.memstr += ["abcdefghijklmnopqrstuvwxyz0123456789 .-",
                                        "ABCDEFGHIJKLMNOPQRSTUVWXYZ)!@#$%^&*( .-"][keys[key.LSHIFT]][K]
                
            
            if not (keys[key.ENTER]):
                self.pressed2 = False
            if not (keys[key.BACKSPACE]) or self.ptimer <= 0.0:
                self.pressed3 = False
            
            if self.ptimer >= 0.0:
                self.ptimer -= dt
            

            self.prev = self.alphanum

    def Render(self,camera=None):
        if self.active:
            FNT[FNT.index(">")+1].blit(16, 16, width=28,height=28)
            i = 0
            if self.memstr != "":
                
            
                for c in self.memstr:
                    if c != " ":
                        FNT[FNT.index(c)+1].blit(16+(i+1)*32, 16, width=28,height=28)
                    i+=1
            
            FNT[FNT.index("|")+1].blit(16+(i+1)*32, 16, width=28,height=28)
            j = 0
            for s in self.outstrs:
                i = 0
                for c in s:
                    if c != " ":
                        FNT[FNT.index(c)+1].blit(16+(i+1)*32, 32*(len(self.outstrs)+1) - (j * 32), width=28,height=28)
                    i+=1
                j+=1

    def PushMessage(self, msg):
        if self.echo:
            self.Print(">"+msg)
        o = self.sysPtr.HandleMessage(msg)
        self.Print(o)
    def Print(self,out):
        if out != "":
            self.outstrs += [out]
        if (len(self.outstrs) > 10):
            del self.outstrs[0]



uibatch = pyglet.graphics.Batch()
class ExampleEntity:
    def __init__(self, pos):
        self.pos = pos
        self.spr = pyglet.sprite.Sprite(img = PLAYER[0], x= 0,y=0, batch=uibatch)
        self.txt = pyglet.text.Label("onetwothree", x=0,y=0, font_size=16, batch=uibatch)
    def Update(self, dt):
        pass
    def Render(self, camera=None):
        #PLAYER[int(time.time()*4) % 2].blit(*camera.GetScreenCoords(self.pos), width=camera.scl*16, height=camera.scl*16)
        self.spr.scale = camera.scl * 8.0
        self.spr.position = camera.GetScreenCoords(self.pos)[0:2]
        #self.spr.draw()
        self.txt.draw()
    def HandleMessage(msg):
        pass


@window.event
def on_mouse_motion(x,y,dx,dy):
    #player.MouseUpdate(x,y,-1)
    scene.MouseMotion(x,y,dx,dy)
    pass

#window.event
@window.event
def on_mouse_release(x,y,btn,mod):
    #player.MouseUpdate(x,y,btn)
    print(x,y)
    pass
    
shouldClose = False
@window.event
def on_close():
    global shouldClose
    shouldClose = True

@window.event
def on_draw():
    window.clear()
    scene.Render()
    uibatch.draw()

audioSystem = Drippy(44100, 32)
audioMgr = AudioLiaison(audioSystem)
camera = Camera()
player = ExampleEntity(pos=[0,0])
camera.SetTarget(player)



##generator init
generator = Generator(audioMgr)

scene = Scene(
    [
        audioMgr,
        generator,
        camera,
        player,


        
     ]
)
window.set_vsync(True)
FPS = []
t = time.time()


#audioMgr.PushMessage("LOADSYNTH")
audioMgr.PushMessage("LOADPIANO")

while True:
    
    
    pyglet.clock.tick()
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()
    #call functions
    
    
    
    dt = time.time()-t
    scene.Update(dt)
    if dt > 0.0:
        FPS.append(int(1.0/dt))

        if len(FPS) > 100:
            del FPS[0]
        window.set_caption("FPS : "+str(int(sum(FPS)/len(FPS))))
    t = time.time()

    if shouldClose:
        window.close()
        sys.exit()
    


    
    
