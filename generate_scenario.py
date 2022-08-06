import json
import numpy as np
import time

"Get base scenario file"
# Number of cars
number_of_cars = 2

# Is SIRO model used? - obstacle avoidance
siro=False

# Get base scenario
file1 = "./output_files_vadere/final_project/scenarios/one_car.scenario"
file2 = "./output_files_vadere/final_project/scenarios/two_cars_task_2.scenario"
file3 = "./output_files_vadere/final_project/scenarios/one_car_task_3.scenario"
file = None

if siro:
    file = file3
    # we implement for one car
    number_of_cars = 1
else: 
    file = file1 if number_of_cars == 1 else file2

f = open(file, "r")
data = json.loads(f.read())
f.close()

"Modify how many pedestrians come out of each source"
# Total number of passengers we want to have
totalNumber = 50

# Number of gates per car
gatesPerCar = 3

# Number of gates
gates = gatesPerCar * number_of_cars

# List of how many passengers each source will spawn; at first, it's empty
spawnNumber = [0] * gates

# First and last gates are busier than the middle one(s)
busierGates = [0, gates - 1]

# Sum to check there are not more passengers than desired
checkPassSum = 0
aux = 0

# Maximum values can be taken only by the first and last gate
lastBusyGate = -1

for gate in range(gates):

    # Factor which determines the business of a gate
    meanFactor = (2 + gates) / (4 * gates) if gate in busierGates else 1 / (2 * gates)

    # Mean of the normal distribution
    mu = totalNumber * meanFactor

    # Standard deviation of the normal distribution which samples number of passengers
    sigma = 1

    # Number of passengers coming through the gate
    x = round(np.random.normal(mu, sigma, 1)[0])

    # Remember the first gate, which should be busier than middle gates
    # Regenerate number of passengers if there are more people
    # coming through the middle gates than outer gates
    if gate == 0:
        lastBusyGate = x
    else:
        while x < 0 or (lastBusyGate <= x and gate not in busierGates):
            x = round(np.random.normal(mu, sigma, 1)[0])

    # Simulate what would happen if we added the current x for this gate
    aux = checkPassSum
    aux += x

    # Check if we already have the necessary number of passengers
    # If we do, break the loop
    if aux == totalNumber:
        spawnNumber[gate] = x
        break
    elif gate != 0:
        # If not, and we are not at the first gate
        # check how many passengers do we need to get the sum
        difference = np.abs(totalNumber - aux)
        # 1 if the sum is less than total number of expected passengers
        # -1 if we have more passengers than needed
        coeff = 1 if aux < totalNumber else -1
        # If we are at the last gate and need more people or if we have too many people
        if (coeff == 1 and gate == gates - 1) or (coeff == -1):
            x = x + coeff * difference
    # Add the correct x to the real passenger sum
    checkPassSum += x
    # Add the number of passengers to their gate
    spawnNumber[gate] = x
# print(spawnNumber)

# Ask the user to manually introduce the number of pedestrians
for gate in range(gates):
    print('Gate ',gate)
    x=input('Give number:')
    spawnNumber[gate]=x
print(spawnNumber)

"Modify here the variables which need to be changed"
variables = {
    "waitingTime": 2.0,
    "spawnNumber": spawnNumber,
    "minimumSpeed": 0.01,
    "maximumSpeed": 1.3
}
variablesSIRO = {
    "intoxicatedAtStart": 7,
    "relievedAtStart": 0,
    "reliefRate": 0.003,
    "obstacleRadius": 3.0
}
print(variables)

"Modify how many pedestrians come out of each source"
# Number of sources per car
sources_per_car = 3
# Total number of sources in current scenario
sources = sources_per_car * number_of_cars
for i in range(sources):
    data["scenario"]["topography"]["sources"][i]["spawnNumber"] = variables["spawnNumber"][i]
    print("source:", i, "pssngrs:", data["scenario"]["topography"]["sources"][i]["spawnNumber"])

"Modify targets waiting times (simulate rise of temperature)"
# Number of targets in one car
targets_per_car = 54
# For each target in first car, modify waiting time
for i in range(targets_per_car):
    data["scenario"]["topography"]["targets"][i]["waitingTime"] = variables["waitingTime"]

"Modify speed of pedestrians"
data["scenario"]["topography"]["attributesPedestrian"]["minimumSpeed"] = variables["minimumSpeed"]
data["scenario"]["topography"]["attributesPedestrian"]["maximumSpeed"] = variables["maximumSpeed"]

"Modify SIRO attributes"
# Modify attributes of the SIRO model using the designated dictionary
if siro:
    for key in variablesSIRO.keys():
        data["scenario"]["attributesModel"]["org.vadere.state.attributes.models.AttributesSIROG"][key]=variablesSIRO[key]

"Generate new scenario"
# The name is of the following structure:
# - number of cars
# - time of creation
one_car_path = "one_car_"
two_car_path = "two_cars_"
car_path = one_car_path if number_of_cars == 1 else two_car_path
file_unique = time.strftime("%Y_%m_%d-%H_%M")
name = car_path + file_unique

# Add this to the JSON object so that there won't be any errors
# saying that two scenarios have the same name
data["name"] = name

# Create the path of the newly generated file
file_base_path = "./output_files_vadere/final_project/scenarios/"
file_extension = ".scenario"
new_file = file_base_path + name + file_extension
print(new_file)

# Format the data file
print(dict(data))
qux = json.dumps(dict(data), sort_keys=True, indent=2)
print(qux)

# Create the new file with the updated data
new_f = open(new_file, "w")
new_f.write(qux)
new_f.close()
