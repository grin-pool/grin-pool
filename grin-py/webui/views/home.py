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


from flask import Flask, Blueprint, render_template, request, session, make_response, flash, url_for, redirect
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SelectField, IntegerField
from flask import Flask, Blueprint, render_template, request, session, make_response


home_profile = Blueprint('search_profile'
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
  colors=('#fcef00', '#0f12c1', '#c10e0e', '#0dc110', '#8b0cc1'))

API_URL = 'http://grin-pool.us:13423'

def get_grin_graph(start='0', r='120'):
    url = API_URL + '/grin/stats/' + start +','+r+'/gps,height'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
    data = [float(i['gps']) for i in parsed]
    # create a bar chart
    title = 'Grin Network - g/s'
    graph = pygal.Line(width=600, height=200, style=grin_style_pygal, interpolate='cubic', 
                       explicit_size=True, title=title, fill=False, show_dots=False,
                       stroke_style={'width': 2}, margin=0, show_legend=False)
    graph.add('G/s', data)
    return graph

def get_pool_graph(start='0', r='120'):
    parsed = json.loads(urlopen(API_URL + '/pool/stats/' + start +','+r+'/gps,height').read().decode('utf-8'))
    data = [float(i['gps']) for i in parsed]
    # create a bar chart
    title = 'GrinPool - g/s'
    graph = pygal.Line(width=600, height=575, style=pool_style_pygal, interpolate='cubic', 
                       explicit_size=True, title=title, fill=False, show_dots=False,
                       stroke_style={'width': 2}, margin=0, show_legend=True, legend_at_bottom=True)
    graph.add('GrinPool', data)
    return graph

# Fix this by using a timestamp for x axis?
def pad_worker_graph_data(worker_stats, start, r=120):
    padded_stats = []
    current = start-r
    previous_stat = worker_stats[0]
    #previous_stat["gps"] = 0
    for stat in worker_stats:
        while int(stat["height"]) > current:
            padded_stats.append(previous_stat)
            current = current + 1
        padded_stats.append(stat)
        previous_stat = stat
        current = current + 1
    while len(padded_stats) < r:
        padded_stats.append(padded_stats[-1])
    return padded_stats

def get_workers_graph(graph, workers, start='0', r='120'):
    url = API_URL + '/worker/stats/' + str(start) +','+r+'/gps,height,worker'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
    
    for miner in workers:
      if miner == "GrinPool":
        continue
      print("miner = {}".format(miner))
      worker_stats = [stat for stat in parsed if stat["worker"] == miner]
      #print("Miner stats {}".format(worker_stats))
      padded_worker_stats = pad_worker_graph_data(worker_stats, int(start), int(r))
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
        latest = json.loads(requests.get(API_URL + "/grin/block").content.decode('utf-8'))
        HEIGHT = latest["height"]
        last_found_ago = int(datetime.utcnow().timestamp()) - int(float(latest["timestamp"]))
        #ts_latest = datetime.fromtimestamp(float(latest["timestamp"]))
       # print("grin: last_found_ago: {}, ts_latest: {}, now: {}".format(last_found_ago, ts_latest, datetime.utcnow()))
        latest_stats = json.loads(requests.get(API_URL + "/grin/stat").content.decode('utf-8'))
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
        latest = json.loads(requests.get(API_URL + "/pool/block").content.decode('utf-8'))
        last_found_ago = int(datetime.utcnow().timestamp()) - int(float(latest["timestamp"]))
        #ts_latest = datetime.fromtimestamp(float(latest["timestamp"]))
       # print("pool: last_found_ago: {}, ts_latest: {}, now: {}".format(last_found_ago, ts_latest, datetime.utcnow()))
        latest_stats = json.loads(requests.get(API_URL + "/pool/stats/0,3").content.decode('utf-8'))[-1]
        active_miners = json.loads(requests.get(API_URL + "/worker/stats/{},25/worker".format(latest["height"])).content.decode('utf-8'))
        active_miners = list(set([d['worker'] for d in active_miners]))
    
        pool = { "gps": round(float(latest_stats["gps"]), 2),
                 "last_block_found": { "found": last_found_ago },
                 "blocks_found": latest_stats["total_blocks_found"],
                 "miner_count": len(active_miners),
                 "graph": pool_graph.render_data_uri()
        }
    
    
        ##
        # TOP WORKERS
        latest_stats = json.loads(requests.get(API_URL + "/worker/stats/0,25").content.decode('utf-8'))
        active_miners = json.loads(requests.get(API_URL + "/worker/stats/{},15/worker".format(latest["height"])).content.decode('utf-8'))
        active_miners = list(set([d['worker'] for d in active_miners]))
        top_workers = []
        workers = []
        #print("Active Miners: {}".format(active_miners))
        #print("latest_stats: {}".format(latest_stats))
        for miner in active_miners:
          miner_stats = [stat for stat in latest_stats if stat["worker"] == miner][-1]
          #print("Adding stats for miner: {}, {}".format(miner, miner_stats))
          workers.append(miner_stats["worker"])
          top_workers.append({"name": obfuscate_name(miner_stats["worker"]), "gps": round(miner_stats["gps"], 2)})
        while len(top_workers) < 5:
          top_workers.append({"name": "None", "gps": 0})
        top_workers.sort(key=lambda s: s["gps"], reverse=True)
        print("Top Workers: {}".format(top_workers))
          
        workers_graph = get_workers_graph(pool_graph, active_miners, HEIGHT) # default is range=120
        graph = workers_graph.render_data_uri()
        
    
        workers = { "top": top_workers,
                    "graph": graph


        }
        ok = True
      except Exception as e:
        print("FAILED - {}".format(e))
        time.sleep(1)
        pass
      
    
    


    return render_template('home/home.html', grin=grin, pool=pool, workers=workers)


