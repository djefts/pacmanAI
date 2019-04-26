"""
This file contains the code for the genetic-algorithm-based searchAgent
"""
from game import Directions
from game import Agent
import random
import search
import time
import util


class Chromosome:
    def __init__(self, problem, chromosome = None, penalty = 0):
        self.chromosome = []
        # Default build
        if chromosome is None:
            # print("Initialize 'None' chromosome")
            for i in range(100):
                self.chromosome.append(random.choice(Directions.directions))
            # print(self.chromosome)
    
        else:
            self.chromosome = chromosome
        # print("Chromosome:", self.chromosome)
    
        # Pacman-specific parameters
        self.problem = problem
        self.cost = 0
        self.dist_s = 1
        self.dist_g = util.manhattanDistance(problem.getStartState(), problem.goal)
        self.score = 0
        self.size = len(problem.gameState.getWalls()[0])
        self.penalty = penalty
    
    def crossover(self, other_chrom):
        multicrossover_len = 2
        
        # multicrossover self chromosome
        x = []
        for i in range(0, len(self.chromosome), multicrossover_len):
            try:  # prevent indexoutofbounds errors
                x.extend(self.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                x.extend(self.chromosome[i:])
                break
            i += multicrossover_len
            try:  # prevent indexoutofbounds errors
                x.extend(other_chrom.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                x.extend(other_chrom.chromosome[i:])
                break
        
        # multicrossover other chromosome
        y = []
        for i in range(0, len(self.chromosome), multicrossover_len):
            try:  # prevent indexoutofbounds errors
                y.extend(self.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                y.extend(self.chromosome[i:])
                break
            i += multicrossover_len
            try:  # prevent indexoutofbounds errors
                y.extend(other_chrom.chromosome[i:i + multicrossover_len])
            except IndexError as e:
                y.extend(other_chrom.chromosome[i:])
                break
        
        # crossover by appending sublists
        child1 = Chromosome(self.problem, x)
        child2 = Chromosome(self.problem, y)
        
        # Verify the children are legal before returning
        # print("\tCrossed", self.chromosome, "with", other_chrom.chromosome, "and got", child1.chromosome, "and",
        # child2.chromosome)
        if child1.verify_legal() and child2.verify_legal():
            return child1, child2
        else:
            # return self.crossover(other_chrom)
            print("Invalid chromosome")
            raise Exception
    
    def mutate(self, switch = False, spot = None):
        # Find a place to mutate
        locationOfMutation = random.randint(0, len(self.chromosome))
        
        # Mutate if will create legal child only
        tempChromosome = self.clone()
        if locationOfMutation < len(self.chromosome):
            tempChromosome.chromosome[locationOfMutation] = random.choice(Directions.directions)
            # if tempChromosome.verify_legal():
            #     print("\t\tMutating",self.chromosome,"to",tempChromosome.chromosome)
            # else:
            #     print("remutate")
            #     self.mutate()
        if switch:
            tempChromosome.chromosome[spot] = random.choice(Directions.directions)
        else:
            tempChromosome.chromosome.append(random.choice(Directions.directions))
        self.chromosome = tempChromosome.chromosome
    
    # def new_move(self):
    #     print("New Move")
    #     # print(type(self.chromosome[len(self.chromosome) - 1]), self.chromosome[len(self.chromosome) - 1])
    #     if self.chromosome[len(self.chromosome) - 1] == Directions.STOP:
    #         self.chromosome[len(self.chromosome) - 1] = random.choice(Directions.directions)
    #     else:
    #         self.chromosome.append(random.choice(Directions.directions))
    #     self.chromosome.append(Directions.STOP)
    
    # Used to determine if chromosome is legal
    def verify_legal(self):
        # print("Verify Legal")
        # if len(self.chromosome) > 100:
        #     return False
        for i in range(len(self.chromosome)):
            move = self.chromosome[i]
            # print(type(move), move)
            if move not in Directions.directions:
                print("move not in Directions.directions:", move)
                return False
        return True
    
    def calculate_fitness(self):
        # print("Calculate Fitness")
        return self.dist_s + self.score - self.cost + self.dist_g - self.penalty
    
    def clone(self):
        return Chromosome(self.problem, self.chromosome, self.cost)
    
    def __str__(self):
        return str(self.chromosome)


class GA:
    def __init__(self, problem):
        print("Initialize Genetic Algorithm")
        # Population parameters
        self.population_size = 150  # this number must be even or reproduction causes errors
        self.num_generations = 15
        self.probC = .8
        self.probM = .1
        
        # Initialize list class variables 0for population and roulette wheel
        self.population = []
        self.roulette_min = [0] * self.population_size
        self.roulette_max = [0] * self.population_size
        
        self.problem = problem
    
    def build_population(self, best):
        # print("Build Population")
        self.population = [best, best, best, best, best]
        for i in range(5, self.population_size):
            self.population.append(Chromosome(self.problem))
            # print("Populated Chromosome as:", self.population[i], self.population[i].calculate_fitness())
    
    def calc_roulette(self):
        """
        Constructs a roulette wheel for parent selection.
        """
        # print("Calculate Roulette")
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
        # print("Pick Chromosome")
        spin = random.uniform(0, 1)
        for i in range(0, self.population_size):
            if self.roulette_min[i] < spin <= self.roulette_max[i]:
                return i
        return self.population_size - 1
    
    def reproduction_loop(self):
        # print("Reproduction Loop")
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
