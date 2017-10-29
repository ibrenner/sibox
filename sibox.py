# -*- coding: utf-8 -*-
'''
Module to interact with Ibox devices.

'''
from __future__ import absolute_import

# Import python libraries
import logging
import json
import os


# Infinisdk interface libraries
try:
    from infinisdk import InfiniBox   
    from capacity import GiB
    HAS_INFINISDK = True
except ImportError:
    HAS_INFINISDK = False

# Import salt libraries
import salt.utils 

# Set up logging
log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'sibox'

__proxyenabled__ = ['sibox']


def __virtual__():
    '''
    We need the ibox adapter libraries for this
    module to work.  We also need a proxymodule entry in __opts__
    in the opts dictionary
    '''
    if HAS_INFINISDK and 'proxy' in __opts__:
        return __virtualname__
    else:
        return (False, 'The ibox module could not be loaded: '
                       'infinisdk  or proxy could not be loaded.')



def ping():
    '''
    Ping?  Pong!
    '''
    conn = __proxy__['sibox.conn']()
    response = conn.api.get('system/product_id')
    if response.get_result() == 'INFINIBOX':
        return response.get_result()


def volcount():
	'''
	show amount of volumes in the system
	Usage:
	.. code-block:: bash
	salt 'ibox_name' sibox.volcount
	'''
	conn = __proxy__['sibox.conn']()	
	return conn.volumes.count()

def get_volume(volname):
	'''
	get a single volume details
	Usage:
	..code-block:: bash
	salt 'ibox_name' sibox.get_volume 'volume_name'
	'''
	conn = __proxy__['sibox.conn']()
	res = conn.volumes.get(name=volname)
	return res.__dict__['_cache']

def get_pool(poolname):
	'''
        get a single pool details
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.get_pool 'pool_name'
        '''
	conn = __proxy__['sibox.conn']()
	res = conn.pools.get(name=poolname)
	return res.__dict__['_cache']

def get_host(hostname):
	'''
        get a single host details
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.get_host 'host_name'
        '''
        conn = __proxy__['sibox.conn']()
        res = conn.hosts.get(name=hostname)
        return res.__dict__['_cache']

def create_volume(poolname, volname, size):
	'''
        create a volume 
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.create_volume 'pool_name' 'vol_name' 'size in GiB'
        '''
	conn = __proxy__['sibox.conn']()
	poolvar = conn.pools.get(name=poolname)
	res = conn.volumes.create(pool=poolvar, name=volname, size=size*GiB)
	return res.__dict__['_cache']

def map_volume(hostname, volname):
	'''
        map a volume to a host
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.map_volume 'host_name' 'volume_name'
        '''
	conn = __proxy__['sibox.conn']()
	host = conn.hosts.get(name=hostname)
	vol = conn.volumes.get(name=volname)
	res = host.map_volume(vol)
	return res.lun

def unmap_volume(hostname, volname):
        '''
        unmap a volume from a host
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.unmap_volume 'host_name' 'volume_name'
        '''
        conn = __proxy__['sibox.conn']()
        host = conn.hosts.get(name=hostname)
        vol = conn.volumes.get(name=volname)
        res = host.unmap_volume(vol)
        return "volume unmapped"

def add_host(clustername, hostname):
	'''
        add host to cluster
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.add_host 'cluster_name' 'host_name' 
        '''
	conn = __proxy__['sibox.conn']()
	host = conn.hosts.get(name=hostname)
	cluster = conn.host_clusters.get(name=clustername)
	add = cluster.add_host(host)
	res = conn.host_clusters.get(name=clustername)
	return res.__dict__['_cache']
	#res = cluster.get_hosts()

def remove_host(clustername, hostname):
	'''
        remove host from a cluster
        Usage:
        ..code-block:: bash
        salt 'ibox_name' sibox.remove_host 'cluster_name' 'host_name'
        '''
        conn = __proxy__['sibox.conn']()
        host = conn.hosts.get(name=hostname)
        cluster = conn.host_clusters.get(name=clustername)
        add = cluster.remove_host(host)
        res = conn.host_clusters.get(name=clustername)
	return res.__dict__['_cache']
