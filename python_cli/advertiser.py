#!/usr/bin/env python3

# Written by Sultan Qasim Khan
# Copyright (c) 2020, NCC Group plc
# Released as open source under GPLv3

import argparse, sys
from pcap import PcapBleWriter
from sniffle_hw import SniffleHW, BLE_ADV_AA, PacketMessage, DebugMessage, StateMessage
from packet_decoder import DPacketMessage, ConnectIndMessage

# global variable to access hardware
hw = None

def main():
    aparse = argparse.ArgumentParser(description="Connection initiator test script for Sniffle BLE5 sniffer")
    aparse.add_argument("-s", "--serport", default="/dev/ttyACM0", help="Sniffer serial port name")
    args = aparse.parse_args()

    global hw
    hw = SniffleHW(args.serport)

    # set the advertising channel (and return to ad-sniffing mode)
    hw.cmd_chan_aa_phy(37, BLE_ADV_AA, 0)

    # pause after sniffing
    hw.cmd_pause_done(True)

    # capture advertisements
    hw.cmd_endtrim(0x10)

    # turn off RSSI filter
    hw.cmd_rssi(-128)

    # Turn off MAC filter
    hw.cmd_mac()

    # initiator doesn't care about this setting, it always accepts aux
    hw.cmd_auxadv(False)

    # advertiser needs a MAC address
    hw.random_addr()

    # advertise roughly every 200 ms
    hw.cmd_adv_interval(200)

    # zero timestamps and flush old packets
    hw.mark_and_flush()

    # advertising and scan response data
    advData = bytes([
        0x02, 0x01, 0x1A, 0x02, 0x0A, 0x0C, 0x11, 0x07,
        0x64, 0x14, 0xEA, 0xD7, 0x2F, 0xDB, 0xA3, 0xB0,
        0x59, 0x48, 0x16, 0xD4, 0x30, 0x82, 0xCB, 0x27,
        0x05, 0x03, 0x0A, 0x18, 0x0D, 0x18])
    devName = b'NCC Goat'
    scanRspData = bytes([len(devName) + 1, 0x09]) + devName

    # now enter advertiser mode
    hw.cmd_advertise(advData, scanRspData)

    while True:
        msg = hw.recv_and_decode()
        print_message(msg)

def print_message(msg):
    if isinstance(msg, PacketMessage):
        print_packet(msg)
    elif isinstance(msg, DebugMessage):
        print(msg)
    elif isinstance(msg, StateMessage):
        print(msg)
    print()

def print_packet(pkt):
    # Further decode and print the packet
    dpkt = DPacketMessage.decode(pkt)
    print(dpkt)

    if isinstance(dpkt, ConnectIndMessage):
        hw.decoder_state.cur_aa = dpkt.aa

if __name__ == "__main__":
    main()
