#!/usr/bin/env python
import time
import homie
import logging
import os
import re
import noolite
import queue
import threading
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = {
    "HOST": os.environ.get('MQTT_SERVER', 'mosquitto'),
    "PORT": os.environ.get('MQTT_PORT', 1883),
    "KEEPALIVE": os.environ.get('KEEPALIVE', 10),
    "USERNAME": os.environ.get('USERNAME', ''),
    "PASSWORD": os.environ.get('PASS', ''),
    "CA_CERTS": os.environ.get('CA_CERTS', ''),
    "DEVICE_ID": os.environ.get('DEVICE_ID', 'noolite'),
    "DEVICE_NAME": os.environ.get('DEVICE_NAME', 'noolite'),
    "TOPIC": os.environ.get('TOPIC', 'homie'),
    "CHANNELS": os.environ.get('CHANNELS', 16)
}

Homie = homie.Homie(config)
nodes = {}
q = queue.Queue()
t = None

def queuee_worker():
    n = noolite.NooLite()
    while True:
        item = q.get()
        if item is None:
            break
        command = item.get('command', None)
        channel = item.get('channel', None)
        args = item.get('args', None)
        if command == 'on':
            n.on(channel)
        elif command == 'off':
            n.off(channel)
        elif command == 'set':
            n.set(channel, args)
        elif command == 'bind':
            n.bind(channel)
        elif command == 'quit':
            q.task_done()
        time.sleep(0.3)

def brightnessHandler(mqttc, obj, msg):
    try:
        payload = msg.payload.decode("UTF-8").lower()
        topic = msg.topic
        channel = parse_channel(topic)
        logger.info("payload: {}, topic: {}, channel: {}".format(payload, topic, channel))
        if channel not in nodes:
            logger.error("Cannot find channel {}".format(channel))
            return true
        if not payload.isdigit():
            logger.error("Invalid payload {}".format(payload))
            return
        node = nodes[channel]
        brightness = int(payload)
        ch_num = int(channel.replace('ch',''))
        logger.info("[{}] brightness: {}".format(channel, brightness))
        q.put({'command':'set', 'channel':ch_num,'args':brightness})
        node.setProperty("brightness").send(brightness)
    except Exception as e:
        logger.error("Something gone wrong in brightnessHandler: {}!".format(e))

def bindHandler(mqttc, obj, msg):
    try:
        payload = msg.payload.decode("UTF-8").lower()
        topic = msg.topic
        channel = parse_channel(topic)
        logger.info("payload: {}, topic: {}, channel: {}".format(payload, topic, channel))
        if channel not in nodes:
            logger.error("Cannot find channel {}".format(channel))
            return true
        node = nodes[channel]
        ch_num = int(channel.replace('ch',''))
        q.put({'command':'bind', 'channel':ch_num})
    except Exception as e:
        logger.error("Something gone wrong in bindHandler: {}!".format(e))

def powerHandler(mqttc, obj, msg):
    try:
        payload = msg.payload.decode("UTF-8").lower()
        topic = msg.topic
        channel = parse_channel(topic)
        logger.info("payload: {}, topic: {}, channel: {}".format(payload, topic, channel))
        if channel not in nodes:
            logger.error("Cannot find channel {}".format(channel))
            return true
        node = nodes[channel]
        ch_num = int(channel.replace('ch',''))
        if payload == 'on' or payload == 'true':
            logger.info("[{}] Power: on".format(channel))
            q.put({'command':'on', 'channel':ch_num})
            node.setProperty("power").send("on")
        else:
            logger.info("[{}] Power: off".format(channel))
            q.put({'command':'off', 'channel':ch_num})
            node.setProperty("power").send("off")
    except Exception as e:
        logger.error("Something gone wrong in powerHandler: {}!".format(e))

def parse_channel(topic):
    found = re.findall('(ch\d+)', topic)
    if len(found) == 0:
        return "";
    return found[0]

def main():
    logger.info("Config: {}".format(config))
    Homie.setFirmware("noolite-gateway", "1.0.0")
    channels = int(config['CHANNELS'])
    for i in range(0, channels):
      nodeName = "ch{}".format(i)
      node = Homie.Node(nodeName, nodeName)
      node.advertise("power").settable(powerHandler)
      node.advertise("brightness").settable(brightnessHandler)
      node.advertise("bind").settable(bindHandler)
      nodes[nodeName]=node
      
    Homie.setup()
    t = threading.Thread(target=queuee_worker)
    t.start()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        q.put({'command':'quit'})
        t.join()
        logger.info("Quitting.")