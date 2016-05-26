#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import socket
from knxnet import *

__author__ = ["Adrien Lescourt", "Gary Marigliano", "Philippe Bonvin"]
__copyright__ = "HES-SO 2015, Project EMG4B"
__credits__ = ["Adrien Lescourt"]
__version__ = "1.0.0"
__email__ = "adrien.lescourt@gmail.com"
__status__ = "Prototype"


class KNXClient:
    def __init__(self, ip="127.0.0.1", port=3671):
        self._udp_ip = ip
        self._udp_port = port

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(('', 3672))

        self.data_endpoint = ('0.0.0.0', 0)  # for NAT
        self.control_enpoint = ('0.0.0.0', 0)

    def send_data_to_group_addr(self, dest_group_addr, data, data_size):
        # todo: handle dest_group_addr, data and data_size

        self._conn_request();
        conn_resp = self._conn_response();

        self._conn_state_request(conn_resp);
        conn_state_resp = self._conn_state_response();

        self._tunnel_request(conn_resp, dest_group_addr, data, data_size);
        tun_ack = self._tunnel_ack();

        self._disconnect_request(conn_resp);
        self._disconnect_response();

    # Connection request
    def _conn_request(self):
        conn_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_REQUEST,
            self.control_enpoint,
            self.data_endpoint)
        print('==> Send connection request to {0}:{1}'.format(self._udp_ip, self._udp_port))
        print(repr(conn_req))
        print(conn_req)
        self._sock.sendto(conn_req.frame, (self._udp_ip, self._udp_port))

    # Connection response
    def _conn_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        conn_resp = knxnet.decode_frame(data_recv)
        print('<== Received connection response:')
        print(repr(conn_resp))
        print(conn_resp)

        return conn_resp

    # Connection state request
    def _conn_state_request(self, conn_resp):
        conn_state_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.CONNECTION_STATE_REQUEST,
            conn_resp.channel_id,
            self.control_enpoint)
        print('==> Send connection state request to channel {0}'.format(conn_resp.channel_id))
        print(repr(conn_state_req))
        print(conn_state_req)
        self._sock.sendto(conn_state_req.frame, (self._udp_ip, self._udp_port))

    # Connection state response
    def _conn_state_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        conn_state_resp = knxnet.decode_frame(data_recv)
        print('<== Received connection state response:')
        print(repr(conn_state_resp))
        print(conn_state_resp)

        return conn_state_resp

    # Tunnel request
    def _tunnel_request(self, conn_resp, dest_group_addr, data, data_size):
        tunnel_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.TUNNELLING_REQUEST,
            dest_group_addr,
            conn_resp.channel_id,
            data,
            data_size)
        print('==> Send tunnelling request to {0}:{1}'.format(self._udp_ip, self._udp_port))
        print(repr(tunnel_req))
        print(tunnel_req)
        self._sock.sendto(tunnel_req.frame, (self._udp_ip, self._udp_port))

    # Tunnel ack
    def _tunnel_ack(self):
        data_recv, addr = self._sock.recvfrom(1024)
        ack = knxnet.decode_frame(data_recv)
        print('<== Received tunnelling ack:')
        print(repr(ack))
        print(ack)

        return ack

    # Disconnect request
    def _disconnect_request(self, conn_resp):
        disconnect_req = knxnet.create_frame(knxnet.ServiceTypeDescriptor.DISCONNECT_REQUEST,
            conn_resp.channel_id,
            self.control_enpoint)
        print('==> Send disconnect request to channel {0}'.format(conn_resp.channel_id))
        print(repr(disconnect_req))
        print(disconnect_req)
        self._sock.sendto(disconnect_req.frame, (self._udp_ip, self._udp_port))

    # Disconnect response
    def _disconnect_response(self):
        data_recv, addr = self._sock.recvfrom(1024)
        disconnect_resp = knxnet.decode_frame(data_recv)
        print('<== Received connection state response:')
        print(repr(disconnect_resp))
        print(disconnect_resp)

        return disconnect_resp


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

        client = KNXClient()

        dest = knxnet.GroupAddress.from_str(sys.argv[2])
        if dest.main_group == 0:
            client.send_data_to_group_addr(dest, int(sys.argv[3]), 2)
        elif dest.main_group == 1:
            client.send_data_to_group_addr(dest, int(sys.argv[3]), 1)
        else:
            print('Unsupported destination group address: main group has to be [0-1]')
    else:
        print_usage()
