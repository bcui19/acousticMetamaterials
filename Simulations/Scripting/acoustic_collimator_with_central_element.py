'''
Working on scripting for salome to create
acoustic collimators 
'''

import numpy as np 
import os
import sys
import salome

salome.salome_init()


import GEOM
from salome.geom import geomBuilder
geompy = geomBuilder.New(salome.myStudy)
gg = salome.ImportComponentGUI("GEOM")


import SMESH, SALOMEDS
from salome.smesh import smeshBuilder
smesh = smeshBuilder.New(salome.myStudy)

from multiprocessing import Pool
import glob

import math

#define constants
CENTER_DIM = 0.006
BOX_LENGTH = 0.002
NUM_PORTS = 4

OUTPUT_DIR = "pillar_simulations/biggerIt"

#creates an acoustic collimator in teh geometry module
class acousticCollimator:
    def __init__(self, H, L, cR, bottomVary):
        self.H = H
        self.L = L
        self.cR = cR
        self.bottomVary = bottomVary
        self.createCollimator()

    def createCollimator(self):
       self.createCenter()
       self.createSmallBoxes()
       self.geompyList.append(self.centerBox)
       unit_cell = geompy.MakeFuseList(self.geompyList)
       self.makeCylinder()
       self.unit_cell = geompy.MakeCut(unit_cell, self.cylinder)

       geompy.addToStudy(self.unit_cell, "temp")

    #makes 
    def makeCylinder(self):
        x = y = (CENTER_DIM - 2*self.L)/2
        pnt1 = geompy.MakeVertex(x, y, 0)
        pnt2 = geompy.MakeVertex(x, y, self.H)
        vector = geompy.MakeVector(pnt1, pnt2) #vector associated with the center of the cylinder
        self.cylinder = geompy.MakeCylinder(pnt1, vector, self.cR, self.H)

    #creates a box that is defined by self.centerBox
    #ensures the bounding box is always of the same size
    def createCenter(self):
        self.curCenterDim = CENTER_DIM - 2*self.L
        pnt1 = geompy.MakeVertex(0, 0, 0)
        pnt2 = geompy.MakeVertex(self.curCenterDim, self.curCenterDim, self.H) #self.H is the dimension to cover the height of the box
        self.centerBox = geompy.MakeBoxTwoPnt(pnt1, pnt2)

    #creates teh surrounding smaller boxes
    def createSmallBoxes(self):
        self.geompyList = []
        self.difPoint = (self.curCenterDim-BOX_LENGTH)/2 #constant from origin to current point
        for i in range(NUM_PORTS):
            self.createBox(i)

        for i in range(NUM_PORTS):
            self.createBottomBox(i)

    def createBox(self, iterNum):
        self.defPnt1(iterNum)
        pnt1 = geompy.MakeVertex(self.x, self.y, self.H)
        print "point 1 coordinates are (", self.x, ", ", self.y, ",", self.H, ")"

        self.defPnt2(iterNum)
        pnt2 = geompy.MakeVertex(self.x, self.y, self.H-BOX_LENGTH)
        print "point 2 coordinates are (", self.x, ", ", self.y, ", ", self.H-BOX_LENGTH, ")"
        
        currBox = geompy.MakeBoxTwoPnt(pnt1, pnt2)
        self.geompyList.append(currBox)

    def createBottomBox(self, iternum):
        self.defPnt1_Bottom(iternum)
        pnt1 = geompy.MakeVertex(self.x, self.y, 0)


        self.defPnt2_Bottom(iternum)
        pnt2 = geompy.MakeVertex(self.x, self.y, BOX_LENGTH)

        currBox = geompy.MakeBoxTwoPnt(pnt1, pnt2)
        self.geompyList.append(currBox)


    def defPnt1(self, iterNum):
        #print iterNum
        self.x = self.difPoint if iterNum == 0 or iterNum == 2 else 0 if iterNum == 1 else self.curCenterDim
        self.y = 0 if iterNum == 0 else self.curCenterDim if iterNum == 2 else self.difPoint

    def defPnt2(self, iterNum):
        self.x = self.difPoint +BOX_LENGTH if iterNum == 0 or iterNum == 2 else -self.L if iterNum ==1 else self.curCenterDim + self.L
        self.y = -self.L if iterNum == 0 else self.curCenterDim + self.L if iterNum == 2 else self.difPoint + BOX_LENGTH

    def defPnt1_Bottom(self, iterNum):
        #print iterNum
        self.x = self.difPoint if iterNum == 0 or iterNum == 2 else 0 if iterNum == 1 else self.curCenterDim
        self.y = 0 if iterNum == 0 else self.curCenterDim if iterNum == 2 else self.difPoint

    def defPnt2_Bottom(self, iterNum):
        self.x = self.difPoint +BOX_LENGTH if iterNum == 0 or iterNum == 2 else -self.L/self.bottomVary if iterNum ==1 else self.curCenterDim + self.L/self.bottomVary
        self.y = -self.L/self.bottomVary if iterNum == 0 else self.curCenterDim + self.L/self.bottomVary if iterNum == 2 else self.difPoint + BOX_LENGTH




    def returnUnitCell(self):
        return self.unit_cell

class meshing:
    def __init__(self, unit_cell, H, L, outputFile):
        #define class variables
        self.unit_cell = unit_cell
        self.H = H
        self.L = L
        self.out_med = outputFile

        #call methods
        self.mesh()
        self.getBoundaryConditions()
        self.outputMed()

    def mesh(self):
        self.allfaces = geompy.SubShapeAllSortedCentres(self.unit_cell, geompy.ShapeType["FACE"])
        self.getPorts()

        print ' -create geometry mesh'

        self.tetra = smesh.Mesh(self.unit_cell, 'unit_cell')

        algo1D = self.tetra.Segment()
        algo1D.LocalLength(0.0006)

        algo2D = self.tetra.Triangle()
        algo2D.LengthFromEdges()

        algo3D = self.tetra.Tetrahedron()
        algo3D.MaxElementVolume(100)

        retVal = self.tetra.Compute()

        if retVal == 0:
            print 'Problem when computing mesh'
        else:
            print 'Mesh computed, # mesh nodes: %u ' %(self.tetra.NbNodes())

        self.tetra.ConvertToQuadratic(theForce3d=0)
        print 'Converted to quadratic mesh, #mesh nodes : %u' %(self.tetra.NbNodes())

    #hacky way to get the ENTREE and SORTIE, probably will not work if Z growth is not monotonic
    def getPorts(self):
        cm_minX = 9999
        cm_maxX = -9999
        cm_minY = 9999
        cm_maxY = -9999
        #cm_minZ = 9999
        #cm_maxZ = -9999
        
        PORT1 = len(self.allfaces) #cast error if not updated
        PORT2 = len(self.allfaces) #cast error if not updated
        PORT3 = len(self.allfaces) #cast error if not updated
        PORT4 = len(self.allfaces) #cast error if not updated
        #PORT5 = len(self.allfaces) #cast error if not updated
        #PORT6 = len(self.allfaces) #cast error if not updated
       
        for ii in range(0, len(self.allfaces)):

            cm = geompy.PointCoordinates(geompy.MakeCDG(self.allfaces[ii]))
            print cm[1], cm_minY
            
            if cm[1] < cm_minY:
                cm_minY = cm[1]
                PORT1 = ii
            if cm[1] > cm_maxY:
                cm_maxY = cm[1]
                PORT3 = ii
            if cm[0] < cm_minX:
                cm_minX = cm[0]
                PORT2 = ii
            if cm[0] > cm_maxX:
                cm_maxX = cm[0]
                PORT4 = ii

        #define new variables so they're class variables but shouldn't change anything?
        self.PORT1 = self.allfaces[PORT1]
        self.PORT2 = self.allfaces[PORT2]
        self.PORT3 = self.allfaces[PORT3]
        self.PORT4 = self.allfaces[PORT4]

        #list of ports
        portList = [self.PORT1, self.PORT2, self.PORT3, self.PORT4]


        for i in range(len(portList)):
            id_PORT = geompy.addToStudyInFather(self.unit_cell, portList[i], "PORT" + str(i))

    def getBoundaryConditions(self):
        self.centerPoint = (CENTER_DIM - 2 * self.L)/2
        

        print 'Grouping boundary condition nodes'

        self.group_PORT1 = self.tetra.GroupOnGeom(self.PORT1, 'PORT1')
        self.group_PORT2 = self.tetra.GroupOnGeom(self.PORT2, 'PORT2')
        self.group_PORT3 = self.tetra.GroupOnGeom(self.PORT3, 'PORT3')
        self.group_PORT4 = self.tetra.GroupOnGeom(self.PORT4, 'PORT4')

        self.ID_listen_list = []

        #listen_node = (CENTER_DIM/2, -self.L/2, self.H-self.L/2)
        #print'extracting node nearest to ', listen_node
        #ID_listen = self.tetra.FindNodeClosestTo(listen_node[0], listen_node[1], listen_node[2])

        #x,y,z = self.tetra.GetNodeXYZ(ID_listen)
        #print 'Extracted node %u has position' %(ID_listen), (x,y,z)
        #self.ID_listen_list.append(ID_listen)

        #self.nodeCheck()
        #self.getFaceNodes()
    
        for i in range(NUM_PORTS):
            self.generateNodes(i)

        print self.ID_listen_list
        
        #print 'Extracted node %u grouped to patch LISTEN' %(ID_listen)
        group_LISTEN = self.tetra.MakeGroupByIds('LISTEN', SMESH.NODE, self.ID_listen_list)        


    #generates the nodes for the collimator
    def generateNodes(self, iterNum):
        x = self.centerPoint if iterNum == 0 or iterNum == 2 else -self.L if iterNum == 1 else self.centerPoint*2 + self.L
        y = self.centerPoint if iterNum == 1 or iterNum == 3 else -self.L if iterNum == 0 else self.centerPoint*2 + self.L
        z = self.H - BOX_LENGTH/2

        
        self.ID_listen = self.tetra.FindNodeClosestTo(x, y, z)
        x,y,z = self.tetra.GetNodeXYZ(self.ID_listen)
        print "Extracted node %u has position " %(self.ID_listen), (x,y,z)

        self.ID_listen_list.append(self.ID_listen)

    def getFaceNodes(self):
        face_nodes = self.group_PORT4.GetNodesId()
        print face_nodes

    #actually not quite sure if this acts as a node check
    #I should really ask LiDing about this
    def nodeCheck(self):
        nodes_on_face = []
        all_nodes = self.tetra.GetElementsId()
        all_nodes = self.tetra.GetNodesId()
        for node_id in all_nodes:
            xyz = self.tetra.GetNodeXYZ(node_id)
            if (xyz[0] < 10e-5):
                nodes_on_face.append(node_id)
            print "xyz is: ", xyz
        #print nodes_on_face

    def outputMed(self):
        if self.out_med is not None:
            file_med = "%s.med" %(self.out_med)
            print "Export med mesh is %s" %(file_med)

            self.tetra.ExportMED(file_med)
            file_listen = "%s.listennode" %(self.out_med)

            print "Recorded listen node ID is: %s " %(file_listen)

            of = open(file_listen, "w")

            if isinstance(self.ID_listen_list, list):
                for i in range(len(self.ID_listen_list)):
                    of.write("PORT%u N%u\n" %(i, self.ID_listen_list[i]))
            else:
                of.write("PORT%u N%u\n" %(0, self.ID_listen))
            of.close()

class massiveGeneration:
    def __init__(self, Hmin, Hmax, Hnum, Lmin, Lmax, Lnum, rMin, rMax, rNum, varNum):
        self.Hmin = Hmin
        self.Hmax = Hmax
        self.Hnum = Hnum
        self.Lmin = Lmin
        self.Lmax = Lmax
        self.Lnum = Lnum
        self.rMin = rMin
        self.rMax = rMax
        self.rNum = rNum
        self.bottomVary = varNum
        self.Dir = os.path.dirname(__file__)
       
        self.HList = [self.Hmin + (self.Hmax-self.Hmin)/Hnum * i for i in range(Hnum+1)]
        self.Llist = [self.Lmin + (self.Lmax-self.Lmin)/Lnum * i for i in range(Lnum+1)]
        self.rList = [self.rMin + (self.rMax-self.rMin)/rNum * i for i in range(rNum+1)]
        
        print "rList is: ", self.rList

        self.createStructures()

    def createStructures(self):
        for currH in self.HList:
            for currL in self.Llist:
                for currR in self.rList: 
                    for vary in range(2, self.bottomVary):
                        currDir = os.path.join(OUTPUT_DIR, "unit_cell_H%f_L%f_R%f_V%d" %(currH, currL, currR, vary))
                        
                        if os.path.exists(currDir):
                            continue


                        #if not os.path.exists(currDir):
                        collimator = acousticCollimator(currH, currL, currR, vary)
                        unit_cell = collimator.returnUnitCell()
                        
                        currDir = os.path.join(OUTPUT_DIR, "unit_cell_H%f_L%f_R%f_V%d" %(currH, currL, currR, vary))

                        if not os.path.exists(currDir):
                            print "the directory doesn't exist"
                        
                            os.makedirs(currDir)
                            out_med =  "unit_cell_H%f_L%f_R%f_V%d" %( currH, currL, currR, vary)
        
                        medPath = os.path.join(self.Dir, currDir, out_med)
        
                        meshing(unit_cell, currH, currL, medPath)
 
if __name__ == "__main__":
    massiveGeneration(0.0040001, 0.01, 14, 0.00001, 0.002, 14, 0.0001, 0.00098, 15, 5)
    
    #    collimator = acousticCollimator(0.006, 0.0005)
#    unit_cell = collimator.returnUnitCell()
#    out_med = "output_file"
#    Meshing(unit_cell, 0.006, 0.0005, out_med)


