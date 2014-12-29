from panda3d.core import *
from direct.directbase import DirectStart
import json
import os, sys

def FindAllVertex(input, look_for):    
    input_egg=file(input, 'r')
    lastVertex=None
    isVertexPos=False  
    foundList=[]    
    for line in input_egg.readlines():
        if isVertexPos:
            vertex=line.split()
            lastVertex=(float(vertex[0]),float(vertex[1]),float(vertex[2]))
            isVertexPos=False
        else:
            if line.strip().startswith('<Vertex>'): 
                isVertexPos=True
            elif line.strip().startswith(look_for): 
                foundList.append(lastVertex)  
    input_egg.close()
    return foundList

if __name__ == "__main__":
    model_path='models/skirt1.egg'
    pinVerts=FindAllVertex(model_path, '<RGBA> { 1 0 0 1 }')
   
    model=loader.loadModel(model_path)
    model.setColor(1,1,1,1)
    model.setTag('pins',json.dumps(pinVerts))
    model.writeBamFile(model_path[:-4]+".bam") 
    #test
    from_bam=loader.loadModel(model_path[:-4]+".bam")
    for vertex in json.loads(from_bam.getTag('pins')):
        print vertex
    