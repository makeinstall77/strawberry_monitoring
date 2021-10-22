import dht
import network
import time
from config import *
from machine import Pin
from micropyserver import MicroPyServer
gc.collect()


relay1 = Pin(0, Pin.OUT)
relay2 = Pin(13, Pin.OUT)
relay3 = Pin(12, Pin.OUT)
relay4 = Pin(4, Pin.OUT)

relay1.on()
relay2.on()
relay3.on()
relay4.on()

blueled = Pin(2, Pin.OUT)
blueled.on()

adc = machine.ADC(0)
m_vin = Pin(5, Pin.OUT)
m_vin.off()

wlan_id = ssid
wlan_pass = password
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
server = MicroPyServer()

# if wlan.isconnected() == False:
    # wlan.connect(wlan_id, wlan_pass)
    # while wlan.isconnected() == False:
        # time.sleep(1)
        
while wlan.isconnected() == False:
    print("trying hui")
    wlan.connect(ssid2, password2)
    time.sleep(15)
    if wlan.isconnected() == False:
        print("trying random")
        wlan.connect(ssid, password)
        time.sleep(15)

print('IP by DHCP:', wlan.ifconfig()[0])

varVolt = 4.1339
varProcess = 0.05
Pc = 0.0
G = 0.0
P = 1.0
Xp = 0.0
Zp = 0.0
Xe = 0.0

def relay_state(n):
    if n == 1:
        if relay1.value() == 1:
            rez = 0
        elif relay1.value() == 0:
            rez = 1
    elif n == 2:
        if relay2.value() == 1:
            rez = 0
        elif relay2.value() == 0:
            rez = 1
    elif n == 3:
        if relay3.value() == 1:
            rez = 0
        elif relay3.value() == 0:
            rez = 1
    elif n == 4:
        if relay4.value() == 1:
            rez = 0
        elif relay4.value() == 0:
            rez = 1
    return rez

def kalman(var):
    global varVolt
    global varProcess
    global Pc
    global G
    global P
    global Xp
    global Zp
    global Xe
    Pc = P + varProcess
    G = Pc / (Pc + varVolt)
    P = (1 - G) * Pc
    Xp = Xe
    Zp = Xp
    Xe = G * (var - Zp) + Xp # "фильтрованное" значение
    return Xe

def show_data(request):
    blueled.on()
    d = dht.DHT11(Pin(14))
    d.measure()
    hum = round(kalman(d.humidity()))
    server.send(str(d.temperature()) + "," + str(hum))
    blueled.off()

def show_moisture(request):
    blueled.on()
    m_vin.on()
    s = str(adc.read())
    time.sleep(1)
    m_vin.off()
    server.send(s);
    blueled.off()

def reboot(request):
    machine.reset()

def relay1_on(request):
    relay1.off()
    relay1_status(request)

def relay1_off(request):
    relay1.on()
    relay1_status(request)

def relay2_on(request):
    relay2.off()
    relay2_status(request)

def relay2_off(request):
    relay2.on()
    relay2_status(request)

def relay3_on(request):
    relay3.off()
    relay3_status(request)

def relay3_off(request):
    relay3.on()
    relay3_status(request)

def relay4_on(request):
    relay4.off()
    relay4_status(request)

def relay4_off(request):
    relay4.on()
    relay4_status(request)

def relay1_status(request):
    server.send(str(relay_state(1)))

def relay2_status(request):
    server.send(str(relay_state(2)))

def relay3_status(request):
    server.send(str(relay_state(3)))

def relay4_status(request):
    server.send(str(relay_state(4)))

''' add request handler '''
server.add_route("/data", show_data)
server.add_route("/moisture", show_moisture)
server.add_route("/reboot", reboot)
server.add_route("/relay1_on", relay1_on)
server.add_route("/relay1_off", relay1_off)
server.add_route("/relay2_on", relay2_on)
server.add_route("/relay2_off", relay2_off)
server.add_route("/relay3_on", relay3_on)
server.add_route("/relay3_off", relay3_off)
server.add_route("/relay4_on", relay4_on)
server.add_route("/relay4_off", relay4_off)
server.add_route("/relay1_status", relay1_status)
server.add_route("/relay2_status", relay2_status)
server.add_route("/relay3_status", relay3_status)
server.add_route("/relay4_status", relay4_status)

print ("starting http server")
''' start server '''
server.start()

blueled.off()
