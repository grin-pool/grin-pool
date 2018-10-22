from datetime import datetime
import hashlib
import timeit
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen # python 3 syntax
import requests
import time
import pygal
from pygal.style import Style
import json
import sys
import traceback 
import cairosvg
import copy


from flask import Flask, Blueprint, render_template, request, session, make_response, flash, url_for, redirect
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from flask import Flask, Blueprint, render_template, request, session, make_response

from grinlib import lib


home_profile = Blueprint('home_profile'
                           , __name__
                           , template_folder='templates'
                           , static_folder='static'
                           )

# Grin Network Graph Style
grin_style_pygal = Style(
  background='transparent',
  plot_background='transparent',
  foreground='#53E89B',
  foreground_strong='#02e205',
  foreground_subtle='#274427',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  colors=('#C0C0C0', '#E8537A', '#E95355', '#E87653', '#E89B53'))

# Pool Graph Style
pool_style_pygal = Style(
  background='transparent',
  plot_background='transparent',
  foreground='#8c8c8c',
  foreground_strong='#fffcfc',
  foreground_subtle='#2d2d2d',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  colors=['#fcef00', '#0f12c1', '#c10e0e', '#0dc110', '#8b0cc1', '#00effc'])

# Worker Graph Style
worker_style_pygal = Style(
  background='transparent',
  plot_background='transparent',
  foreground='#2b26b7',
  foreground_strong='#9bdfff',
  foreground_subtle='#00033d',
  opacity='.6',
  opacity_hover='.9',
  transition='4000ms ease-in',
  colors=('#0f12c1', '#c10e0e', '#0dc110', '#8b0cc1', '#00effc'))

def get_api_url():
    CONFIG = lib.get_config()
    return "http://" + CONFIG["webui"]["api_url"]
    # API_URL = 'http://api.mwgrinpool.com:13423'

def get_grin_graph(start='0', r='120'):
    url = get_api_url() + '/grin/stats/' + start +','+str(r)+'/gps,height,difficulty'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
    gps_data = [float(i['gps']) for i in parsed]
    height_data = sorted(set([int(i['height']) for i in parsed]))
    difficulty_data = [int(i['difficulty']) for i in parsed]
    min_difficulty = min(d for d in difficulty_data)
    max_difficulty = max(d for d in difficulty_data)
    #print("HEIGHT DATA: {}".format(height_data))
    # create a line graph
    title = 'Grin Network - g/s'
    graph = pygal.Line(width=500, # 3.75
                       height=175,
                       style=grin_style_pygal,
                       interpolate='hermite', 
                       explicit_size=True,
#                       title=title,
                       fill=False,
                       show_dots=False,
                       stroke_style={'width': 2},
                       margin=0,
                       show_legend=False,
                       x_label_rotation=1,
                       x_labels_major_count=5,
                       show_minor_x_labels=False,
                       y_labels_major_count=3,
                       show_minor_y_labels=False,
                       # secondary_range=(min_difficulty, max_difficulty) 
    )
    graph.x_labels = height_data
    graph.add('g/s', gps_data)
#    graph.add('diff', difficulty_data, secondary=True)
    return graph

def get_pool_graph(start='0', r='120'):
    parsed = json.loads(urlopen(get_api_url() + '/pool/stats/' + start +','+str(r)+'/gps,height').read().decode('utf-8'))
    gps_data = [float(i['gps']) for i in parsed]
    height_data = sorted(set([int(i['height']) for i in parsed]))
    # create a line graph
    title = 'GrinPool - g/s'
    graph = pygal.Line(width=500, # 1.875
                       height=175, # 340
                       explicit_size=True,
                       style=pool_style_pygal,
                       interpolate='hermite', 
#                       title=title,
                       fill=False,
                       show_dots=False,
                       stroke_style={'width': 2},
                       margin=0,
                       show_legend=False,
                       legend_at_bottom=True,
                       x_label_rotation=1,
                       x_labels_major_count=5,
                       show_minor_x_labels=False,
                       y_labels_major_count=5,
                       show_minor_y_labels=False)
    graph.x_labels = height_data
    print("Len of pool stats: {}".format(len(gps_data)))
    graph.add('GrinPool', gps_data)
    return graph

def pad_worker_graph_data(worker_stats, start, r=120):
    padded_stats = []
    current = start-r
    # Missing from the beginning
    # If its only a few clone the first, else Zero
    while current < int(worker_stats[0]["height"]):
        pad_stat = copy.copy(worker_stats[0])
        pad_stat["height"] = current
        pad_stat["gps"] = 0
        padded_stats.append(pad_stat)
        current += 1
    # Missing from middle
    for stat in worker_stats:
        while int(stat["height"]) > current:
            fill_stat = copy.copy(stat)
            fill_stat["height"] = current
            padded_stats.append(fill_stat)
            current = current + 1
        padded_stats.append(stat)
        current = current + 1
    # Missing from the end
    while len(padded_stats) < r:
        pad_stat = copy.copy(padded_stats[-1])
        pad_stat["height"] = pad_stat["height"] + 1
        padded_stats.append(pad_stat)
    return padded_stats


def get_workers_graph(workers, start='0', r='120'):
    url = get_api_url() + '/worker/stats/' + str(start) +','+str(r)+'/gps,height,worker'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
    height_data = sorted(set([int(i['height']) for i in parsed]))
    print("height data:  {}".format(height_data))

    # create a line graph
    title = 'PoolWorkers - g/s'
    graph = pygal.Line(width=500, # 1.875
                       height=175, # 340
                       explicit_size=True,
                       style=worker_style_pygal,
                       interpolate='cubic', 
#                       title=title,
                       fill=False,
                       show_dots=False,
                       stroke_style={'width': 2},
                       margin=0,
                       show_legend=False,
                       legend_at_bottom=True,
                       x_label_rotation=1,
                       x_labels_major_count=5,
                       show_minor_x_labels=False,
                       y_labels_major_count=5,
                       show_minor_y_labels=False)
    graph.x_labels = height_data

    for miner in workers:
      if miner == "GrinPool":
        continue
      print("miner = {}".format(miner))
      worker_stats = [stat for stat in parsed if stat["worker"] == miner]
      if worker_stats is None:
        continue
      print("Len of worker stats: {}".format(len(worker_stats)))
      padded_worker_stats = pad_worker_graph_data(worker_stats, int(start), int(r))
      if padded_worker_stats is None:
        continue
      print("Len of padded worker stats: {}".format(len(padded_worker_stats)))
      #print("PADDED Miner stats {}".format(padded_worker_stats))
      worker_data = [float(i['gps']) for i in padded_worker_stats]
      graph.add(obfuscate_name(miner), worker_data)

    return graph

def obfuscate_name(name):
    obfname = ''
    for i in range(0, min(18,len(name))):
      if i < 11 or i % 3 != 0:
        obfname += name[i]
      else:
        obfname += '*'
    obfname += '**'
    return obfname

@home_profile.route('/')
def home_template():
    ok = False
    while ok == False:
      try:
        ##
        # Get the data (from the API), structure it, pass it into the jinja2 templated page
        ##

        HEIGHT = 0

        ##
        # GRIN NETWORK
        grin_graph = get_grin_graph() # default is height=0, range=120
        latest = json.loads(requests.get(get_api_url() + "/grin/block").content.decode('utf-8'))
        HEIGHT = latest["height"]
        last_found_ago = int(datetime.utcnow().timestamp()) - int(float(latest["timestamp"]))
        print("last_found_ago = {} - {} = {}".format(last_found_ago, int(datetime.utcnow().timestamp()), int(float(latest["timestamp"]))))
        #ts_latest = datetime.fromtimestamp(float(latest["timestamp"]))
       # print("grin: last_found_ago: {}, ts_latest: {}, now: {}".format(last_found_ago, ts_latest, datetime.utcnow()))
        latest_stats = json.loads(requests.get(get_api_url() + "/grin/stat").content.decode('utf-8'))
        grin = { "gps": round(float(latest_stats["gps"]), 2),
                 "last_block_found": { "found": last_found_ago, "height": latest["height"] },
                 "difficulty": latest_stats["difficulty"],
                 "height": HEIGHT,
                 "rewards": 60,
                 "graph": grin_graph.render_data_uri()
        }
    
        ##
        # POOL
        pool_graph = get_pool_graph() # default is height=0, range=120
        try:
          latest_pool = json.loads(requests.get(get_api_url() + "/pool/block").content.decode('utf-8'))
        except:
          latest_pool = -1
        try:
          last_found_ago = int(datetime.utcnow().timestamp()) - int(float(latest_pool["timestamp"]))
        except:
          last_found_ago = -1
        #ts_latest = datetime.fromtimestamp(float(latest["timestamp"]))
        #print("pool: last_found_ago: {}, ts_latest: {}, now: {}".format(last_found_ago, ts_latest, datetime.utcnow()))
        last_hour_stats = json.loads(requests.get(get_api_url() + "/pool/stats/0,60").content.decode('utf-8'))
        latest_stats = last_hour_stats[-1]
    
        pool = { "gps": round(float(latest_stats["gps"]), 2),
                 "last_block_found": { "found": last_found_ago },
                 "blocks_found": latest_stats["total_blocks_found"],
                 "miner_count": max([s["active_miners"] for s in last_hour_stats]),
                 "graph": pool_graph.render_data_uri()
        }
    
    
        ##
        # TOP WORKERS
        latest_stats = []
        active_miners = []
        r = 60
        active_miners = json.loads(requests.get(get_api_url() + "/worker/stats/{},{}/worker".format(latest["height"], r)).content.decode('utf-8'))
        active_miners = list(set([d['worker'] for d in active_miners]))
        latest_stats = json.loads(requests.get(get_api_url() + "/worker/stats/0,{}".format(r)).content.decode('utf-8'))
        top_workers = []
        workers = []
        #print("Active Miners: {}".format(active_miners))
        #print("latest_stats: {}".format(latest_stats))
        for miner in active_miners:
          print("Miner: {}".format(miner))
          try:
            miner_stats = [stat for stat in latest_stats if stat["worker"] == miner][-1]
            #print("Adding stats for miner: {}, {}".format(miner, miner_stats))
            workers.append(miner_stats["worker"])
            top_workers.append({"name": obfuscate_name(miner_stats["worker"]), "gps": round(miner_stats["gps"], 2)})
          except Exception as e:
           pass
        while len(top_workers) < 5:
          top_workers.append({"name": "None", "gps": 0})
        top_workers.sort(key=lambda s: s["gps"], reverse=True)
        print("Top Workers: {}".format(top_workers))
          
        workers_graph = get_workers_graph(active_miners, HEIGHT) #  get_workers_graph(active_miners) # default is range=120
        
        workers = { "top": top_workers,
                    "graph": workers_graph.render_data_uri()
        }
        ok = True
      except Exception as e:
        print("FAILED - {}".format(e))
        traceback.print_exc(file=sys.stdout)
        time.sleep(1)
        pass
      
    
    


    return render_template('home/home.html', grin=grin, pool=pool, workers=workers)


