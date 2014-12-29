from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
import random
from direct.showbase.PythonUtil import fitSrcAngle2Dest

class PC(DirectObject):    
    
    def __init__(self, keymap):          
        #>>>>>>>>>>>>>>>>>>>>>actor<<<<<<<<<<<<<<<<<<<<<
        self.actor=Actor('models/model_girl',
                        {'idle':'models/anim_idle',
                         'die':'models/anim_die',
                         'push_button':'models/anim_push_button',
                         'run':'models/anim_run',
                         'take_hi':'models/anim_take_hi',
                         'take_low':'models/anim_take_low',
                         'take_mid':'models/anim_take_mid',
                         'use_comp':'models/anim_use_computer',
                         'strafe_l':'models/anim_strafe_l',
                         'strafe_r':'models/anim_strafe_r',
                         'reach':'models/anim_reach',
                         'walk':'models/anim_walk'}) 
        self.actor.setBlend(frameBlend = True) 
        self.actor.setH(180.0)         
        self.actor.loop("idle")         
        self.actor.reparentTo(render)
        self.actor.setShader(Shader.load("shaders/player_shader.cg"))  
        self.actor.find("**/hair").setShader(Shader.load("shaders/hair_shader.cg"))   
        
        #>>>>>>>>>>>>>>>>>>>>>key mapping:<<<<<<<<<<<<<<<<<<<<<        
        self.keyMap = {'key_forward': False,
                       'key_back': False,
                       'key_left': False,
                       'key_right': False,
                       'key_run': False}  
        #constant keys                    
        self.accept(keymap['key_forward'], self.keyMap.__setitem__, ["key_forward", True])                
        self.accept(keymap['key_forward']+"-up", self.keyMap.__setitem__, ["key_forward", False])
        self.accept(keymap['key_back'], self.keyMap.__setitem__, ["key_back", True])                
        self.accept(keymap['key_back']+"-up", self.keyMap.__setitem__, ["key_back", False])
        self.accept(keymap['key_left'], self.keyMap.__setitem__, ["key_left", True])                
        self.accept(keymap['key_left']+"-up", self.keyMap.__setitem__, ["key_left", False])
        self.accept(keymap['key_right'], self.keyMap.__setitem__, ["key_right", True])                
        self.accept(keymap['key_right']+"-up", self.keyMap.__setitem__, ["key_right", False])
        self.accept(keymap['key_run'], self.keyMap.__setitem__, ["key_run", True])                
        self.accept(keymap['key_run']+"-up", self.keyMap.__setitem__, ["key_run", False])
        #fire and forget keys:        
        #use
        self.accept(keymap['key_use'],self.use)
              
        
        #>>>>>>>>>>>>>>>>>>>>>Game Variables:<<<<<<<<<<<<<<<<<<<<<
        self.isIdle=True        
        self.lastPos=self.actor.getPos()       
        
        
        #>>>>>>>>>>>>>>>>>>>>>task:<<<<<<<<<<<<<<<<<<<<<
        taskMgr.add(self.update, "updatePC") 
        
    def use(self):
        pass
          
    def update(self, task):
        dt = globalClock.getDt()        
        self.isIdle=True
        anim=self.actor.getCurrentAnim()
        if anim not in ("walk","idle",'strafe_r','strafe_l',None):
            return task.cont         
        
        #move         
        self.lastPos=self.actor.getPos(render) 
        if self.keyMap["key_forward"]:             
            self.actor.setY(self.actor, -dt*40)
            self.isIdle=False
            self.actor.setPlayRate(1.0, "walk")
            if(anim!="walk"):
                self.actor.loop("walk")            
        if self.keyMap["key_right"]:                         
            self.actor.setH(self.actor, -dt*120)                        
            self.isIdle=False            
            if(anim!="walk"):
                self.actor.loop("walk")
        if self.keyMap["key_left"]:              
            self.actor.setH(self.actor, dt*120)            
            self.isIdle=False            
            if(anim!="walk"):
                self.actor.loop("walk")
        if self.keyMap["key_back"]:              
            self.actor.setY(self.actor, dt*40)
            self.isIdle=False
            self.actor.setPlayRate(-1, "walk") 
            if(anim!="walk"):
                self.actor.loop("walk")               
                 
        if self.isIdle:  
            if(anim!="idle"):
                self.actor.loop("idle")        
        return task.cont   