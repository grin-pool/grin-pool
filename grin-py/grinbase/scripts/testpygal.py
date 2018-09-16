#!/usr/bin/env python3
import pygal
import json
import sys
import traceback 
from urllib.request import urlopen # python 3 syntax
 
 
from flask import Flask
from pygal.style import DarkSolarizedStyle
 
app = Flask(__name__)
 
#----------------------------------------------------------------------
@app.route('/')
def get_weather_data(start='0', r='120'):
    url = 'http://grin-pool.us:13423/grin/stats/' + start +','+r+'/gps,height'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
 
    imp_temps = [float(i['gps']) for i in parsed]
    times = ['%s' % (i['height']) for i in parsed]
 
    # create a bar chart
    title = 'GPS'
    #bar_chart = pygal.Bar(width=1200, height=600,
    #                      explicit_size=True, title=title, style=DarkSolarizedStyle)
    bar_chart = pygal.Line(width=1200, height=600,
                          explicit_size=True, title=title, fill=False, show_dots=False)
 
#    bar_chart.x_labels = times
    print("Num grin stats: {}".format(len(imp_temps)))
    bar_chart.add('Grin GPS', imp_temps)

    # --------
    start_height = int(times[0])

    # --------
  
    url = 'http://grin-pool.us:13423/pool/stats/' + start +','+r+'/gps,height'
    result = urlopen(url)
    js_string = result.read().decode('utf-8')
    parsed = json.loads(js_string)
    imp_temps = [float(i['gps']) for i in parsed]
    print("Num pool stats: {}".format(len(imp_temps)))
    bar_chart.add('Pool GPS', imp_temps)

    # --------

    try:
        url = 'http://grin-pool.us:13423/worker/stats/' + start +','+r+'/worker,gps,height'
        result = urlopen(url)
        js_string = result.read().decode('utf-8')
        parsed = json.loads(js_string)
        workers = list(set(['%s' % (i['worker']) for i in parsed]))
        for worker in workers:
            try:
                worker_parsed = []
                for i in parsed:
                    if i["worker"] == worker:
                        worker_parsed.append(i)
                # Fill in missing records
                for i in range(int(start), int(r)-1):
                    if i+start_height != int(worker_parsed[i]["height"]):
                        x = worker_parsed[i]
                        x["gps"] = 0
                        worker_parsed.insert(i, x)
                imp_temps = [float(i['gps']) for i in worker_parsed]
                print("Num worker stats for {}: {}".format(worker,len(imp_temps)))
                bar_chart.add(str(worker), imp_temps)
            except Exception as e:
                print("Something went wrong: {}\n{}".format(e, traceback.format_exc().splitlines()))

    except Exception as e:
        print("Failed to get worker graph stats: {}".format(sys.exc_info()[0]))
        print("Something went wrong: {}\n{}".format(e, traceback.format_exc().splitlines()))

 
 
    html = """
        <html>
             <head>
                  <title>%s</title>
             </head>
              <body>
                 %s
             </body>
        </html>
        """ % (title, bar_chart.render())
    return html
 
 
#----------------------------------------------------------------------
if __name__ == '__main__':    
    app.run(host='0.0.0.0', port=13424)
