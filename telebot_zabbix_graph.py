#!/usr/bin/python
from configparser import ConfigParser
from pyzabbix import ZabbixAPI
import telebot
import requests
import datetime
import subprocess

config = ConfigParser()

config.read('/home/makeinstall/.scripts/config.ini')
bot_id = config.get('conf', 'bot_id')
chat_id = config.get('conf', 'chat_id')
user_agent_val = config.get('conf', 'user_agent_val')
zabbix_url = config.get('conf', 'zabbix_url')
zabbix_login = config.get('conf', 'zabbix_login')
zabbix_password = config.get('conf', 'zabbix_password')
host = config.get('conf', 'host')

bot = telebot.TeleBot(bot_id)
zapi = ZabbixAPI(zabbix_url)
zapi.login(zabbix_login, zabbix_password)

class Relay(object):
    def __init__(self, host, relay_name, name):
        self.__host_name = host
        self.__name = relay_name
        self.__text = name
        self.__cmd = '/usr/bin/curl --http0.9 http://' + self.__host_name + '/' + self.__name + '_'
    
    def on(self):
        proc = subprocess.Popen(self.__cmd + 'on', stdout=subprocess.PIPE, shell=True)
        if int(proc.stdout.read()) == 1:
            result = True
        else:
            result = False
        return result
    
    def off(self):
        proc = subprocess.Popen(self.__cmd + 'off', stdout=subprocess.PIPE, shell=True)
        if int(proc.stdout.read()) == 1:
            result = True
        else:
            result = False
        return result
        
    def status(self):
        proc = subprocess.Popen(self.__cmd + 'status', stdout=subprocess.PIPE, shell=True)
        if int(proc.stdout.read()) == 1:
            result = self.__text + ' вкл'
        else:
            result = self.__text + ' выкл'
        return result
    
    def ison(self):
        proc = subprocess.Popen(self.__cmd + 'status', stdout=subprocess.PIPE, shell=True)
        if int(proc.stdout.read()) == 1:
            result = True
        else:
            result = False
        return result
        
    def isoff(self):
        proc = subprocess.Popen(self.__cmd + 'status', stdout=subprocess.PIPE, shell=True)
        if int(proc.stdout.read()) == 1:
            result = False
        else:
            result = True
        return result

def get_graph(host, name):
    graph_id = zapi.graph.get(search={'host': host, 'name': name})[0].get('graphid')
    graph_url = zabbix_url + '/chart2.php?graphid=' + graph_id + '&from=now-12h&to=now&height=400&width=800&profileIdx=web.charts.filter&_=uqsff1f5'
    
    s = requests.Session()
    r = s.get(zabbix_url, headers = {'User-Agent': user_agent_val})
    cookie = s.cookies.get('zbx_session', domain='s1.1vlan')
    s.headers.update({'Referer':zabbix_url})
    p = s.post(zabbix_url + '/index.php?login=1', {
            'name' : zabbix_login, 
            'password' : zabbix_password,
            'enter' : 'Enter'
            })
    r = s.get(graph_url, headers = {'User-Agent': user_agent_val})
    img = r.content
    r.close()
    return img

def get_last_value(host, name):   
    result = int(zapi.item.get(search={'host': host, 'name': name})[0].get('lastvalue'))
    return result

def main():
    light = Relay(host, 'relay4', 'освещение')
    heat = Relay(host, 'relay3', 'отопление')
    vent = Relay(host, 'relay2', 'вентиляция')
    
    t = get_last_value(host, 'температура')
    humid = get_last_value(host, 'влажность')
    moist = get_last_value(host, 'увлажнённость')
    
    h = int(datetime.datetime.now().time().hour)
    m = int(datetime.datetime.now().time().minute)
    
    c = "Температура: " + str(t) + "°C" + ", Влажность воздуха: " + str(humid) + "%, Увлажнённость почвы: " + str(moist) + "%"
    img = get_graph(host, 'values')
    bot.send_photo(chat_id, img, caption = c)
    
    #day
    if h >= 7 or h < 22:
        if light.isoff():
            light.on()
            vent.on()
            
        if t < 21:
            heat.on()
            vent.off()
            
        if t >= 21 and t < 23:
            heat.off()
            vent.off()
        
        if t > 26:
            vent.on()
    
    #night
    if h < 7 or h >= 22:
        if light.ison():
            light.off()
            vent.off()
    
        if t < 21:
            heat.on()
            
        if t > 25 and t < 27:
            heat.off()
            vent.off()

        if t > 29:
            vent.on()
            
    c = light.status() + ', ' + heat.status() + ', ' + vent.status()
    img = get_graph(host, 'relay')
    message = bot.send_photo(chat_id, img, caption = c)
    bot.delete_message(chat_id, message.id - 2)
    bot.delete_message(chat_id, message.id - 3)

if __name__ == '__main__':
    main()
