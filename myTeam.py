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

#################
# Team creation #
#################

# Globals
# global enemyIndexA = None
# global enemyIndexB = None

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
  # global enemyIndexA
  # global enemyIndexB
  #
  # print enemyIndexA
  # print enemyIndexB
  # if (firstIndex == 0 and secondIndex == 2 or firstIndex == 2 and secondIndex == 0):
  #   enemyIndexA = 1
  #   enemyIndexB = 3
  # else:
  #   enemyIndexA = 0
  #   enemyIndexB = 2

  return [eval(first)(firstIndex), eval(second)(secondIndex)]

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
  def getFeatures(self, gameState, action):
    features = util.Counter()
    currentFoodList = self.getFood(gameState).asList()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList() # based on successor
    if len(foodList) > 0: # This should always be True,  but better safe than sorry

      # Define closest food distance feature
      myPos = successor.getAgentState(self.index).getPosition() # coordinates of where you are after move
      min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList]) # after making move, get min distance to next food in successor food list
      #min_food_distance = min([util.manhattanDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = min_food_distance

      #print("distances", gameState.getAgentDistances())
      # Define closest,  ghost distance feature
      enemy_one_position = successor.getAgentState(0).getPosition()
      enemy_two_position = successor.getAgentState(2).getPosition()

      #print("eneny one", successor.getAgentState(0).getPosition())

      #min_ghost_distance = 3

      #print("pos1", enemy_one_position)
      if enemy_one_position is not None and enemy_two_position is not None:
        ghost_positions = [enemy_one_position, enemy_two_position]
        min_ghost_distance = min([self.getMazeDistance(myPos, ghost) for ghost in ghost_positions]) # after making move, get min distance to next food in successor food list
        #min_ghost_distance = min([util.manhattanDistance(myPos, ghost) for ghost in ghost_positions])
        features['closest_ghost'] = 1/(min_ghost_distance + 0.1)


      #print("min ghost distance", min_ghost_distance)

      # if len(currentFoodList) == len(foodList) and min_ghost_distance >= 2: #If we dont eat food but ghost is far away, get direction towards next closest food
      #   features['distanceToFood'] = min_food_distance
      #
      # elif len(currentFoodList) > len(foodList) and min_ghost_distance >= 2: #If we're going to eat food and the ghost is far away, +50
      #   features['eatFood'] = 1
      #
      #
      # if min_ghost_distance == 2: #If you move and ghost moves next to you, maybe dont go there
      #   features['maybe_kill_range_ghost'] = 1 / min_ghost_distance
      # if min_ghost_distance == 1:
      #   print("poopnut!")
      #   features['kill_range_ghost'] = 1 / min_ghost_distance



    return features

  # make it value capsules more than food and run away if near a ghost

  def getWeights(self, gameState, action):

    #return {'successorScore': 0, 'distanceToFood': -1, 'eatFood': 50, 'maybe_kill_range_ghost': -50 ,'kill_range_ghost': -100}
    return {'successorScore': 100, 'distanceToFood': -1, 'closest_ghost': -15}

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
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
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

