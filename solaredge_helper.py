import logging

from solaredge import solaredge

import authentication

solaredge_instance = solaredge.Solaredge(authentication.solar_edge_api_key)


def get_overproduction():
    """
    :return: Current overproduction in Watt
    """

    current_power_flow = solaredge_instance.get_current_power_flow(authentication.solar_edge_site_id)

    load = current_power_flow["siteCurrentPowerFlow"]["LOAD"]["currentPower"] * 1000

    pv = current_power_flow["siteCurrentPowerFlow"]["PV"]["currentPower"] * 1000

    logging.info(f"Current load: {load}W, current PV production: {pv}W")

    return pv - load
