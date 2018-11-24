from copy import deepcopy
import queue as Q

"""#############################################################################
                                GLOBAL VARIABLES
#############################################################################"""
cols  = '123456789'
rows  = 'ABCDEFGHI'
uRows = ('ABC','DEF','GHI')
uCols = ('123','456','789')
numbersAssigned = 0
decisionsTaken=0
depth=-1
bottomTouched = False
totalSearched = 0
totalNumberWriten=0

"""#############################################################################
    Pair the input values to construct the different referencies to the table
#############################################################################"""
def pair(X, Y):
    aux=[]
    for x in X:
         for y in Y:
             aux.append(x+y)
    return aux

"""#############################################################################
                    Units, Peers and Squares initialization
#############################################################################"""
squares   =  pair(rows, cols)
uList     =([pair(rows, c) for c in cols]
          + [pair(r, cols) for r in rows]
          + [pair(r, c) for r in uRows for c in uCols])

eachUnit  = dict((square,[unit for unit in uList if square in unit])
            for square in squares)
eachPeers = dict((square, set(sum(eachUnit[square],[]))-set([square]))
            for square in squares)


def iniVars():
    global bottomTouched, depth, decisionsTaken, numbersAssigned
    bottomTouched=False
    depth=-1
    decisionsTaken=0
    numbersAssigned=0

"""#############################################################################
                            Class node for UCS and A*
#############################################################################"""
class Node:
    def __init__ (self,state,cost,deep=0,expNodes=0):
        self.state  = state
        self.cost   = cost
        self.depth  = deep
        self.exp = expNodes

"""#############################################################################
                            Class node for UCS and A*
#############################################################################"""
def Compare(values):
    ones = True
    for square in squares:
        if len(values[square]) != 1:
            ones = False
    if ones:
        return values
    else:
        return False

"""#############################################################################
                            Class node for UCS and A*
#############################################################################"""
def h(values):
    sum = 0
    for square in squares:
        sum += len(values[square])
    if sum >= 81:
        sum -= 81
    return sum

"""#############################################################################
Function eliminate
#############################################################################"""
def eliminate(values, square, digit):
    #Value was already deleted
    if digit not in values[square]:
        return values
    #Delete de digit from the square
    values[square] = values[square].replace(digit,'')
    #The Square do not have posible values left - WRONG
    if len(values[square]) == 0:
       return False
   #The Square only have one value left
    elif len(values[square]) == 1:
        lastDigit = values[square]
        #Eliminate the digit from peers
        for peerSquare in eachPeers[square]:
            if not eliminate(values,peerSquare,lastDigit):
                return False
    #Search the places in the units of the square were the digit might match
    foundPlaces = []
    for unit in eachUnit[square]:
        foundPlaces=[]
        for square2 in unit:
            if digit in values[square2]:
                foundPlaces.append(square2)
        #Digit does not have a place in the unit of the sudoku - WRONG
        if len(foundPlaces)==0:
           return False
        #One place found in the unit where the digit match
        elif len(foundPlaces)==1:
            #Assign the value
            if not assign(values, foundPlaces[0], digit):
                return False
    return values

"""#############################################################################
      Assign a specific by deleting all not wanted values from the square
#############################################################################"""
def assign(values, square, digit):
    global numbersAssigned
    global totalNumberWriten
    numbersAssigned += 1
    totalNumberWriten += 1
    for digitInSquare in values[square]:
        if digitInSquare != digit:
            if not eliminate(values,square,digitInSquare):
                return False
    return values

"""#############################################################################
Prints the board stored in a dictionary, the values are stored af follows
    dictionary[Square]  = 'posibleValues'
    values['A4']        = '136'
#############################################################################"""
def displayBoard(values):
    print('\n\nANSWER')
    maxL=0
    for square in squares:
        if (len(values[square])+1) > maxL:
            maxL = len(values[square])+1
    quadLine = '-'*(maxL*9+3)
    for row in rows:
        outLine = ''
        for col in cols:
            outLine = outLine + (values[row+col].center(maxL))
            if (col == '3') or (col == '6'):
                 outLine = outLine + '| '
        print(outLine)
        if (row == 'C') or (row == 'F'):
            print(quadLine)

"""#############################################################################
Prints the board stored in the initial string, the values are stored af follows
    dataString  = 'givenInitialValues' len(dataString)=81
    dataString  = '136..4...etc'
#############################################################################"""
def displayInitialBoard(dataString):
    global numbersAssigned
    print('\n\nINITIAL')
    quadLine = '-'*(2*9+3)
    outLine = ''
    for pos in range(81):
        if dataString[pos] != '.':
            outLine = outLine + dataString[pos] + ' '
            numbersAssigned-=1
        else:
            outLine = outLine + 'X '
        if (pos%3 == 2) and not (pos%9==8):
             outLine = outLine + '| '
        if pos%28 == 27:
            print(quadLine)
        if pos%9 == 8:
            print(outLine)
            outLine = ''

"""#############################################################################
Parse the input string and creates the values directory which is going to be
used in all the other fucntions
#############################################################################"""
def obtainInput(board):
    data = ''
    for value in board:
        if (value=='.') or (value in cols):
            data = data+value
        else:
            print('ERROR - Incorrect input char')
            exit()
    if len(board)!= 81:
        print('ERROR - Input chars must be 81')
        return 0
    values = dict((s, cols) for s in squares)
    dir = dict(zip(squares, [c for c in board if c in cols or c == '.']))
    for s,d in dir.items():
        if d in cols and not assign(values, s, d):
            return False
    return values

"""#############################################################################
                Implementation on depth first search algorithm
#############################################################################"""
def depthFirstNonOrdered(values):
    global decisionsTaken
    global depth
    depth+=1
    decisionsTaken+=1
    if values is False:
        depth-=1
        return False
    ones = True
    for square in squares:
        if len(values[square]) != 1:
            ones = False
    if ones:
        return values
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
        result = depthFirstNonOrdered(assign(values.copy(), s, d))
        if result:
            return result
    depth-=1
    return False

"""#############################################################################
Implementation of depth limited search algorithm, the secon parameter is the
value of the limit in depth as an integer.
When the limit depth is reached, the flag bottomTouched is True
#############################################################################"""
def depthLimitedNonOrdered(values,limDepth):
    global decisionsTaken
    global bottomTouched
    global totalSearched
    global depth
    depth+=1
    if depth > limDepth:
        depth-=1
        bottomTouched = True
        return False
    decisionsTaken+=1
    totalSearched+=1
    if values is False:
        depth-=1
        return False
    ones = True
    for square in squares:
        if len(values[square]) != 1:
            ones = False
    if ones and (depth <= limDepth):
        return values
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    for d in values[s]:
        result = depthLimitedNonOrdered(assign(values.copy(), s, d),limDepth)
        if result:
            return result
    depth-=1
    return False

"""#############################################################################
Implementation of iterative deepening search algorithm, it uses the depth
limited algorithm for finding the values
#############################################################################"""
def iterativeDeepening(values):
    global bottomTouched, depth, totalSearched, totalNumberWriten, decisionsTaken, numbersAssigned
    limDepth=0
    iniVars()
    ret = depthLimitedNonOrdered(values,0)
    while (not ret) and (bottomTouched):
        iniVars()
        limDepth+=1
        ret = depthLimitedNonOrdered(values,limDepth)
    return ret


"""#############################################################################
               Implementation on breadth first search algorithm
#############################################################################"""
def breadthFirstNonOrdered(values):
    global decisionsTaken
    global depth

    q = Q.PriorityQueue()

    IniNode = Node(values,0,0)
    index = 0
    q.put((IniNode.cost,index,IniNode))
    PoppedNode = Node(values,0)
    Visited = []
    Visited.append(values)
    emptyFlag = False
    while (not Compare(PoppedNode.state)) and (not emptyFlag):
        if (index == 0):
            PoppedNode = q.get()[2]
        n,s = min((len(PoppedNode.state[s]), s) for s in squares if len(PoppedNode.state[s]) > 1)
        for d in PoppedNode.state[s]:
            NewState = assign(PoppedNode.state.copy(), s, d)
            if NewState:
                index += 1
                AlVisited=False
                for Vis in Visited:
                    if(NewState==Vis):
                        AlVisited=True
                if not AlVisited:
                    NewCost  = PoppedNode.cost + 1
                    NewDepht = PoppedNode.depth + 1
                    AuxNode=Node(state=NewState,cost=NewCost, deep=NewDepht)
                    q.put([NewCost,index,AuxNode])
                    Visited.append(NewState)
        if q.empty():
            emptyFlag=True
        PoppedNode = q.get()[2]
        decisionsTaken+=1
    if (not Compare(PoppedNode.state)) and q.empty():
        return False
    else:
        if decisionsTaken == 0:
            decisionsTaken=1
        depth = PoppedNode.depth
        return PoppedNode.state

"""#############################################################################
Implementation on UCS search algorithm
Cost is the exploded numbers
#############################################################################"""
def UCS(values):
    global decisionsTaken
    global depth
    global numbersAssigned
    global totalSearched
    q = Q.PriorityQueue()
    IniNode = Node(values,0,0)
    index = 0
    q.put((IniNode.cost,index,IniNode))
    PoppedNode = Node(values,0)
    Visited = []
    Visited.append(values)
    emptyFlag = False
    while (not Compare(PoppedNode.state)) and (not emptyFlag):
        if (index == 0):
            PoppedNode = q.get()[2]
        n,s = min((len(PoppedNode.state[s]), s) for s in squares if len(PoppedNode.state[s]) > 1)
        for d in PoppedNode.state[s]:
            numbersAssigned = PoppedNode.cost
            NewState = assign(PoppedNode.state.copy(), s, d)
            if NewState:
                index += 1
                AlVisited=False
                for Vis in Visited:
                    if(NewState==Vis):
                        AlVisited=True
                if not AlVisited:
                    NewCost  = numbersAssigned + 1
                    NewDepht = PoppedNode.depth + 1
                    NewExpNodes = PoppedNode.exp + 1
                    AuxNode=Node(state=NewState,cost=NewCost, deep=NewDepht, expNodes=NewExpNodes)
                    q.put([NewCost,index,AuxNode])
                    Visited.append(NewState)
        if q.empty():
            emptyFlag=True
        PoppedNode = q.get()[2]
        totalSearched+=1
        decisionsTaken=PoppedNode.exp
    if (not Compare(PoppedNode.state)) and q.empty():
        return False
    else:
        if decisionsTaken == 0:
            decisionsTaken=1
        depth = PoppedNode.depth
        return PoppedNode.state

"""#############################################################################
A star Implementation
#############################################################################"""
def aStar(values):
    global decisionsTaken
    global depth
    global numbersAssigned
    global totalSearched
    q = Q.PriorityQueue()
    IniNode = Node(values,h(values),0)
    index = 0
    q.put((IniNode.cost,index,IniNode))
    PoppedNode = Node(values,h(values))
    Visited = []
    Visited.append(values)
    emptyFlag = False
    while (not Compare(PoppedNode.state)) and (not emptyFlag):
        if (index == 0):
            PoppedNode = q.get()[2]
        n,s = min((len(PoppedNode.state[s]), s) for s in squares if len(PoppedNode.state[s]) > 1)
        for d in PoppedNode.state[s]:
            numbersAssigned = PoppedNode.cost
            NewState = assign(PoppedNode.state.copy(), s, d)
            if NewState:
                index += 1
                AlVisited=False
                for Vis in Visited:
                    if(NewState==Vis):
                        AlVisited=True
                if not AlVisited:
                    NewCost  = numbersAssigned + 1 + h(NewState) - h(PoppedNode.state)
                    NewDepht = PoppedNode.depth + 1
                    NewExpNodes = PoppedNode.exp + 1
                    AuxNode=Node(state=NewState,cost=NewCost, deep=NewDepht, expNodes=NewExpNodes)
                    q.put([NewCost,index,AuxNode])
                    Visited.append(NewState)
        if q.empty():
            emptyFlag=True
        PoppedNode = q.get()[2]
        totalSearched+=1
        decisionsTaken=PoppedNode.exp
    if (not Compare(PoppedNode.state)) and q.empty():
        return False
    else:
        if decisionsTaken == 0:
            decisionsTaken=1
        depth = PoppedNode.depth
        return PoppedNode.state

"""#############################################################################
   Main code with menues for selecting the desired method to solve the sodoku
#############################################################################"""
print('\n\tSUDOKU SOLVER')
print('\nSearch algorithm:')
print('\t1 - Depth-First')
print('\t2 - Limited Depth')
print('\t3 - Iterative Deepening')
print('\t4 - Breadth-First')
print('\t5 - UCS')
print('\t6 - A Star')
selection1 = input('>')
if selection1 != '7':
    selection2 = input('Input format:\n\t1 - 1 line\n\t2 - 9 lines\n>')
    if selection2 == '1':
        sudoku=input('>')
    elif selection2 == '2':
        sudoku = ''
        for i in range(9):
            sudoku=sudoku+input('>')
    else:
        print('ERROR - Non-valid selection')
        exit()
    if not obtainInput(sudoku):
        exit()
################################################################################
if selection1 == '1':
     iniVars()
     if not depthFirstNonOrdered(obtainInput(sudoku)):
         print('Sudoku is not solvable')
         exit()
     displayInitialBoard(sudoku)
     iniVars()
     displayBoard(depthFirstNonOrdered(obtainInput(sudoku)))
################################################################################
elif selection1 == '2':
    limDepth=int(input('Limit in depth> '))
    iniVars()
    if not depthLimitedNonOrdered(obtainInput(sudoku),limDepth):
        print('None solution reached with given depth (sudoku might not be solvable)')
        exit()
    displayInitialBoard(sudoku)
    iniVars()
    displayBoard(depthLimitedNonOrdered(obtainInput(sudoku),limDepth))
################################################################################
elif selection1 == '3':
    iniVars()
    result = iterativeDeepening(obtainInput(sudoku))
    if not result:
        print('Sudoku is not solvable')
        exit()
    displayInitialBoard(sudoku)
    displayBoard(result)
    print('Total writen numbers until solution: ' + str(totalNumberWriten))
    print('Total searched nodes until solution: ' + str(totalSearched))
################################################################################
elif selection1 == '4':
    iniVars()
    result = breadthFirstNonOrdered(obtainInput(sudoku))
    if not result:
        print('Sudoku is not solvable or might be killing you computer')
        exit()
    displayInitialBoard(sudoku)
    displayBoard(result)
################################################################################
elif selection1 == '5':
    iniVars()
    result = UCS(obtainInput(sudoku))
    if not result:
        print('Sudoku is not solvable')
        exit()
    displayInitialBoard(sudoku)
    displayBoard(result)
    print('Total writen numbers until solution: ' + str(totalNumberWriten))
    print('Total searched nodes until solution: ' + str(totalSearched))
################################################################################
elif selection1 == '6':
    iniVars()
    result = aStar(obtainInput(sudoku))
    if not result:
        print('Sudoku is not solvable')
        exit()
    displayInitialBoard(sudoku)
    displayBoard(result)
    print('Total writen numbers until solution: ' + str(totalNumberWriten))
    print('Total searched nodes until solution: ' + str(totalSearched))
################################################################################
elif selection1 == '7':
    lines = []
    costs = []
    nExpanded = []
    totalExp= []
    file = open('Sudokus.txt', 'r')
    for line in file:
        sudoku = str(line).split('\n')[0]
        numbersAssigned = 0
        decisionsTaken=0
        depth=-1
        bottomTouched = False
        totalSearched = 0
        totalNumberWriten=0
        result = depthFirstNonOrdered(obtainInput(sudoku))
        costs.append(numbersAssigned)
        nExpanded.append(decisionsTaken)
        numbersAssigned = 0
        decisionsTaken=0
        depth=-1
        bottomTouched = False
        totalSearched = 0
        totalNumberWriten=0
        result = iterativeDeepening(obtainInput(sudoku))
        costs.append(numbersAssigned)
        nExpanded.append(decisionsTaken)
        totalExp.append(totalSearched)
        numbersAssigned = 0
        decisionsTaken=0
        depth=-1
        bottomTouched = False
        totalSearched = 0
        totalNumberWriten=0
        result = breadthFirstNonOrdered(obtainInput(sudoku))
        costs.append(numbersAssigned)
        nExpanded.append(decisionsTaken)
        numbersAssigned = 0
        decisionsTaken=0
        depth=-1
        bottomTouched = False
        totalSearched = 0
        totalNumberWriten=0
        result = UCS(obtainInput(sudoku))
        costs.append(numbersAssigned)
        nExpanded.append(decisionsTaken)
        totalExp.append(totalSearched)
        numbersAssigned = 0
        decisionsTaken=0
        depth=-1
        bottomTouched = False
        totalSearched = 0
        totalNumberWriten=0
        result = aStar(obtainInput(sudoku))
        costs.append(numbersAssigned)
        nExpanded.append(decisionsTaken)
        totalExp.append(totalSearched)
        lines.append(sudoku)
        index = int(len(costs)/5)
        print(index)
    file.close()
    file = open('costs2.txt', 'w')
    for i in range(len(lines)):
        file.write(str(i) + '/' + lines[i] + '/' + str(costs[i*5]) + '/' + str(costs[i*5+1]) + '/' + str(costs[i*5+2]) + '/' + str(costs[i*5+3]) + '/' + str(costs[i*5+4]) + '\n')
        print(i)
    file.close()
    file = open('expNodes2.txt', 'w')
    for i in range(len(lines)):
        file.write(str(i) + '/' + lines[i] + '/' + str(nExpanded[i*5]) + '/' + str(nExpanded[i*5+1]) + '/' + str(nExpanded[i*5+2]) + '/' + str(nExpanded[i*5+3]) + '/' + str(nExpanded[i*5+4]) + '\n')
        print(i)
    file.close()
    file = open('TexpNodes2.txt', 'w')
    for i in range(len(lines)):
        file.write(str(i) + '/' + lines[i] + '/' + str(totalExp[i*3]) + '/' + str(totalExp[i*3+1]) + '/' + str(totalExp[i*3+2]) + '\n')
        print(i)
    file.close()

################################################################################
else:
    print('ERROR - Non-valid selection')
    exit()
if selection1 != '7':
    print('\nNumbers writen until solution: ' + str(numbersAssigned))
    print('Number of searched nodes: ' + str(decisionsTaken))
    print('Depth where solution was found: ' + str(depth))
