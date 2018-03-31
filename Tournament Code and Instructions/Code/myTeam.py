# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

# from captureAgents import CaptureAgent
# import random, time, util
# from game import Directions
# import game

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint
from game import Grid

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  global agentOneTarget
  agentOneTarget = None

  global agentOneIndex
  agentOneIndex = None

  global agentTwoTarget
  agentTwoTarget = None

  global agentTwoIndex
  agentTwoIndex = None

  global capsulePath
  capsulePath = []

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def chooseAction(self, gameState):  # WILL NEED TO CHANGE
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):  # THIS COULD POTENTIALLY CHANGE LATER
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    currentPos = gameState.getAgentState(self.index).getPosition()
    features['successorScore'] = self.getScore(successor)  # The score value (based on the game) after you make a move

    capsuleList = self.getCapsules(successor)
    currCapsuleList = self.getCapsules(gameState)
    # print ("Capsules: ", capsuleList)

    teamNumbers = self.getTeam(gameState)

    if teamNumbers[0] == 1 or teamNumbers[0] == 3:  # assumes blue team
      # print "You are Blue Team"
      enemy_one = successor.getAgentState(0)
      enemy_two = successor.getAgentState(2)
      enemy_one_position = successor.getAgentState(0).getPosition()
      enemy_two_position = successor.getAgentState(2).getPosition()
      enemy_one_index = 0
      enemy_two_index = 2
      current_enemy_one = gameState.getAgentState(0)
      current_enemy_two = gameState.getAgentState(2)
      current_enemy_one_position = gameState.getAgentState(0).getPosition()
      current_enemy_two_position = gameState.getAgentState(2).getPosition()
    else:
      # print "You are Red Team"
      enemy_one = successor.getAgentState(1)
      enemy_two = successor.getAgentState(3)
      enemy_one_position = successor.getAgentState(1).getPosition()
      enemy_two_position = successor.getAgentState(3).getPosition()
      enemy_one_index = 1
      enemy_two_index = 3
      current_enemy_one = gameState.getAgentState(1)
      current_enemy_two = gameState.getAgentState(3)
      current_enemy_one_position = gameState.getAgentState(1).getPosition()
      current_enemy_two_position = gameState.getAgentState(3).getPosition()

    runawayPacmanOne = False
    killPacmanOne = False
    killOne = False
    runawayOne = False

    runawayPacmanTwo = False
    killPacmanTwo = False
    killTwo = False
    runawayTwo = False

    myPos = successor.getAgentState(self.index).getPosition()
    teammatePos = None
    teammateIndex = None

    if (self.index == teamNumbers[0]):
      teammatePos = successor.getAgentState(teamNumbers[1]).getPosition()
      teammateIndex = teamNumbers[1]
    else:
      teammatePos = successor.getAgentState(teamNumbers[0]).getPosition()
      teammateIndex = teamNumbers[0]

    global agentOneTarget
    global agentOneIndex
    global agentTwoTarget
    global agentTwoIndex

    # Reset targets
    if agentOneTarget == enemy_one_index and enemy_one_position is None:
      agentOneTarget = None
      agentOneIndex = None

    if agentOneTarget == enemy_two_index and enemy_two_position is None:
      agentOneTarget = None
      agentOneIndex = None

    if agentTwoTarget == enemy_one_index and enemy_one_position is None:
      agentTwoTarget = None
      agentTwoIndex = None

    if agentTwoTarget == enemy_two_index and enemy_two_position is None:
      agentTwoTarget = None
      agentTwoIndex = None

    # print ("Agent One target: ", agentOneTarget)
    # print ("Agent Two target: ", agentTwoTarget)
    # print ("Agent One index: ", agentOneIndex)
    # print ("Agent Two index: ", agentTwoIndex)

    # Acts like switches for later added features
    if enemy_one_position is not None or enemy_two_position is not None:  # changed from and to or
      if enemy_one_position is not None and enemy_one.isPacman:
        if gameState.getAgentState(self.index).scaredTimer > 0:
          print "Run away from enemy pacman one!"
          runawayPacmanOne = True

        else:
          print "Kill enemy pacman one!"
          killPacmanOne = True
          enemies = []
          enemy1 = None
          enemy2 = None
          j = 0
          for i in self.getOpponents(successor):
            # print ('i:', i)
            # print ('j:', j)
            enemies.append(successor.getAgentState(i))
            if (j == 0):
              enemy1 = i
            if (j == 1):
              enemy2 = i
            j = j + 1

          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range

          if len(invaders) == 1:
            if agentOneTarget is None and agentTwoTarget is None:  # initialize if none
              myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
              if myRangeDist < teammateRangeDist:
                if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                  agentOneTarget = enemy1
                  agentOneIndex = self.index
                if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                  agentOneTarget = enemy2
                  agentOneIndex = self.index
              else:
                if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                  agentOneTarget = enemy1
                  agentOneIndex = teammateIndex
                if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                  agentOneTarget = enemy2
                  agentOneIndex = teammateIndex
            if agentOneIndex == self.index or agentTwoIndex == self.index:  # proceed to chase ghost if you are assigned to it
              features['numInvaders'] = len(invaders)
              if len(invaders) > 0:
                print "FACK"
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)
                if (min(dists) < 3):
                  print "KILL INVADER"
                  features['killInvader'] += 1  # seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)
          elif len(invaders) == 2:  # do same behavior (for now)
            if agentOneTarget is not None and agentTwoTarget is None:  # initialize if none
              if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                agentTwoTarget = enemy1
                agentTwoIndex = self.index
              if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                agentTwoTarget = enemy2
                agentTwoIndex = self.index
              if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
                agentTwoTarget = enemy1
                agentTwoIndex = self.index
              if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
                agentTwoTarget = enemy2
                agentTwoIndex = self.index
            features['numInvaders'] = len(invaders)
            if len(invaders) > 0:
              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              features['invaderDistance'] = min(dists)
              if (min(dists) < 3):
                print "KILL INVADER"
                features['killInvader'] += 1  # seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)

      elif enemy_one_position is not None and not enemy_one.isPacman:  # enemy not pacman
        if gameState.getAgentState(enemy_one_index).scaredTimer > 0:
          print "Kill enemy one!"
          killOne = True

        else:
          print "Run away from enemy one!"
          runawayOne = True

          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

          defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range

          ghost_positions = []
          closeDefenders = []

          if enemy_one_position is not None:
            ghost_positions.append((enemy_one_position, enemy_one))
          if enemy_two_position is not None:
            ghost_positions.append((enemy_two_position, enemy_two))
          min_distance = 999
          for ghost in ghost_positions:  # 1 or 2 ghosts
            current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
            if min_distance > current_ghost_distance:  # always updates
              min_distance = current_ghost_distance
              min_ghost = ghost[1]
              if min_distance < 4 and not successor.getAgentState(self.index).isPacman:
                features['onDefense'] = 1
              if min_distance < 3:
                closeDefenders.append(min_ghost)

          if ((agentOneIndex == self.index) or (agentTwoIndex == self.index)):
            print "Do nothing, kill invader1"
          else:
            features['numCloseDefenders'] = len(closeDefenders)
            if len(closeDefenders) > 0:
              print "ONE!"

              features['onDefense'] = 1
              if successor.getAgentState(self.index).isPacman:
                features['onDefense'] = 0

                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
                features['closeDefenderDistance'] = -min(dists)

      if enemy_two_position is not None and enemy_two.isPacman:
        if gameState.getAgentState(self.index).scaredTimer > 0:
          print "Run away from enemy pacman two!"
          runawayPacmanTwo = True

        else:
          print "Kill enemy pacman two!"

          killPacmanOne = True

          enemies = []
          enemy1 = None
          enemy2 = None
          j = 0
          for i in self.getOpponents(successor):
            # print ('i:', i)
            # print ('j:', j)
            enemies.append(successor.getAgentState(i))
            if (j == 0):
              enemy1 = i
            if (j == 1):
              enemy2 = i
            j = j + 1

          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range

          if len(invaders) == 1:
            if agentOneTarget is None and agentTwoTarget is None:  # initialize if none
              myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
              if myRangeDist < teammateRangeDist:
                if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                  agentOneTarget = enemy1
                  agentOneIndex = self.index
                if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                  agentOneTarget = enemy2
                  agentOneIndex = self.index
              else:
                if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                  agentOneTarget = enemy1
                  agentOneIndex = teammateIndex
                if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                  agentOneTarget = enemy2
                  agentOneIndex = teammateIndex
            if agentOneIndex == self.index or agentTwoIndex == self.index:  # proceed to chase ghost if you are assigned to it
              features['numInvaders'] = len(invaders)
              if len(invaders) > 0:
                print "FACK 2"
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)
                if (min(dists) < 3):
                  print "KILL INVADER"
                  features['killInvader'] += 1  # seems to work mostly
          elif len(invaders) == 2:  # do same behavior (for now)
            if agentOneTarget is not None and agentTwoTarget is None:  # initialize if none
              if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
                agentTwoTarget = enemy1
                agentTwoIndex = self.index
              if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
                agentTwoTarget = enemy2
                agentTwoIndex = self.index
              if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
                agentTwoTarget = enemy1
                agentTwoIndex = self.index
              if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
                agentTwoTarget = enemy2
                agentTwoIndex = self.index
            features['numInvaders'] = len(invaders)
            if len(invaders) > 0:
              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              features['invaderDistance'] = min(dists)
              if (min(dists) < 3):
                print "KILL INVADER"
                features['killInvader'] += 1  # seems to work mostly (NO IT DOESN'T, MAKE IT NEGATIVE?)

      elif (enemy_two_position is not None) and not enemy_two.isPacman:  # enemy not pacman
        if gameState.getAgentState(enemy_two_index).scaredTimer > 0:
          print "Kill enemy two!"
          killTwo = True

        else:
          print "Run away from enemy two!"
          runawayTwo = True
          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

          defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range

          ghost_positions = []
          closeDefenders = []

          if enemy_one_position is not None:
            ghost_positions.append((enemy_one_position, enemy_one))
          if enemy_two_position is not None:
            ghost_positions.append((enemy_two_position, enemy_two))
          min_distance = 999
          for ghost in ghost_positions:  # 1 or 2 ghosts
            current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
            if min_distance > current_ghost_distance:  # always updates
              min_distance = current_ghost_distance
              min_ghost = ghost[1]
              if min_distance < 4 and not successor.getAgentState(self.index).isPacman:
                features['onDefense'] = 1
              if min_distance < 3:
                closeDefenders.append(min_ghost)

          if ((agentOneIndex == self.index) or (agentTwoIndex == self.index)):
            print "Do nothing, kill invader2"
          else:
            features['numCloseDefenders'] = len(closeDefenders)
            if len(closeDefenders) > 0:
              print "TWO!"

              if successor.getAgentState(self.index).isPacman:
                features['onDefense'] = 0

                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
                features['closeDefenderDistance'] = -min(dists)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()  # based on successor

    if (self.index == 0 or self.index == 1):
      foodAreaID = 'top_half'
    else:
      foodAreaID = 'bottom_half'

    boardHeight = gameState.data.food.height
    halfHeight = boardHeight / 2
    topFood = []
    bottomFood = []
    for food in foodList:
      if food[1] > halfHeight / 1.5:
        topFood.append(food)
      else:
        bottomFood.append(food)

    # print ("Top food: ", topFood)
    # print ("Bottom food: ", bottomFood)
    newFoodList = []
    if foodAreaID == 'top_half':
      newFoodList = topFood  # changed to topFood not foodList lol
    else:
      newFoodList = bottomFood  # changed to topFood not foodList lol

    if len(foodList) > 0:  # This should always be True,  but better safe than sorry

      myPos = successor.getAgentState(self.index).getPosition()  # coordinates of where you are after move
      if (len(newFoodList) > 0):
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in
                                 newFoodList])  # after making move, get min distance to next food in successor food list
      else:
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
        teammate_positions = []
        closeTeammates = []

        teammate_position = None
        teammate_obj = None

        if successor.getAgentState(teamNumbers[0]).getPosition() is not None and self.index is not teamNumbers[0]:
          teammate_position = successor.getAgentState(teamNumbers[0]).getPosition()
          teammate_obj = successor.getAgentState(teamNumbers[0])
        elif successor.getAgentState(teamNumbers[1]).getPosition() is not None and self.index is not teamNumbers[1]:
          teammate_position = successor.getAgentState(teamNumbers[1]).getPosition()
          teammate_obj = successor.getAgentState(teamNumbers[1])

        if teammate_position is not None:
          teammate_positions.append((teammate_position, teammate_obj))
        min_distance = 999
        for teammate in teammate_positions:  # should only be one teammember
          current_teammate_distance = self.getMazeDistance(myPos, teammate[0])
          if min_distance > current_teammate_distance:  # always updates
            min_distance = current_teammate_distance
            min_teammate = teammate[1]

            if min_distance < 2:  # or some other min distance < 3?
              closeTeammates.append(min_teammate)

        features['numCloseTeammates'] = len(closeTeammates)
        if len(closeTeammates) > 0:
          print "CLOSE TEAMMATE!"
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeTeammates]
          features['closeTeammateDistance'] = -min(dists)

      features['distanceToFood'] = min_food_distance

    return features

  # make it value capsules more than food and run away if near a ghost

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'takeThisAction': 1, 'onDefense': 100, 'distanceToFood': -1, 'distancetToCapsule': -1, 'numInvaders': -1000, 'invaderDistance': -10,
            'numDefenders': -1000, 'defenderDistance': -10, 'numCloseDefenders': -1000, 'closeDefenderDistance': -10,
            'numCloseTeammates': -1000, 'closeTeammateDistance': -10, 'numCloseAttackers': -1000,
            'closeAttackerDistance': -10, 'killInvader': 1, 'munchCapsule': 1, 'separateAgents': -1, 'avoidCapsule': 1}

  # def aStarCapsule(self, gameState, action, myPos, capsulePos, currPos):
  #   print "IN A STAR"
  #   "Search the node that has the lowest combined cost and heuristic first."
  #
  #   # Initializations
  #   nodeQueue = util.PriorityQueue()
  #   pathToNode = {}
  #   costToNode = {}
  #   goalPath = []
  #   # initialState = problem.startingState()
  #   # initialState = (gameState, action, self.heuristic(gameState, capsulePos)) # action wrong?
  #   initialState = (myPos)  # action wrong?
  #   visitedStates = []
  #   visitedPos = []
  #
  #   # Check if initial node is goal to stop algorithm early
  #   # if problem.isGoal(initialState):
  #   if (currPos == capsulePos):
  #     return None
  #
  #   # Prepare while-loop's first nodes
  #   visitedStates.append(initialState)
  #   visitedPos.append(myPos)
  #   for node in self.successorStates(gameState, myPos):
  #     pathToNode[node] = node[1]
  #     # Heuristic added to cost so that f(n) = g(n) + h(n) for each new node
  #     # print node[0]
  #     # print capsulePos
  #     costToNode[node] = int(node[2]) + self.heuristic(node[0], capsulePos)
  #     # print "COST: ", costToNode[node]
  #     # print "HEURISTIC: ", self.heuristic(node[0], capsulePos)
  #     nodeQueue.push(node, costToNode[node])
  #
  #   firstTime = True
  #
  #   while not (nodeQueue.isEmpty()):
  #     # Pop based on priority (sum of compounded cost of path and state heuristic)
  #     currentNode = nodeQueue.pop()
  #
  #     # Visit node, check if goal reached, and add successors to stack.
  #     print currentNode[0]
  #     if (currentNode[0][3] not in visitedStates):
  #       visitedStates.append(currentNode[0][3])
  #       # visitedPos.append(currentNode[0])
  #
  #       # goalPath obtained from getting dictionary path value for current victory node (calculated continuosly while getting successor nodes)
  #       # if problem.isGoal(currentNode[0]):
  #       # print "BAAAAAAAAB: ", currentNode[0].getAgentState(self.index).getPosition()
  #       # if firstTime == True:
  #       #   firstTime = False # do nothing here
  #       # if currentNode[0].getAgentState(self.index).getPosition() == capsulePos:
  #       if currentNode[0][3].getAgentState(self.index).getPosition() == capsulePos:
  #         goalPath = pathToNode[currentNode].split(", ")
  #         return goalPath
  #
  #       # Add successors to PriorityQueue and use pathToNode/costToNode dictionaries to store paths/costs for priority function and goalPath lookup
  #       # Cost is compounded to preserve accuracy of f(n) = g(n) + h(n) calculation for each new node
  #       currentSuccessors = self.successorStatesTwo(currentNode)
  #       for (state, pathDir, cost, pos) in currentSuccessors:
  #         if (pos not in visitedStates):
  #           compoundedCost = currentNode[2] + int(cost)
  #           # print compoundedCost
  #           node = (state, pathDir, compoundedCost, pos)
  #           pathToNode[node] = pathToNode[currentNode] + ", " + pathDir
  #           # costToNode[node] calculation the crucial difference between UCS and AStar (below)
  #           costToNode[node] = int(compoundedCost) + self.heuristic(state, capsulePos)
  #           nodeQueue.push(node, costToNode[node])
  #
  #   # Return None if no path found
  #   return None
  #
  # def heuristic(self, gameState, capsulePos):
  #   hValue = 0
  #
  #   # print gameState
  #   # successor = self.getSuccessor(gameState, action)
  #
  #   myPos = gameState.getAgentState(self.index).getPosition()
  #
  #   # print myPos
  #
  #   hValue = self.getMazeDistance(myPos, capsulePos)
  #   return hValue
  #
  # def successorStates(self, gameState, myPos):
  #   actions = []
  #   states = []
  #   actions = gameState.getLegalActions(self.index)
  #   for action in actions: #(state, pathDir, cost)
  #     # print ("Action: ", action)
  #     successor = self.getSuccessor(gameState, action)
  #     pos = successor.getAgentState(self.index).getPosition()
  #     states.append((successor, action, 0, pos))
  #
  #   # print "STATES: ", states
  #
  #   return states # an array of actions -> needs to be states related to those actions (now it is)
  #
  # def successorStatesTwo(self, node):
  #   actions = []
  #   states = []
  #   actions = node[0].getLegalActions(self.index)
  #   for action in actions: #(state, pathDir, cost)
  #     # print ("Action: ", action)
  #     successor = self.getSuccessor(node[0], action)
  #     pos = successor.getAgentState(self.index).getPosition()
  #     states.append((successor, action, node[2], pos))
  #
  #   # print "STATES: ", states
  #
  #   return states # an array of actions -> needs to be states related to those actions (now it is)

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  # Defend flag valued more than going on wild goose chase (be defensive overall) -> attack when opponent killed?

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
































































#   global agentOneTarget
#   agentOneTarget = None
#
#   global agentOneIndex
#   agentOneIndex = None
#
#   global agentTwoTarget
#   agentTwoTarget = None
#
#   global agentTwoIndex
#   agentTwoIndex = None
#
#   # global invader1
#   # invader1 = [False, False]
#   #
#   # global invader2
#   # invader2 = [False, False]
#
#   # global AgentClass
#   # AgentClass = ourAgentTracker(eval(first)(firstIndex), eval(second)(secondIndex))
#
#   # global invader
#   # invader = 'poop'
#
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]
#
# # class ourAgentTracker():
# #   def __init__(self, agent1, agent2):
# #     print("index of offensiveAgent1", agent1.index)
# #     print("index of offensiveAgent2", agent2.index)
# #     self.agent1 = agent1
# #     self.agent2 = agent2
# #     self.agent1_index = agent1.index
# #     self.agent2_index = agent2.index
# #     self.agent1_chasing_enemy = False
# #     self.agent2_chasing_enemy = False
#
# ##########
# # Agents #
# ##########
#
# class ReflexCaptureAgent(CaptureAgent):
#   """
#   A base class for reflex agents that chooses score-maximizing actions
#   """
#   def chooseAction(self, gameState): #WILL NEED TO CHANGE
#     """
#     Picks among the actions with the highest Q(s,a).
#     """
#     actions = gameState.getLegalActions(self.index)
#
#     # You can profile your evaluation time by uncommenting these lines
#     # start = time.time()
#     values = [self.evaluate(gameState, a) for a in actions]
#     # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
#
#     maxValue = max(values)
#     bestActions = [a for a, v in zip(actions, values) if v == maxValue]
#
#     return random.choice(bestActions)
#
#   def getSuccessor(self, gameState, action):
#     """
#     Finds the next successor which is a grid position (location tuple).
#     """
#     successor = gameState.generateSuccessor(self.index, action)
#     pos = successor.getAgentState(self.index).getPosition()
#     if pos != nearestPoint(pos):
#       # Only half a grid position was covered
#       return successor.generateSuccessor(self.index, action)
#     else:
#       return successor
#
#   def evaluate(self, gameState, action):   # THIS COULD POTENTIALLY CHANGE LATER
#     """
#     Computes a linear combination of features and feature weights
#     """
#     features = self.getFeatures(gameState, action)
#     weights = self.getWeights(gameState, action)
#     return features * weights
#
#   def getFeatures(self, gameState, action):
#     """
#     Returns a counter of features for the state
#     """
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     features['successorScore'] = self.getScore(successor)
#     return features
#
#   def getWeights(self, gameState, action):
#     """
#     Normally, weights do not depend on the gamestate.  They can be either
#     a counter or a dictionary.
#     """
#     return {'successorScore': 1.0}
#
# class OffensiveReflexAgent(ReflexCaptureAgent):
#   """
#   A reflex agent that seeks food. This is an agent
#   we give you to get an idea of what an offensive agent might look like,
#   but it is by no means the best or only way to build an offensive agent.
#   """
#   # def __init__(self, index):
#   #   print("index", index)
#
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move
#
#     # capsuleList = self.getCapsules(successor)
#     # print ("Capsules: ", capsuleList)
#
#     teamNumbers = self.getTeam(gameState)
#
#     if teamNumbers[0] == 1 or teamNumbers[0] == 3: # assumes blue team
#       # print "You are Blue Team"
#       enemy_one = successor.getAgentState(0)
#       enemy_two = successor.getAgentState(2)
#       enemy_one_position = successor.getAgentState(0).getPosition()
#       enemy_two_position = successor.getAgentState(2).getPosition()
#       enemy_one_index = 0
#       enemy_two_index = 2
#       current_enemy_one = gameState.getAgentState(0)
#       current_enemy_two = gameState.getAgentState(2)
#       current_enemy_one_position = gameState.getAgentState(0).getPosition()
#       current_enemy_two_position = gameState.getAgentState(2).getPosition()
#     else:
#       # print "You are Red Team"
#       enemy_one = successor.getAgentState(1)
#       enemy_two = successor.getAgentState(3)
#       enemy_one_position = successor.getAgentState(1).getPosition()
#       enemy_two_position = successor.getAgentState(3).getPosition()
#       enemy_one_index = 1
#       enemy_two_index = 3
#       current_enemy_one = gameState.getAgentState(1)
#       current_enemy_two = gameState.getAgentState(3)
#       current_enemy_one_position = gameState.getAgentState(1).getPosition()
#       current_enemy_two_position = gameState.getAgentState(3).getPosition()
#
#     runawayPacmanOne = False
#     killPacmanOne = False
#     killOne = False
#     runawayOne = False
#
#     runawayPacmanTwo = False
#     killPacmanTwo = False
#     killTwo = False
#     runawayTwo = False
#
#     myPos = successor.getAgentState(self.index).getPosition()
#     teammatePos = None
#     teammateIndex = None
#
#     if (self.index == teamNumbers[0]):
#       teammatePos = successor.getAgentState(teamNumbers[1]).getPosition()
#       teammateIndex = teamNumbers[1]
#     else:
#       teammatePos = successor.getAgentState(teamNumbers[0]).getPosition()
#       teammateIndex = teamNumbers[0]
#
#     global agentOneTarget
#     global agentOneIndex
#     global agentTwoTarget
#     global agentTwoIndex
#
#     # Reset targets
#     if agentOneTarget == enemy_one_index and enemy_one_position is None:
#       agentOneTarget = None
#       agentOneIndex = None
#
#     if agentOneTarget == enemy_two_index and enemy_two_position is None:
#       agentOneTarget = None
#       agentOneIndex = None
#
#     if agentTwoTarget == enemy_one_index and enemy_one_position is None:
#       agentTwoTarget = None
#       agentTwoIndex = None
#
#     if agentTwoTarget == enemy_two_index and enemy_two_position is None:
#       agentTwoTarget = None
#       agentTwoIndex = None
#
#
#     print ("Agent One target: ", agentOneTarget)
#     print ("Agent Two target: ", agentTwoTarget)
#     print ("Agent One index: ", agentOneIndex)
#     print ("Agent Two index: ", agentTwoIndex)
#
#     # Acts like switches for later added features
#     if enemy_one_position is not None or enemy_two_position is not None: # changed from and to or
#       if enemy_one_position is not None and enemy_one.isPacman:
#         if gameState.getAgentState(self.index).scaredTimer > 0:
#           print "Run away from enemy pacman one!"
#           runawayPacmanOne = True
#
#           # IF ACTIONS == REVERSE BECAUSE OF ENEMY PACMAN, FORGET ABOUT FOOD? -> A-STAR another path?
#
#           # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
#           # if action == rev: features['reverse'] = 1
#
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # attackers = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           #
#           # # min_ghost_distance = 3
#           # # min_ghost = None
#           # ghost_positions = []
#           # closeAttackers = []
#           #
#           # if enemy_one_position is not None:
#           #   ghost_positions.append((enemy_one_position, enemy_one))
#           # if enemy_two_position is not None:
#           #   ghost_positions.append((enemy_two_position, enemy_two))
#           # min_distance = 999
#           # for ghost in ghost_positions:  # 1 or 2 ghosts
#           #   current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
#           #   if min_distance > current_ghost_distance:  # always updates
#           #     min_distance = current_ghost_distance
#           #     min_ghost = ghost[1]
#           #     if min_distance < 2:
#           #       closeAttackers.append(min_ghost)
#           #
#           # features['numCloseAttackers'] = len(closeAttackers)
#           # if len(closeAttackers) > 0:
#           #   print "ONE ATTACK!"
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeAttackers]
#           #   features['closeAttackerDistance'] = -min(dists)
#         else:
#           print "Kill enemy pacman one!"
#           killPacmanOne = True
#           enemies = []
#           enemy1 = None
#           enemy2 = None
#           j = 0
#           for i in self.getOpponents(successor):
#             # print ('i:', i)
#             # print ('j:', j)
#             enemies.append(successor.getAgentState(i))
#             if (j == 0):
#               enemy1 = i
#             if (j == 1):
#               enemy2 = i
#             j = j + 1
#
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # print ('ENEMIES: ', enemies)
#
#           # invaders = []
#           # v = 0
#           # for a in enemies:
#           #   if a.isPacman and a.getPosition() != None:
#           #     invaders.append(a)
#           #     if (v == 0):
#           #       enemy1 = i
#           #     if (v == 1):
#           #       enemy2 = i
#           #     v = v + 1
#           invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#           # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
#           # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
#           # if ((invader1[0] == True and invader2[0] == False) or (invader2[0] == True and invader1[0] == False)):
#           # print ("INDEX: ", self.index)
#           # global agentOneTarget
#           # global agentOneIndex
#           # global agentTwoTarget
#           # global agentTwoIndex
#
#           if len(invaders) == 1:
#             if agentOneTarget is None and agentTwoTarget is None: #initialize if none
#               # To not make the far away one come back for it
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#                 if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#               else:
#                 if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                   agentOneTarget = enemy1
#                   agentOneIndex = teammateIndex
#                 if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                   agentOneTarget = enemy2
#                   agentOneIndex = teammateIndex
#
#             if agentOneTarget is not None and agentTwoTarget is None: # change agent for targeting when the other is closer to it
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 agentOneIndex = self.index
#             if agentOneTarget is None and agentTwoTarget is not None: # change agent for targeting when the other is closer to it (other case)
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 agentOneIndex = self.index
#
#             if agentOneIndex == self.index or agentTwoIndex == self.index: # proceed to chase ghost if you are assigned to it (or handles case where a1 dies first)
#               features['numInvaders'] = len(invaders)
#               if len(invaders) > 0:
#                 print "FACK"
#                 dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#                 features['invaderDistance'] = min(dists)
#                 if (min(dists) < 3):
#                   print "KILL INVADER"
#                   features['killInvader'] += 1 #seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)
#           elif len(invaders) == 2: # do same behavior (for now)
#             if agentOneTarget is not None and agentTwoTarget is None: #initialize if none
#               if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy1
#                   agentTwoIndex = self.index
#               if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy2
#                   agentTwoIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy1
#                   agentTwoIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy2
#                   agentTwoIndex = self.index
#             if agentOneTarget is None and agentTwoTarget is not None: #initialize if none
#               if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#               if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#             features['numInvaders'] = len(invaders)
#             if len(invaders) > 0:
#               print "FACK"
#               dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               features['invaderDistance'] = min(dists)
#               if (min(dists) < 3):
#                 print "KILL INVADER"
#                 features['killInvader'] += 1  # seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)
#           # print ("INDEX: ", self.index)
#           # features['numInvaders'] = len(invaders)
#           # if len(invaders) > 0:
#           #   print "FACK"
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           #   features['invaderDistance'] = min(dists)
#           #   if (min(dists) < 3):
#           #     print "KILL INVADER"
#           #     features['killInvader'] += 1  # seems to work mostly
#           # else:
#           #   invader = "no"
#       elif enemy_one_position is not None and not enemy_one.isPacman: # enemy not pacman
#         if gameState.getAgentState(enemy_one_index).scaredTimer > 0:
#           print "Kill enemy one!"
#           killOne = True
#
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
#           # features['numDefenders'] = len(defenders)
#           # if len(defenders) > 0:
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
#           #   if min(dists) <= 3: #tune
#           #     print "Kill enemy one!"
#           #     features['defenderDistance'] = min(dists)
#         else:
#           # if (gameState.getAgentState(self.index).isPacman):
#           print "Run away from enemy one!"
#           runawayOne = True
#
#           # if(not successor.getAgentState(self.index).isPacman):       // THIS ONE MAKES BOTH OF THEM STOP
#           #   # Computes whether we're on defense (1) or offense (0)
#           #   features['onDefense'] = 1
#           #
#           # if successor.getAgentState(self.index).isPacman:
#           #   features['onDefense'] = 0
#
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#
#           # defenders = []
#
#           # for a in enemies:
#           #   if not a.isPacman and a.getPosition() != None:
#           #     if agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not a:  # if ghost scaring you doesn't match your target, don't include it
#           #       print "OMG"
#           #     else:
#           #       defenders.append(a)
#           defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
#
#           # min_ghost_distance = 3
#           # min_ghost = None
#           ghost_positions = []
#           closeDefenders = []
#
#           if enemy_one_position is not None:
#             ghost_positions.append((enemy_one_position, enemy_one))
#           if enemy_two_position is not None:
#             ghost_positions.append((enemy_two_position, enemy_two))
#           min_distance = 999
#           for ghost in ghost_positions: # 1 or 2 ghosts
#             current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
#             if min_distance > current_ghost_distance: #always updates
#               min_distance = current_ghost_distance
#               min_ghost = ghost[1]
#               if min_distance < 3:
#                 closeDefenders.append(min_ghost)
#           # min_ghost_distance = min_distance
#
#           # if (successor.getAgentState(teamNumbers[0]).isPacman and successor.getAgentState(teamNumbers[1]).isPacman):
#           #   x = 0
#           # else:
#           # if len(closeDefenders) > 0 and ((agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]) or (agentTwoIndex == self.index and successor.getAgentState(agentTwoTarget) is not closeDefenders[0])):
#           #   print "Do nothing, kill invader"
#           if ((agentOneIndex == self.index and agentOneTarget is not None) or (agentTwoIndex == self.index and agentTwoTarget is not None)):
#             print "Do nothing, kill invader1"
#             # if (not successor.getAgentState(self.index).isPacman and agentOneIndex == self.index):
#             #   if not successor.getAgentState(agentOneTarget).isPacman:
#             #     print "JK1"
#             #     features['numCloseDefenders'] = len(closeDefenders)
#             #     if len(closeDefenders) > 0:
#             #       print "ONE!"
#             #
#             #       features['onDefense'] = 1
#             #       if successor.getAgentState(self.index).isPacman:
#             #         features['onDefense'] = 0
#             #         print "Cross 50!"
#             #
#             #       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             #       features['closeDefenderDistance'] = -min(dists)
#             # if (not successor.getAgentState(self.index).isPacman and agentTwoIndex == self.index):
#             #   if not successor.getAgentState(agentTwoTarget).isPacman:
#             #     print "JK1"
#             #     features['numCloseDefenders'] = len(closeDefenders)
#             #     if len(closeDefenders) > 0:
#             #       print "ONE!"
#             #
#             #       features['onDefense'] = 1
#             #       if successor.getAgentState(self.index).isPacman:
#             #         features['onDefense'] = 0
#             #         print "Cross 50!"
#             #
#             #       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             #       features['closeDefenderDistance'] = -min(dists)
#             # features['onDefense'] = 1
#             # if successor.getAgentState(self.index).isPacman:
#             #   features['onDefense'] = 0
#           else:
#             features['numCloseDefenders'] = len(closeDefenders)
#             if len(closeDefenders) > 0:
#               print "ONE!"
#               # if (not successor.getAgentState(self.index).isPacman):
#               #   # Computes whether we're on defense (1) or offense (0)
#               #   features['onDefense'] = 1
#               #
#               # if successor.getAgentState(self.index).isPacman:
#               #   features['onDefense'] = 0
#               features['onDefense'] = 1
#               if successor.getAgentState(self.index).isPacman:
#                 features['onDefense'] = 0
#                 print "Cross 50!"
#
#               dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#               features['closeDefenderDistance'] = -min(dists)
#     #      -min(dists) - 1000?
#
#
#       if enemy_two_position is not None and enemy_two.isPacman:
#         if gameState.getAgentState(self.index).scaredTimer > 0:
#           print "Run away from enemy pacman two!"
#           runawayPacmanTwo = True
#
#           # IF ACTIONS == REVERSE BECAUSE OF ENEMY PACMAN, FORGET ABOUT FOOD? -> A-STAR another path?
#
#           # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
#           # if action == rev: features['reverse'] = 1
#
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # attackers = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           #
#           # # min_ghost_distance = 3
#           # # min_ghost = None
#           # ghost_positions = []
#           # closeAttackers = []
#           #
#           # if enemy_one_position is not None:
#           #   ghost_positions.append((enemy_one_position, enemy_one))
#           # if enemy_two_position is not None:
#           #   ghost_positions.append((enemy_two_position, enemy_two))
#           # min_distance = 999
#           # for ghost in ghost_positions:  # 1 or 2 ghosts
#           #   current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
#           #   if min_distance > current_ghost_distance:  # always updates
#           #     min_distance = current_ghost_distance
#           #     min_ghost = ghost[1]
#           #     if min_distance < 2:
#           #       closeAttackers.append(min_ghost)
#           #
#           # features['numCloseAttackers'] = len(closeAttackers)
#           # if len(closeAttackers) > 0:
#           #   print "TWO ATTACK!"
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeAttackers]
#           #   features['closeAttackerDistance'] = -min(dists)
#         else:
#           print "Kill enemy pacman two!"
#           # killPacmanTwo = True
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           # features['numInvaders'] = len(invaders)
#           # if len(invaders) > 0:
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           #   features['invaderDistance'] = min(dists)
#           #   if (min(dists) < 3):
#           #     print "KILL INVADER"
#           #     features['killInvader'] += 1 #seems to work mostly
#           # global invader
#           #
#           # if (invader == "no"):
#           #   print ("INVADER BOOL BEFORE: ", invader)
#           #   invader = "yes"
#           #   print ("INVADER BOOL AFTER: ", invader)
#
#           # global invader1
#           # global invader2
#           #
#           # if (self.index == teamNumbers[0]):  # first time will make one of them (True, False) and the other (False, False)
#           #   invader1[0] = False
#           #   invader1[1] = True
#           #   # invader2[0] = False
#           #   # invader2[1] = False
#           # elif (self.index == teamNumbers[1]):
#           #   # invader1[0] = False
#           #   # invader1[1] = False
#           #   invader2[0] = False
#           #   invader2[1] = True
#
#           killPacmanOne = True
#
#           enemies = []
#           enemy1 = None
#           enemy2 = None
#           j = 0
#           for i in self.getOpponents(successor):
#             # print ('i:', i)
#             # print ('j:', j)
#             enemies.append(successor.getAgentState(i))
#             if (j == 0):
#               enemy1 = i
#             if (j == 1):
#               enemy2 = i
#             j = j + 1
#
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#
#           invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#           # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
#           # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
#           # if (min(myRangeDist) <= min(teammateRangeDist)):
#           # if ((invader1[1] == True and invader2[1] == False) or (invader2[1] == True and invader1[1] == False)):
#
#           # global agentOneTarget
#           # global agentOneIndex
#           # global agentTwoTarget
#           # global agentTwoIndex
#
#           if len(invaders) == 1:
#             if agentOneTarget is None and agentTwoTarget is None: #initialize if none
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#                 if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#               else:
#                 if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                   agentOneTarget = enemy1
#                   agentOneIndex = teammateIndex
#                 if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                   agentOneTarget = enemy2
#                   agentOneIndex = teammateIndex
#
#             if agentOneTarget is not None and agentTwoTarget is None: # change agent for targeting when the other is closer to it
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 agentOneIndex = self.index
#             if agentOneTarget is None and agentTwoTarget is not None: # change agent for targeting when the other is closer to it (other case)
#               myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#               if myRangeDist < teammateRangeDist:
#                 agentOneIndex = self.index
#
#             if agentOneIndex == self.index or agentTwoIndex == self.index:  # proceed to chase ghost if you are assigned to it (or handles case where a1 dies first)
#               features['numInvaders'] = len(invaders)
#               if len(invaders) > 0:
#                 print "FACK 2"
#                 dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#                 features['invaderDistance'] = min(dists)
#                 if (min(dists) < 3):
#                   print "KILL INVADER"
#                   features['killInvader'] += 1  # seems to work mostly
#           elif len(invaders) == 2:  # do same behavior (for now)
#             if agentOneTarget is not None and agentTwoTarget is None: #initialize if none
#               if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy1
#                   agentTwoIndex = self.index
#               if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy2
#                   agentTwoIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy1
#                   agentTwoIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentOneTarget and agentOneIndex != self.index:
#                   agentTwoTarget = enemy2
#                   agentTwoIndex = self.index
#             if agentOneTarget is None and agentTwoTarget is not None: #initialize if none
#               if invaders[0].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#               if invaders[0].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy1).getPosition():
#                 if enemy1 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy1
#                   agentOneIndex = self.index
#               if invaders[1].getPosition() == successor.getAgentState(enemy2).getPosition():
#                 if enemy2 != agentTwoTarget and agentTwoIndex != self.index:
#                   agentOneTarget = enemy2
#                   agentOneIndex = self.index
#             features['numInvaders'] = len(invaders)
#             if len(invaders) > 0:
#               print "FACK 2"
#               dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#               features['invaderDistance'] = min(dists)
#               if (min(dists) < 3):
#                 print "KILL INVADER"
#                 features['killInvader'] += 1  # seems to work mostly (NO IT DOESN'T, MAKE IT NEGATIVE?)
#           # print ("INDEX2: ", self.index)
#           # features['numInvaders'] = len(invaders)
#           # if len(invaders) > 0:
#           #   print "FACK 2"
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           #   features['invaderDistance'] = min(dists)
#           #   if (min(dists) < 3):
#           #     print "KILL INVADER"
#           #     features['killInvader'] += 1  # seems to work mostly
#           # else:
#           #   invader = "no"
#       elif (enemy_two_position is not None) and not enemy_two.isPacman:  # enemy not pacman
#         if gameState.getAgentState(enemy_two_index).scaredTimer > 0:
#           print "Kill enemy two!"
#           killTwo = True
#           # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           # defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
#           # features['numDefenders'] = len(defenders)
#           # if len(defenders) > 0:
#           #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
#           #   if min(dists) <= 3:
#           #     print "Kill enemy two!"
#           #     features['defenderDistance'] = min(dists)
#         else:
#           # if (gameState.getAgentState(self.index).isPacman):
#           print "Run away from enemy two!"
#           runawayTwo = True
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#
#           # defenders = []
#           #
#           # for a in enemies:
#           #   if not a.isPacman and a.getPosition() != None:
#           #     if agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not a: #if ghost scaring you doesn't match your target, don't include it //double check you are agent 1
#           #       print "OMG2"
#           #     else:
#           #       defenders.append(a)
#           defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
#
#           # min_ghost_distance = 3
#           # min_ghost = None
#           ghost_positions = []
#           closeDefenders = []
#
#           if enemy_one_position is not None:
#             ghost_positions.append((enemy_one_position, enemy_one))
#           if enemy_two_position is not None:
#             ghost_positions.append((enemy_two_position, enemy_two))
#           min_distance = 999
#           for ghost in ghost_positions:  # 1 or 2 ghosts
#             current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
#             if min_distance > current_ghost_distance:  # always updates
#               min_distance = current_ghost_distance
#               min_ghost = ghost[1]
#               if min_distance < 3:
#                 closeDefenders.append(min_ghost)
#           # min_ghost_distance = min_distance
#
#           # if len(closeDefenders) > 0 and (agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]):
#           #   print "Do nothing2"
#           # else:
#
#           # has a target so ghost distance doesn't affect it!!?
#           # if len(closeDefenders) > 0 and ((agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]) or (agentTwoIndex == self.index and successor.getAgentState(agentTwoTarget) is not closeDefenders[0])):
#           #   print "Do nothing, kill invader"
#           if ((agentOneIndex == self.index and agentOneTarget is not None) or (agentTwoIndex == self.index and agentTwoTarget is not None)):
#             print "Do nothing, kill invader2"
#             # if (not successor.getAgentState(self.index).isPacman and agentOneIndex == self.index):
#             #   if not successor.getAgentState(agentOneTarget).isPacman:
#             #     print "JK2"
#             #     features['numCloseDefenders'] = len(closeDefenders)
#             #     if len(closeDefenders) > 0:
#             #       print "TWO!"
#             #
#             #       features['onDefense'] = 1
#             #       if successor.getAgentState(self.index).isPacman:
#             #         features['onDefense'] = 0
#             #         print "Cross 50!"
#             #
#             #       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             #       features['closeDefenderDistance'] = -min(dists)
#             # if (not successor.getAgentState(self.index).isPacman and agentTwoIndex == self.index):
#             #   if not successor.getAgentState(agentTwoTarget).isPacman:
#             #     print "JK2"
#             #     features['numCloseDefenders'] = len(closeDefenders)
#             #     if len(closeDefenders) > 0:
#             #       print "TWO!"
#             #
#             #       features['onDefense'] = 1
#             #       if successor.getAgentState(self.index).isPacman:
#             #         features['onDefense'] = 0
#             #         print "Cross 50!"
#             #
#             #       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             #       features['closeDefenderDistance'] = -min(dists)
#             # features['onDefense'] = 1
#             # if successor.getAgentState(self.index).isPacman:
#             #   features['onDefense'] = 0
#           else:
#             features['numCloseDefenders'] = len(closeDefenders)
#             if len(closeDefenders) > 0:
#               print "TWO!"
#
#               features['onDefense'] = 1
#               if successor.getAgentState(self.index).isPacman:
#                 features['onDefense'] = 0
#                 print "Cross 50!"
#
#               dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#               features['closeDefenderDistance'] = -min(dists)
#         #     -min(dists) - 1000?
#
#
#         # ghost_positions = [enemy_one_position, enemy_two_position]
#         # min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
#         # #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
#         # features['closest_ghost'] = 1/(min_ghost_distance + 0.1)
#
#     # Compute distance to the nearest food
#     # currentFoodList = self.getFood(gameState).asList()
#     foodList = self.getFood(successor).asList()  # based on successor
#
#     if (self.index == 0 or self.index == 1):
#       foodAreaID = 'top_half'
#     else:
#       foodAreaID = 'bottom_half'
#
#     boardHeight = gameState.data.food.height
#     halfHeight = boardHeight / 2
#     topFood = []
#     bottomFood = []
#     for food in foodList:
#       if food[1] > halfHeight/1.5:
#         topFood.append(food)
#       else:
#         bottomFood.append(food)
#
#     # print ("Top food: ", topFood)
#     # print ("Bottom food: ", bottomFood)
#     newFoodList = []
#     if foodAreaID == 'top_half':
#       newFoodList = topFood  # changed to topFood not foodList lol
#     else:
#       newFoodList = bottomFood # changed to topFood not foodList lol
#
#     # and ((self.index != agentOneIndex and self.index != agentTwoIndex))
#
#     if len(foodList) > 0:  # This should always be True,  but better safe than sorry
#       # if(self.index != agentOneIndex and self.index != agentTwoIndex):
#       #   minCapsuleDistance = 999
#       #   for capsule in capsuleList:
#       #     currCapsuleDist = self.getMazeDistance(myPos, capsule)
#       #     if minCapsuleDistance > currCapsuleDist:
#       #       minCapsuleDistance = currCapsuleDist
#       #   # minCapsuleDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
#       #   if minCapsuleDistance < 2:
#       #     features['munchCapsule'] = 1
#
#       myPos = successor.getAgentState(self.index).getPosition()  # coordinates of where you are after move
#       if (len(newFoodList) > 0):
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in newFoodList]) # after making move, get min distance to next food in successor food list
#       else:
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
#         teammate_positions = []
#         closeTeammates = []
#
#         teammate_position = None
#         teammate_obj= None
#
#         if successor.getAgentState(teamNumbers[0]).getPosition() is not None and self.index is not teamNumbers[0]:
#           teammate_position = successor.getAgentState(teamNumbers[0]).getPosition()
#           teammate_obj = successor.getAgentState(teamNumbers[0])
#         elif successor.getAgentState(teamNumbers[1]).getPosition() is not None and self.index is not teamNumbers[1]:
#           teammate_position = successor.getAgentState(teamNumbers[1]).getPosition()
#           teammate_obj = successor.getAgentState(teamNumbers[1])
#
#         if teammate_position is not None:
#           teammate_positions.append((teammate_position, teammate_obj))
#         min_distance = 999
#         for teammate in teammate_positions:  # should only be one teammember
#           current_teammate_distance = self.getMazeDistance(myPos, teammate[0])
#           if min_distance > current_teammate_distance:  # always updates
#             min_distance = current_teammate_distance
#             min_teammate = teammate[1]
#             if min_distance < 2: # or some other mid distance < 3?
#               closeTeammates.append(min_teammate)
#         # min_ghost_distance = min_distance
#
#         features['numCloseTeammates'] = len(closeTeammates)
#         if len(closeTeammates) > 0:
#           print "CLOSE TEAMMATE!"
#           dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeTeammates]
#           features['closeTeammateDistance'] = -min(dists)
#       # teamSeparationDistance = self.getMazeDistance(gameState.getAgentState(teamNumbers[0]).getPosition(),
#       #                                               gameState.getAgentState(teamNumbers[1]).getPosition())
#       # print ('Team Separation Distance: ', teamSeparationDistance)
#       # nextTeamSeparationDistance = self.getMazeDistance(successor.getAgentState(teamNumbers[0]).getPosition(),
#       #                                                   successor.getAgentState(teamNumbers[1]).getPosition())
#       # if teamSeparationDistance < nextTeamSeparationDistance:
#       #   # features['separateAgents'] = (self.index) # still causes tons of issues
#       #   features['separateAgents'] = teamSeparationDistance  # still causes tons of issues make it based on distance (closer = higher)
#       features['distanceToFood'] = min_food_distance
#
#     # Computes distance to invaders we can see
#     # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#     # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#     # features['numInvaders'] = len(invaders)
#     # if len(invaders) > 0:
#     #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#     #   features['invaderDistance'] = min(dists)
#       # dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#       # if (killPacmanTwo == True or killPacmanTwo == True):
#       #   print "Boop"
#       #   features['invaderDistance'] = min(dists)
#       # elif (runawayPacmanOne == True or runawayPacmanTwo == True):
#       #   print "Aye"
#       #   features['invaderDistance'] = -min(dists)
#
#     # # if len(currentFoodList) > len(foodList) and min_next_ghost_distance > 2:  # If we're going to eat food and the ghost is far away, +50
#     # if min_next_ghost_distance > 2
#     #   features['eatFood'] = 1
#     #   for ghost in defenders:
#     #     if (ghost.scaredTimer > 0):
#     #       features['numScared'] = len(defenders)
#     #       if len(defenders) > 0:
#     #         dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
#     #         if min(dists) <= 2:
#     #           print "BLAHAHAHAHA"
#     #           features['scaredDistance'] = min(dists)
#     #       # features['eat_range_ghost'] = -1
#     #
#     # if len(currentCapsuleList) > len(successorCapsules):
#     #   features['eatCapsule'] = 10
#     #
#     # if min_next_ghost_distance < 3:
#     #   if min_capsule_distance_now > min_capsule_distance_later:
#     #     features['goToCapsule'] = 1
#     #
#     #
#     #
#     # if min_next_ghost_distance == 2:  # If you move and ghost moves next to you, maybe dont go there
#     #   print("partialnut!")
#     #   features['maybe_kill_range_ghost'] = 1  # -50
#     #   # print "c"
#     # if min_next_ghost_distance <= 1:
#     #       # features['eat_range_ghost'] = 1
#     #     # else:
#     #       # print("poopnut!")
#     #     if (len(currentCapsuleList) > 0):
#     #       features['goToCapsule'] = +10
#     #       features['distanceToFood'] = 0 # forget about food (NEEDS TWEAKING! IF GOING TO CAPSULe DIRECTION KILLS VERSUS GETTING 1 EXTRA FOOD GET tHE FOOD)
#     #     features['kill_range_ghost'] = 1  # -100
#     #       # print "d"
#     #     print("poopnut!")
#     #   # features['kill_range_ghost'] = 1  # -100
#     #   # # print "d"
#
#     # print ("Kill Invader: ", features['killInvader'])
#
#     return features
#
#   # make it value capsules more than food and run away if near a ghost
#
#   def getWeights(self, gameState, action):
#     return {'successorScore': 100, 'onDefense': 100, 'distanceToFood': -1, 'numInvaders': -1000, 'invaderDistance': -10,'numDefenders': -1000, 'defenderDistance': -10, 'numCloseDefenders': -1000, 'closeDefenderDistance': -10, 'numCloseTeammates': -1000, 'closeTeammateDistance': -10, 'numCloseAttackers': -1000, 'closeAttackerDistance': -10,'killInvader': 1, 'munchCapsule': 1, 'separateAgents': -1}
#
# class DefensiveReflexAgent(ReflexCaptureAgent):
#   """
#   A reflex agent that keeps its side Pacman-free. Again,
#   this is to give you an idea of what a defensive agent
#   could be like.  It is not the best or only way to make
#   such an agent.
#   """
#
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#
#     myState = successor.getAgentState(self.index)
#     myPos = myState.getPosition()
#
#     # Computes whether we're on defense (1) or offense (0)
#     features['onDefense'] = 1
#     if myState.isPacman: features['onDefense'] = 0
#
#     # Computes distance to invaders we can see
#     enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] #in range
#     features['numInvaders'] = len(invaders)
#     if len(invaders) > 0:
#       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#       features['invaderDistance'] = min(dists)
#
#     if action == Directions.STOP: features['stop'] = 1
#     rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
#     if action == rev: features['reverse'] = 1
#
#     return features
#
#   # Defend flag valued more than going on wild goose chase (be defensive overall) -> attack when opponent killed?
#
#   def getWeights(self, gameState, action):
#     return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}



















# def createTeam(firstIndex, secondIndex, isRed,
#                first = 'DummyAgent', second = 'DummyAgent'):
#   """
#   This function should return a list of two agents that will form the
#   team, initialized using firstIndex and secondIndex as their agent
#   index numbers.  isRed is True if the red team is being created, and
#   will be False if the blue team is being created.
#
#   As a potentially helpful development aid, this function can take
#   additional string-valued keyword arguments ("first" and "second" are
#   such arguments in the case of this function), which will come from
#   the --redOpts and --blueOpts command-line arguments to capture.py.
#   For the nightly contest, however, your team will be created without
#   any extra arguments, so you should make sure that the default
#   behavior is what you want for the nightly contest.
#   """
#
#   # The following line is an example only; feel free to change it.
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]
#
# ##########
# # Agents #
# ##########
#
# class DummyAgent(CaptureAgent):
#   """
#   A Dummy agent to serve as an example of the necessary agent structure.
#   You should look at baselineTeam.py for more details about how to
#   create an agent as this is the bare minimum.
#   """
#
#   def registerInitialState(self, gameState):
#     """
#     This method handles the initial setup of the
#     agent to populate useful fields (such as what team
#     we're on).
#
#     A distanceCalculator instance caches the maze distances
#     between each pair of positions, so your agents can use:
#     self.distancer.getDistance(p1, p2)
#
#     IMPORTANT: This method may run for at most 15 seconds.
#     """
#
#     '''
#     Make sure you do not delete the following line. If you would like to
#     use Manhattan distances instead of maze distances in order to save
#     on initialization time, please take a look at
#     CaptureAgent.registerInitialState in captureAgents.py.
#     '''
#     CaptureAgent.registerInitialState(self, gameState)
#
#     '''
#     Your initialization code goes here, if you need any.
#     '''
#
#
#   def chooseAction(self, gameState):
#     """
#     Picks among actions randomly.
#     """
#     actions = gameState.getLegalActions(self.index)
#
#     '''
#     You should change this in your own agent.
#     '''
#
#     return random.choice(actions)


























# class OffensiveReflexAgent(ReflexCaptureAgent):
#   """
#   A reflex agent that seeks food. This is an agent
#   we give you to get an idea of what an offensive agent might look like,
#   but it is by no means the best or only way to build an offensive agent.
#   """
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     currentFoodList = self.getFood(gameState).asList()
#     successor = self.getSuccessor(gameState, action)
#     features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move
#
#     # Compute distance to the nearest food
#     foodList = self.getFood(successor).asList() # based on successor
#     if len(foodList) > 0: # This should always be True,  but better safe than sorry
#
#       # Define closest food distance feature
#       myPos = successor.getAgentState(self.index).getPosition() # coordinates of where you are after move
#       min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList]) # after making move, get min distance to next food in successor food list
#       #min_food_distance = min([util.manhattanDistance(myPos, food) for food in foodList])
#       features['distanceToFood'] = min_food_distance
#
#       #print("distances", gameState.getAgentDistances())
#       # Define closest,  ghost distance feature
#       enemy_one_position = successor.getAgentState(0).getPosition()
#       enemy_two_position = successor.getAgentState(2).getPosition()
#
#       #print("eneny one", successor.getAgentState(0).getPosition())
#
#       #min_ghost_distance = 3
#
#       #print("pos1", enemy_one_position)
#       if enemy_one_position is not None and enemy_two_position is not None:
#         ghost_positions = [enemy_one_position, enemy_two_position]
#         min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
#         #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
#         features['closest_ghost'] = 1/(min_ghost_distance + 0.1)
#
#
#       #print("min ghost distance", min_ghost_distance)
#
#       # if len(currentFoodList) == len(foodList) and min_ghost_distance >= 2: #If we dont eat food but ghost is far away, get direction towards next closest food
#       #   features['distanceToFood'] = min_food_distance
#       #
#       # elif len(currentFoodList) > len(foodList) and min_ghost_distance >= 2: #If we're going to eat food and the ghost is far away, +50
#       #   features['eatFood'] = 1
#       #
#       #
#       # if min_ghost_distance == 2: #If you move and ghost moves next to you, maybe dont go there
#       #   features['maybe_kill_range_ghost'] = 1 / min_ghost_distance
#       # if min_ghost_distance == 1:
#       #   print("poopnut!")
#       #   features['kill_range_ghost'] = 1 / min_ghost_distance
#
#
#
#     return features
#
#   # make it value capsules more than food and run away if near a ghost
#
#   def getWeights(self, gameState, action):
#
#     #return {'successorScore': 0, 'distanceToFood': -1, 'eatFood': 50, 'maybe_kill_range_ghost': -50 ,'kill_range_ghost': -100}
#     return {'successorScore': 100, 'distanceToFood': -1, 'closest_ghost': -15}





















# class OffensiveReflexAgent(ReflexCaptureAgent):
#   """
#   A reflex agent that seeks food. This is an agent
#   we give you to get an idea of what an offensive agent might look like,
#   but it is by no means the best or only way to build an offensive agent.
#   """
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     currentFoodList = self.getFood(gameState).asList()
#     # print currentFoodList
#     currentCapsuleList = self.getCapsules(gameState)
#     successor = self.getSuccessor(gameState, action)
#     successorCapsules = self.getCapsules(successor)
#     # features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move
#     features['successorScore'] = 1
#     features['distanceToFood'] = 0
#     features['maybe_kill_range_ghost'] = 0
#     features['kill_range_ghost'] = 0
#     features['eatFood'] = 0
#
#     # print self.getTeam(gameState)
#     teamNumbers = self.getTeam(gameState)
#     ourAgentStates = []
#     for index in teamNumbers:
#       ourAgentStates.append(successor.getAgentState(index))
#
#     enemyPacman = []     # Enemy is pacman
#     enemyGhosts = []    # Enemy is still ghost
#
#     ghostNumbers = self.getOpponents(gameState)
#     ghostAgentStates = []
#     for index in ghostNumbers:
#       ghostAgentStates.append(successor.getAgentState(index))
#       if successor.getAgentState(index).isPacman:
#         enemyPacman.append(successor.getAgentState(index).getPosition())
#       else:
#         enemyGhosts.append(successor.getAgentState(index).getPosition())
#
#     # print ("Enemy pacman: ", enemyPacman)
#     if (self.index == 0 or self.index == 1):
#       foodAreaID = 'top_half'
#     else:
#       foodAreaID = 'bottom_half'
#
#     foodList = self.getFood(successor).asList()  # based on successor
#
#     boardHeight = gameState.data.food.height
#     halfHeight = boardHeight / 2
#     topFood = []
#     bottomFood = []
#     for food in foodList:
#       if food[1] > halfHeight:
#         topFood.append(food)
#       else:
#         bottomFood.append(food)
#
#     print ("Top food: ", topFood)
#     print ("Bottom food: ", bottomFood)
#     newFoodList = []
#     if foodAreaID == 'top_half':
#       newFoodList = foodList
#     else:
#       newFoodList = foodList
#
#
#
#     # Compute distance to the nearest food
#     if len(foodList) > 0: # This should always be True,  but better safe than sorry
#
#       # Define closest food distance feature
#       currPos = gameState.getAgentState(self.index).getPosition()
#       myPos = successor.getAgentState(self.index).getPosition() # coordinates of where you are after move
#       if (len(newFoodList) > 0):
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in newFoodList]) # after making move, get min distance to next food in successor food list
#       else:
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
#       #min_food_distance = min([util.manhattanDistance(myPos, food) for food in foodList])
#       features['distanceToFood'] = min_food_distance
#
#       min_capsule_distance_now = 0
#       min_capsule_distance_later = 0
#
#       if len(currentCapsuleList) > 0:
#         min_capsule_distance_now = min([self.getMazeDistance(currPos, capsule) for capsule in currentCapsuleList])
#         min_capsule_distance_later = min([self.getMazeDistance(myPos, capsule) for capsule in currentCapsuleList])
#
#       all_indicies = [0, 1, 2, 3]
#       if teamNumbers[0] == 1 or teamNumbers[0] == 3:
#         # print "AHHHH"
#         current_enemy_one_position = gameState.getAgentState(0).getPosition()
#         current_enemy_two_position = gameState.getAgentState(2).getPosition()
#       else:
#         current_enemy_one_position = gameState.getAgentState(1).getPosition()
#         current_enemy_two_position = gameState.getAgentState(3).getPosition()
#
#       #print("distances", gameState.getAgentDistances())
#       # Define closest,  ghost distance feature
#       next_enemy_one_position = successor.getAgentState(0).getPosition()
#       next_enemy_two_position = successor.getAgentState(2).getPosition()
#
#       # print("eneny one", successor.getAgentState(0).getPosition())
#
#       min_ghost_distance = 3
#       min_ghost = None
#
#       # print("pos1", enemy_one_position)
#       if current_enemy_one_position is not None and current_enemy_two_position is not None:
#         ghost_positions = [current_enemy_one_position, current_enemy_two_position]
#         min_distance = 999
#         for ghost in ghost_positions:
#           current_ghost_distance = self.getMazeDistance(myPos, ghost)
#           if min_distance > current_ghost_distance:
#             min_distance = current_ghost_distance
#             min_ghost = ghost
#         min_ghost_distance = min_distance
#
#       min_next_ghost_distance = 3
#       min_next_ghost = None
#
#       #print("pos1", enemy_one_position)
#       if next_enemy_one_position is not None and next_enemy_two_position is not None:
#         next_ghost_positions = [next_enemy_one_position, next_enemy_two_position]
#         min_next_distance = 999
#         for ghost in next_ghost_positions:
#           current_ghost_distance = self.getMazeDistance(myPos, ghost)
#           if min_next_distance > current_ghost_distance:
#             min_next_distance = current_ghost_distance
#             min_next_ghost = ghost
#         min_next_ghost_distance = min_next_distance
#         # min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
#         #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
#         #features['closest_ghost'] = 1/(min_ghost_distance + 0.1)
#
#
#       # print("min ghost distance", min_ghost_distance)
#       # print action
#
#       # //////////////////////////////////////////////////////////
#
#       # gameState.getWalls()
#       # print gameState.data.food.height
#       # boardHeight = gameState.data.food.height
#       # halfHeight = boardHeight / 2
#       # topFood = []
#       # bottomFood = []
#       # for food in currentFoodList:
#       #   if food[1] > halfHeight:
#       #     topFood.append(food)
#       #   else:
#       #     bottomFood.apped(food)
#       # halfway = grid.width / 2
#       # halfgrid = Grid(grid.width, grid.height, False)
#       # if red:
#       #   xrange = range(halfway)
#       # else:
#       #   xrange = range(halfway, grid.width)
#       #
#       # for y in range(grid.height):
#       #   for x in xrange:
#       #     if grid[x][y]: halfgrid[x][y] = True
#
#       teamSeparationDistance = self.getMazeDistance(gameState.getAgentState(teamNumbers[0]).getPosition(), gameState.getAgentState(teamNumbers[0]).getPosition())
#       nextTeamSeparationDistance = self.getMazeDistance(successor.getAgentState(teamNumbers[0]).getPosition(), successor.getAgentState(teamNumbers[0]).getPosition())
#       if teamSeparationDistance < nextTeamSeparationDistance:
#        features['separateAgents'] = (self.index+1)*self.index # still causes tons of issues
#
#       # if action == Directions.STOP: features['stop'] = 1
#       # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
#       # if action == rev: features['reverse'] = 1
#
#         # print "a"
#       # elif len(currentFoodList) == len(foodList) and min_ghost_distance >= 2: #If we dont eat food but ghost is far away, get direction towards next closest food
#       #   features['distanceToFood'] = 1/min_food_distance # smaller the value the better it is
#       #   # print "b"
#       # Computes distance to invaders we can see
#       enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#       friendlies = [successor.getAgentState(i) for i in self.getTeam(successor)]
#       invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#       defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]
#       if len(invaders) > 0:
#         features['numInvaders'] = len(invaders)
#         dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#         for friend in friendlies:
#           if friend.scaredTimer > 0:
#             features['runAwayScared'] = -min(dists) #this is rewarding for runing away-> pushes away
#           else:
#             features['invaderDistance'] = min(dists) #this is rewarding for getting closer-> finds invader
#       # print ("Min ghost: ", min_ghost)
#
#
#       # if min_ghost in enemyPacman: # not null checked
#       #   if min_ghost_distance < min_next_ghost_distance:
#       #     features["turn_around"] = 1 #-100
#       #   else:
#       #     # features["eat_dat_boi"] = 1 #+100
#       #     if min_ghost_distance <= 5:  # OR not None, i.e. the ghost pacman is in range
#       #       print("nuttypoop!")
#       #       features['eat_range_ghost'] = 2  # +100
#       # # if enemyPacman:  # not null checked
#       #   # if min_ghost_distance == 2: #If you move and ghost moves next to you, maybe dont go there
#       #   #   features['maybe_eat_range_ghost'] = 1  # -50
#       #   #   print "c"
#       #   # print("nuttypoop!")
#       #   # features['eat_range_ghost'] = 1  # +100
#       #   # if min_ghost_distance <= 5: #OR not None, i.e. the ghost pacman is in range
#       #   #   print("nuttypoop!")
#       #   #   features['eat_range_ghost'] = 2 # -100
#       #   #   # print "d"
#       # else: # enemy ghost
#
#
#
#       if len(currentFoodList) > len(foodList) and min_next_ghost_distance > 2: #If we're going to eat food and the ghost is far away, +50
#         features['eatFood'] = 1
#       for ghost in defenders:
#           if (ghost.scaredTimer > 0):
#             features['numScared'] = len(defenders)
#             if len(defenders) > 0:
#               dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
#               if min(dists) <= 2:
#                 print "BLAHAHAHAHA"
#                 features['scaredDistance'] = min(dists)
#             # features['eat_range_ghost'] = -1
#
#       if len(currentCapsuleList) > len(successorCapsules):
#         features['eatCapsule'] = 10
#
#       if min_next_ghost_distance < 3:
#         if min_capsule_distance_now > min_capsule_distance_later:
#           features['goToCapsule'] = 1
#
#
#
#       if min_next_ghost_distance == 2:  # If you move and ghost moves next to you, maybe dont go there
#         print("partialnut!")
#         features['maybe_kill_range_ghost'] = 1  # -50
#         # print "c"
#       if min_next_ghost_distance <= 1:
#             # features['eat_range_ghost'] = 1
#           # else:
#             # print("poopnut!")
#           if (len(currentCapsuleList) > 0):
#             features['goToCapsule'] = +10
#             features['distanceToFood'] = 0 # forget about food (NEEDS TWEAKING! IF GOING TO CAPSULe DIRECTION KILLS VERSUS GETTING 1 EXTRA FOOD GET tHE FOOD)
#           features['kill_range_ghost'] = 1  # -100
#             # print "d"
#           print("poopnut!")
#         # features['kill_range_ghost'] = 1  # -100
#         # # print "d"
#
#
#
#     return features
#
#   # make it value capsules more than food and run away if near a ghost
#
#   def getWeights(self, gameState, action):
#
#     return {'successorScore': 100, 'goToCapsule': 5, 'eatCapsule': 500, 'separate': 10, 'numScared': -1000, 'numInvaders': -1000, 'distanceToFood': -1, 'eatFood': 50, 'maybe_kill_range_ghost': -50 ,'kill_range_ghost': -100, 'stop': -100, 'reverse': -2, 'eat_range_ghost': 100, 'turn_around': -100, 'eat_dat_boi': 100, 'invaderDistance': -10, 'scaredDistance': -10}
#     # return {'successorScore': 100, 'distanceToFood': -1, 'closest_ghost': -15}