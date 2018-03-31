# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint

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

  # global invader1
  # invader1 = [False, False]
  #
  # global invader2
  # invader2 = [False, False]

  # global AgentClass
  # AgentClass = ourAgentTracker(eval(first)(firstIndex), eval(second)(secondIndex))

  # global invader
  # invader = 'poop'

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

# class ourAgentTracker():
#   def __init__(self, agent1, agent2):
#     print("index of offensiveAgent1", agent1.index)
#     print("index of offensiveAgent2", agent2.index)
#     self.agent1 = agent1
#     self.agent2 = agent2
#     self.agent1_index = agent1.index
#     self.agent2_index = agent2.index
#     self.agent1_chasing_enemy = False
#     self.agent2_chasing_enemy = False

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState): #WILL NEED TO CHANGE
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

  def evaluate(self, gameState, action):   # THIS COULD POTENTIALLY CHANGE LATER
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
  # def __init__(self, index):
  #   print("index", index)

  def getFeatures(self, gameState, action):
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move

    # capsuleList = self.getCapsules(successor)
    # print ("Capsules: ", capsuleList)

    teamNumbers = self.getTeam(gameState)

    if teamNumbers[0] == 1 or teamNumbers[0] == 3: # assumes blue team
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
    if enemy_one_position is not None or enemy_two_position is not None: # changed from and to or
      if enemy_one_position is not None and enemy_one.isPacman:
        if gameState.getAgentState(self.index).scaredTimer > 0:
          # print "Run away from enemy pacman one!"
          runawayPacmanOne = True

          # IF ACTIONS == REVERSE BECAUSE OF ENEMY PACMAN, FORGET ABOUT FOOD? -> A-STAR another path?

          # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
          # if action == rev: features['reverse'] = 1

          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # attackers = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          #
          # # min_ghost_distance = 3
          # # min_ghost = None
          # ghost_positions = []
          # closeAttackers = []
          #
          # if enemy_one_position is not None:
          #   ghost_positions.append((enemy_one_position, enemy_one))
          # if enemy_two_position is not None:
          #   ghost_positions.append((enemy_two_position, enemy_two))
          # min_distance = 999
          # for ghost in ghost_positions:  # 1 or 2 ghosts
          #   current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
          #   if min_distance > current_ghost_distance:  # always updates
          #     min_distance = current_ghost_distance
          #     min_ghost = ghost[1]
          #     if min_distance < 2:
          #       closeAttackers.append(min_ghost)
          #
          # features['numCloseAttackers'] = len(closeAttackers)
          # if len(closeAttackers) > 0:
          #   print "ONE ATTACK!"
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeAttackers]
          #   features['closeAttackerDistance'] = -min(dists)
        else:
          # print "Kill enemy pacman one!"
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

          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # print ('ENEMIES: ', enemies)

          # invaders = []
          # v = 0
          # for a in enemies:
          #   if a.isPacman and a.getPosition() != None:
          #     invaders.append(a)
          #     if (v == 0):
          #       enemy1 = i
          #     if (v == 1):
          #       enemy2 = i
          #     v = v + 1
          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
          # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
          # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
          # if ((invader1[0] == True and invader2[0] == False) or (invader2[0] == True and invader1[0] == False)):
          # print ("INDEX: ", self.index)
          # global agentOneTarget
          # global agentOneIndex
          # global agentTwoTarget
          # global agentTwoIndex

          if len(invaders) == 1:
            if agentOneTarget is None and agentTwoTarget is None: #initialize if none
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
            if agentOneIndex == self.index or agentTwoIndex == self.index: # proceed to chase ghost if you are assigned to it
              features['numInvaders'] = len(invaders)
              if len(invaders) > 0:
                # print "FACK"

                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)
                if (min(dists) < 3):
                  # print "KILL INVADER"
                  features['killInvader'] += 1 #seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)
          elif len(invaders) == 2: # do same behavior (for now)
            if agentOneTarget is not None and agentTwoTarget is None: #initialize if none
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
              # print "FACK"
              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              features['invaderDistance'] = min(dists)
              if (min(dists) < 3):
                # print "KILL INVADER"
                features['killInvader'] += 1  # seems to work mostly (NO, ITS STILL BROKEN ADJUST WEIGHTS)
          # print ("INDEX: ", self.index)
          # features['numInvaders'] = len(invaders)
          # if len(invaders) > 0:
          #   print "FACK"
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          #   features['invaderDistance'] = min(dists)
          #   if (min(dists) < 3):
          #     print "KILL INVADER"
          #     features['killInvader'] += 1  # seems to work mostly
          # else:
          #   invader = "no"
      elif enemy_one_position is not None and not enemy_one.isPacman: # enemy not pacman
        if gameState.getAgentState(enemy_one_index).scaredTimer > 0:
          # print "Kill enemy one!"
          killOne = True

          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
          # features['numDefenders'] = len(defenders)
          # if len(defenders) > 0:
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
          #   if min(dists) <= 3: #tune
          #     print "Kill enemy one!"
          #     features['defenderDistance'] = min(dists)
        else:
          # if (gameState.getAgentState(self.index).isPacman):
          # print "Run away from enemy one!"
          runawayOne = True

          # if(not successor.getAgentState(self.index).isPacman):       // THIS ONE MAKES BOTH OF THEM STOP
          #   # Computes whether we're on defense (1) or offense (0)
          #   features['onDefense'] = 1
          #
          # if successor.getAgentState(self.index).isPacman:
          #   features['onDefense'] = 0

          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

          # defenders = []

          # for a in enemies:
          #   if not a.isPacman and a.getPosition() != None:
          #     if agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not a:  # if ghost scaring you doesn't match your target, don't include it
          #       print "OMG"
          #     else:
          #       defenders.append(a)
          defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range

          # min_ghost_distance = 3
          # min_ghost = None
          ghost_positions = []
          closeDefenders = []

          if enemy_one_position is not None:
            ghost_positions.append((enemy_one_position, enemy_one))
          if enemy_two_position is not None:
            ghost_positions.append((enemy_two_position, enemy_two))
          min_distance = 999
          for ghost in ghost_positions: # 1 or 2 ghosts
            current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
            if min_distance > current_ghost_distance: #always updates
              min_distance = current_ghost_distance
              min_ghost = ghost[1]
              if min_distance < 3:
                closeDefenders.append(min_ghost)
          # min_ghost_distance = min_distance

          # if (successor.getAgentState(teamNumbers[0]).isPacman and successor.getAgentState(teamNumbers[1]).isPacman):
          #   x = 0
          # else:
          # if len(closeDefenders) > 0 and ((agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]) or (agentTwoIndex == self.index and successor.getAgentState(agentTwoTarget) is not closeDefenders[0])):
          #   print "Do nothing, kill invader"
          if ((agentOneIndex == self.index) or (agentTwoIndex == self.index)):
            # print "Do nothing, kill invader1"
            n = 0
          else:
            features['numCloseDefenders'] = len(closeDefenders)
            if len(closeDefenders) > 0:
              # print "ONE!"
              # if (not successor.getAgentState(self.index).isPacman):
              #   # Computes whether we're on defense (1) or offense (0)
              #   features['onDefense'] = 1
              #
              # if successor.getAgentState(self.index).isPacman:
              #   features['onDefense'] = 0
              # features['onDefense'] = 1
              # if successor.getAgentState(self.index).isPacman:features['onDefense'] = 0

              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
              features['closeDefenderDistance'] = -min(dists)
    #      -min(dists) - 1000?


      if enemy_two_position is not None and enemy_two.isPacman:
        if gameState.getAgentState(self.index).scaredTimer > 0:
          # print "Run away from enemy pacman two!"
          runawayPacmanTwo = True

          # IF ACTIONS == REVERSE BECAUSE OF ENEMY PACMAN, FORGET ABOUT FOOD? -> A-STAR another path?

          # rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
          # if action == rev: features['reverse'] = 1

          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # attackers = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          #
          # # min_ghost_distance = 3
          # # min_ghost = None
          # ghost_positions = []
          # closeAttackers = []
          #
          # if enemy_one_position is not None:
          #   ghost_positions.append((enemy_one_position, enemy_one))
          # if enemy_two_position is not None:
          #   ghost_positions.append((enemy_two_position, enemy_two))
          # min_distance = 999
          # for ghost in ghost_positions:  # 1 or 2 ghosts
          #   current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
          #   if min_distance > current_ghost_distance:  # always updates
          #     min_distance = current_ghost_distance
          #     min_ghost = ghost[1]
          #     if min_distance < 2:
          #       closeAttackers.append(min_ghost)
          #
          # features['numCloseAttackers'] = len(closeAttackers)
          # if len(closeAttackers) > 0:
          #   print "TWO ATTACK!"
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeAttackers]
          #   features['closeAttackerDistance'] = -min(dists)
        else:
          # print "Kill enemy pacman two!"
          # killPacmanTwo = True
          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          # features['numInvaders'] = len(invaders)
          # if len(invaders) > 0:
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          #   features['invaderDistance'] = min(dists)
          #   if (min(dists) < 3):
          #     print "KILL INVADER"
          #     features['killInvader'] += 1 #seems to work mostly
          # global invader
          #
          # if (invader == "no"):
          #   print ("INVADER BOOL BEFORE: ", invader)
          #   invader = "yes"
          #   print ("INVADER BOOL AFTER: ", invader)

          # global invader1
          # global invader2
          #
          # if (self.index == teamNumbers[0]):  # first time will make one of them (True, False) and the other (False, False)
          #   invader1[0] = False
          #   invader1[1] = True
          #   # invader2[0] = False
          #   # invader2[1] = False
          # elif (self.index == teamNumbers[1]):
          #   # invader1[0] = False
          #   # invader1[1] = False
          #   invader2[0] = False
          #   invader2[1] = True

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

          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
          # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
          # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
          # if (min(myRangeDist) <= min(teammateRangeDist)):
          # if ((invader1[1] == True and invader2[1] == False) or (invader2[1] == True and invader1[1] == False)):

          # global agentOneTarget
          # global agentOneIndex
          # global agentTwoTarget
          # global agentTwoIndex

          if len(invaders) == 1:
            if agentOneTarget is None and agentTwoTarget is None: #initialize if none
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
                # print "FACK 2"
                dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
                features['invaderDistance'] = min(dists)
                if (min(dists) < 3):
                  # print "KILL INVADER"
                  features['killInvader'] += 1  # seems to work mostly
          elif len(invaders) == 2:  # do same behavior (for now)
            if agentOneTarget is not None and agentTwoTarget is None: #initialize if none
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
              # print "FACK 2"
              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
              features['invaderDistance'] = min(dists)
              if (min(dists) < 3):
                # print "KILL INVADER"
                features['killInvader'] += 1  # seems to work mostly (NO IT DOESN'T, MAKE IT NEGATIVE?)
          # print ("INDEX2: ", self.index)
          # features['numInvaders'] = len(invaders)
          # if len(invaders) > 0:
          #   print "FACK 2"
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
          #   features['invaderDistance'] = min(dists)
          #   if (min(dists) < 3):
          #     print "KILL INVADER"
          #     features['killInvader'] += 1  # seems to work mostly
          # else:
          #   invader = "no"
      elif (enemy_two_position is not None) and not enemy_two.isPacman:  # enemy not pacman
        if gameState.getAgentState(enemy_two_index).scaredTimer > 0:
          # print "Kill enemy two!"
          killTwo = True
          # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          # defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
          # features['numDefenders'] = len(defenders)
          # if len(defenders) > 0:
          #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
          #   if min(dists) <= 3:
          #     print "Kill enemy two!"
          #     features['defenderDistance'] = min(dists)
        else:
          # if (gameState.getAgentState(self.index).isPacman):
          # print "Run away from enemy two!"
          runawayTwo = True
          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

          # defenders = []
          #
          # for a in enemies:
          #   if not a.isPacman and a.getPosition() != None:
          #     if agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not a: #if ghost scaring you doesn't match your target, don't include it //double check you are agent 1
          #       print "OMG2"
          #     else:
          #       defenders.append(a)
          defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range

          # min_ghost_distance = 3
          # min_ghost = None
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
              if min_distance < 3:
                closeDefenders.append(min_ghost)
          # min_ghost_distance = min_distance

          # if len(closeDefenders) > 0 and (agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]):
          #   print "Do nothing2"
          # else:

          # has a target so ghost distance doesn't affect it!!?
          # if len(closeDefenders) > 0 and ((agentOneIndex == self.index and successor.getAgentState(agentOneTarget) is not closeDefenders[0]) or (agentTwoIndex == self.index and successor.getAgentState(agentTwoTarget) is not closeDefenders[0])):
          #   print "Do nothing, kill invader"
          if ((agentOneIndex == self.index) or (agentTwoIndex == self.index)):
            # print "Do nothing, kill invader2"
            n = 0
          else:
            features['numCloseDefenders'] = len(closeDefenders)
            if len(closeDefenders) > 0:
              # print "TWO!"

              # features['onDefense'] = 1
              # if successor.getAgentState(self.index).isPacman: features['onDefense'] = 0

              dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
              features['closeDefenderDistance'] = -min(dists)
        #     -min(dists) - 1000?


        # ghost_positions = [enemy_one_position, enemy_two_position]
        # min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
        # #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
        # features['closest_ghost'] = 1/(min_ghost_distance + 0.1)

    # Compute distance to the nearest food
    # currentFoodList = self.getFood(gameState).asList()
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
      if food[1] > halfHeight/1.5:
        topFood.append(food)
      else:
        bottomFood.append(food)

    # print ("Top food: ", topFood)
    # print ("Bottom food: ", bottomFood)
    newFoodList = []
    if foodAreaID == 'top_half':
      newFoodList = topFood  # changed to topFood not foodList lol
    else:
      newFoodList = bottomFood # changed to topFood not foodList lol

    # and ((self.index != agentOneIndex and self.index != agentTwoIndex))

    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      # if(self.index != agentOneIndex and self.index != agentTwoIndex):
      #   minCapsuleDistance = 999
      #   for capsule in capsuleList:
      #     currCapsuleDist = self.getMazeDistance(myPos, capsule)
      #     if minCapsuleDistance > currCapsuleDist:
      #       minCapsuleDistance = currCapsuleDist
      #   # minCapsuleDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsuleList])
      #   if minCapsuleDistance < 2:
      #     features['munchCapsule'] = 1

      myPos = successor.getAgentState(self.index).getPosition()  # coordinates of where you are after move
      if (len(newFoodList) > 0):
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in newFoodList]) # after making move, get min distance to next food in successor food list
      else:
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
        teammate_positions = []
        closeTeammates = []

        teammate_position = None
        teammate_obj= None

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
            if min_distance < 2: # or some other mid distance < 3?
              closeTeammates.append(min_teammate)
        # min_ghost_distance = min_distance

        features['numCloseTeammates'] = len(closeTeammates)
        if len(closeTeammates) > 0:
          # print "CLOSE TEAMMATE!"
          dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeTeammates]
          features['closeTeammateDistance'] = -min(dists)
      # teamSeparationDistance = self.getMazeDistance(gameState.getAgentState(teamNumbers[0]).getPosition(),
      #                                               gameState.getAgentState(teamNumbers[1]).getPosition())
      # print ('Team Separation Distance: ', teamSeparationDistance)
      # nextTeamSeparationDistance = self.getMazeDistance(successor.getAgentState(teamNumbers[0]).getPosition(),
      #                                                   successor.getAgentState(teamNumbers[1]).getPosition())
      # if teamSeparationDistance < nextTeamSeparationDistance:
      #   # features['separateAgents'] = (self.index) # still causes tons of issues
      #   features['separateAgents'] = teamSeparationDistance  # still causes tons of issues make it based on distance (closer = higher)
      features['distanceToFood'] = min_food_distance

    # Computes distance to invaders we can see
    # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
    # features['numInvaders'] = len(invaders)
    # if len(invaders) > 0:
    #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
    #   features['invaderDistance'] = min(dists)
      # dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      # if (killPacmanTwo == True or killPacmanTwo == True):
      #   print "Boop"
      #   features['invaderDistance'] = min(dists)
      # elif (runawayPacmanOne == True or runawayPacmanTwo == True):
      #   print "Aye"
      #   features['invaderDistance'] = -min(dists)

    # # if len(currentFoodList) > len(foodList) and min_next_ghost_distance > 2:  # If we're going to eat food and the ghost is far away, +50
    # if min_next_ghost_distance > 2
    #   features['eatFood'] = 1
    #   for ghost in defenders:
    #     if (ghost.scaredTimer > 0):
    #       features['numScared'] = len(defenders)
    #       if len(defenders) > 0:
    #         dists = [self.getMazeDistance(myPos, a.getPosition()) for a in defenders]
    #         if min(dists) <= 2:
    #           print "BLAHAHAHAHA"
    #           features['scaredDistance'] = min(dists)
    #       # features['eat_range_ghost'] = -1
    #
    # if len(currentCapsuleList) > len(successorCapsules):
    #   features['eatCapsule'] = 10
    #
    # if min_next_ghost_distance < 3:
    #   if min_capsule_distance_now > min_capsule_distance_later:
    #     features['goToCapsule'] = 1
    #
    #
    #
    # if min_next_ghost_distance == 2:  # If you move and ghost moves next to you, maybe dont go there
    #   print("partialnut!")
    #   features['maybe_kill_range_ghost'] = 1  # -50
    #   # print "c"
    # if min_next_ghost_distance <= 1:
    #       # features['eat_range_ghost'] = 1
    #     # else:
    #       # print("poopnut!")
    #     if (len(currentCapsuleList) > 0):
    #       features['goToCapsule'] = +10
    #       features['distanceToFood'] = 0 # forget about food (NEEDS TWEAKING! IF GOING TO CAPSULe DIRECTION KILLS VERSUS GETTING 1 EXTRA FOOD GET tHE FOOD)
    #     features['kill_range_ghost'] = 1  # -100
    #       # print "d"
    #     print("poopnut!")
    #   # features['kill_range_ghost'] = 1  # -100
    #   # # print "d"

    # print ("Kill Invader: ", features['killInvader'])

    return features

  # make it value capsules more than food and run away if near a ghost

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'onDefense': 100, 'distanceToFood': -1, 'numInvaders': -1000, 'invaderDistance': -10,'numDefenders': -1000, 'defenderDistance': -10, 'numCloseDefenders': -1000, 'closeDefenderDistance': -10, 'numCloseTeammates': -1000, 'closeTeammateDistance': -10, 'numCloseAttackers': -1000, 'closeAttackerDistance': -10,'killInvader': 1, 'munchCapsule': 1, 'separateAgents': -1}

class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  # A reflex agent that keeps its side Pacman-free. Again,
  # this is to give you an idea of what a defensive agent
  # could be like.  It is not the best or only way to make
  # such an agent.
  # """
  #
  # def getFeatures(self, gameState, action):
  #   features = util.Counter()
  #   successor = self.getSuccessor(gameState, action)
  #
  #   myState = successor.getAgentState(self.index)
  #   myPos = myState.getPosition()
  #
  #   # Computes whether we're on defense (1) or offense (0)
  #   features['onDefense'] = 1
  #   if myState.isPacman: features['onDefense'] = 0
  #
  #   # Computes distance to invaders we can see
  #   enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
  #   invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] #in range
  #   features['numInvaders'] = len(invaders)
  #   if len(invaders) > 0:
  #     dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
  #     features['invaderDistance'] = min(dists)
  #
  #   if action == Directions.STOP: features['stop'] = 1
  #   rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
  #   if action == rev: features['reverse'] = 1
  #
  #   return features
  #
  # # Defend flag valued more than going on wild goose chase (be defensive overall) -> attack when opponent killed?
  #
  # def getWeights(self, gameState, action):
  #   return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
















# # baselineTeam.py
# # ---------------
# # Licensing Information: Please do not distribute or publish solutions to this
# # project. You are free to use and extend these projects for educational
# # purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# # John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# # For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
#
# from captureAgents import CaptureAgent
# import distanceCalculator
# import random, time, util
# from game import Directions
# import game
# from util import nearestPoint
#
# #################
# # Team creation #
# #################
#
# def createTeam(firstIndex, secondIndex, isRed,
#                first = 'OffensiveReflexAgent', second = 'OffensiveReflexAgent'):
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
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]
#
# ##########
# # Agents #
# ##########
#
# class ReflexCaptureAgent(CaptureAgent):
#   """
#   A base class for reflex agents that chooses score-maximizing actions
#   """
#   def chooseAction(self, gameState):
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
#   def evaluateEnemy(self, gameState, action):   # THIS COULD POTENTIALLY CHANGE LATER
#     """
#     Computes a linear combination of features and feature weights
#     """
#     featuresEnemy = self.getFeaturesEnemy(gameState, action)
#     weightsEnemy = self.getWeightsEnemy(gameState, action)
#     return featuresEnemy * weightsEnemy
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
#   def getFeaturesEnemy(self, gameState, action):
#     """
#     Returns a counter of features for the state
#     """
#     featuresEnemy = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     featuresEnemy['successorScore'] = self.getScore(successor)
#     return featuresEnemy
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
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     features['successorScore'] = self.getScore(successor)  # The score value (based on the game) after you make a move
#
#     teamNumbers = self.getTeam(gameState)
#
#     if teamNumbers[0] == 1 or teamNumbers[0] == 3:  # assumes blue team
#       # print "You are Blue Team"
#       enemy_one = successor.getAgentState(0)
#       enemy_two = successor.getAgentState(2)
#       enemy_one_position = successor.getAgentState(0).getPosition()
#       enemy_two_position = successor.getAgentState(2).getPosition()
#       enemy_one_index = 0
#       enemy_two_index = 2
#       # current_enemy_one_position = gameState.getAgentState(0).getPosition()
#       # current_enemy_two_position = gameState.getAgentState(2).getPosition()
#     else:
#       # print "You are Red Team"
#       enemy_one = successor.getAgentState(1)
#       enemy_two = successor.getAgentState(3)
#       enemy_one_position = successor.getAgentState(1).getPosition()
#       enemy_two_position = successor.getAgentState(3).getPosition()
#       enemy_one_index = 1
#       enemy_two_index = 3
#       # current_enemy_one_position = gameState.getAgentState(1).getPosition()
#       # current_enemy_two_position = gameState.getAgentState(3).getPosition()
#
#     # min_ghost_distance = 3
#
#     # "Enemy in range!"
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
#
#     if (self.index == teamNumbers[0]):
#       teammatePos = successor.getAgentState(teamNumbers[1]).getPosition()
#     else:
#       teammatePos = successor.getAgentState(teamNumbers[0]).getPosition()
#
#     # Acts like switches for later added features
#     if enemy_one_position is not None or enemy_two_position is not None:  # changed from and to or
#       if enemy_one_position is not None and enemy_one.isPacman:
#         if gameState.getAgentState(self.index).scaredTimer > 0:
#           # print "Run away from enemy pacman one!"
#           runawayPacmanOne = True
#         else:
#           # global invaderTargetingArray
#           # invaderTargetingArray[0] = True
#           # global invader
#           # print "Kill enemy pacman one!"
#           #
#           # if (invader == "no"):
#           #   print ("INVADER BOOL BEFORE: ", invader)
#           #   invader = "yes"
#           #   print ("INVADER BOOL AFTER: ", invader)
#           # if (invaderTargetingArray[0] == True):
#           killPacmanOne = True
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#           # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
#           # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
#           # print ("INDEX: ", self.index)
#           features['numInvaders'] = len(invaders)
#           if len(invaders) > 0:
#             # print "FACK"
#             dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#             features['invaderDistance'] = min(dists)
#             if (min(dists) < 3):
#               # print "KILL INVADER"
#               features['killInvader'] += 1  # seems to work mostly
#               # else:
#               #   invader = "no"
#       elif enemy_one_position is not None and not enemy_one.isPacman:  # enemy not pacman
#         if gameState.getAgentState(enemy_one_index).scaredTimer > 0:
#           # print "Kill enemy one!"
#           killOne = True
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
#           # print "Run away from enemy one!"
#           runawayOne = True
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
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
#           features['numCloseDefenders'] = len(closeDefenders)
#           if len(closeDefenders) > 0:
#             # print "ONE!"
#             dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             features['closeDefenderDistance'] = -min(dists)
#
#       if enemy_two_position is not None and enemy_two.isPacman:
#         if gameState.getAgentState(self.index).scaredTimer > 0:
#           # print "Run away from enemy pacman two!"
#           runawayPacmanTwo = True
#         else:
#           # print "Kill enemy pacman two!"
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
#           killPacmanOne = True
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#           invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#           # myRangeDist = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#           # teammateRangeDist = [self.getMazeDistance(teammatePos, a.getPosition()) for a in invaders]
#           # distDifference = abs(min(myRangeDist) - min(teammateRangeDist))
#           # if (min(myRangeDist) <= min(teammateRangeDist) and distDifference < 16):
#           # if (min(myRangeDist) <= min(teammateRangeDist)):
#           # print ("INDEX2: ", self.index)
#           features['numInvaders'] = len(invaders)
#           if len(invaders) > 0:
#             # print "FACK 2"
#             dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#             features['invaderDistance'] = min(dists)
#             if (min(dists) < 3):
#               # print "KILL INVADER"
#               features['killInvader'] += 1  # seems to work mostly
#               # else:
#               #   invader = "no"
#       elif enemy_two_position is not None and not enemy_two.isPacman:  # enemy not pacman
#         if gameState.getAgentState(enemy_two_index).scaredTimer > 0:
#           # print "Kill enemy two!"
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
#           # print "Run away from enemy two!"
#           runawayTwo = True
#           enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
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
#           features['numCloseDefenders'] = len(closeDefenders)
#           if len(closeDefenders) > 0:
#             # print "TWO!"
#             dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
#             features['closeDefenderDistance'] = -min(dists)
#
#
#             # ghost_positions = [enemy_one_position, enemy_two_position]
#             # min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
#             # #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
#             # features['closest_ghost'] = 1/(min_ghost_distance + 0.1)
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
#       if food[1] > halfHeight / 1.5:
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
#       newFoodList = bottomFood  # changed to topFood not foodList lol
#
#     if len(foodList) > 0:  # This should always be True,  but better safe than sorry
#       myPos = successor.getAgentState(self.index).getPosition()  # coordinates of where you are after move
#       if (len(newFoodList) > 0):
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in
#                                  newFoodList])  # after making move, get min distance to next food in successor food list
#       else:
#         min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
#         teammate_positions = []
#         closeTeammates = []
#
#         teammate_position = None
#         teammate_obj = None
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
#             if min_distance < 2:  # or some other mid distance < 3?
#               closeTeammates.append(min_teammate)
#         # min_ghost_distance = min_distance
#
#         features['numCloseTeammates'] = len(closeTeammates)
#         if len(closeTeammates) > 0:
#           # print "CLOSE TEAMMATE!"
#           dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeTeammates]
#           features['closeTeammateDistance'] = -min(dists)
#           # teamSeparationDistance = self.getMazeDistance(gameState.getAgentState(teamNumbers[0]).getPosition(),
#           #                                               gameState.getAgentState(teamNumbers[1]).getPosition())
#           # print ('Team Separation Distance: ', teamSeparationDistance)
#           # nextTeamSeparationDistance = self.getMazeDistance(successor.getAgentState(teamNumbers[0]).getPosition(),
#           #                                                   successor.getAgentState(teamNumbers[1]).getPosition())
#           # if teamSeparationDistance < nextTeamSeparationDistance:
#           #   # features['separateAgents'] = (self.index) # still causes tons of issues
#           #   features['separateAgents'] = teamSeparationDistance  # still causes tons of issues make it based on distance (closer = higher)
#       features['distanceToFood'] = min_food_distance
#
#       # Computes distance to invaders we can see
#       # enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
#       # invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
#       # features['numInvaders'] = len(invaders)
#       # if len(invaders) > 0:
#       #   dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
#       #   features['invaderDistance'] = min(dists)
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
#     # make it value capsules more than food and run away if near a ghost
#
#   def getWeights(self, gameState, action):
#     return {'successorScore': 100, 'distanceToFood': -1, 'numInvaders': -1000, 'invaderDistance': -10,
#             'numDefenders': -1000, 'defenderDistance': -10, 'numCloseDefenders': -1000, 'closeDefenderDistance': -10,
#             'numCloseTeammates': -1000, 'closeTeammateDistance': -10, 'killInvader': 1, 'separateAgents': -1}
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
#     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
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





























# # baselineTeam.py
# # ---------------
# # Licensing Information: Please do not distribute or publish solutions to this
# # project. You are free to use and extend these projects for educational
# # purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# # John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# # For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
#
# from captureAgents import CaptureAgent
# import distanceCalculator
# import random, time, util
# from game import Directions
# import game
# from util import nearestPoint
#
# #################
# # Team creation #
# #################
#
# def createTeam(firstIndex, secondIndex, isRed,
#                first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
#   return [eval(first)(firstIndex), eval(second)(secondIndex)]
#
# ##########
# # Agents #
# ##########
#
# class ReflexCaptureAgent(CaptureAgent):
#   """
#   A base class for reflex agents that chooses score-maximizing actions
#   """
#   def chooseAction(self, gameState):
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
#   def evaluateEnemy(self, gameState, action):   # THIS COULD POTENTIALLY CHANGE LATER
#     """
#     Computes a linear combination of features and feature weights
#     """
#     featuresEnemy = self.getFeaturesEnemy(gameState, action)
#     weightsEnemy = self.getWeightsEnemy(gameState, action)
#     return featuresEnemy * weightsEnemy
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
#   def getFeaturesEnemy(self, gameState, action):
#     """
#     Returns a counter of features for the state
#     """
#     featuresEnemy = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     featuresEnemy['successorScore'] = self.getScore(successor)
#     return featuresEnemy
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
#   def getFeatures(self, gameState, action):
#     features = util.Counter()
#     successor = self.getSuccessor(gameState, action)
#     features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move
#
#     # Compute distance to the nearest food
#     foodList = self.getFood(successor).asList() # based on successor
#     if len(foodList) > 0: # This should always be True,  but better safe than sorry
#       myPos = successor.getAgentState(self.index).getPosition() # coordinates of where you are after move
#       minDistance = min([self.getMazeDistance(myPos, food) for food in foodList]) # after making move, get min distance to next food in successor food list
#       features['distanceToFood'] = minDistance
#     return features
#
#   # make it value capsules more than food and run away if near a ghost
#
#   def getWeights(self, gameState, action):
#     return {'successorScore': 100, 'distanceToFood': -1}
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
#     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
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
#     # return {'numInvaders': 0, 'onDefense': 0, 'invaderDistance': 0, 'stop': 0, 'reverse': 0}
