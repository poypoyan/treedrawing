# Rooted Tree Drawing in Python 3
# Core Functions

import sys
from typing import Callable

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ sys functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# removeTraceback: remove traceback from error/exception messages
# adapted from https://stackoverflow.com/a/6598286
def removeTraceback():
    def rtExceptionHandler(exctype, value, traceback):
        print("{0}: {1}".format(exctype.__name__, value), file=sys.stderr)
    sys.excepthook = rtExceptionHandler

# restoreTraceback: restore default excepthook
def restoreTraceback():
    sys.excepthook = sys.__excepthook__
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~ sys functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~ algorithm functions ~~~~~~~~~~~~~~~~~~~~~~~~~
# analyzeNode: record relevant information for each node recursively
def analyzeNode(fillCtr, connex: list, labels: dict,   # fillCtr is always int inside []
                weights: list, majors: list, currentStr: str,
                procNewNodes: Callable, stack = []) -> None:
    currScan = currentStr   # init
    # traverse lines iteratively until the node either
    # has no child node or has multiple child nodes
    while True:
        weights[labels[currScan]] = 0   # init (for weights)
        currChildNodes = procNewNodes(fillCtr, connex, labels, currScan)   # process new nodes
        currLength = len(currChildNodes)
        if currLength != 1:
            break
        currScan = currChildNodes[0]
    # variables for better readability 
    currentStrLabel = labels[currentStr]
    currScanLabel = labels[currScan]
    # init (for majors)
    majors[currentStrLabel] = stack
    if currScan != currentStr:
        majors[currScanLabel] = stack + [currentStrLabel]
    # do all below if currScan has multiple child nodes
    if currLength != 0:
        newStack = majors[currScanLabel] + [currScanLabel]
        for i in currChildNodes:
            analyzeNode(fillCtr, connex, labels, weights, majors, i, procNewNodes, newStack)
            weights[currScanLabel] += weights[labels[i]]
    # final increments
    weights[currScanLabel] += 1
    if currScan != currentStr:
        weights[currentStrLabel] = weights[currScanLabel] + 1
    return

# preProcNewNodes: store labels and structure of newly discovered nodes (prior to closure)
def preProcNewNodes(inputTree: object, fillCtr, connex: list, labels: dict,
                currentStr: str, getChildNodes: Callable) -> list:
    childNodeNames = getChildNodes(inputTree, currentStr)
    childNodeLength = len(childNodeNames)
    connexArr = [None] * childNodeLength
    for i in range(childNodeLength):
        if childNodeNames[i] in labels:   # one of reasons labels is dict
            raise ValueError("cycle detected at node '{}'.".format(currentStr))
        fillCtr[0] += 1
        labels[childNodeNames[i]] = fillCtr[0]
        connexArr[i] = fillCtr[0]
    connex[labels[currentStr]] = connexArr   # save to connex
    return childNodeNames

# setInitCoord: set initial coordinates to each node recursively
def setInitCoord(connex: list, weights: list, coords: list,
                outDir: str, sideDir:str, current = 0, dist = 1.0) -> None:
    currScan = current   # init
    lineNodes = []   # store nodes with only 1 child node
    # traverse lines iteratively until the node either
    # has no child node or has multiple child nodes
    while True:
        currLength = len(connex[currScan])
        if currLength != 1:
            break
        currScan = connex[currScan][0]
        lineNodes += [currScan]
    # assign initial coordinates to line nodes
    for i in range(len(lineNodes)):
        spacing = dist * (i + 1) / len(lineNodes)
        coords[lineNodes[i]] = addCoord(coords[current], spacing, outDir)
    # do all below if currScan has multiple child nodes
    if currLength != 0:
        connex[currScan] = connexSort(connex, weights, currScan)   # sort connex[currScan]
        # opposite direction to sideDir is the sideDir for all child nodes
        if sideDir == 'U':
            childSideDir = 'D'
        elif sideDir == 'D':
            childSideDir = 'U'
        elif sideDir == 'L':
            childSideDir = 'R'
        elif sideDir == 'R':
            childSideDir = 'L'
        # the child node with the highest measure should be on center
        centerChild = connex[currScan][-1]
        coords[centerChild] = addCoord(coords[currScan], dist, outDir)
        setInitCoord(connex, weights, coords, outDir, childSideDir, centerChild, dist)
        # assign coordinates to other child nodes
        for (i, j) in enumerate(connex[currScan][0:-1]):
            spacing = dist * ((i // 2) + 1)
            if i % 2 == 0:
                coords[j] = addCoord(coords[centerChild], spacing, sideDir)
            else:
                coords[j] = addCoord(coords[centerChild], spacing, childSideDir)
            setInitCoord(connex, weights, coords, outDir, childSideDir, j, dist)
    # final stuff
    return

# connexSort: sort connex[current] according to ascending weights
def connexSort(connex: list, weights: list, current: int) -> list:
    return [i for (v, i) in sorted ((weights[i], i) for i in connex[current])]

# fixCoord: fix coordinates of nodes so that there are no nodes with same location
def fixCoord(connex: list, weights: list, majors: list, coords: list,
                sideDir: str, dist = 1.0) -> None:
    while True:
        notDone = False
        subList = []
        for i in range(len(connex)):
            if coords[i] == None:
                continue   # ignore disconnected nodes
            if coords[i] in subList:
                # duplicate coord found, so we're not yet done
                notDone = True
                overNode = subList.index(coords[i])
                for j in range(len(majors[i])):
                    splitNodeA = majors[i][j]   # init
                    splitNodeB = majors[overNode][j]   # init
                    if splitNodeA != splitNodeB:
                        break   # tree split is found
                # set relevant nodes and coord
                if weights[splitNodeA] < weights[splitNodeB]:
                    stayRootNode = splitNodeB   # split node leading to overNode (will NOT move)
                    moveRootNode = splitNodeA   # split node leading to i (will move)
                    stayParNode = majors[overNode][-1]   # parent of overNode (will NOT move)
                    testCoord = coords[i]   # coord of i (will move)
                else:
                    stayRootNode = splitNodeA   # split node leading to i (will NOT move)
                    moveRootNode = splitNodeB   # split node leading to overNode (will move)
                    stayParNode = majors[i][-1]   # parent of i (will NOT move)
                    testCoord = coords[overNode]   # coord of overNode (will move)
                # set move direction
                if sideDir == 'L' or sideDir == 'R':   # horizontal
                    if coords[moveRootNode][0] > coords[stayRootNode][0]:
                        moveDir = 'R'
                    else:
                        moveDir = 'L'
                elif sideDir == 'U' or sideDir == 'D':   # vertical
                    if coords[moveRootNode][1] > coords[stayRootNode][1]:
                        moveDir = 'U'
                    else:
                        moveDir = 'D'
                # set move distance
                moveCount = 0
                while True:
                    moveCount += 1
                    testCoord = addCoord(testCoord, dist, moveDir)   # move coord
                    vacant = True
                    for j in connex[stayParNode]:
                        if testCoord == coords[j]:
                            vacant = False   # new testCoord is already occupied by
                            break   # another child of stayParNode, so move again
                    if vacant:   # testCoord is now vacant
                        break   # so escape loop
                moveSubtree(connex, coords, moveRootNode, moveCount * dist, moveDir)   # move subtree now!
                subList = coords[0:i + 1]   # define new subList
            else:
                # coord has no duplicate yet, so add it to subList
                subList += [coords[i]]
        if not notDone:
            break
    return

# moveSubtree: move subtree (all nodes under the rootNode)
def moveSubtree(connex: list, coords: list, rootNode: int, add: float, direct: str) -> None:
    currScan = rootNode   # init
    # traverse lines iteratively until the node either
    # has no child node or has multiple child nodes
    while True:
        coords[currScan] = addCoord(coords[currScan], add, direct)   # move coord
        #print("---------", currScan, add, direct)
        currLength = len(connex[currScan])
        if currLength != 1:
            break
        currScan = connex[currScan][0]
    # do all below if currScan has multiple child nodes
    if currLength != 0:
        for i in connex[currScan]:
             moveSubtree(connex, coords, i, add, direct)
    return

# addCoord: add a distance to coordinate depending on screen direction
def addCoord(initCoord: list, add: float, direction: str) -> list:   # coord output
    if direction == 'U':
        return [initCoord[0], initCoord[1] + add]   # UP: add (+) to y-coord
    if direction == 'D':
        return [initCoord[0], initCoord[1] - add]   # DOWN: add (-) to y-coord
    if direction == 'L':
        return [initCoord[0] - add, initCoord[1]]   # LEFT: add (-) to x-coord
    if direction == 'R':
        return [initCoord[0] + add, initCoord[1]]   # RIGHT: add (+) to x-coord
# ~~~~~~~~~~~~~~~~~~~~~~~~~ algorithm functions ~~~~~~~~~~~~~~~~~~~~~~~~~

# drawTree: initial tree drawing
def drawTree(inputTree: object, rootName: str, outDir: str, sideRelDir: str,
                countTree: Callable, getChildNodes: Callable) -> tuple:
    # init directions
    cwDirs = {'U':'R', 'D':'L', 'L':'U', 'R':'D'}
    ccwDirs = {'U':'L', 'D':'R', 'L':'D', 'R':'U'}
    if not outDir in cwDirs:
        raise ValueError("invalid outDir input.")
    if sideRelDir == 'CW':
        sideDir = cwDirs[outDir]
    elif sideRelDir == 'CCW':
        sideDir = ccwDirs[outDir]
    else:
        raise ValueError("invalid sideRelDir input.")
    # init other structures
    fillCtr = [0]   # int pointer: counter for filled entries so far in connecNodes
    lenTree = countTree(inputTree)   # number of nodes
    connecNodes = [None] * lenTree
    weightNodes = [None] * lenTree
    majorNodes = [None] * lenTree
    coordNodes = [None] * lenTree
    coordNodes[0] = [0,0]   # coordinate of root node
    labelDict = {}   # dict, a set-like datatype, has faster 'in'
    labelDict[rootName] = 0   # label of root node
    # doClosure: closure of inputTree and getChildNodes on preProcNewNodes
    def doClosure(inpTree: object, inpFxn: Callable):
        def outFxn(fillCtr, connex: list, labels: dict, currentStr: str) -> list:
            return preProcNewNodes(inpTree, fillCtr, connex, labels, currentStr, inpFxn)
        return outFxn
    # perform the processing functions
    # print("Began Phase 1: analyzing nodes...")
    analyzeNode(fillCtr, connecNodes, labelDict, weightNodes, majorNodes,
                rootName, doClosure(inputTree, getChildNodes))
    # print("Began Phase 2: setting initial coordinates...")
    setInitCoord(connecNodes, weightNodes, coordNodes, outDir, sideDir)
    # print("Began Phase 3: fixing coordinates...")
    fixCoord(connecNodes, weightNodes, majorNodes, coordNodes, sideDir)
    return connecNodes, labelDict, coordNodes, weightNodes, majorNodes
