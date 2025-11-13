import pyglet
from pyglet.window import key
from pyglet import shapes
import math,random,time,sys,os
from pyglet.gl import *

from pyglet.graphics import *

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
glClearColor(0.6,0.6,0.6,1)

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
        pass
    def Render(self,camera=None):
        pass

class Scene:
    def __init__(self, stuff=[]):
        self.stuff = stuff
        
        
        
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



class ExampleEntity:
    def __init__(self, pos):
        self.pos = pos
        #self.timer 0.0
    def Update(self, dt):
        #self.timer += dt
        pass
    def Render(self, camera=None):
        PLAYER[int(time.time()*4) % 2].blit(*camera.GetScreenCoords(self.pos), width=camera.scl*16, height=camera.scl*16)



@window.event
def on_mouse_motion(x,y,dx,dy):
    #player.MouseUpdate(x,y,-1)
    pass

#window.event
@window.event
def on_mouse_release(x,y,btn,mod):
    #player.MouseUpdate(x,y,btn)
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

camera = Camera()
player = ExampleEntity(pos=[0,0])
camera.SetTarget(player)
scene = Scene(
    [
        camera,
        player
     ]
)
window.set_vsync(False)
FPS = []
t = time.time()
while 0 == 0:
    
    
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
    


    
    
