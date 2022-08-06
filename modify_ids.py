import json

"Variables"
# How many targets per car
target_count_car = 54
# How many cars; modify here
how_many_cars = 2
# How many sources per car
sources_per_car = 3
# How many targets are set to one source in one car
targets_per_source = target_count_car / sources_per_car
# Data from scenario
data = None

"Get the data from the base scenario file"
# Base scenario files
# One car
file1 = "./output_files_vadere/final_project/scenarios/one_car.scenario"
# Two cars
file2 = "./output_files_vadere/final_project/scenarios/two_cars.scenario"
#
file = file1 if how_many_cars == 1 else file2
f = open(file, "r")
data = json.loads(f.reads())
f.close()

"""
Modify IDs of targets such that the IDs' ranges are:
- for the first car: 100->153
- for the second car: 200->253
"""
# Variable to keep track of the target ID in current car
counter_car = 0
# Starting ID for first car
car_id = 100
for i in range(target_count_car * how_many_cars):
    if i == target_count_car and how_many_cars == 2:
        counter_car = 0
        car_id = 200
    data["scenario"]["topography"]["targets"][i]["id"] = car_id + counter_car
    counter_car += 1


def generate_target_list(source_id):
    """
    Modify IDs of sources and their target list such that the IDs' ranges are:
    - for source with ID=0: 100->117
    - for source with ID=1: 118->135
    - for source with ID=2: 136->154
    - for source with ID=3: 200->217
    - for source with ID=4: 218->235
    - for source with ID=5: 236->254
    :param source_id: The ID of the current source
    :type source_id: int
    :return: list with targets corresponding to current source
    :rtype: list
    """
    targets = []
    if source_id >= sources_per_car:
        car_id = 200
    else:
        car_id = 100

    # Compute min and max for target ID for current source
    range_min = int(car_id + targets_per_source * (source_id % 3))

    if (source_id + 1) % 3 == 0:  # last source in car
        range_max = int(car_id + target_count_car)
    else:
        range_max = int(car_id + targets_per_source * ((source_id + 1) % 3))

    # Append all the targets within computed range
    for i in range(range_min, range_max):
        targets.append(i)

    print("source_id",source_id)
    print('targets: ',targets)
    return targets


"Update lists for each source"
for i in range(sources_per_car * how_many_cars):
    data["scenario"]["topography"]["sources"][i]["id"] = i
    data["scenario"]["topography"]["sources"][i]["targetIds"] = generate_target_list(i)

"Update IDs in given file"
f = open(file, "w")
f.write(json.dumps(data, sort_keys=True, indent=2))
f.close()
