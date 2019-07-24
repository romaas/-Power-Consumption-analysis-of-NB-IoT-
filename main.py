import time
from network import LTE
import socket
import ussl
import usocket
import pycom

import machine
import network
import os
from network import WLAN
from network import Bluetooth
from network import LoRa
from machine import RTC


def client():

    rtc = RTC()
    rtc.ntp_sync("se.pool.ntp.org")

    usocket.dnsserver(0,'8.8.8.8')#setting  DNS Server to Google's DNS Servers
    usocket.dnsserver(1,'4.4.4.4')
    print("\nDNS Server = ",usocket.dnsserver())

    host = '0.tcp.ngrok.io'
    port = 12739

    ad = socket.getaddrinfo(host, port)
    addr = ad[0][-1]

    print("\naddr = ",addr)
    s = socket.socket()
    s.connect(addr)
    print("Sleeping for 5 seconds after connecting to the TCP server")
    time.sleep(5)
    i=1

    while i < 11:
        t1 = time.ticks_ms()
        bytes_Sent = s.send(bytes(i*100))
        t2 = time.ticks_ms()
        print("Time taken to send %s Bytes of data =  %s" % (bytes_Sent, time.ticks_diff(t1,t2)))
        time.sleep(10)
        i = i + 1
    s.close()
    print("\nconnection closed")


#This returns a network LTE object with an active Internet connection.
def getLTE():
    lte = LTE()
    # If already used, the lte device will have an active connection.
    # If not, need to set up a new connection.
    if lte.isconnected():
        return lte

    print("Resetting LTE modem ... ", end='')
    lte.send_at_cmd('AT^RESET')
    print("OK")
    time.sleep(1)


    print("Configuring LTE ", end='')
    lte.send_at_cmd('AT+CGDCONT=1,"IP","lpwa.telia.iot"')
    #cid =1 , PDP = IP, APN = lpwa.telia.iot
    print(".", end='')
    lte.send_at_cmd('AT!="RRC::addscanfreq band=28 dl-earfcn=9410"')
    print(".", end='')
    lte.send_at_cmd('AT+CFUN=1')#It indicates full functionality
    print(" OK")

    # If correctly configured for carrier network, attach() should succeed.
    if not lte.isattached():
        print("Attaching to LTE network ", end='')
        lte.attach()
        while(True):
            if lte.isattached():
                print(" attached")
                break
            print('.', end='')
            time.sleep(1)

    # Once attached, connect() should succeed.
    if not lte.isconnected():
        print("Connecting on LTE network ", end='')
        lte.connect()
        while(True):
            if lte.isconnected():
                print(" connected")
                break
            print('.', end='')
            time.sleep(1)

    client()
    
    return lte

def endLTE(LTE):

    lte = LTE
    print("Disonnecting LTE ... ", end='')
    lte.disconnect()
    if lte.isconnected():
        print("could not disconnect")
    else:
        print("disconnected")
    time.sleep(1)
    print("Detaching LTE ... ", end='')
    lte.dettach()
    if lte.isattached():
        print("Could not dettach")
    else:
        print("Dettached")
    lte.deinit()


def Turn_off():

    print("******************************************************************")
    print('Switching off Heartbeat')
    pycom.heartbeat(False)
    pycom.rgbled(0x220000)

    print("******************************************************************")
    print('Switching off WLAN')
    wlan = network.WLAN()
    wlan.deinit()

    print("******************************************************************")
    print('Switching off Server')
    server = network.Server()
    server.deinit()

    print("******************************************************************")
    print('Switching off Bluetooth')
    bt = Bluetooth()
    bt.deinit()

    print("******************************************************************")
    print('Switching off RGB Led')
    pycom.rgbled(0x000000)

# Program starts here.
def main_program():

    print( "---Inside main_program---")
    Turn_off()
    lte = getLTE()
    endLTE(lte)

main_program()
