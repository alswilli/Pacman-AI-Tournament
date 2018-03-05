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

# Globals
# global enemyIndexA = None
# global enemyIndexB = None

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
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor) # The score value (based on the game) after you make a move
    teamNumbers = self.getTeam(gameState)

    if teamNumbers[0] == 1 or teamNumbers[0] == 3:
      enemy_one = successor.getAgentState(0)
      enemy_two = successor.getAgentState(2)
      enemy_one_position = successor.getAgentState(0).getPosition()
      enemy_two_position = successor.getAgentState(2).getPosition()
      enemy_one_index = 0
      enemy_two_index = 2
    else:
      enemy_one = successor.getAgentState(1)
      enemy_two = successor.getAgentState(3)
      enemy_one_position = successor.getAgentState(1).getPosition()
      enemy_two_position = successor.getAgentState(3).getPosition()
      enemy_one_index = 1
      enemy_two_index = 3

    myPos = successor.getAgentState(self.index).getPosition()


    ### Tried to dumb it down and put this back in, instead of zone offense for now ######

    foodList = self.getFood(successor).asList()  # based on successor
    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(
        self.index).getPosition()  # coordinates of where you are after move
      minDistance = min([self.getMazeDistance(myPos, food) for food in
                         foodList])  # after making move, get min distance to next food in successor food list
      features['distanceToFood'] = 0

    ############################
    #### FOR ENEMY ONE ONLY ####
    ############################
    if enemy_one_position is not None:
      if enemy_one.isPacman:
        #If enemy one is a pacman and just ate a capsule, we gotta get the fuck out of there
        if gameState.getAgentState(self.index).scaredTimer > 0:
          print("My dude ate a capsule its time to dip")
          ghost_positions = []
          closeAttackers = []
          ghost_positions.append((enemy_one_position, enemy_one))
          min_distance = 999
          for ghost in ghost_positions: # 1 or 2 ghosts
            current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
            if min_distance > current_ghost_distance: #always updates
              min_distance = current_ghost_distance
              min_ghost = ghost[1]
              if min_distance < 50:
                closeAttackers.append(min_ghost)
          features['numCloseAttackers'] = len(closeAttackers)
          if len(closeAttackers) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeAttackers]
            features['closeAttackerDistance'] = -min(dists)

        # If enemy one is a pacman and hasnt ate a capsule, we gotta kill him
        else:
          print("lets kill this idiot")
          enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
          invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
          features['numInvaders'] = len(invaders)
          if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

      ##################################
      #### If we're on their side ######
      ##################################

      ### somehow when we go to kill the pacman on our side, Run away from enemy one is also called?

      elif enemy_one_position is not None and not enemy_one.isPacman:
        # Lets kill the ghosts since we've just ate a capsule
        if gameState.getAgentState(enemy_one_index).scaredTimer > 0:
          print("kill enemy One!")
        # We gotta run away if a ghost is within range!!
        else:
          print ("Run away from enemy One!")
          ghost_positions = []
          closeDefenders = []
          if enemy_one_position is not None:
            ghost_positions.append((enemy_one_position, enemy_one))
          min_distance = 999
          for ghost in ghost_positions: # 1 or 2 ghosts
            current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
            if min_distance > current_ghost_distance: #always updates
              min_distance = current_ghost_distance
              min_ghost = ghost[1]
              if min_distance < 3:
                closeDefenders.append(min_ghost)
          features['numCloseDefenders'] = len(closeDefenders)
          if len(closeDefenders) > 0:
            print "ONE!"
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
            features['closeDefenderDistance'] = -min(dists)

      ############################################################################################
      ### If we're doing one enemy at a time, we should doing += to our features for enemy two?? ###
      ############################################################################################

      ### does not need consideration right now, baselineTeam only has agent 1 come on our side
      # for testing capsule logic
      if enemy_two_position is not None and enemy_two.isPacman:
        if gameState.getAgentState(self.index).scaredTimer > 0:
          print("scuuuuuured")
      #   else:
      #     print "Kill enemy pacman two!"
      #     enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
      #     invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]  # in range
      #     features['numInvaders'] = len(invaders)
      #     if len(invaders) > 0:
      #       dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      #       features['invaderDistance'] = min(dists)
      # elif enemy_two_position is not None and not enemy_two.isPacman:  # enemy not pacman
      #   if gameState.getAgentState(enemy_two_index).scaredTimer > 0:
      #     print "Kill enemy two!"
        # else:
        #   print "Run away from enemy two!"
        #   enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        #   defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None]  # in range
        #
        #   ghost_positions = []
        #   closeDefenders = []
        #
        #   if enemy_one_position is not None:
        #     ghost_positions.append((enemy_one_position, enemy_one))
        #   if enemy_two_position is not None:
        #     ghost_positions.append((enemy_two_position, enemy_two))
        #   min_distance = 999
        #   for ghost in ghost_positions:  # 1 or 2 ghosts
        #     current_ghost_distance = self.getMazeDistance(myPos, ghost[0])
        #     if min_distance > current_ghost_distance:  # always updates
        #       min_distance = current_ghost_distance
        #       min_ghost = ghost[1]
        #       if min_distance < 3:
        #         closeDefenders.append(min_ghost)
        #   # min_ghost_distance = min_distance
        #
        #   features['numCloseDefenders'] = len(closeDefenders)
        #   if len(closeDefenders) > 0:
        #     print "TWO!"
        #     dists = [self.getMazeDistance(myPos, a.getPosition()) for a in closeDefenders]
        #     features['closeDefenderDistance'] = -min(dists)


    # Compute distance to the nearest food
    currentFoodList = self.getFood(gameState).asList()
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
      if food[1] > halfHeight:
        topFood.append(food)
      else:
        bottomFood.append(food)

    newFoodList = []
    if foodAreaID == 'top_half':
      newFoodList = topFood  # changed to topFood not foodList lol
    else:
      newFoodList = bottomFood # changed to topFood not foodList lol

    if len(foodList) > 0:  # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()  # coordinates of where you are after move
      if (len(newFoodList) > 0):
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in newFoodList]) # after making move, get min distance to next food in successor food list
      else:
        min_food_distance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = min_food_distance
    return features


  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'numInvaders': -1000, 'invaderDistance': -10,
            'numDefenders': -1000, 'defenderDistance': -10, 'numCloseDefenders': -1000, 'closeDefenderDistance': -10,
            'numCloseAttackers': -1000, 'closeAttackerDistance': -10}

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
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None] #in range
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
