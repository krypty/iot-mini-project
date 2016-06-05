#!flask/bin/python
from flask import Flask, jsonify, request

from test_client import KNXClient, Action

PARAMETER_SEPARATOR = "_"

app = Flask(__name__)


class Message:

    @staticmethod
    def _build(is_error, msg):
        response = {"error": is_error, "msg": msg}
        return jsonify(response)

    @staticmethod
    def error(msg):
        return Message._build(is_error=True, msg=msg)

    @staticmethod
    def info(msg):
        return Message._build(is_error=False, msg=msg)


# @app.route('/block/<string:group_addr>', methods=['GET'])
# def get_task(group_addr):
#     print("group_addr %s" % group_addr)
#     return jsonify({'task': group_addr})


@app.route('/block/<string:group_addr>', methods=['POST'])
def post_block(group_addr):
    response = None

    print("group_addr : %s" % group_addr)

    try:
        action, floor, block = parse_group_addr(group_addr)
        print("action : %s, floor: %s, block: %s" % (action, floor, block))

        posted_json = request.json
        response = handle_action(action, floor, block, posted_json)
    except ValueError:
        return Message.error("Invalid group_addr. Received : %s" % group_addr)

    return response


def parse_group_addr(group_addr):
    error = ValueError("Invalid group address for %s" % group_addr)

    try:
        params = group_addr.split(PARAMETER_SEPARATOR)
        if len(params) != 3:
            raise error
        return [int(p) for p in params]
    except:
        raise error


def handle_action(action, floor, block, posted_json):
    response = None

    with KNXClient(ip="127.0.0.1", port=3671) as client:
        if action == Action.VALVE_POSITION:
            return handle_valve_position(client, floor, block, posted_json)
        elif action == Action.TOGGLE_BLIND:
            return handle_toggle_blind(client, floor, block, posted_json)
        elif action == Action.SET_BLIND:
            return handle_set_blind(client, floor, block, posted_json)
        else:
            raise ValueError("Invalid action for %s" % action)

    # return response
    return Message.info("OK")


def handle_valve_position(client, floor, block, posted_json):
    def is_value_valid(value):
        return 0 <= value and value <= 255

    try:
        value = posted_json.get("value")
        if value is not None and is_value_valid(value):
            client.set_valve_position(floor, block, value=value)
            return Message.info("OK")
        else:
            return Message.error("value provided is not valid")
    except IndexError:
        return Message.error("you must provide a POST parameter called value")


def handle_toggle_blind(client, floor, block, posted_json):
    def is_value_valid(value):
        return 0 <= value and value <= 1

    try:
        value = posted_json.get("value")
        if value is None or not is_value_valid(value):
            return Message.error("value provided is not valid")

        if value == 0:
            handle_open_blind(client, floor, block)
        else:
            handle_close_blind(client, floor, block)

        return Message.info("OK")

    except IndexError:
        return Message.error("you must provide a POST parameter called value")


def handle_close_blind(client, floor, block):
    client.close_blind(floor, block)


def handle_open_blind(client, floor, block):
    client.open_blind(floor, block)


def handle_set_blind(client, floor, block, posted_json):
    def is_value_valid(value):
        return 0 <= value and value <= 255

    try:
        value = posted_json.get("value")
        if value is None or not is_value_valid(value):
            return Message.error("value provided is not valid")

        client.set_blind(floor, block, value)
        return Message.info("OK")
    except IndexError:
        return Message.error("you must provide a POST parameter called value")


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
