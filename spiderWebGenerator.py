import maya.cmds as cmds
import random as rnd
import math
ZV = 0.000000000000000000001  # Zero value to compare against

if 'myWin' in globals():
    if cmds.window(myWin, exists=True):
        cmds.deleteUI(myWin, window=True)
        
if 'nextWebId' not in globals():
    nextWebId = 1000


##########################################          UI          ###########################################

myWin = cmds.window(title="Spider Web Generator", menuBar=True)

cmds.columnLayout(rowSpacing=20)
cmds.picture(image="F:\Desktop\webs\spiderWebs.png", h= 250, w=200)
cmds.intSliderGrp('density',l="Web Density", f=True, min=1, max=10, value=1)
cmds.intSliderGrp('hangAmount', l="Amount of Hang", f=True, min=1, max=5, value=1)
cmds.intSliderGrp('webIntricacy', l="Web Intricacy", f=True, min=1, max=5, value=1)
cmds.button(label="Create Webs", command=('generateWebs()'))
#cmds.setParent( '..' )
#cmds.setParent( '..' )

cmds.showWindow(myWin)



##########################################    Doing The Thing    ###########################################

def generateWebs():
    meshes = determineSelectedObjects()
    obj1 = findFaces(meshes[0])     # Returns list of faces as [face normal, center, vertexA, vtxB, vtxC, vtxD]
    obj2 = findFaces(meshes[1])
    pairs = curveFaces(obj1, obj2)  # Return list if start/end potential pairs as [start point, end point, midpoint]
    createCurve(pairs)




##########################################    Setup Functions   ###########################################

def determineSelectedObjects():
    # Create a list of all selected shapes
    selectedShapes = cmds.ls(selection=True)
    meshList = []
    for shape in selectedShapes:
        if(cmds.objectType(shape) == 'transform'):
            childShape = cmds.listRelatives(shape, fullPath=True, shapes=True)
        if(cmds.objectType(childShape) == 'mesh'):
            meshList.append(shape)

    # Adjusting mesh list so it's only first 2 objects used        
    if len(meshList) < 2:
        print ('Not enough shapes selected.')
    elif len(meshList) > 2:
        print ('Too many shapes. Only first two will be used.')
        meshList = meshList[0:2]
    return meshList


def findFaces(mesh):
    faces = []
    faceCount = cmds.polyEvaluate(mesh, face=True)

    meshTransform = cmds.xform(mesh, query=True, matrix=True, worldSpace=True)
    # center = getfacecenters()
    
    for face in range(0, faceCount):
        faceName = mesh + ".f[" + str(face) + "]"
        vtxLst = cmds.polyInfo(faceName, faceToVertex=True) 
        vtxIdx = str(vtxLst[0]).split()
        vtxIdx = vtxIdx[2:]
        # Vertex positions
        vtxA = cmds.getAttr(mesh + ".vt[" + vtxIdx[0] + "]")   
        vtxB = cmds.getAttr(mesh + ".vt[" + vtxIdx[1] + "]")
        vtxC = cmds.getAttr(mesh + ".vt[" + vtxIdx[2] + "]")
        #vtxD = cmds.getAttr(mesh + ".vt[" + vtxIdx[3] + "]")
        
        #Make each vertex a list    
        vtxA = list(vtxA[0])
        vtxB = list(vtxB[0])
        vtxC = list(vtxC[0])
        #vtxD = list(vtxD[0])
        
        # Multiply verticies by transform matrix (convert to world space)
        vtxA = matrixMult(meshTransform, vtxA)
        vtxB = matrixMult(meshTransform, vtxB)
        vtxC = matrixMult(meshTransform, vtxC)
        #vtxD = matrixMult(meshTransform, vtxD)

        normal = getNormal(vtxA, vtxB, vtxC)

        # Getting center of the face
        cmds.select(faceName)
        cmds.setToolTo('moveSuperContext')
        centerPos = cmds.manipMoveContext('Move', q=True, p=True)

        faceInfo = [normal, centerPos, vtxA[:3], vtxB[:3], vtxC[:3]]
        faces.append(faceInfo)
    return faces


def curveFaces(obj1, obj2):
    #Finds faces with opposite normals and close in distance
    distances = []
    for start in obj1:
        tmp = []
        for end in obj2:
            distance = convertToVec(start[1], end[1])
            distance = getMagnitude(distance)
            distance = [distance, start[1], start[0], end[1], end[0]]
            tmp.append(distance)
        tmp.sort()
        distances.append(tmp[0])

    pairs = []
    for item in distances:
        dp = getDotProduct(item[2], item[4])
        if dp < 0:
            # Center (for hang)
            midPoint = [0.0, 0.0, 0.0]
            midPoint[0] =  item[1][0] + (0.5 * (item[3][0] -item[1][0]))
            midPoint[1] =  item[1][1] + (0.5 * (item[3][1] -item[1][1]))
            midPoint[2] =  item[1][2] + (0.5 * (item[3][2] -item[1][2]))

            pair = [item[1], item[3], midPoint]
            pairs.append(pair)
         
    return pairs


##########################################     Bezier Curve     ###########################################


def createCurve(pairs):
    for pair in pairs:
        cmds.curve(bez=True, degree=3, p=[pair[0], pair[0], pair[2], pair[2], pair[2], pair[1], pair[1]], k=[0,0,0,1,1,1,2,2,2])





##########################################   Helper Functions   ###########################################


def matrixMult(Mtx, Pt):
    PtOut = [0.0, 0.0, 0.0, 0.0]
    PtIn = [Pt[0], Pt[1], Pt[2], 1] # Convert to Homogeneous Point
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
    #Convert to vectors
    vBA = convertToVec(VtxB, VtxA)
    vCB = convertToVec(VtxC, VtxB)
  
    #Cross Porduct
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