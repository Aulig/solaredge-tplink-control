import base64
import logging

import requests
import uuid

import authentication

# alternative: https://eu-wap.tplinkcloud.com
tp_link_base_url = "https://wap.tplinkcloud.com"

# get with
# requests_session.get("https://app-server.iot.i.tplinknbu.com/v1/server-info", headers={
#         'app-cid': 'app:x:x'
#     }).json()["appServerUrl"]
tapo_app_server_url = "https://euw1-app-server.iot.i.tplinknbu.com"

# we use our own implementation because most packages that can control p100 plugs can only do so on the local
# network, but we want to run this code on a server that is not on the same network as the plugs

requests_session = requests.Session()
terminal_uuid = str(uuid.uuid4())


def _login():
    logging.info("Logging in...")

    login_response = requests_session.post(tp_link_base_url, json={
        "method": "login",
        "params": {
            "appType": "Tapo_Android",
            "cloudUserName": authentication.tplink_email,
            "cloudPassword": authentication.tplink_password,
            "refreshTokenNeeded": True,
            "terminalUUID": terminal_uuid
        }
    })

    global refresh_token
    global cloud_token

    refresh_token = login_response.json()["result"]["refreshToken"]
    cloud_token = login_response.json()["result"]["token"]


cloud_token = None
refresh_token = None

# sets cloud & refresh token
_login()


class TokenExpiredException(Exception):
    pass


def _refresh_token():
    logging.info("Refreshing token...")

    refresh_response = requests_session.post(tp_link_base_url, json={
        "method": "refreshToken",
        "params": {
            "appType": "Tapo_Android",
            "refreshToken": refresh_token,
            "terminalUUID": terminal_uuid
        }
    })

    global cloud_token
    cloud_token = refresh_response.json()["result"]["token"]


def _check_for_token_expiry(request_response):
    response_json = request_response.json()

    if response_json.get("error_code", 0) == -20651 and response_json.get("msg") == "Token expired":
        logging.info("Token expired - raising exception")
        raise TokenExpiredException()


def refresh_token_if_expired(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except TokenExpiredException:
            _refresh_token()
            result = func(*args, **kwargs)

        return result

    return wrapper


@refresh_token_if_expired
def _find_plug_ids():
    device_list_response = requests_session.post(f"{tp_link_base_url}?token={cloud_token}&termID={terminal_uuid}",
                                                 json={
                                                     "method": "getDeviceList"
                                                 })

    _check_for_token_expiry(device_list_response)

    device_list = device_list_response.json()["result"]["deviceList"]

    logging.info(f"Found devices: {device_list}")

    plug_ids = []

    for device in device_list:
        if device["deviceType"] == "SMART.TAPOPLUG" and base64.b64decode(device["alias"]).decode(
                "utf-8").startswith("PV-"):
            plug_ids.append(device["deviceId"])

    return plug_ids


@refresh_token_if_expired
def _tapo_plug_state(plug_id):
    current_state_response = requests_session.get(
        f"{tapo_app_server_url}/v1/things/shadows?thingNames={plug_id}",
        headers={
            'app-cid': 'app:x:x',
            "Authorization": f"ut|{cloud_token}",
        }, verify=False)

    _check_for_token_expiry(current_state_response)

    logging.info(current_state_response.text)

    return current_state_response.json()["shadows"][0]


def get_plug_states():
    plug_ids = _find_plug_ids()

    states = []

    for plug_id in plug_ids:
        current_state = _tapo_plug_state(plug_id)

        states.append(current_state["state"]["desired"]["on"] == "true")

    return states


@refresh_token_if_expired
def set_plug_states(new_on_state):
    plug_ids = _find_plug_ids()

    for plug_id in plug_ids:
        # tried using these endpoints but they always report that the device is offline
        # base_url = device['appServerUrl']

        # get_system_info_response = requests_session.post(f"{base_url}?token={cloud_token}&termID={terminal_uuid}", json={
        #     "method": "passthrough",
        #     "params": {
        #         # encode device id somehow?
        #         "deviceId": device["deviceId"],
        #         "requestData": json.dumps(
        #             {
        #                 "system": {
        #                     "get_sysinfo": {}
        #                 }
        #             }
        #         )
        #     }
        # }, headers=headers)
        #
        # logging.info(get_system_info_response.text)
        #
        # set_relay_state_response = requests_session.post(f"{base_url}?token={cloud_token}&termID={terminal_uuid}", json={
        #     "method": "passthrough",
        #     "params": {
        #         # encode device id somehow?
        #         # use fw or hwid?
        #         "deviceId": device["deviceId"],
        #         "requestData": json.dumps({
        #             "system": {
        #                 "set_relay_state": {
        #                     "state": 1
        #                 }
        #             }
        #         })
        #     }
        # }, headers=headers)
        #
        # logging.info(set_relay_state_response.text)

        # -----------------

        # Instead, this part is inspired by the code attached to
        # https://github.com/adumont/tplink-cloud-api/issues/42#issuecomment-758167089

        # most of these requests need to use verify=False because tplink uses self-signed certs

        current_state = _tapo_plug_state(plug_id)

        is_on = current_state["state"]["desired"]["on"]

        if is_on != new_on_state:
            logging.info(f"Setting plug state to {new_on_state}")
            current_version = current_state["version"]

            set_state_response = requests_session.patch(f"{tapo_app_server_url}/v1/things/{plug_id}/shadows",
                                                        headers={
                                                            'app-cid': 'app:x:x',
                                                            "Authorization": f"ut|{cloud_token}",
                                                        },
                                                        json={
                                                            "state": {
                                                                "desired": {
                                                                    "on": new_on_state
                                                                }
                                                            },
                                                            "version": current_version + 1
                                                        }, verify=False)

            _check_for_token_expiry(set_state_response)

            logging.info(set_state_response.text)
