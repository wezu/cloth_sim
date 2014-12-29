import direct.directbase.DirectStart

from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from panda3d.bullet import *
from direct.showbase.PythonUtil import fitSrcAngle2Dest
from direct.interval.IntervalGlobal import *
from player import PC
import json

class Game(DirectObject):

    def __init__(self):
        #base.disableMouse()  
        render.setShaderAuto()
        
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
        self.sLight.showFrustum() 
        self.Ambient = render.attachNewNode( self.sLight)        
        self.Ambient.setPos(0, -50,0)        
        self.Ambient.wrtReparentTo(base.camera)
        render.setLight(self.Ambient)
        render.setShaderInput("slight0", self.Ambient)        
        render.setShaderInput("plight0", self.pLightNode)
        
        self.player=PC(keymap)
        self.pLightNode.wrtReparentTo(self.player.actor)
        
        #cloth stuff        
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -9.81))    
        

        #self.debugNP = render.attachNewNode(BulletDebugNode('Debug'))
        #self.debugNP.show()
        #self.debugNP.node().showWireframe(True)
        #self.debugNP.node().showConstraints(True)
        #self.debugNP.node().showBoundingBoxes(False)
        #self.debugNP.node().showNormals(True)
        
        #self.world.setDebugNode(self.debugNP.node())
        
        # Soft body world information
        info = self.world.getWorldInfo()
        info.setAirDensity(0.2)
        info.setWaterDensity(0)
        info.setWaterOffset(0)
        info.setWaterNormal(Vec3(0, 0, 0))
        
        #load the skirt model
        model=loader.loadModel('models/skirt1.bam')
        geom = model.findAllMatches('**/+GeomNode').getPath(0).node().modifyGeom(0)                
        geomNode = GeomNode('')
        geomNode.addGeom(geom)      
        node = BulletSoftBodyNode.makeTriMesh(info, geom) 
        node.linkGeom(geomNode.modifyGeom(0))
        
        #material and properties setup        
        #node.getMaterial(0).setAngularStiffness(1) 	
        node.getMaterial(0).setLinearStiffness(0.5) 	
        #node.getMaterial(0).setVolumePreservation(0.001) 
        
        #node.generateBendingConstraints(10)
        
        #node.getCfg().setAeroModel(BulletSoftBodyConfig.AMFaceTwoSided  )
        node.getCfg().setDampingCoefficient(0.5)
        #node.getCfg().setDragCoefficient(0.0)
        #node.getCfg().setDriftSolverIterations(0.2)
        #node.getCfg().setDynamicFrictionCoefficient(0.0)
        #node.getCfg().setKineticContactsHardness(0.2)
        #node.getCfg().setLiftCoefficient(0.0)
        #node.getCfg().setMaxvolume(0.2)
        node.getCfg().setPoseMatchingCoefficient(0.2)
        #node.getCfg().setPositionsSolverIterations(0.2)
        #node.getCfg().setPressureCoefficient(0.0)
        #node.getCfg().setRigidContactsHardness(0.2)
        #node.getCfg().setSoftContactsHardness(0.2)
        #node.getCfg().setSoftVsKineticHardness(0.2)
        #node.getCfg().setSoftVsKineticImpulseSplit(0.2)
        #node.getCfg().setSoftVsRigidHardness(0.2)
        #node.getCfg().setSoftVsRigidImpulseSplit(0.2)
        #node.getCfg().setSoftVsSoftHardness(0.2)
        #node.getCfg().setSoftVsSoftImpulseSplit(0.2)
        #node.getCfg().setTimescale(0.2)
        #node.getCfg().setVelocitiesCorrectionFactor(0.0)
        #node.getCfg().setVelocitiesSolverIterations(0.2)
        #node.getCfg().setVolumeConversationCoefficient(0.0)  
        #node.getCfg().setCollisionFlag(BulletSoftBodyConfig.CFVertexFaceSoftSoft, True)        
        node.setPose (True, True)            
        #node.setTotalDensity(1.0) 	
        node.setTotalMass(10) 	
        #node.getShape(0).setMargin(0.5)
        #node.setVolumeDensity(1.0)
        #node.setVolumeMass(100)
        
        softNP = render.attachNewNode(node)
        self.world.attachSoftBody(node)
        geomNP = softNP.attachNewNode(geomNode)
        
        #pin it down
        self.hip_bone=self.player.actor.exposeJoint(None, 'modelRoot', 'Bip001 Pelvis')  
            
        self.pin = self.hip_bone.attachNewNode(BulletRigidBodyNode('pin')) 
        #The position of the skirt get's shifted, need t correct
        self.pin.setY(-2.6)
        #the model should know what verts to pin
        for vertex in json.loads(model.getTag('pins')):
            softNP.node().appendAnchor(softNP.node().getClosestNodeIndex(Vec3(*vertex), True), self.pin.node()) 
       
        #collisions
        #not working!
        bone1=self.player.actor.exposeJoint(None, 'modelRoot', 'Bip001 R Thigh')  
        shape = BulletCapsuleShape(3.0, 8.0, ZUp)
        np = bone1.attachNewNode(BulletRigidBodyNode('Capsule'))        
        np.node().addShape(shape)
        np.setHpr(0,90,90)
        np.setPos(6,0,0)
        np.setCollideMask(BitMask32.allOn())
        self.world.attachRigidBody(np.node())    
            
        # Task
        taskMgr.add(self.update, 'updateWorld')


    def update(self, task):
        dt = globalClock.getDt()
        #self.pin is a child of self.hip_bone but without these lines it won't work
        self.pin.setPos(render,self.hip_bone.getPos(render))
        self.pin.setHpr(render,self.hip_bone.getHpr(render))
        #do magic!
        self.world.doPhysics(dt, 10, 0.004)
        return task.cont
        
game = Game()
run()