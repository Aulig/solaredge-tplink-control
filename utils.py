import itertools


def find_load_maximizing_plugs(plugs, overproduction_without_optional_load):
    """
    enable the combination of plugs that maximizes the sum of the enabled plugs' optional loads while being smaller
    than the overproduction
    :param plugs:
    :param overproduction_without_optional_load:
    :return: list of plugs that should be enabled
    """
    max_load = 0
    load_maximizing_plugs = []

    # using a brute force algorithm, could improve by using dynamic programming, see knapsack problem
    for i in range(1, len(plugs) + 1):
        for combination in itertools.combinations(plugs, i):

            load = sum([plug.optional_load for plug in combination])

            if load <= overproduction_without_optional_load and load > max_load:
                max_load = load
                load_maximizing_plugs = combination

    return load_maximizing_plugs
