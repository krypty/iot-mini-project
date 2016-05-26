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
    CLOSE_BLIND = 1
    OPEN_BLIND = 2
    SET_BLIND = 3


class KNXClient:
    DATA_SIZE = 0x2

    def __init__(self, ip, port):
        self._udp_ip = ip
        self._udp_port = port

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', 3672))

        self.data_endpoint = ('0.0.0.0', 0)  # for NAT
        self.control_enpoint = ('0.0.0.0', 0)

    def set_valve_position(self, floor, block, value):
        '''value in [0, 255]'''
        data = "%s/%s/%s" % (Action.VALVE_POSITION, floor, block)
        dest = knxnet.GroupAddress.from_str(data)

        self._send_data(dest, value, KNXClient.DATA_SIZE)

    def open_blind(self, floor, block):
        self.set_blind(floor, block, value=255)

    def close_blind(self, floor, block):
        self.set_blind(floor, block, value=0)

    def set_blind(self, floor, block, value):
        '''value in [0,255] '''
        data = "%s/%s/%s" % (Action.SET_BLIND, floor, block)
        dest = knxnet.GroupAddress.from_str(data)

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


###################################
# Set your KNXnet gateway address #
###################################

def print_usage():
    print('Usage: python3 test_client.py COMMAND [GROUP_ADDR] DATA')
    print('COMMAND LIST:')
    print('              -a GROUP_ADDR DATA    one blind/valve')
    print('              -b      no longer supported')
    print('              -v      no longer supported')
    print('DATA (INTEGER):')
    print('              0 for blind up')
    print('              1 for blind down')
    print('              [0-255] for valve position')
    print('Example: python3 test_client.py -a 1/4/1 1')

if __name__ == '__main__':
    import time  # todo delete me

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    elif sys.argv[1] == '-a':
        if len(sys.argv) != 4:
            print_usage()
            sys.exit(0)

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
        time.sleep(1.0)
        client.close_blind(floor=4, block=1)

        # dest = knxnet.GroupAddress.from_str(sys.argv[2])
        # if dest.main_group == 0:
        #     client.send_data(dest, data=int(sys.argv[3]), data_size=2)
        # elif dest.main_group == 1:
        #     client.send_data(dest, data=int(sys.argv[3]), data_size=1)
        # else:
        #     print(
        #         'Unsupported destination group address: main group has to be [0-1]')
    else:
        print_usage()
