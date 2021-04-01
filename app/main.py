import json
import dht
import network
import time
import senko
import utime
from config import *
from machine import Pin
from micropyserver import MicroPyServer

start = utime.time()

ver = "version: 0.557"
print (ver)

OTA = senko.Senko(
  user="makeinstall77", # Required
  repo="strawberry_monitoring", # Required
  branch="main", # Optional: Defaults to "master"
  working_dir="app", # Optional: Defaults to "app"
  files = ["boot.py", "main.py"]
)

relay1 = Pin(0, Pin.OUT)
relay2 = Pin(12, Pin.OUT)
relay3 = Pin(13, Pin.OUT)
relay4 = Pin(4, Pin.OUT)

relay1.on()
relay2.on()
relay3.on()
relay4.on()

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



time.sleep(3)

try:
    # if OTA.fetch():
        # print("A newer version is available!")
    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()
    else:
        print("Up to date!")
except Exception as e:
    print (e)
    pass

varVolt = 4.1339 # среднее отклонение (ищем в excel)
varProcess = 0.05 # скорость реакции на изменение (подбирается вручную)
Pc = 0.0
G = 0.0
P = 1.0
Xp = 0.0
Zp = 0.0
Xe = 0.0

def uptime():
    u = utime.time() - int(start)
    u = "Uptime: " + str(u)
    return u
    
def relay_state(n):
    if n == 1:
        if relay1.value() == 1:
            rez = """<p>Relay 1 - State off</p>
        <p><a href="/relay1_on"><button class="button">ON</button></a></p>"""
        elif relay1.value() == 0:
            rez = """<p>Relay 1 - State on</p>
        <p><a href="/relay1_off"><button class="button button2">OFF</button></a></p>"""
    elif n == 2:
        if relay2.value() == 1:
            rez = """<p>Relay 2 - State off</p>
        <p><a href="/relay2_on"><button class="button">ON</button></a></p>"""
        elif relay2.value() == 0:
            rez = """<p>Relay 2 - State on</p>
        <p><a href="/relay2_off"><button class="button button2">OFF</button></a></p>"""
    elif n == 3:
        if relay3.value() == 1:
            rez = """<p>Relay 3 - State off</p>
        <p><a href="/relay3_on"><button class="button">ON</button></a></p>"""
        elif relay3.value() == 0:
            rez = """<p>Relay 3 - State on</p>
        <p><a href="/relay3_off"><button class="button button2">OFF</button></a></p>"""
    elif n == 4:
        if relay4.value() == 1:
            rez = """<p>Relay 4 - State off</p>
        <p><a href="/relay4_on"><button class="button">ON</button></a></p>"""
        elif relay4.value() == 0:
            rez = """<p>Relay 4 - State on</p>
        <p><a href="/relay4_off"><button class="button button2">OFF</button></a></p>"""
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
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    machine.reset()
    
def version(request):
    server.send(ver)

def relay1_on(request):
    relay1.off()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay1_off(request):
    relay1.on()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay2_on(request):
    relay2.off()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay2_off(request):
    relay2.on()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay3_on(request):
    relay3.off()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay3_off(request):
    relay3.on()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay4_on(request):
    relay4.off()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")
    
def relay4_off(request):
    relay4.on()
    server.send("HTTP/1.1 302 Found\r\n")
    server.send("Location: ./\r\n")

def root(request):
    html = '''<!DOCTYPE html>
<html>
<head>
 <title>Strawberry monitoring</title>
 <meta name="viewport" content="width=device-width, initialscale=1">
 <link rel="icon" href="data:,">
  <style>
    html {
      font-family: Helvetica;
      display: inline-block;
      margin: 0px auto;
      text-align: center;
    }
    .button {
      background-color: #4CAF50;
      border: none;
      color: white;
      padding: 16px 40px;
      text-decoration: none;
      font-size: 30px;
      margin: 2px;
      cursor: pointer;
    }
    .button2 {
      background-color: #555555;
    }
  </style>
</head>
<body>
 <h1>Strawberry monitoring</h1>
 <p><h2>System:<h2></p>
 <p>%s</p>
 <p>%s</p>
 <p><a href="/reboot"><button class="button">reboot</button></a></p>
 %s
 %s
 %s
 %s
</body>
</html>''' % (ver, uptime(), str(relay_state(1)), str(relay_state(2)), str(relay_state(3)), str(relay_state(4)))
    server.send(html)



''' add request handler '''
server.add_route("/data", show_data)
server.add_route("/moisture", show_moisture)
server.add_route("/reboot", reboot)
server.add_route("/version", version)
server.add_route("/version", version)
server.add_route("/", root)
server.add_route("/relay1_on", relay1_on)
server.add_route("/relay1_off", relay1_off)
server.add_route("/relay2_on", relay2_on)
server.add_route("/relay2_off", relay2_off)
server.add_route("/relay3_on", relay3_on)
server.add_route("/relay3_off", relay3_off)
server.add_route("/relay4_on", relay4_on)
server.add_route("/relay4_off", relay4_off)

print ("starting http server")
''' start server '''
server.start()
blueled.off()