# Salt module for Infinidat IBOX
Module for Salt, to retrieve, control and update configuration of infinibox machines.

## Salt basics
If you're just starting with salt check out this [document](https://docs.saltstack.com/en/latest/topics/tutorials/walkthrough.html) for a brief introduction to get up to speed on the basics.

## Prerequisites 
the module requires that you have:
* [InfiniSDK](https://infinisdk.readthedocs.io/en/latest/) installed on your master and minion 
* latest salt-proxy module version (currently 2017.7.2)

## Install sibox
copy each of the sibox.py files to their relevant directories according to the directory structure listed here.
It usually should be in:
```
/srv/salt/_modules/sibox.py
/srv/salt/_proxy/sibox.py
```
verify the location at your [`FILE_ROOTS`](https://docs.saltstack.com/en/latest/ref/configuration/master.html#file-roots)

## Configure salt proxy
The main configuration file needed to make Salt run as proxy-master is located at `/etc/salt/proxy`. 
This file should already exist, though you may need to create it.

Here we tell the proxy process that the local machine is the salt-master. make sure you have the following in your proxy file:
```
master: localhost
```
Additionally, you may want to edit the `/etc/salt/minion` file to point the master location to itself.

## Configure the connection with an IBOX machine
The `master` config file is expecting pillar to be in `/srv/pillar`, if this directory doesn't exist, make sure to create it:
```
mkdir -p /srv/pillar
```
Next, we need to create a `top.sls` file in that directory, which tells the salt-master which minions receive which pillar. Create and edit the `/srv/pillar/top.sls` file and make it look like this:

```
base:
  ibox01:
    - ibox01
```
 where:
* ibox01 is the name used to interact with the device: `salt 'ibox01' sibox.ping`
* `/srv/pillar/ibox01.sls` is the file containing the specifications of this device

**Pay attention** to this structure: Notice that the `- ibox01` portion of the `top.sls` file is missing the `.sls` extension, even though this line is expecting to see a file in the same directory called `ibox01.sls`. In addtion, note that there should not be any dots used when referencing the `.sls` file, as this will be interpreted as a directory structure. For example, if you had the line configured as `- ibox01.pillar`, salt would look in the `/srv/pillar` directory for a folder called `ibox01`, and then for a file in that directory called `pillar.sls`. 

Now that we've referenced the `ibox01` file, we need to create it and add the pillar. Create and edit the `/srv/pillar/ibox01.sls` file and add the following:
```
proxy:
  proxytype: sibox
  host: [HOSTNAME]
  username: [USERNAME]
  password: [PASSWORD]
```
* HOSTNAME, USERNAME, PASSWORD are the connection details

Example `/srv/pillar/ibox01.sls`:
```
proxy:
    proxytype: sibox
    host: 192.168.0.10
    username: saltadm
    password: 123456
```
## Start salt services
```
systemctl start salt-master
systemctl restart salt-minion
```

## Start the proxy minion for your device
Start with testing proxy minion:
`sudo salt-proxy --proxyid=[DEVICE_ID] -l debug`
On the first connection attempt you will find that the minion cannot connect and is stuck with the following error message:
```
[ERROR   ] The Salt Master has cached the public key for this node, this salt minion will wait for 10 seconds before attempting to re-authenticate
[INFO    ] Waiting 10 seconds before retry.
```

This is normal and is due to the fact that the salt key from the minion have not been accepted yet by the master. Stop the minion process with <kbd>CTRL</kbd>+<kbd>C</kbd> and run `sudo salt-key`. Under `Unaccepted Keys`: you should see your [DEVICE_ID]. Accept the key with `sudo salt-key -a [DEVICE_ID]`. Now rerun the minion debug and you should see the minion connecting to your device.

## Test your configuration

Once the key has been accepted, restart the proxy in debug mode. Issue the following command:

`sudo salt ibox01 sibox.ping`
output:
```
ibox01:
    INFINIBOX
```
It should return `INFINIBOX` if there are no problems. If everything checks out, hit <kbd>CTRL</kbd>+<kbd>C</kbd> and restart salt-proxy as a daemon:
``` sudo salt-proxy --proxyid=[DEVICE_ID] -d```

## Start using Salt
Now that everything is set up, you can start issuing commands to get/set the relevant entities in the system.

Syntax:
`salt [DEVICE ID] [FUNCTION]`

the following table summerises the current commands we have with the sibox module:

| **command name** | **command details** |
| ------------ | --------------- |
| ping | checks connectivity |
| volcount | show amount of volumes in the system |
| get_volume [volume_name] | Get volume details |
| get_pool [pool_name] | Get pool details |
| get_host [host_name] | Get host details |
| create_volume [pool_name] [volume_name] [size_in_gb] | creates a volume |
| map_volume [host_name] [vol_name] | map a volume to a host |
| unmap_volume [hostname] [vol_name] | unmap a volume from a host |
| add_host [cluster_name] [hostname] | add a host to a cluster |
| remove_host [cluster_name] [hostname] | remove a host from a cluster |

### A few examples
volume creation example:

![Output Image #1 ](https://git.infinidat.com/ibrenner/infinisalt/raw/master/Screen%20Shot%202017-10-29%20at%2017.21.09.png)

Removing a host from a cluster:

![Output Image #2 ](https://git.infinidat.com/ibrenner/infinisalt/raw/master/Screen%20Shot%202017-10-29%20at%2017.26.00.png)






