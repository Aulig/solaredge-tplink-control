import sys
import time

import settings
import solaredge_helper
import tplink_helper

import logging

logging.basicConfig(level=logging.DEBUG, handlers=[
    # log both to file & stdout
    logging.FileHandler("activity.log"),
    logging.StreamHandler(sys.stdout)
])

plug_enabled = False

tplink_helper.set_plug_states(plug_enabled)

logging.info("Disabled all plugs at startup - waiting a minute to let solaredge update load.")

time.sleep(60)

while True:
    overproduction = solaredge_helper.get_overproduction()

    threshold = settings.min_overproduction

    if plug_enabled:
        threshold -= settings.optional_load

    plug_enabled_before = plug_enabled

    if overproduction > threshold:
        plug_enabled = True
        logging.info(f"Enough overproduction: {overproduction} Watt")
    else:
        plug_enabled = False
        logging.info(f"NOT enough overproduction: {overproduction} Watt")

    if plug_enabled != plug_enabled_before:
        # minimize requests sent to tplink by only sending a request if the state actually changed
        tplink_helper.set_plug_states(plug_enabled)

    time.sleep(settings.check_every_minutes * 60)
