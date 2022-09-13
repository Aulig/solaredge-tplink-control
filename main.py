import time

import settings
import solaredge_helper
import tplink_helper


plug_enabled = False

tplink_helper.set_plug_states(plug_enabled)

print("Disabled all plugs at startup - waiting a minute to let solaredge update load.")

time.sleep(60)

while True:
    overproduction = solaredge_helper.get_overproduction()

    threshold = settings.min_overproduction

    if plug_enabled:
        threshold -= settings.optional_load

    if overproduction > threshold:
        plug_enabled = True
        print(f"Enough overproduction: {overproduction} Watt")
    else:
        plug_enabled = False
        print(f"NOT enough overproduction: {overproduction} Watt")

    tplink_helper.set_plug_states(plug_enabled)

    time.sleep(settings.check_every_minutes * 60)