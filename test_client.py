#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
from knxnet import *
from enum import Enum
from math import ceil, log

__author__ = ["Adrien Lescourt", "Gary Marigliano", "Philippe Bonvin"]
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.1"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class Action:
    VALVE_POSITION = 0
    TOGGLE_BLIND = 1
    SET_BLIND = 3
    READ_BLIND = 4


class KNXClient:
    DATA_SIZE = 0x2

    def __init__(self, ip, port):
        self._udp_ip = ip
        self._udp_port = port

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', 3672))

        self.data_endpoint = ('0.0.0.0', 0)  # for NAT
        self.control_enpoint = ('0.0.0.0', 0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sock.close()

    def set_valve_position(self, floor, block, value):
        '''value in [0, 255]'''
        data = "%s/%s/%s" % (Action.VALVE_POSITION, floor, block)
        try:
            dest = knxnet.GroupAddress.from_str(data)
        except utils.KnxnetUtilsException as e:
            raise e

        self._send_data(dest, value, KNXClient.DATA_SIZE)

    def open_blind(self, floor, block):
        data = "%s/%s/%s" % (Action.TOGGLE_BLIND, floor, block)
        try:
            dest = knxnet.GroupAddress.from_str(data)
        except utils.KnxnetUtilsException as e:
            raise e

        value = 1
        self._send_data(dest, value, KNXClient.DATA_SIZE)

    def close_blind(self, floor, block):
        data = "%s/%s/%s" % (Action.TOGGLE_BLIND, floor, block)
        try:
            dest = knxnet.GroupAddress.from_str(data)
        except utils.KnxnetUtilsException as e:
            raise e

        value = 0
        self._send_data(dest, value, KNXClient.DATA_SIZE)

    def set_blind(self, floor, block, value):
        '''value in [0,255] '''
        data = "%s/%s/%s" % (Action.SET_BLIND, floor, block)
        try:
            dest = knxnet.GroupAddress.from_str(data)
        except utils.KnxnetUtilsException as e:
            raise e

        self._send_data(dest, value, KNXClient.DATA_SIZE)

    def _send_data(self, dest_group_addr, data, data_size):
        self._conn_request()
        conn_resp = self._conn_response()
        channel_id = conn_resp.channel_id

        self._conn_state_request(channel_id)
        conn_state_resp = self._conn_state_response()

        self._tunnel_request(channel_id, dest_group_addr, data, data_size)
        tun_ack = self._tunnel_ack()

        self._disconnect_request(channel_id)
        self._disconnect_response()

    def _conn_request(self):
        conn_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
                                       self.control_enpoint,
                                       self.data_endpoint)

        print('==> Send connection request to %s:%s' %
              (self._udp_ip, self._udp_port))
        KNXClient._print_debug(conn_req)

        self._sock.sendto(conn_req.frame, (self._udp_ip, self._udp_port))

    def _conn_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        conn_resp = knxnet.decode_frame(data_recv)

        print('<== Received connection response:')
        KNXClient._print_debug(conn_resp)

        return conn_resp

    def _conn_state_request(self, channel_id):
        conn_state_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
                                             channel_id,
                                             self.control_enpoint)

        print(
            '==> Send connection state request to channel %s' % channel_id)
        KNXClient._print_debug(conn_state_req)

        self._sock.sendto(conn_state_req.frame, (self._udp_ip, self._udp_port))

    def _conn_state_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        conn_state_resp = knxnet.decode_frame(data_recv)

        print('<== Received connection state response:')
        KNXClient._print_debug(conn_state_resp)

        return conn_state_resp

    def _tunnel_request(self, channel_id, dest_group_addr, data, data_size):
        tunnel_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
                                         dest_group_addr,
                                         channel_id,
                                         data,
                                         data_size)

        print('==> Send tunnelling request to %s:%s' %
              (self._udp_ip, self._udp_port))
        KNXClient._print_debug(tunnel_req)

        self._sock.sendto(tunnel_req.frame, (self._udp_ip, self._udp_port))

    def _tunnel_ack(self):
        data_recv, addr = self._sock.recvfrom(1024)
        ack = knxnet.decode_frame(data_recv)

        print('<== Received tunnelling ack:')
        KNXClient._print_debug(ack)

        return ack

    def _disconnect_request(self, channel_id):
        disconnect_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST,
                                             channel_id,
                                             self.control_enpoint)

        print('==> Send disconnect request to channel %s' % channel_id)
        KNXClient._print_debug(disconnect_req)

        self._sock.sendto(disconnect_req.frame, (self._udp_ip, self._udp_port))

    def _disconnect_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        disconnect_resp = knxnet.decode_frame(data_recv)

        print('<== Received connection state response:')
        KNXClient._print_debug(disconnect_resp)

        return disconnect_resp

    @staticmethod
    def _print_debug(r):
        '''Print request or response data'''
        print(repr(r))
        print(r)

"""
Usage: python3 test_client.py COMMAND [GROUP_ADDR] DATA')
COMMAND LIST:')
              -a GROUP_ADDR DATA    one blind/valve')
              -b      no longer supported')
              -v      no longer supported')
DATA (INTEGER):')
              0 for blind up')
              1 for blind down')
              [0-255] for valve position')
Example: python3 test_client.py -a 1/4/1 1')
"""

if __name__ == '__main__':
    import time  # todo delete me

    client = KNXClient(ip="127.0.0.1", port=3671)

    # VALVE TESTS
    client.set_valve_position(floor=4, block=1, value=100)
    time.sleep(0.5)
    client.set_valve_position(floor=4, block=1, value=0)
    time.sleep(0.5)
    client.set_valve_position(floor=4, block=1, value=255)
    time.sleep(0.5)

    # BLIND TESTS
    client.open_blind(floor=4, block=1)
    time.sleep(2.0)
    client.close_blind(floor=4, block=1)

    # at the moment this cannot be tested on the simulator
    time.sleep(2.0)
    client.set_blind(floor=4, block=1, value=128)

    time.sleep(2.0)
    client.set_blind(floor=4, block=1, value=0)

    time.sleep(2.0)
    client.set_blind(floor=4, block=1, value=255)
