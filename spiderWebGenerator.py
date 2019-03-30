import maya.cmds as cmds
import random as rnd

if 'myWin' in globals():
    if cmds.window(myWin, exists=True):
        cmds.deleteUI(myWin, window=True)
        
if 'nextWebId' not in globals():
    nextWebId = 1000

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

def generateWebs():
    print "haaaa"





