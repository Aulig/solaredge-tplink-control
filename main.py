import logging
import sys
import time

import settings
import solaredge_helper
import tplink_helper
# set up logging
import utils

logging.root.handlers = []
logging.basicConfig(level=logging.DEBUG, handlers=[
    # log both to file & stdout
    logging.FileHandler("activity.log"),
    logging.StreamHandler(sys.stdout)
])

while True:
    overproduction = solaredge_helper.get_overproduction()

    overproduction_without_optional_load = overproduction

    plugs = tplink_helper.get_plugs_with_state()

    for plug in plugs:
        if plug.enabled:
            overproduction_without_optional_load += plug.optional_load

    # enable the combination of plugs that maximizes the sum of the enabled plugs' optional loads while being smaller
    # than the overproduction
    # using a brute force algorithm, could improve by using dynamic programming, see knapsack problem

    load_maximizing_plugs = utils.find_load_maximizing_plugs(plugs, overproduction_without_optional_load)

    for plug in plugs:
        should_be_enabled = plug in load_maximizing_plugs
        tplink_helper.set_plug_state(plug, should_be_enabled)

    time.sleep(settings.check_every_minutes * 60)
