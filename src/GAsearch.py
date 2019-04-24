"""
This file contains the code for the genetic-algorithm-based searchAgent
"""
from game import Directions
from game import Agent
import random
import search
import time


class GenAlgAgent(Agent):
    """
    Genetic Algorithm Agent
    """
    
    def __init__(self, fn = 'depthFirstSearch', prob = 'PositionSearchProblem', heuristic = 'nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems
        
        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError(fn + ' is not a search function in search.py.')
        func = getattr(search, fn)
        if 'heuristic' not in func.__code__.co_varnames:
            print(('[SearchAgent] using function ' + fn))
            self.searchFunction = func
        else:
            if heuristic in list(globals().keys()):
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError(heuristic + ' is not a function in searchAgents.py or search.py.')
            print(('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic)))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic = heur)
        
        # Get the search problem type from the name
        if prob not in list(globals().keys()) or not prob.endswith('Problem'):
            raise AttributeError(prob + ' is not a search problem type in SearchAgents.py.')
        self.searchType = globals()[prob]
        print(('[SearchAgent] using problem type ' + prob))
    
    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game
        board. Here, we choose a path to the goal. In this phase, the agent
        should compute the path to the goal and store it in a local variable.
        All of the work is done in this method!

        state: a GameState object (pacman.py)
        """
        if self.searchFunction is None:
            raise Exception("No search function provided for SearchAgent")
        starttime = time.time()
        problem = self.searchType(state)  # Makes a new search problem
        self.actions = self.searchFunction(problem)  # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print(('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime)))
        if '_expanded' in dir(problem):
            print(('Search nodes expanded: %d' % problem._expanded))
    
    def getAction(self, state):
        """
        Returns the next action in the path chosen earlier (in
        registerInitialState).  Return Directions.STOP if there is no further
        action to take.

        state: a GameState object (pacman.py)
        """
        if 'actionIndex' not in dir(self):
            self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP


class Chromosome:
    def __init__(self, chromosome = None):
        self.chromosome = []
        
        # Default build
        if chromosome is None:
            self.default_build()
        # Copy parent
        else:
            self.chromosome = chromosome[:]
    
    def default_build(self):
        chromosome = []
        for i in range(50):
            chromosome.append(
                random.choice(Directions.directions))
        self.chromosome = chromosome
        if not self.verify_legal():
            self.default_build()
        return chromosome
    
    def crossover(self, other_chrom):
        multicrossover_len = 3
        
        # multicrossover self chromosome
        x = []
        for i in range(0, len(self.chromosome), multicrossover_len):
            try:  # prevent indexoutofbounds errors
                x.append(self.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                x.append(self.chromosome[i:])
                break
            i += multicrossover_len
            try:  # prevent indexoutofbounds errors
                x.append(other_chrom[i:i + multicrossover_len])
            except IndexError as e:
                x.append(other_chrom[i:])
                break
        
        # multicrossover other chromosome
        y = []
        for i in range(0, len(self.chromosome), multicrossover_len):
            try:  # prevent indexoutofbounds errors
                y.append(self.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                y.append(self.chromosome[i:])
                break
            i += multicrossover_len
            try:  # prevent indexoutofbounds errors
                y.append(other_chrom[i:i + multicrossover_len])
            except IndexError as e:
                y.append(other_chrom[i:])
                break
        
        # crossover by appending sublists
        child1 = Chromosome(x)
        child2 = Chromosome(y)
        
        # Verify the children are legal before returning
        if child1.verify_legal() and child2.verify_legal():
            # print("\tCrossed",self.chromosome,"with",other_chrom.chromosome,"and got",child1.chromosome, "and",
            # child2.chromosome)
            return child1, child2
        else:
            # return self.crossover(other_chrom)
            print("Invalid chromosome")
            raise Exception
    
    def mutate(self):
        # Find a place to mutate
        locationOfMutation = random.randint(0, len(self.chromosome) - 1)
        
        # Mutate if will create legal child only
        tempChromosome = self.clone()
        tempChromosome.chromosome[locationOfMutation] = random.choice(Directions.directions)
        if tempChromosome.verify_legal():
            # print("\t\tMutating",self.chromosome,"to",tempChromosome.chromosome)
            self.chromosome = tempChromosome.chromosome
        else:
            self.mutate()
    
    # Used to determine if chromosome is legal
    def verify_legal(self):
        for move in range(len(self.chromosome)):
            if move == Directions.STOP:  # cut the chromosome off if there is a STOP move
                self.chromosome = self.chromosome[:self.chromosome.index(move) + 1]
                return True
            if move not in Directions.directions:
                return False
        return True
    
    def calculate_fitness(self):
        fitness = 1000
        fitness -= len(self.chromosome)
        fitness += game.state.getScore()
        return fitness
    
    def clone(self):
        return Chromosome(self.chromosome)
    
    def __str__(self):
        return str(self.chromosome)


class GA:
    def __init__(self):
        # Population parameters
        self.population_size = 20  # this number must be even or reproduction causes errors
        self.num_generations = 30
        self.probC = .7
        self.probM = .1
        
        # Initialize list class variables for population and roulette wheel
        self.population = []
        self.roulette_min = [0] * self.population_size
        self.roulette_max = [0] * self.population_size
    
    def build_population(self):
        for i in range(0, self.population_size):
            self.population.append(Chromosome())
            for bit in range(len(self.population[i].chromosome)):
                rand = random.randint(0, 100)
                if rand >= 50:
                    self.population[i].chromosome[bit] = 1
                if not self.population[i].verify_legal():
                    self.population[i].chromosome[bit] = 0
            # print("Populated Chromosome as:", self.population[i], self.population[i].calculate_fitness())
    
    def calc_roulette(self):
        """
        Constructs a roulette wheel for parent selection.
        """
        # Determine the total fitness
        sum = 0
        for chromosome in self.population:
            sum = sum + chromosome.calculate_fitness()
        
        # Generates roulette wheel where roulette_max[i] - roulette_min[i] == chromosome[i].getFitness()
        self.roulette_min[0] = 0
        for i in range(0, self.population_size):
            if i != 0:
                self.roulette_min[i] = self.roulette_max[i - 1]
            self.roulette_max[i] = self.roulette_min[i] + self.population[i].calculate_fitness() / sum
    
    def pick_chromosome(self):
        """
        Using roulette wheel, returns the index of a parent for reproduction.
        @:return index of chromosome to reproduce.
        """
        spin = random.uniform(0, 1)
        for i in range(0, self.population_size):
            if self.roulette_min[i] < spin <= self.roulette_max[i]:
                return i
        return self.population_size - 1
    
    def reproduction_loop(self):
        self.calc_roulette()
        new_population = []
        for i in range(0, self.population_size, 2):
            parent1 = self.population[self.pick_chromosome()]
            parent2 = self.population[self.pick_chromosome()]
            x = parent1.clone()
            y = parent2.clone()
            rand = random.uniform(0, 1)
            # crossover
            if rand <= self.probC:
                x, y = x.crossover(y)
            rand = random.uniform(0, 1)
            # mutate
            if rand <= self.probM:
                x.mutate()
                y.mutate()
            new_population.append(x)
            new_population.append(y)
        self.population = new_population
    
    def get_average(self):
        sum = 0
        for pop in self.population:
            sum += pop.calculate_fitness()
        return sum / self.population_size
    
    def get_best(self):
        bestF = 0
        best = self.population[0]
        for pop in self.population:
            fit = pop.calculate_fitness()
            if fit > bestF:
                best = pop
                bestF = fit
        return best
    
    def run(self):
        best = Chromosome(self.num_bags, self.items, self.max_weight)
        best_overall = Chromosome(self.num_bags, self.items, self.max_weight)
        self.build_population()
        for i in range(self.num_generations):
            print("\nGeneration", i + 1)
            self.reproduction_loop()
            best = self.get_best().clone()
            if best.calculate_fitness() < best_overall.calculate_fitness():
                best_overall = best.clone()
            print("\tBest chromosome:", best)
            print("\tBest fitness:", best.calculate_fitness())
            print("\tAverage:", self.get_average())
        self.print_results(best_overall)
    
    def print_results(self, best):
        print()
        
        print("=====FINAL RESULTS=====")
        for i in range(len(self.items)):
            if best.get_bag_num(i) == 0:
                print("Place item", i + 1, "in no bag")
            else:
                print("Place item", i + 1, "in bag", best.get_bag_num(i))
        
        for i in range(self.num_bags):
            print("Bag", i + 1, "with weight:", best.knapsacks[i][1], "and profit:", best.knapsacks[i][0])
        
        print("Final best fitness:", best.calculate_fitness())
