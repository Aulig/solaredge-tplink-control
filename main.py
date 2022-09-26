import logging
import sys
import time
from datetime import datetime

import pytz

import settings
import solaredge_helper
import tplink_helper
# set up logging
import utils

logging.root.handlers = []
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        # log both to file & stdout
                        logging.FileHandler("activity.log"),
                        logging.StreamHandler(sys.stdout)
                    ])

while True:
    try:
        current_time_at_location = datetime.now(pytz.timezone(settings.timezone))

        if current_time_at_location.hour >= 22 or current_time_at_location.hour < 5:
            logging.info("It is dark outside, not checking the photovoltaic system status")
        else:
            overproduction = solaredge_helper.get_overproduction()

            overproduction_without_optional_load = overproduction

            plugs = tplink_helper.get_plugs_with_state()

            for plug in plugs:
                if plug.enabled:
                    overproduction_without_optional_load += plug.optional_load

            logging.info(f"Overproduction without optional load: {overproduction_without_optional_load}")

            load_maximizing_plugs = utils.find_load_maximizing_plugs(plugs, overproduction_without_optional_load)

            logging.info(f"Load maximizing plugs: {[plug.id for plug in load_maximizing_plugs]}")

            for plug in plugs:
                should_be_enabled = plug in load_maximizing_plugs
                tplink_helper.set_plug_state(plug, should_be_enabled)

    except Exception as e:
        logging.error(e)

    time.sleep(settings.check_every_minutes * 60)
