#!/usr/bin/python3.6
import json
import sys
import os
import time

commands_json = 'commands.json'

with open(str(commands_json)) as commands:
    json_data = json.load(commands)
    array = json_data['commands_array']
    json_dict = json_data['commands_dict']
    # print(str(array))
    # print(str(json_dict))
    # we leave these variables available for use with our program
    commands_array = array
    commands_dict = json_dict