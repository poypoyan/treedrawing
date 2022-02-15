# Tree Drawing Example
#
# This script outlines how to use tdcore.py. For now, the only main
# function to work on is tdcore.drawTree(), which is for initial drawing;
# drawing of edited input tree is todo.
#
# tdcore.drawTree arguments (in order):
#     * inputTree: object
#               the object/pointer of input raw tree
#     * rootName: str
#               string to be set as the root node
#     * outDir: str
#               direction of 'spreading' of the tree;
#               one in {'U', 'D', 'L', 'R'}
#     * sideRelDir: str
#               direction of where to put the child with highest
#               weight in the first branching out; one in {'CW', 'CCW'};
#               this is not critical, so both are fine
#     * countTree: Callable - function for counting all nodes
#     * getChildNodes: Callable - function for getting the list of child
#               nodes of a given node
#
# tdcore.drawTree outputs (in order):
#     * connecNodes: list
#               connecNodes[nodeIdx] is the list of node indices
#               connected to nodeIdx
#     * labelDict: dict
#               assigns node index (type int) to named nodes
#     * coordNodes: list
#                coordNodes[nodeIdx] is the (x, y) coords of nodeIdx
#     * weightNodes: list
#                weightNodes[nodeIdx] is the 'weight' of nodeIdx
#                most likely not useful to the user
#     * majorNodes: list
#                majorNodes[nodeIdx] is the list of 'major' nodes 
#                above nodeIdx; None if nodeIdx is 'minor'
#                most likely not useful to the user

import tdcore
import pickle

# Execute tdcore.removeTraceback() to remove remove traceback from error
# /exception messages. The algorithms of tree drawing do recursion.
# Hence when there is error during recursion, removing traceback hides
# potentially several lines of text, and just prints the relevant error
# info. To reset this, execute tdcore.restoreTraceback().
tdcore.removeTraceback()

# tdcore only works with trees with named nodes
treeX = {
    'node0':['node1'],
    'node1':['node2','node3','node4'],
    'node2':['node5','node6'],
    'node3':['node7','node8'],
    'node4':['node9'],
    'node5':['node10','node11','node12'],
    'node6':[],
    'node7':['node13'],
    'node8':[],
    'node9':['node14'],
    'node10':[],
    'node11':['node15','node17'],
    'node12':['node18'],
    'node13':[],
    'node14':['node16'],
    'node15':[],
    'node16':[],
    'node17':[],
    'node18':[]
}

# countTree: count the total number of nodes
def countTree(inputTree: object) -> int:
    return len(inputTree)

# getChildNodes: get the 'content' of node in raw tree
def getChildNodes(inputTree: object, nodeName: str) -> list:
    return inputTree[nodeName]

# svgOutput: SVG (in HTML) visual output
# note: in SVG coordinates, the vertical coordinate is reversed:
#       if outDir is 'U' (up), then SVG drawing goes down, and vice versa
def svgOutput(connecNodes, labelDict, coordNodes, weightNodes, majorNodes):
    svgSize = (80*16, 80*7)   # width/x, height/y
    origin = (80*8, 80*1)   # width/x, height/y
    zoom = (60, 60)   # width/x, height/y
    # write html with svg
    with open("TreeDrawing.html", "w") as out:
        out.write("<!DOCTYPE html>\n<html>\n<title>Rooted Tree Drawing Output</title>\n<body>\n")
        out.write("<svg width=\"" + str(svgSize[0]) + "\" height=\"" + str(svgSize[1]) + "\" ")
        out.write("style=\"border-style:solid;\">\n")
        for i in labelDict:
            nodeNum = labelDict[i]
            if coordNodes[nodeNum] == None:
                continue   # ignore disconnected nodes
            x1 = coordNodes[nodeNum][0] * zoom[0] + origin[0]
            y1 = coordNodes[nodeNum][1] * zoom[1] + origin[1]
            # insert lines
            for j in connecNodes[nodeNum]:
                x2 = coordNodes[j][0] * zoom[0] + origin[0]
                y2 = coordNodes[j][1] * zoom[1] + origin[1]
                out.write("<line x1=\"" + str(x1) + "\" y1=\"" + str(y1) + "\" ")
                out.write("x2=\"" + str(x2) + "\" y2=\"" + str(y2) + "\" ")
                out.write("style=\"stroke:red;stroke-width:3\" />\n")
            # insert nodes
            out.write("<circle cx=\"" + str(x1) + "\" cy=\"" + str(y1) + "\" ")
            out.write("r=\"6\" fill=\"black\" />\n")
            out.write("<text x=\"" + str(x1 - 10) + "\" y=\"" + str(y1 + 20) + "\" ")
            out.write("fill=\"blue\" font-size=\"12\">"+ str(i) + "</text>\n")
        out.write("No inline SVG support.\n</svg>\n</body>\n</html>")
    print("Output File: TreeDrawing.html")

# pickleOutput: pickle all the outputs of tdcore.drawTree()
# note: this may be useful for drawing of edited input tree (which is todo)
def pickleOutput(connecNodes, labelDict, coordNodes, weightNodes, majorNodes):
    with open("TreeInfo.pickle", "wb") as file:
        pickle.dump({"connecNodes": connecNodes,
                     "labelDict": labelDict,
                     "coordNodes": coordNodes,
                     "weightNodes": weightNodes,
                     "majorNodes": majorNodes}, file)
    print("Output File: TreeInfo.pickle")

if __name__ == '__main__':
    finalConnex, finalLabels, finalCoords, finalWeights, finalMajors = \
                tdcore.drawTree(treeX, 'node0', 'U', 'CW', countTree, getChildNodes)
    svgOutput(finalConnex, finalLabels, finalCoords, finalWeights, finalMajors)
    pickleOutput(finalConnex, finalLabels, finalCoords, finalWeights, finalMajors)