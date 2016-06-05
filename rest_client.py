#!/bin/python3
# coding : utf-8

import json
import urllib.request
import argparse
import sys
from test_client import Action


SUPPORTED_ACTIONS = [Action.VALVE_POSITION,
                     Action.TOGGLE_BLIND,
                     Action.SET_BLIND]


def check_negative(value):
    exception = argparse.ArgumentTypeError(
        "%s is an invalid positive int value" % value)
    try:
        ivalue = int(value)
        if ivalue < 0:
            raise exception
        return ivalue
    except ValueError:
        raise exception


def is_value_valid(value, valid_range):
    if args.value is None or args.value not in valid_range:
        raise argparse.ArgumentTypeError(
            "you must provide a value [%s-%s] argument" % (min(valid_range), max(valid_range)))
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='REST client for IoT mini project')
    parser.add_argument('action', action="store", type=int,
                        choices=SUPPORTED_ACTIONS, help="action")
    parser.add_argument('floor', action="store", type=check_negative)
    parser.add_argument('block', action="store", type=check_negative)
    parser.add_argument('--value', action="store",
                        type=check_negative, required=False)

    args = parser.parse_args()
    print("args : %s" % args)
    action = args.action
    floor = args.floor
    block = args.block
    value = None

    if action == Action.VALVE_POSITION:
        if is_value_valid(args.value, range(0, 255 + 1)):
            value = args.value

    elif action == Action.TOGGLE_BLIND:
        if is_value_valid(args.value, range(0, 1 + 1)):
            value = args.value

    elif action == Action.SET_BLIND:
        if is_value_valid(args.value, range(0, 255 + 1)):
            value = args.value

    else:
        raise ValueError("Insupported action")
        sys.exit(-1)

    # POST REQUEST
    REST_SERVER_URL = "http://127.0.0.1:5000/block/%s_%s_%s" % (
        action, floor, block)
    print("REST_SERVER_URL : %s" % REST_SERVER_URL)

    params = {"value": value}
    json_params = json.dumps(params).encode('utf8')
    req = urllib.request.Request(REST_SERVER_URL, data=json_params,
                                 headers={'content-type': 'application/json'})

    # Handle response
    response = urllib.request.urlopen(req)
    printable_resp = response.read().decode('utf8')
    print("response: %s" % printable_resp)
