import utils
from tplink_helper import Plug


def check_plug_ids(plugs, ids):

    assert len(plugs) == len(ids)

    for id in ids:
        if not any(plug.id == id for plug in plugs):
            return False

    return True


def test_find_load_maximizing_plugs():
    plugs = [
        Plug(id=1, optional_load=3),
        Plug(id=2, optional_load=5),
        Plug(id=3, optional_load=6),
    ]

    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 10), [1, 3])
    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 1), [])
    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 100), [1, 2, 3])
    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 5), [2])
    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 7), [3])
    assert check_plug_ids(utils.find_load_maximizing_plugs(plugs, 8), [1, 2])


