# search.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""
import random

import searchAgents
import util as util
from game import Directions
from util import Stack
from GAsearch import GA, Chromosome


class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """
    
    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()
    
    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()
    
    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()
    
    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return [s, s, w, s, w, w, s, w]


def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print "Start:", problem.getStartState()
    print "Is the start a goal?", problem.isGoalState(problem.getStartState())
    print "Start's successors:", problem.getSuccessors(problem.getStartState())
    """
    "*** YOUR CODE HERE ***"
    stack = Stack()
    path = []
    closed = []
    stack.push((problem.getStartState(), path))
    while True:
        if stack.isEmpty():
            return []
        state, path = stack.pop()
        closed.append(state)
        if problem.isGoalState(state):
            return path
        closed.append(state)
        # PriorityQueue()
        successor = problem.getSuccessors(state)
        successor = sorted(successor, key = lambda x: x[2])
        # print("Current spot:", state, "Successor:", successor)
        for s in successor:
            if s[0] not in closed:
                newPath = path + [s[1]]
                stack.push((s[0], newPath))


def genAlgSearch(problem):
    """Use a genetic algorithm to create possible paths
    this method will verify the path and make a new generation if it doesn't work
    
    This should replace the run() method in GAsearch.py"""
    print("Genetic Algorithm Search")
    ga = GA(problem)
    
    best_overall = Chromosome(problem, [Directions.STOP], 500)
    best_generation = 0
    for gen in range(ga.num_generations):  # loop generations
        best = Chromosome(problem, [Directions.STOP], 300)  # empty initial best generation chromosome
        ga.build_population(best)
        # print(ga.population)
        for pop in ga.population:
            state, path = build_path(problem, problem.getStartState(), pop)
            
            # update scores for fitness function
            pop.cost = problem.getCostOfActions(path)
            pop.dist_s = searchAgents.mazeDistance(state, problem.getStartState(), problem.gameState)
            pop.dist_g = searchAgents.mazeDistance(state, problem.goal, problem.gameState)
            pop.score = problem.gameState.getScore()
            pop.size = len(problem.gameState.getWalls()[0])
            
            # print("Gene:", pop.calculate_fitness(), "\tBest:", best.calculate_fitness(), end = '\t')
            if pop.calculate_fitness() > best.calculate_fitness():
                best = pop.clone()
                # print("Clone:", best.calculate_fitness())
            # optimization
            if not problem.isGoalState(state):  # did not reach goal state, add another move
                pop.chromosome.append(
                    random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]))
        if best.calculate_fitness() > best_overall.calculate_fitness():
            best_overall = best
            best_generation = gen
        print("\nGeneration %d of %d, best:" % (gen + 1, ga.num_generations), best.chromosome)
        ga.reproduction_loop()
    # _, path = build_path(problem, problem.getStartState(), best)
    # if len(best_overall.chromosome) <= 1:
    #     print("Path result too short. Re-running...")
    #     genAlgSearch(problem)
    print("\nBest solution was found in generation %d out of %d" % ((best_generation + 1), ga.num_generations))
    print(best_overall.chromosome)
    return best_overall.chromosome


def build_path(problem, state, pop, rerun = False):
    path = []
    spot = 0
    for spot in range(len(pop.chromosome)):
        move = pop.chromosome[spot]
        # print(len(pop.chromosome))
        if move == Directions.STOP:
            pass
        successor = problem.getSuccessors(state)  # list: [next position, direction taken, cost]
        valid = False  # tracks whether the move was valid
        for option in successor:
            # print("Successor:", type(option), option, "\tChromosome:", type(move), move)
            s = option[0]
            d = option[1]
            c = option[2]
            # print(type(d), d, type(move), move, d == move)
            if d == move:  # option[1] is the cardinal direction
                pop.mutate(switch = True, spot = spot)
                state = s
                path.append(d)
                pop.cost += c
                valid = True
        # optimization
        if not valid:  # tried to move into a wall
            # print(pop.penalty)
            pop.penalty += 1  # each move into wall decreases fitness
            pop.chromosome[spot] = random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])
    # optimization
    if problem.isGoalState(state):  # reached the goal state, end
        # print("Found the goal!!!")
        return state, path
    elif not rerun:  # did not reach goal state, add another move
        pop.chromosome.append(random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]))
        build_path(problem, state, pop, rerun = True)
    return state, path


def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


def nullHeuristic(state, problem = None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0


def aStarSearch(problem, heuristic = nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()


# Abbreviations
dfs = depthFirstSearch
bfs = breadthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
gas = genAlgSearch
