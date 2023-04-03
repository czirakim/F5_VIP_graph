"""
Create graph

"""

import requests
from pyvis.network import Network
import os
import sys
import json
import re
from logger import logger
import logging
import itertools
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

net = Network()

# options for graph
options = {
  "edges": {
    "color": {
      "inherit": True
    },
    "font": {
      "align": "top"
    },
    "selfReferenceSize": 0,
    "selfReference": {
      "angle": 0.7853981633974483
    },
    "smooth": False
  },
  "layout": {
    "hierarchical": {
      "enabled": True,
      "levelSeparation": -240,
      "direction": "DU",
      "sortMethod": "directed",
      "shakeTowards": "roots"
    }
  }
  }


# create a logger
logg = logging.getLogger(__name__)
logg.setLevel(logging.INFO)
# add the handler to the logger
logg.addHandler(logger())

# F5 device
IP_ADDRESS = os.environ.get('IP_ADDRESS')

# VIP-name
vip_name = f"{sys.argv[1]}"

API_string = os.environ.get('Authorization_string')
url = f"https://{IP_ADDRESS}/mgmt/tm/ltm/virtual/{vip_name}"
headers = {
        'Authorization': f'Basic {API_string}',
        'Accept': 'application/json'
             }
try:
    vip_response = requests.request("GET", url, headers=headers, verify=False)
    vip_response.raise_for_status()
except requests.exceptions.HTTPError:
    if (vip_response.status_code == 404 or vip_response.status_code == 400):
        logg.error(f"An error occurred while making the request:  {vip_response.text}")
        exit()
except requests.exceptions.RequestException as e:
    logg.error(f"An error occurred while making the request: {e}")
    exit()
else:
    logg.info(f"Virtual Server name: {vip_name}")
    reply = json.loads(vip_response.text)


# add nodes and edges to the graph: vip-->pool-->nodes
def vip2nodes(vips, pools, nodes, pool_name, member_list, label_string):
    # vip --> pool
    pools = pools + 1
    label1 = pool_name
    net.add_node(pools, label=label1, color='#3da831')
    if label_string == 'default':
        net.add_edge(vips, pools, label=label_string)
    elif label_string is None:
        net.add_edge(vips, pools, label='else/default')
    else:
        net.add_edge(vips, pools, label=f'uri: {label_string}')

    # pool --> nodes
    for member in member_list:
        nodes = nodes + 1
        # print(f"member: {member}")
        label1 = member['name']
        net.add_node(nodes, label=label1, color='#9a31a8')
        net.add_edges([(pools, nodes, 2)])

    return pools, nodes


# get the uri and pool lists from irules
def get_uri_pool(item):
    uri = []
    pool = []
    my_list_switch = []
    # define regex expresion to match {...}
    regex = r"{([^{}]*)}"
    # get a list of {...}
    match = re.findall(regex, item)
    # print ('match', match)
    if match:
        for segment in match:
            # get everything that is between " " , domains and uri
            tmp = re.findall(r'"([^"]*[^.\s])"', segment)
            if tmp:
                for thing in tmp:
                    # if not a domain name  ( does not contain .)
                    if not re.findall(r'([.\s])', thing):
                        uri.append(thing)
                        index = match.index(segment)
                        line1 = match[index+1]
                        if 'pool' in line1:
                            found = re.findall(r"pool (.*?) ", line1)
                            pool.append(found[0])
                            # for else pool lines
                            if (index+2) < len(match):
                                if 'pool' in match[index+2]:
                                    found = re.findall(r"pool (.*?) ", match[index+2])
                                    pool.append(found[0])
                                    uri.append(f'else_{thing}')
                        else:
                            pool.append(None)
                            # if uri has no pool check else pool on the next segment
                            if (index+2) < len(match):
                                if 'pool' in match[index+2]:
                                    found = re.findall(r"pool (.*?) ", match[index+2])
                                    pool.append(found[0])
                                    uri.append(f'else_{thing}')
        # create a list of tuples [(uri,pool)]
        my_list = list(itertools.zip_longest(uri, pool))
    # for SWITCH statements
    # find every thing after 'switch', till empty line or 'end_switch'
    # tmp = re.findall(r"(?s)(?<=switch \[HTTP::uri\] )(.*})(?:(?:\r*\n){2})", item)
    tmp = re.findall(r"(?s)(?<=switch \[HTTP::uri\] )(.*)(?:(?:\r*\n){2}|\bend_switch\b)", item)
    for segment in tmp:
        # get the pool list
        found_pool = re.findall(r"pool (.*?) ", segment)
        # get the uri list
        found_uri = re.findall(r'"([^"]*[^.\s])"', segment)
        # create a list of tuples
        my_list_switch = list(itertools.zip_longest(found_uri, found_pool))

    if my_list_switch:
        return my_list + my_list_switch
    else:
        return my_list


# get the members of a pool
def get_members(pool_name):
    API_string = os.environ.get('Authorization_string')
    url = f"https://{IP_ADDRESS}/mgmt/tm/ltm/pool/{pool_name}/members"
    headers = {
            'Authorization': f'Basic {API_string}',
            'Accept': 'application/json'
             }
    try:
        response = requests.request("GET", url, headers=headers, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if (response.status_code == 404 or response.status_code == 400):
            logg.error(f"An error occurred while making the request:  {response.text}")
    except requests.exceptions.RequestException as e:
        logg.error(f"An error occurred while making the request: {e}")
    else:
        logg.info(f"Pool name: {pool_name}")
        data = json.loads(response.text)
        return data


# get irule content
def get_irule(rule_name):
    API_string = os.environ.get('Authorization_string')
    url = f"https://{IP_ADDRESS}/mgmt/tm/ltm/rule/{rule_name}"
    headers = {
            'Authorization': f'Basic {API_string}',
            'Accept': 'application/json'
             }
    try:
        response = requests.request("GET", url, headers=headers, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        if (response.status_code == 404 or response.status_code == 400):
            logg.error(f"An error occurred while making the request:  {response.text}")
    except requests.exceptions.RequestException as e:
        logg.error(f"An error occurred while making the request: {e}")
    else:
        logg.info(f"Rule name: {rule_name}")
        data = json.loads(response.text)
        return data


# add pools,nodes and vips
def add_obj():
    # initialize indexes
    nodes = 0
    pools = 500
    vips = 1000
    members_list = []

    # if we have a response
    if reply:
        label1 = reply['name']
        label2 = reply['destination'].replace('/Common/', '')
        label3 = f"{label1} \n {label2}"
        # draw if vip has default pool
        if 'pool' in reply:
            pool_name = reply['pool'].replace('/Common/', '')
            members_list = get_members(pool_name)['items']
            # add the vip
            net.add_node(vips, label=label3, color='#3155a8')
            pools, nodes = vip2nodes(vips, pools, nodes, pool_name, members_list, 'default')
        # draw if vip has irules
        if 'rules' in reply:
            # this is the list of irules of the vip
            irule_file = reply['rules']
            if 'pool' not in reply:
                # add the vip if it does not have a default pool
                net.add_node(vips, label=label3, color='#3155a8')
            for item in irule_file:
                item = item.replace('/Common/', '')
                # get irule content where item is the name of irule
                rule = get_irule(item)
                data1 = rule["apiAnonymous"]
                # this the list of tuples [(uri, pool)]
                custom_list = get_uri_pool(data1)
                for thing in custom_list:
                    if thing[1]:
                        members_list = get_members(thing[1])['items']
                        pools, nodes = vip2nodes(vips, pools, nodes, thing[1], members_list, thing[0])
                        # with irule name
                        # pools, nodes = vip2nodes(vips, pools, nodes, thing[1], members_list, item)


if __name__ == "__main__":
    add_obj()
    net.repulsion(node_distance=100, spring_length=200)
    net.show_buttons(filter_=True)
    net.options.__dict__.update(options)
    net.show(f'./edges_{sys.argv[1]}.html')
