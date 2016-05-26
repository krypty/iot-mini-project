#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
from knxnet import *

__author__ = ["Adrien Lescourt", "Gary Marigliano", "Philippe Bonvin"]
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.1"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class KNXClient:

    def __init__(self, ip, port):
        self._udp_ip = ip
        self._udp_port = port

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', 3672))

        self.data_endpoint = ('0.0.0.0', 0)  # for NAT
        self.control_enpoint = ('0.0.0.0', 0)

    def send_data(self, dest_group_addr, data, data_size):
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

        print('==> Send connection request to {0}:{1}'.format(
            self._udp_ip, self._udp_port))
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
            '==> Send connection state request to channel {0}'.format(channel_id))
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

        print('==> Send tunnelling request to {0}:{1}'.format(
            self._udp_ip, self._udp_port))
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

        print('==> Send disconnect request to channel {0}'.format(channel_id))
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
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    elif sys.argv[1] == '-a':
        if len(sys.argv) != 4:
            print_usage()
            sys.exit(0)

        client = KNXClient(ip="127.0.0.1", port=3671)

        dest = knxnet.GroupAddress.from_str(sys.argv[2])
        if dest.main_group == 0:
            client.send_data(dest, int(sys.argv[3]), 2)
        elif dest.main_group == 1:
            client.send_data(dest, int(sys.argv[3]), 1)
        else:
            print(
                'Unsupported destination group address: main group has to be [0-1]')
    else:
        print_usage()
