from typing import List, Callable, Tuple
from random import choices, randint, randrange, random
from collections import namedtuple
from enum import Enum
from functools import partial
from rich import print, pretty
from rich.table import Table
from rich.console import Console

pretty.install()

# sequence of 0s and 1s
Genome = List[int]

# sequence of genomes
Population = List[Genome]

Food = namedtuple("Food", ["name", "calories", "fat", "protein", "carbs", "sugar", "price", "taste"])
foods = [
    Food("Eggs          ", 231, 15, 18, 1.8, 1.8, 2.99, 7),
    Food("Chicken Breast", 165, 3.6, 31, 0.01, 0.01, 1.99, 8),
    Food("Rye Bread     ", 260, 3.3, 9, 48, 4, 4.99, 7),
    Food("Butter        ", 717, 81, 0.9, 0.1, 0.1, 5.99, 8),
    Food("Milk Chocolate", 535, 30, 8, 59, 52, 2.49, 9),
    Food("Honey         ", 304, 0.01, 0.3, 82, 82, 4.49, 8.5),
    Food("Milk          ", 149, 8, 8, 12, 12, 1.59, 6),
    Food("Greek Yoghurt ", 146, 3.8, 20, 7.8, 4, 1.99, 8),
    Food("Strawberries  ", 91, 0.3, 0.67, 7.7, 4.9, 4.99, 9),
    Food("Banana        ", 89, 0.3, 1, 23, 12, 1.39, 9.5),
    Food("Apple         ", 52, 0.2, 0.3, 14, 10, 1.29, 7),
    Food("Pecan Nuts    ", 400, 40, 5, 8, 2, 5.99, 6),
    Food("Steak         ", 405, 30, 38, 0.01, 0.01, 10.99, 10),
    Food("Protein Powder", 100, 2, 22, 4, 2, 1.99, 8),
    Food("Protein Yogurt", 180, 1, 20, 6, 4, 1.29, 8.5),
    Food("Blueberries   ", 60, 0.3, 0.7, 15, 10, 4.99, 9),
    Food("Almonds       ", 580, 50, 21, 21.55, 4.35, 4.79, 5.5),
    Food("Broccoli      ", 34, 0.4, 2.8, 7, 1.7, 4.69, 3.5),
    Food("Tomatoes      ", 22.5, 0.25, 1.1, 4.86, 2.6, 1.99, 6.5),
    Food("Potatoes      ", 320, 0.1, 2, 19, 0.2, 2.49, 9),
    Food("Rice          ", 150, 0.3, 2.7, 28, 0.1, 2.09, 8.5),
    Food("Watermelon    ", 30, 0.2, 0.6, 8, 6, 3.99, 9.5)
]

FoodWeight = Enum("Food Weight", ["CALORIES", "FAT", "PROTEIN", "CARBS", "SUGAR", "TASTE"])

FitnessFunction = Callable[[Genome, [Food], FoodWeight], int]
PopulateFunction = Callable[[], Population]
SelectionFunction = Callable[[Population, FitnessFunction], Tuple[Genome, Genome]]
CrossoverFunction = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunction = Callable[[Genome], Genome]


# generates a genome
# which is a sequence of 0s and 1s
# 1 - the food fits into our meal
# 0 - the food doesn't fit into our mean
def generate_genome(length: int) -> Genome:
    return choices([0, 1], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    population: Population = []
    for _ in range(size):
        genome: Genome = generate_genome(genome_length)
        population.append(genome)
    
    return population


def fitness(genome: Genome, foods: [Food], food_weight: FoodWeight, weight_limit: int) -> int:
    if len(genome) != len(foods):
        raise ValueError("genome and foods list must be of the same length")
    
    weight = 0  # cumulative chosen weight for all food items
    value = 0   # total cost of foods items

    for i, food in enumerate(foods):
        if genome[i] == 1:
            match food_weight:
                case FoodWeight.CALORIES:
                    weight += food.calories
                case FoodWeight.FAT:
                    weight += food.fat
                case FoodWeight.PROTEIN:
                    weight += food.protein
                case FoodWeight.CARBS:
                    weight += food.carbs
                case FoodWeight.SUGAR:
                    weight += food.sugar
                case FoodWeight.TASTE:
                    weight += food.taste

            value += food.price

            if weight > weight_limit:
                return 0
    
    return value


def selection(population: Population, fitness_func: FitnessFunction) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2  # only 2 parents to form the next generation of genomes
    )


def crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    if len(a) != len(b):
        raise ValueError("genomes a and b must be of the same length")

    length = len(a)
    if length < 2:
        return a, b
    
    p = randint(1, length-1)

    # return genomes a and b, mixed between each other
    return a[0:p] + b[p:], b[0:p] + a[p:]


def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome))
        if random() <= probability:
            genome[index] = abs(genome[index] - 1)
    
    return genome


def run_evolution(
        populate_function: PopulateFunction,
        fitness_function: FitnessFunction,
        fitness_limit: int,
        selection_function: SelectionFunction = selection,
        crossover_function: CrossoverFunction = crossover,
        mutation_function: MutationFunction = mutation,
        generation_limit: int = 100
) -> Tuple[Population, int]:
    
    # generate first generation
    population = populate_function()

    value = 0

    # loop until generation limit
    for i in range(generation_limit):
        # sort population by fitness
        # top solutions inhabit first indices of our list of genomes
        population = sorted(
            population,
            key=lambda genome: fitness_function(genome),
            reverse=True
        )

        value = fitness_function(population[0])
        if value >= fitness_limit:
            break

        # elitism - we keep our top 2 solutions to move to our next generation regardless of selection, crossover & mutation
        next_generation = population[0:2]

        # generate next generation
        for _ in range(int(len(population) / 2) - 1):
            # select 2 parents
            parents = selection_function(population, fitness_function)
            # perform crossover & get 2 children
            child_a, child_b = crossover_function(parents[0], parents[1])
            # mutate both children - expands the variety of solutions that we generate
            child_a = mutation_function(child_a)
            child_b = mutation_function(child_b)

            # add newly generated children to the next generation
            next_generation += [child_a, child_b]
        
        population = next_generation

    # current population sorted by fitness
    population = sorted(
        population,
        key=lambda genome: fitness_function(genome),
        reverse=True
    )

    # return current (sorted) population & number of generations it took to find the optimal solution
    return population, i, value





def ui():
    print("""
============================================================================================================================
              GENETIC ALGORITHM designed for picking optimal food items based on a specific nutrient and price                          
============================================================================================================================
PICK A NUTRIENT, ITS TARGET AMOUNT, YOUR BUDGET, SIZE OF THE INITIAL POPULATION & THE MAXIMUM NUMBER OF GENERATIONS""")    

def user_input():
    nutrient = input("\npick a nutrient [calories/fat/protein/carbs/sugar]: ")
    nutrient_intake = 0
    if nutrient != "calories":
        nutrient_intake = int(input(f"enter max amount of {nutrient} (g): "))
    else:
        nutrient_intake = int(input(f"enter max amount of {nutrient}: "))
    
    budget = int(input("enter your budget (€): "))
    population_size = int(input("enter initial population size: "))
    num_gen = int(input("enter the max number of generations: "))

    food_weight: FoodWeight
    match nutrient:
        case "calories":
            food_weight = FoodWeight.CALORIES
        case "fat":
            food_weight = FoodWeight.FAT
        case "protein":
            food_weight = FoodWeight.PROTEIN
        case "carbs":
            food_weight = FoodWeight.CARBS
        case "sugar":
            food_weight = FoodWeight.SUGAR
    
    return nutrient, nutrient_intake, budget, population_size, num_gen, food_weight



# main function
def main():

    # print user interface
    ui()

    # get user input
    nutrient, nutrient_intake, budget, population_size, num_gen, food_weight = user_input()
    
    
    # start algorithm
    population, generations, price = run_evolution(
        populate_function=partial(
            generate_population, size=population_size, genome_length=len(foods)
        ),
        fitness_function=partial(
            fitness, foods=foods, food_weight=food_weight, weight_limit=nutrient_intake
        ),
        fitness_limit=budget,
        generation_limit=num_gen
    )

    #print(population[0])

    total_calories = total_fat = total_carbs = total_sugars = total_protein = total_taste = 0

    rows = len(population[0])

    results_table = Table(title="Results")
    
    results_table.add_column("FOOD ITEM", style="white")
    results_table.add_column("CALORIES", style="yellow")
    results_table.add_column("FAT", style="cyan")
    results_table.add_column("CARBS", style="magenta")
    results_table.add_column("SUGAR", style="red")
    results_table.add_column("PROTEIN", style="green")
    results_table.add_column("PRICE", style="magenta", justify="right")
    results_table.add_column("TASTE", style="blue", justify="center")


    valid_genes = 0
    for i in range(rows):
        if population[0][i] == 1:
            valid_genes += 1

            results_table.add_row(str(foods[i].name), str(foods[i].calories), str(foods[i].fat), str(foods[i].carbs), str(foods[i].sugar), str(foods[i].protein), str(foods[i].price), str(foods[i].taste))

            #print(f"{foods[i].name}\t|{foods[i].calories}\t\t|{foods[i].fat}\t|{foods[i].carbs}\t|{foods[i].sugar}\t|{foods[i].protein}\t\t|{foods[i].price}\t|{foods[i].taste}")

            total_calories += foods[i].calories
            total_fat += foods[i].fat
            total_carbs += foods[i].carbs
            total_sugars += foods[i].sugar
            total_protein += foods[i].protein
            total_taste += foods[i].taste

    avg_taste = total_taste / valid_genes


    results_table.add_row()
    results_table.add_row("total", str(total_calories), str(round(total_fat, 1)), str(round(total_carbs, 1)), str(round(total_sugars, 1)), str(round(total_protein, 1)), str(round(price, 2)), str(round(avg_taste, 1)), style="white")
    
    print("\n")

    console = Console()
    console.print(results_table)


    if nutrient != "calories":
        print(f"\nThe above table is a list of food items which contain close to {nutrient_intake} grams of {nutrient} using a budget of approximately {round(price, 2)}€")
    else:
        print(f"\nThe above table is a list of food items which contain close to {nutrient_intake} {nutrient} using a budget of approximately {round(price, 2)}€")

    print(f"The optimal result was found in {generations} generations.")

    return 0


main()