from panda3d.core import *
loadPrcFileData('','win-size 640 360')
loadPrcFileData('','undecorated 1')
loadPrcFileData('','show-frame-rate-meter 0')
#loadPrcFileData('','sync-video 1')
#loadPrcFileData('','threading-model Cull/Draw')
loadPrcFileData('','multisamples 2')

from direct.showbase.DirectObject import DirectObject
from panda3d.bullet import *
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from player import PC
import json

import direct.directbase.DirectStart


class Game(DirectObject):

    def __init__(self):
        #base.disableMouse()  
        render.setShaderAuto()
        render.setAntialias(AntialiasAttrib.MMultisample)
        
        keymap={'key_zoomin':'wheel_up',
                'key_zoomout':'wheel_down',
                'key_forward':'w',
                'key_back':'s',
                'key_left':'a',
                'key_right':'d',
                'key_run':'mouse2',
                'key_use':'mouse1'
                }
        #lights
        self.pLight = PointLight('plight')                
        self.pLight.setColor(VBase4(.7, .7, .8, 1))        
        #self.pLight.setAttenuation(Point3(0.0, 1.0, 0.0))         
        self.pLightNode = render.attachNewNode(self.pLight) 
        self.pLightNode.setPos(0,50,80.0)
        render.setLight(self.pLightNode)  
        
        self.sLight=Spotlight('sLight')        
        self.sLight.setColor(VBase4(0.9, 0.9, 0.9, 1))        
        spot_lens = PerspectiveLens()
        spot_lens.setFov(40)
        self.sLight.setLens(spot_lens)
        #self.sLight.showFrustum() 
        self.Ambient = render.attachNewNode( self.sLight)        
        self.Ambient.setPos(0, -50,0)        
        self.Ambient.wrtReparentTo(base.camera)
        render.setLight(self.Ambient)
        render.setShaderInput("slight0", self.Ambient)        
        render.setShaderInput("plight0", self.pLightNode)
        
        self.player=PC(keymap,'models/model_w_skirt')
        self.pLightNode.wrtReparentTo(self.player.actor)
        
        #cloth stuff               
        #rope for physics
        # World
        self.worldNP = render.attachNewNode('World') 
        #self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()

        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))
        #self.world.setDebugNode(self.debugNP.node())

        # Soft body world information
        info = self.world.getWorldInfo()
        info.setAirDensity(1.2)
        info.setWaterDensity(0)
        info.setWaterOffset(0)
        info.setWaterNormal(Vec3(0, 0, 0))
        #pin node
        self.hip_bone=self.player.actor.exposeJoint(None, 'modelRoot', 'Bip001 Pelvis')              
        self.pin = self.worldNP.attachNewNode(BulletRigidBodyNode('pin')) 
        #self.pin.setPos(render,self.hip_bone.getPos(render))
        
        #rope1
        #from_pos=self.hip_bone.getPos(render)
        from_pos=(0,0,30)
        to_pos=(0,0,0)
        ropeNode = BulletSoftBodyNode.makeRope(info, from_pos, to_pos, res=3, fixeds=0) 
        #material and properties setup        	
        ropeNode.getMaterial(0).setLinearStiffness(0.1) 	
        ropeNode.getMaterial(0).setAngularStiffness(0.9)
        ropeNode.getCfg().setDampingCoefficient(0.6)        
        ropeNode.getCfg().setPoseMatchingCoefficient(0.1)
        ropeNode.setPose (True, True) 
        ropeNode.setTotalMass(1.0)
        ropeNP = self.worldNP.attachNewNode(ropeNode)
        self.world.attachSoftBody(ropeNode)
                
        # Box
        shape = BulletBoxShape(Vec3(1, 1,1))
        self.boxNP = self.worldNP.attachNewNode(BulletRigidBodyNode('Box'))
        self.boxNP.node().setMass(15.0)
        self.boxNP.node().addShape(shape)
        self.boxNP.setPos(0, 0, 0)
        self.world.attachRigidBody(self.boxNP.node())        
        ropeNP.node().appendAnchor(0, self.pin.node()) 
        ropeNP.node().appendAnchor(ropeNP.node().getNumNodes() - 1, self.boxNP.node())
        
        #ref node
        self.ref_node=render.attachNewNode('ref_node')
        self.ref_node.wrtReparentTo(self.player.actor)        
        
        # Task
        taskMgr.add(self.update, 'updateWorld')


    def update(self, task):
        dt = globalClock.getDt()  
        self.pin.setTransform(self.player.actor.getTransform(render))
        #self.pin.setPos(render,self.hip_bone.getPos(render))
        #self.pin.setHpr(render,self.hip_bone.getHpr(render))             
        #do magic!
        self.world.doPhysics(dt, 10, 0.004)
        pos=self.boxNP.getPos(self.ref_node)
        offset=Vec4(pos[0],pos[1],pos[2],0)
        render.setShaderInput("offset",offset)        
        return task.cont
        
        
        
game = Game()
run()