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
IP_ADDRESS = "192.168.88.100"

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
    it = json.loads(vip_response.text)


# add nodes and edges to the graph: vip-->pool-->nodes
def vip2nodes(vips, pools, nodes, pool_name, member_list, label_string):
    # vip --> pool
    pools = pools + 1
    label1 = pool_name
    net.add_node(pools, label=label1, color='#3da831')
    if label_string != 'default':
        net.add_edge(vips, pools, label=f'uri: {label_string}')
    else:
        net.add_edge(vips, pools, label=label_string)

    # pool --> nodes
    for member in member_list:
        nodes = nodes + 1
        # print(f"member: {member}")
        label1 = member['name']
        net.add_node(nodes, label=label1, color='#9a31a8')
        net.add_edges([(pools, nodes, 2)])

    return pools, nodes


# get the uri and pool lists
def get_uri_pool(item):
    uri = []
    # get everything that is between " " , domains and uri
    tmp = re.findall(r'"([^"]*[^.\s])"', item)
    for thing in tmp:
        # select only strings without . , so no domains , only uri
        if not re.findall(r'([.\s])', thing):
            uri.append(thing)
    pool = re.findall(r"pool (.*?) ", item)
    # create the list of tuples
    my_list = list(itertools.zip_longest(uri, pool))

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
    nodes = 0
    pools = 500
    vips = 1000
    members_list = []
    # if we have a response
    if it:
        label1 = it['name']
        # draw if vip has default pool
        if 'pool' in it:
            pool_name = it['pool'].replace('/Common/', '')
            members_list = get_members(pool_name)['items']
            label2 = it['destination'].replace('/Common/', '')
            label3 = f"{label1} \n {label2}"
            net.add_node(vips, label=label3, color='#3155a8')
            pools, nodes = vip2nodes(vips, pools, nodes, pool_name, members_list, 'default')
        # draw if vip has irules
        if 'rules' in it:
            # this is the list of irules of the vip
            irule_file = it['rules']
            for item in irule_file:
                item = item.replace('/Common/', '')
                # get irule content where item is the name of irule
                rule = get_irule(item)
                data1 = rule["apiAnonymous"]
                # this the list of tuples [(uri, pool)]
                custom_list = get_uri_pool(data1)
                for thing in custom_list:
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
