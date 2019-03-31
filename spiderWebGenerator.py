import maya.cmds as cmds
import random as rnd

if 'myWin' in globals():
    if cmds.window(myWin, exists=True):
        cmds.deleteUI(myWin, window=True)
        
if 'nextWebId' not in globals():
    nextWebId = 1000

myWin = cmds.window(title="Spider Web Generator", menuBar=True)

cmds.columnLayout(rowSpacing=20, adjustableColumn=True)
cmds.picture(image="F:\Desktop\webs\spiderWebs.png", h= 440, w=500)
cmds.intSliderGrp('density',l="Web Density", f=True, min=1, max=10, value=1)
cmds.intSliderGrp('hangAmount', l="Amount of Hang", f=True, min=1, max=5, value=1)
cmds.intSliderGrp('webIntricacy', l="Web Intricacy", f=True, min=1, max=5, value=1)
cmds.button(label="Create Webs", command=('generateWebs()'), align='center', height=50)
cmds.button(label="Generate Geometry", command=('generateGeometry(webCurve)'), align='center', height=50)
cmds.showWindow(myWin)

def generateWebs():
    print "haaaa"

#this is just here right now to make a curve for generateGeometry to use before we impliment our functionality to add curves
webCurve = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), sw=160, r=0.3, n='webCurveMap')
webCurve = 'webCurveMap'
def generateGeometry(webCurve):
    stringThickness = 0.002  
    cmds.circle(nr=(0, 0, 0), c=(0, 0, 0), sw=360, r=stringThickness, n='webExtrudeMap')
    circleGeo = 'webExtrudeMap'
    cmds.extrude(circleGeo, webCurve, ch=True, rn=False, po=1, et=2, ucp=1, fpt=1, upn=1, rotation=0, scale=1, rsp=1)

    #need to add a check here to flip normals if they are going the wrong way (in instead of out)
    



