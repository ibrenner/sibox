# -*- coding: utf-8 -*-
'''
Interface with a Junos device via proxy-minion. To connect to a junos device \
via junos proxy, specify the host information in the pillar in '/srv/pillar/details.sls'

.. code-block:: yaml

    proxy:
      proxytype: junos
      host: <ip or dns name of host>
      username: <username>
      port: 830
      password: <secret>

In '/srv/pillar/top.sls' map the device details with the proxy name.

.. code-block:: yaml

    base:
      'vmx':
        - details

After storing the device information in the pillar, configure the proxy \
in '/etc/salt/proxy'

.. code-block:: yaml

    master: <ip or hostname of salt-master>

Run the salt proxy via the following command:

.. code-block:: bash

    salt-proxy --proxyid=vmx


'''
from __future__ import absolute_import

# Import python libs
import logging

# Import 3rd-party libs
try:
    HAS_INFINISDK = True
    from infinisdk import InfiniBox
except ImportError:
    HAS_INFINISDK = False

__proxyenabled__ = ['sibox']

thisproxy = {}

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'sibox'


def __virtual__():
    '''
    Only return if all the modules are available
    '''
    if not HAS_INFINISDK:
        return False, 'Missing dependency: The infinibox proxy minion requires the \'infinisdk\' Python module.'

    return __virtualname__


def init(opts):
    '''
    Open the connection to the ibox device, login, and bind to the
    Resource class
    '''
    opts['multiprocessing'] = False
    log.debug('Opening connection to ibox')

    args = {"host": opts['proxy']['host'],"user": opts['proxy']['username'],"password":opts['proxy']['password']}
#    optional_args = ['user',
#                     'username',
#                     'password',
#                     'passwd'
#                     ]
#
#    if 'username' in opts['proxy'].keys():
#        opts['proxy']['user'] = opts['proxy'].pop('username')
#    proxy_keys = opts['proxy'].keys()
#    for arg in optional_args:
#        if arg in proxy_keys:
#            args[arg] = opts['proxy'][arg]

    
    thisproxy['conn'] = InfiniBox(args["host"], auth=(args["user"], str(args["password"])))
    thisproxy['conn'].login()
    thisproxy['initialized'] = True


def initialized():
    return thisproxy.get('initialized', False)


def conn():
    return thisproxy['conn']


def proxytype():
    '''
    Returns the name of this proxy
    '''
    return 'sibox'


def ping():
    '''
    Ping?  Pong!
    '''
    thisproxy['ping'] = thisproxy['conn'].api.get('system/product_id')
    if thisproxy['ping'].get_result() == 'INFINIBOX':
	    return thisproxy['ping']


def shutdown(opts):
    '''
    This is called when the proxy-minion is exiting to make sure the
    connection to the device is closed cleanly.
    '''
    log.debug('Proxy module {0} shutting down!!'.format(opts['id']))
    try:
        thisproxy['conn'].close()

    except Exception:
        pass
