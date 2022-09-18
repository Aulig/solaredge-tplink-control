import itertools


def find_load_maximizing_plugs(plugs, overproduction_without_optional_load):
    max_load = 0
    load_maximizing_plugs = []

    for i in range(1, len(plugs) + 1):
        for combination in itertools.combinations(plugs, i):

            load = sum([plug.optional_load for plug in combination])

            if load <= overproduction_without_optional_load and load > max_load:
                max_load = load
                load_maximizing_plugs = combination

    return load_maximizing_plugs