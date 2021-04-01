import json
import dht
import network
import time
import onewire
#import ds18x20
from machine import Pin
from micropyserver import MicroPyServer

# ds_pin = machine.Pin(4)
# ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

blueled = Pin(2, Pin.OUT)
adc = machine.ADC(0)
m_vin = Pin(5, Pin.OUT)
m_vin.off()
wlan_id = "random"
wlan_pass = "500pxFORall"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
server = MicroPyServer()

if wlan.isconnected() == False:
    wlan.connect(wlan_id, wlan_pass)
    while wlan.isconnected() == False:
        time.sleep(1)
print('Device IP:', wlan.ifconfig()[0])

blueled.off()

varVolt = 4.1339 # среднее отклонение (ищем в excel)
varProcess = 0.05 # скорость реакции на изменение (подбирается вручную)
Pc = 0.0
G = 0.0
P = 1.0
Xp = 0.0
Zp = 0.0
Xe = 0.0

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
    ''' request handler '''
    d = dht.DHT11(Pin(14))
    # roms = ds_sensor.scan()
    # ds_sensor.convert_temp()
    d.measure()
    hum = round(kalman(d.humidity()))
    data = {"temperature":  d.temperature(), "humidity": hum}
    json_str = json.dumps(data)
    server.send("HTTP/1.0 200 OK\r\n")
    server.send("Content-Type: application/json\r\n\r\n")
    server.send(json_str)
    blueled.off()
    
def show_moisture(request):
    blueled.on()
    m_vin.on()
    time.sleep(1)
    data = {"moisture": adc.read()}
    m_vin.off()
    json_str = json.dumps(data)
    server.send("HTTP/1.0 200 OK\r\n")
    server.send("Content-Type: application/json\r\n\r\n")
    server.send(json_str)
    blueled.off()

''' add request handler '''
server.add_route("/data", show_data)
server.add_route("/moisture", show_moisture)

''' start server '''
server.start()