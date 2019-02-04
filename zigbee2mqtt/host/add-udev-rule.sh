#!/bin/bash
sudo cp 100-zigbee.rules /etc/udev/rules.d/
sudo udevadm trigger
