import json
import dht
import network
import time
import onewire
import senko
from config import *
#import ds18x20
from machine import Pin
from micropyserver import MicroPyServer

ver = "version: 0.544"
print (ver)

html = '''<!DOCTYPE html>
<html>
<head>
<title>ESP32 Web Server</title>
</head>
<body>
 <h1>ESP32 Web Server</h1>
 <p>system</p>
 <p>%s</p>
 <p><a href="/reboot"><button>reboot</button></a></p>
 <p>GPIO 26 - State</p>
 <p><a href="/26/on"><button>ON</button></a></p>
 <p><a href="/26/off"><button>OFF</button></a></p>
 <p>GPIO 27 - State</p>
 <p><a href="/27/on"><button>ON</button></a></p>
 <p><a href="/27/off"><button>OFF</button></a></p>
</body>
</html>''' % ver

OTA = senko.Senko(
  user="makeinstall77", # Required
  repo="strawberry_monitoring", # Required
  branch="main", # Optional: Defaults to "master"
  working_dir="app", # Optional: Defaults to "app"
  files = ["boot.py", "main.py"]
)

# ds_pin = machine.Pin(4)
# ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

blueled = Pin(2, Pin.OUT)
adc = machine.ADC(0)
m_vin = Pin(5, Pin.OUT)
m_vin.off()
wlan_id = ssid
wlan_pass = password
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
server = MicroPyServer()

if wlan.isconnected() == False:
    wlan.connect(wlan_id, wlan_pass)
    while wlan.isconnected() == False:
        time.sleep(1)
        
print('IP by DHCP:', wlan.ifconfig()[0])

blueled.off()

try:
    # if OTA.fetch():
        # print("A newer version is available!")
    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()
    else:
        print("Up to date!")
except:
    print ("error while checking new version")
    pass

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
    server.send("Connection: close");
    blueled.off()
    
def reboot(request):
    server.send("reboot")
    time.sleep(3)
    machine.reset()
    
def version(request):
    server.send(ver)


def root(req):
    server.send(html)


''' add request handler '''
server.add_route("/data", show_data)
server.add_route("/moisture", show_moisture)
server.add_route("/reboot", reboot)
server.add_route("/version", version)
server.add_route("/", root)

print ("starting http server")
''' start server '''
server.start()