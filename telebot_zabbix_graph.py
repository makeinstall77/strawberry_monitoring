#!/usr/bin/python
from pyzabbix import ZabbixAPI
import telebot
import requests
import time

bot = telebot.TeleBot('1685107456:AAFaYuo8ROAUxvCoN72r-miYnHAACbIMWvU')

user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'
root_url = 'http://s1.1vlan/zabbix'

def write_file(n, h):
    f = open(n, "wb")
    r = get_file(h)
    f.write(r.content)
    f.close()
    
def get_file(arg):
    s = requests.Session()
    r = s.get(root_url, headers = {'User-Agent': user_agent_val})
    cookie = s.cookies.get('zbx_session', domain='s1.1vlan')
    s.headers.update({'Referer':root_url})
    p = s.post(root_url + '/index.php?login=1', {
    'name' : 'Admin', 
    'password' : 'VFSffkqB2MSly4vk',
    'enter' : 'Enter'
    })
    r = s.get(arg, headers = {'User-Agent': user_agent_val})
    r.close()
    return r

def plant_zabbix():
    zapi = ZabbixAPI(root_url)
    zapi.login("Admin", "VFSffkqB2MSly4vk")
    link = root_url + '/chart2.php?graphid=2656&from=now-12h&to=now&height=400&width=800&profileIdx=web.charts.filter&_=uqsff1f5'
    print(link)
    write_file('graph.png', link)
    img = open('graph.png', 'rb')
    # bot.delete_message(message.chat.id, id)
    humid = zapi.item.get(itemids=42997)[0].get('lastvalue')
    temp = zapi.item.get(itemids=42996)[0].get('lastvalue')
    moist = zapi.item.get(itemids=42998)[0].get('lastvalue')
    c = "Температура: " + temp + "°C" + ", Влажность: " + humid + "%, Увлажнённость почвы: " + moist + "%"
    res = bot.send_photo('-1001349719134', img, caption = c)
    bot.delete_message('-1001349719134', res.id - 1)

plant_zabbix()

