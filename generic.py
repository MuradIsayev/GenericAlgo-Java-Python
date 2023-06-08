import random
import socket

# Genetic Algorithm Parameters
POPULATION_SIZE = 100
GENERATIONS = 100
MUTATION_RATE = 0.1

# Problem Parameters
NUM_STUDENTS = 4
NUM_COUNTRIES = 4
COUNTRY_NAMES = ["A", "B", "C", "D"]
NUM_CHOICES = 4

# Generate initial population
def generate_population():
    population = []
    for _ in range(POPULATION_SIZE):
        allocation = [random.randint(0, NUM_COUNTRIES - 1) for _ in range(NUM_STUDENTS)]
        population.append(allocation)
    return population

# Calculate fitness of an allocation
def calculate_fitness(allocation, student_choices):
    fitness = 0
    for student_id, country_id in enumerate(allocation):
        choices = student_choices[student_id]
        if country_id in choices:
            index = choices.index(country_id)
            fitness += (index - 1) ** 2
        elif not choices:  # Empty choice list
            fitness += 1000  # Assign a high penalty
        else:
            fitness += 10 * len(choices) ** 2
    return fitness

# Perform crossover between two parents
def crossover(parent1, parent2):
    cutoff = random.randint(1, NUM_STUDENTS - 1)
    child1 = parent1[:cutoff] + parent2[cutoff:]
    child2 = parent2[:cutoff] + parent1[cutoff:]
    return child1, child2

# Perform mutation on an allocation
def mutate(allocation):
    for i in range(NUM_STUDENTS):
        if random.random() < MUTATION_RATE:
            allocation[i] = random.randint(0, NUM_COUNTRIES - 1)
    return allocation

# Select parents for reproduction using tournament selection
def select_parents(population):
    parent1 = random.choice(population)
    parent2 = random.choice(population)
    return parent1, parent2

# Create the next generation
def create_next_generation(population, student_choices):
    next_generation = []
    fitness_scores = []

    for _ in range(POPULATION_SIZE):
        parent1, parent2 = select_parents(population)
        child1, child2 = crossover(parent1, parent2)
        child1 = mutate(child1)
        child2 = mutate(child2)

        next_generation.append(child1)
        next_generation.append(child2)

        fitness_scores.append(calculate_fitness(child1, student_choices))
        fitness_scores.append(calculate_fitness(child2, student_choices))

    # Select the best two individuals from the previous population
    best_index1 = fitness_scores.index(min(fitness_scores))
    fitness_scores[best_index1] = float('inf')
    best_index2 = fitness_scores.index(min(fitness_scores))

    # Replace the worst two individuals in the next generation with the best individuals from the previous population
    next_generation[-2] = population[best_index1].copy()
    next_generation[-1] = population[best_index2].copy()

    return next_generation, fitness_scores[best_index1]


# Find the best allocation in the population
def find_best_allocation(population, student_choices):
    best_allocation = population[0]
    best_fitness = calculate_fitness(best_allocation, student_choices)
    country_allocations = [[] for _ in range(NUM_COUNTRIES)]
    for student_id, country_id in enumerate(best_allocation):
        country_allocations[country_id].append(student_id)

    return country_allocations, best_fitness

def send_best_allocation_data(country_allocations, best_fitness, client_sockets, usernames):
    best_allocations_str = ""
    for country_id, student_ids in enumerate(country_allocations):
        country_name = COUNTRY_NAMES[country_id]
        allocation_str = country_name + ": " + ", ".join([usernames[student_id] for student_id in student_ids])
        best_allocations_str += allocation_str + "\n"

    for client_socket in client_sockets:
        client_socket.sendall(best_allocations_str.encode())

# Main Genetic Algorithm function
def genetic_algorithm():
    # Create a socket for server-client communication
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(NUM_STUDENTS)
    print('Waiting for clients to connect...')

    # Accept client connections and receive choices
    client_sockets = []
    student_choices = []
    usernames = []
        # Continue accepting client connections and receiving choices
    while len(client_sockets) < NUM_STUDENTS:
        client_socket, client_address = server_socket.accept()
        print('Client connected:', client_address)
        client_sockets.append(client_socket)
        username = client_socket.recv(1024).decode()
        usernames.append(username)
        choices_str = client_socket.recv(1024).decode().strip()
        choices = choices_str.split(",")  # Split the choices string into a list
        student_choices.append(choices)
        print('Student Choices for', username + ':', choices)

    print('Student Choices:', student_choices)

    # Generate initial population
    population = generate_population()

    for generation in range(GENERATIONS):
        country_allocations, best_fitness = find_best_allocation(population, student_choices)
        population, best_fitness = create_next_generation(population, student_choices)
        print("Generation:", generation + 1)
        for username, choices in zip(usernames, student_choices):
            print("Username:", username)
            print("Choices of", username + ":", choices)

        print("Best Allocation:")
        for country_id, student_ids in enumerate(country_allocations):
            country_name = COUNTRY_NAMES[country_id]
            print(country_name, ":", [usernames[student_id] for student_id in student_ids])
        print("-------------------------")
        if generation == GENERATIONS - 1:
            # Find the best allocation after the last generation
            country_allocations, best_fitness = find_best_allocation(population, student_choices)
            # Send the best allocation data to all clients
            send_best_allocation_data(country_allocations, best_fitness, client_sockets, usernames)
    # Close the client sockets and server socket
    for client_socket in client_sockets:
        client_socket.close()
    server_socket.close()

genetic_algorithm()
