## ALL RIGHTS RESERVED.
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## Neither the name of the SONATA-NFV, 5GTANGO [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote
## products derived from this software without specific prior written
## permission.
##
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the SONATA
## partner consortium (www.sonata-nfv.eu).
##
## This work has been performed in the framework of the 5GTANGO project,
## funded by the European Commission under Grant number 761493 through
## the Horizon 2020 and 5G-PPP programmes. The authors would like to
## acknowledge the contributions of their colleagues of the 5GTANGO
## partner consortium (www.5gtango.eu).
# encoding: utf-8


import urllib2, time, logging
import json, os, subprocess
from threading import  Thread
from VmData import vmdt
from DtFiltering import valdt 
from configure import configuration
from logging.handlers import RotatingFileHandler


def init():
    global prometh_server
    global node_name
    global interval
    global logger
    global vm_id
       
    #read configuration
    interval=3
    conf = configuration("/opt/Monitoring/node.conf")
    node_name = os.getenv('NODE_NAME', conf.ConfigSectionMap("vm_node")['node_name'])
    prometh_server = os.getenv('PROM_SRV', conf.ConfigSectionMap("Prometheus")['server_url'])
    interval = conf.ConfigSectionMap("vm_node")['post_freq']
    if is_json(prometh_server):
        prometh_server = json.loads(prometh_server)
    else:
        prometh_server = [prometh_server]
    logger = logging.getLogger('dataCollector')
    #hdlr = logging.FileHandler('dataCollector.log', mode='w')
    hdlr = RotatingFileHandler('dataCollector.log', maxBytes=10000, backupCount=1)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.WARNING)
    logger.setLevel(logging.INFO)
    #vm_id = getMetaData()
    vm_id = getUUID()
    if vm_id == None:
        vm_id = node_name
    node_name +=":"+vm_id
    print vm_id
    logger.info('SP Data Collector')
    logger.info('Promth P/W Server '+json.dumps(prometh_server))
    logger.info('Monitoring Node '+node_name)
    logger.info('Monitoring time interval '+interval)

def postNode(node_,type_, data_,server_):
    url = server_+"/job/"+type_+"/instance/"+node_
    logger.info('Post on: \n'+url)
    #logger.info('Post ports metrics: \n'+data_)
    try: 
        req = urllib2.Request(url)
        req.add_header('Content-Type','text/html')
        req.get_method = lambda: 'PUT'
        response=urllib2.urlopen(req,data_, timeout = 10)
        code = response.code
        logger.info('Response Code: '+str(code))      
    except urllib2.HTTPError, e:
        logger.warning('Error: '+str(e))
    except urllib2.URLError, e:
        logger.warning('Error: '+str(e))
    except:
        logger.warning('Generic Error on postNode function')
        pass

def getUUID():
    path = '/usr/sbin/dmidecode | grep UUID'
    print(os.path.isdir("/rootfs"))
    if (os.path.isdir("/rootfs")):
        path = '/rootfs'+path
    p = subprocess.Popen(path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = p.stdout.readlines()
    try:
        for line in lines:
            if 'UUID' in line:
                ar = line.split(" ")
                return ar[1].strip().lower()
    except:
        logger.warning('Error on retrieving UUID')
        return None
        pass

def getMetaData():
    try:
        url = 'http://169.254.169.254/openstack/latest/meta_data.json'
        req = urllib2.Request(url)
        req.add_header('Content-Type','application/json')
        
        response=urllib2.urlopen(req, timeout = 180)
        code = response.code
        data = json.loads(response.read())
        #print json.dumps(data)
        return data["uuid"]
    
    except urllib2.HTTPError, e:
        logger.warning('Error: '+str(e))
        pass
    except urllib2.URLError, e:
        logger.warning('Error: '+str(e))
        pass
    except:
        logger.warning('Generic Error on getMetaData function')
        pass

def collectVM(id_):
    global vm_dt
    vm_dt = ''
    lsval={}
    while 1:
        dt_collector = vmdt(id_,lsval)
        lsval = dt_collector.getCurrentDT()
        vm_dt = dt_collector.prom_parser()
        time.sleep(1)

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  except ValueError, e:
    return False
  return True


if __name__ == "__main__":
    init()
    t1 = Thread(target = collectVM, args=(vm_id,))
    t1.daemon = True
    t1.start()
    
    
    while 1:
        time.sleep(float(interval))
        #print vm_dt
        for url in prometh_server:
            postNode(node_name,"vnf",vm_dt,url)

