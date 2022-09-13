from solaredge import solaredge

import authentication


def get_overproduction():
    """
    :return: Current overproduction in Watt
    """

    s = solaredge.Solaredge(authentication.solar_edge_api_key)

    current_power_flow = s.get_current_power_flow(authentication.solar_edge_site_id)

    load = current_power_flow["siteCurrentPowerFlow"]["LOAD"]["currentPower"] * 1000

    pv = current_power_flow["siteCurrentPowerFlow"]["PV"]["currentPower"] * 1000

    return pv - load
