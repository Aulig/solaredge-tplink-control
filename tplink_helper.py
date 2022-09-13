import base64
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

def _login(requests_session, terminal_uuid):
    login_response = requests_session.post(tp_link_base_url, json={
        "method": "login",
        "params": {
            "appType": "Tapo_Android",
            "cloudUserName": authentication.tplink_email,
            "cloudPassword": authentication.tplink_password,
            # "refreshTokenNeeded": True,
            "terminalUUID": terminal_uuid
        }
    })
    # not sure what it's needed for
    # refresh_token = login_response.json()["result"]["refreshToken"]

    return login_response.json()["result"]["token"]


def _find_plug_ids(requests_session, cloud_token, terminal_uuid):
    device_list_response = requests_session.post(f"{tp_link_base_url}?token={cloud_token}&termID={terminal_uuid}",
                                                 json={
                                                     "method": "getDeviceList"
                                                 })

    device_list = device_list_response.json()["result"]["deviceList"]

    print(f"Found devices: {device_list}")

    plug_ids = []

    for device in device_list:
        if device["deviceType"] == "SMART.TAPOPLUG" and base64.b64decode(device["alias"]).decode(
                "utf-8").startswith("PV-"):
            plug_ids.append(device["deviceId"])

    return plug_ids


def _tapo_plug_state(requests_session, cloud_token, plug_id):
    current_state_response = requests_session.get(
        f"{tapo_app_server_url}/v1/things/shadows?thingNames={plug_id}",
        headers={
            'app-cid': 'app:x:x',
            "Authorization": f"ut|{cloud_token}",
        }, verify=False)

    print(current_state_response.text)

    return current_state_response.json()["shadows"][0]


def get_plug_states():
    requests_session = requests.Session()

    terminal_uuid = str(uuid.uuid4())

    cloud_token = _login(requests_session, terminal_uuid)

    plug_ids = _find_plug_ids(requests_session, cloud_token, terminal_uuid)

    states = []

    for plug_id in plug_ids:
        current_state = _tapo_plug_state(requests_session, cloud_token, plug_id)

        states.append(current_state["state"]["desired"]["on"] == "true")

    return states


def set_plug_states(new_on_state):
    requests_session = requests.Session()

    terminal_uuid = str(uuid.uuid4())

    cloud_token = _login(requests_session, terminal_uuid)

    plug_ids = _find_plug_ids(requests_session, cloud_token, terminal_uuid)

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
        # print(get_system_info_response.text)
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
        # print(set_relay_state_response.text)

        # -----------------

        # Instead, this part is inspired by the code attached to
        # https://github.com/adumont/tplink-cloud-api/issues/42#issuecomment-758167089

        # most of these requests need to use verify=False because tplink uses self-signed certs

        current_state = _tapo_plug_state(requests_session, cloud_token, plug_id)

        is_on = current_state["state"]["desired"]["on"]

        if is_on != new_on_state:
            print(f"Setting plug state to {new_on_state}")
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

            print(set_state_response.text)
