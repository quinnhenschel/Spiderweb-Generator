import maya.cmds as cmds
import random as rnd
import math

# Definitions
ZV = 0.000000000000000000001  
rnd.seed()

if 'myWin' in globals():
    if cmds.window(myWin, exists=True):
        cmds.deleteUI(myWin, window=True)
        
if 'nextWebId' not in globals():
    nextWebId = 1000


##########################################          UI          ###########################################

myWin = cmds.window(title="Spider Web Generator", menuBar=True)

cmds.columnLayout(rowSpacing=20, adjustableColumn=True)
cmds.picture(image="F:\Desktop\Spiderweb-Generator\spiderWebs.png", h= 440, w=500)
cmds.intSliderGrp('density',l="Web Density", f=True, min=1, max=10, value=1)
cmds.intSliderGrp('hangAmount', l="Amount of Hang", f=True, min=1, max=20, value=1)
cmds.intSliderGrp('hangOffset', l="Hang Offset", f=True, min=-10, max=10, value=0)
cmds.intSliderGrp('webIntricacy', l="Web Intricacy", f=True, min=1, max=5, value=1)
cmds.intSliderGrp('random', l="Random Factor", f=True, min=0, max=10, value=1)               
cmds.button(label="Create Webs", command=('generateWebs()'), align='center', height=50)
cmds.intSliderGrp('stringThickness', l="Strand Thickness", f=True, min=1, max=20, value=1)               
cmds.button(label="Generate Geometry", command=('generateGeometry()'), align='center', height=50)
cmds.showWindow(myWin)




##########################################    High Level Procedures    ###########################################
    
def generateWebs():
    setDensity()
    setRandomness()
    setIntricacy()
    meshes = determineSelectedObjects()
    """ obj1/2 = list of faces as [face normal, center, pointCloud] """
    obj1 = findFaces(meshes[0])     
    obj2 = findFaces(meshes[1])
    """ pairs = list of start/end potential pairs as [startPointCloud, endPointCloud, midpoint] """
    pairs = curveFaces(obj1, obj2)  
    createCurve(pairs)
    processWebIntricacy()

def generateGeometry():
    webCurves = determineSelectedCurves()
    stringThickness = cmds.intSliderGrp('stringThickness', q=True, v=True)
    stringThickness = float(stringThickness)
    stringThickness = 0.002 * stringThickness 
    """ Create circle curve with radius based on stringThickness as webExtrudeMap """
    cmds.circle(nr=(0, 0, 0), c=(0, 0, 0), sw=360, r=stringThickness, n='webExtrudeMap')
    circleGeo = 'webExtrudeMap'
    
    for web in webCurves:
        #cmds.insertKnotCurve(web, p=(1), ch=True, nk=5, ib=True, rpo=True)
        """ Extrude circle curve along web curve to create geometry (po=0 is nurbs surface, po=1 is polygons, po=3 is bezier surface) """
        cmds.extrude(circleGeo, web, ch=True, rn=False, po=1, et=2, ucp=1, fpt=1, upn=1, rotation=0, scale=1, rsp=1, n='web')
        #with polygons the verticies are getting messed up in some places. We could maybe tesselate them at the end if we want to (next line)
        #cmds.nurbsToPoly(ch=True, f=2, n='web_GEO')

        cmds.delete(web)

    cmds.delete(circleGeo)
    #need to add a check here to flip normals if they are going the wrong way (in instead of out). Im honestly not sure how to do this but will come back

def createCurve(pairs):
    global nextWebId
   
    """ Offset broken up into two pieces: L/R side of the middle control vertex. Not allowed to be below 0. """
    hangOffset = cmds.intSliderGrp('hangOffset', q=True, v=True)
    hangOffset = float(hangOffset) 
    offsetCV1 = (hangOffset * -1) / 3 
    offsetCV3 = hangOffset / 5
    if(offsetCV1 < 0):
        offsetCV1 = 0
    if(offsetCV3 < 0):
        offsetCV3 = 0

    hangAmount = cmds.intSliderGrp('hangAmount', q=True, v=True)
    hangAmount = float(hangAmount)/8
    print "base", hangAmount

    for pair in pairs:
        for i in range (0, density):
            randomize = tick()
            ns = "Web" + str(nextWebId)

            """ Midpoint of curve for hang """
            midPoint = [0.0, 0.0, 0.0]
            midPoint[0] = pair[0][i][0] + (0.5 * (pair[1][i][0] - pair[0][i][0]))
            midPoint[1] = pair[0][i][1] + (0.5 * (pair[1][i][1] - pair[0][i][1]))
            midPoint[2] = pair[0][i][2] + (0.5 * (pair[1][i][2] - pair[0][i][2]))
        
            cmds.curve(degree=3, ep=[pair[0][i], midPoint, pair[1][i]], n=ns)



            if randomize:
                hang = randomizeMe(hangAmount, hangAmount + 2)
            else:
                hang = hangAmount
            
            """ Midpoint (ep[1]), and control verticy to L/R of it (cv[1], cv[3]) moved down to create web hang. Moving cv[1] and cv[3] also determines offset"""
            cmds.select(ns + ".ep[1]")
            cmds.move(0.0, -hang/1.5, 0.0, r=True)
            cmds.select(ns + ".cv[1]")
            cmds.move(0.0, -hang - offsetCV1, 0.0, r=True)
            cmds.select(ns + ".cv[3]")
            cmds.move(0.0, -hang - offsetCV3, 0.0, r=True)
            
            #validateCurve()

            if(webIntricacy > 1):
                cmds.rename((ns), ("processingIntricacy"),)

            nextWebId = nextWebId + 1
    print "Curves created"


def processWebIntricacy():
    pointsPerCurve = 6
    incriment = 1.0 / float(pointsPerCurve)
    
    cmds.select(("processingIntricacy*"))
    #cmds.move(0.0, -2.0, 0.0, r=True)
    webCurves = determineSelectedCurves()

    for web in webCurves:
        distanceAlongLine = 0 
        for i in range (0, pointsPerCurve):
            distanceAlongLine = distanceAlongLine + incriment
            if(distanceAlongLine == 1):
                break
            pointOnLine = cmds.pointOnCurve(web, top=True, pr=distanceAlongLine, p=True )
            cube = cmds.polyCube( sx=1, sy=1, sz=1, h=0.02, w=0.02, d=0.02)
            cmds.move(pointOnLine[0], pointOnLine[1], pointOnLine[2], r=True)









##########################################    General Procedures   ###########################################

def determineSelectedObjects():
    """ Create a list of all selected shapes """
    selectedShapes = cmds.ls(selection=True)
    meshList = []
    for shape in selectedShapes:
        if(cmds.objectType(shape) == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
        if(cmds.objectType(childShape) == 'mesh'):
            meshList.append(shape)

    # This to be taken out/adjusted for when we're ready for multiple shapes      
    if len(meshList) < 2:
        print ('Not enough shapes selected.')
    elif len(meshList) > 2:
        print ('Too many shapes. Only first two will be used.')
        meshList = meshList[0:2]

    return meshList
    
    
def determineSelectedCurves():
    selectedCurves = cmds.ls(selection=True)
    curveList = []
    for shape in selectedCurves:
        if(cmds.objectType(shape) == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
        if(cmds.objectType(childShape) == 'nurbsCurve'):
            curveList.append(shape)
      
    if len(curveList) < 1:
        print ('Not enough curves selected.')

    return curveList


def findFaces(mesh):
    faces = []
    faceCount = cmds.polyEvaluate(mesh, face=True)

    meshTransform = cmds.xform(mesh, query=True, matrix=True, worldSpace=True)
    
    for face in range(0, faceCount):
        faceName = mesh + ".f[" + str(face) + "]"
        vtxLst = cmds.polyInfo(faceName, faceToVertex=True) 
        vtxIdx = str(vtxLst[0]).split()
        vtxIdx = vtxIdx[2:]
        """ Vertex positions """
        vtxA = cmds.getAttr(mesh + ".vt[" + vtxIdx[0] + "]")   
        vtxB = cmds.getAttr(mesh + ".vt[" + vtxIdx[1] + "]")
        vtxC = cmds.getAttr(mesh + ".vt[" + vtxIdx[2] + "]")
        
        """ Make each vertex a list """
        vtxA = list(vtxA[0])
        vtxB = list(vtxB[0])
        vtxC = list(vtxC[0])
        
        """ Multiply verticies by transform matrix (convert to world space) """
        vtxA = matrixMult(meshTransform, vtxA)
        vtxB = matrixMult(meshTransform, vtxB)
        vtxC = matrixMult(meshTransform, vtxC)

        normal = getNormal(vtxA, vtxB, vtxC)

        """ Getting center of the face by querying the position of the move manipulator """
        cmds.select(faceName)
        cmds.setToolTo('moveSuperContext')
        centerPos = cmds.manipMoveContext('Move', q=True, p=True)

        """ Get range around center to place start/end point at """
        radius = [0.0 ,0.0, 0.0]
        vecAB = convertToVec(vtxA, vtxB)
        vecAC = convertToVec(vtxA, vtxC)
        for axes in range(0, len(vecAB)):
            radius[axes] = ((vecAB[axes] + vecAC[axes])/ 2.0)

        faceInfo = [normal, centerPos, radius]
        faces.append(faceInfo)
    print "Got faces"
    return faces


def curveFaces(obj1, obj2):
    """ Finds faces with opposite normals and close in distance """
    distances = []
    for start in obj1:
        tmp = []
        for end in obj2:
            distance = convertToVec(start[1], end[1])
            distance = getMagnitude(distance)
            """ distance = [distance, start center, start normal, end center, end normal, start radius, end radius] """
            distance = [distance, start[1], start[0], end[1], end[0], start[2], end[2]]
            tmp.append(distance)
        tmp.sort()
        """ Selecting faces closest together, should expand this for randomization """
        distances.append(tmp[0])

    pairs = []
    for item in distances:
        dp = getDotProduct(item[2], item[4])
        if dp < 0:
            """ Getting point cloud """
            startPE = getPlaneEq(item[1], item[2])
            startPoints = generatePointCloud(startPE, item[1], item[5])
            endPE = getPlaneEq(item[3], item[4])
            endPoints = generatePointCloud(endPE, item[3], item[6])

            pair = [startPoints, endPoints]
            pairs.append(pair)
    
    print "Got pairs"
    return pairs

def setDensity():
    global density
    density = cmds.intSliderGrp('density', q=True, v=True)

def setRandomness():
    global randomValue, randomTick
    randomValue = cmds.intSliderGrp('random', q=True, v=True)
    randomTick = 0 #(maxValue + 1) - randomValue

def setIntricacy():
    global webIntricacy
    webIntricacy = cmds.intSliderGrp('webIntricacy', q=True, v=True)














##########################################   Base Procedures   ###########################################

# def validateCurve():

def tick():
    global randomTick, randomValue
    maxValue = cmds.intSliderGrp('random', q=True, max=True)
    if randomTick >= (maxValue - randomValue)/2.5:
        randomTick = 0
        return True
    else:
        randomTick += 1
        return False


def randomizeMe(value, seed):
    newValue = value * rnd.uniform(1.0, seed)
    return newValue


def generatePointCloud(planeEq, POP, radius):
    global density
    spawnPoint = []

    for axes in range(len(POP)):    
        """ Moving the start point (POP) off of face along the normal """
        spawnPoint.append(POP[axes] + (planeEq[axes] * 0.3))    

    pointCloud = []
    point = []
    while len(pointCloud) < density:
        """ Generate random point to send new curve to """
        x = rnd.uniform((-1*(radius[0]/2.0)), (radius[0]/2.0))
        y = rnd.uniform((-1*(radius[1]/2.0)), (radius[1]/2.0))
        z = rnd.uniform((-1*(radius[2]/2.0)), (radius[2]/2.0))
        point = [POP[0] + x, POP[1] + y, POP[2]+z]

        """  Check that the line intersects the plane """
        POI = findIntersect(planeEq, spawnPoint, POP, point)
        if POI:
            pointCloud.append(POI)
        else:
            continue
    
    return pointCloud



def findIntersect(planeEq, startPoint, POP, endPoint):
    """  Check to see if the curve intersected the plane """
    vecStart = convertToVec(startPoint, POP) 
    vecEnd = convertToVec(endPoint, POP)
    kStart = (planeEq[0]*vecStart[0])+(planeEq[1]*vecStart[1])+(planeEq[2]*vecStart[2])
    kEnd = (planeEq[0]*vecEnd[0])+(planeEq[1]*vecEnd[1])+(planeEq[2]*vecEnd[2])

    if(((kStart>0.0) and (kEnd>0.0)) or ((kStart<0.0) and (kEnd<0.0))):
        """ Same side of plane, did not intersect """
        print "same side"
        return
    else:
        """  Intersected, find intersection point and add to pointCloud """
        tValue = getTValue(planeEq, startPoint, endPoint)
        if tValue == False:
            print ("denom zero")
        else:
            """  Sub t into line equation to get intersection point """
            POI = [0.0, 0.0, 0.0]
            POI[0] = startPoint[0] + (tValue * (endPoint[0] - startPoint[0]))
            POI[1] = startPoint[1] + (tValue * (endPoint[1] - startPoint[1]))
            POI[2] = startPoint[2] + (tValue * (endPoint[2] - startPoint[2]))
            return POI


def getTValue(pEq, PtA, PtB):
    denEq = 0.0
    nomEq = 0.0
    denEq=(pEq[0]*(PtA[0]-PtB[0]))+(pEq[1]*(PtA[1]-PtB[1]))+(pEq[2]*(PtA[2]-PtB[2]))
    
    if(abs(denEq) < ZV):
        print ("Denominator is Zero")
        return False
        
    nomEq = (pEq[0] * PtA[0]) + (pEq[1] * PtA[1]) + (pEq[2] * PtA[2]) + pEq[3]
    return(nomEq/denEq)


def getPlaneEq(vertex, normal):
    planeEq = [0.0, 0.0, 0.0, 0.0]
    planeEq[0] = normal[0] 
    planeEq[1] = normal[1]
    planeEq[2] = normal[2]
    planeEq[3] = 0 - (planeEq[0]*vertex[0] + planeEq[1]*vertex[1] + planeEq[2]*vertex[2])
    """  Check if they are colinear """
    if((abs(planeEq[0]) < ZV) and (abs(planeEq[1]) < ZV) and (abs(planeEq[2]) < ZV)):
        print("Error Points are Colinear")
        return False
        
    return planeEq


def matrixMult(Mtx, Pt):
    PtOut = [0.0, 0.0, 0.0, 0.0]
    """  Convert to Homogeneous Point """
    PtIn = [Pt[0], Pt[1], Pt[2], 1] 
    PtOut[0] =(Mtx[0]*PtIn[0])+(Mtx[4]*PtIn[1])+(Mtx[8]*PtIn[2])+(Mtx[12]*PtIn[3])
    PtOut[1] =(Mtx[1]*PtIn[0])+(Mtx[5]*PtIn[1])+(Mtx[9]*PtIn[2])+(Mtx[13]*PtIn[3])
    PtOut[2] =(Mtx[2]*PtIn[0])+(Mtx[6]*PtIn[1])+(Mtx[10]*PtIn[2])+(Mtx[14]*PtIn[3])
    PtOut[3] =(Mtx[3]*PtIn[0])+(Mtx[7]*PtIn[1])+(Mtx[11]*PtIn[2])+(Mtx[15]*PtIn[3])
    return(PtOut)


def getMagnitude(vec):
    value = 0
    for item in vec:
        value += item**2
  
    mag = math.sqrt(value)  
    return mag


def convertToVec(VtxA, VtxB):
    vec = ((VtxA[0]-VtxB[0]), (VtxA[1]-VtxB[1]), (VtxA[2]-VtxB[2]))
    return vec


def getCrossProduct(v1, v2):
    v = (((v1[1] * v2[2])-(v1[2] * v2[1])),((v1[2] * v2[0])-(v1[0] * v2[2])), ((v1[0] * v2[1])-(v1[1] * v2[0])))
    return v


def getNormal(VtxA, VtxB, VtxC):
    """ Convert to vectors """
    vBA = convertToVec(VtxB, VtxA)
    vCB = convertToVec(VtxC, VtxB)
  
    """ Cross Porduct """
    vNormal = getCrossProduct(vBA, vCB)
    magNormal = getMagnitude(vNormal)
    if(abs(magNormal) < ZV):
        print ("Magnitude is Zero")
    normal = ((vNormal[0] / magNormal), (vNormal[1] / magNormal), (vNormal[2] / magNormal))
    return normal

def getDotProduct(vA, vB):
    result = 0
    for item in range(len(vA)):
        result += (vA[item] * vB[item]) 

    return result 