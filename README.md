Network search makes operational data available in real-time to management applications. In contrast to traditional monitoring, neither the data location nor the data format needs to be known to the invoking process, which simplifies application development, but requires an efficient search plane inside the managed system. The search plane is realized as a network of search nodes that process search queries in a decentralized fashion. Each search node maintains a real-time database of configuration and operational information and allows for parallel processing of search queries. 

### How to install
##### Required libraries
* Python 2.7
* MongoDB > 2.4 
* ZeroMQ 3.2.4

##### Required Python modules 
* bottle 0.12.5
* distribute 0.7.3
* tornado 3.2
* pymongo 2.7
* pyzmq 14.1.1


1 Move NetworkSeach dir to /opt
```
cp -rf NetworkSeach /opt
```
2 Install dependency
```
#You need to execute follow as root user
#if you use ubuntu
./install-ubuntu
#if you use Centos
./install-centos
```
3 Configure NetworkSearch2/config.cfg

```
[Interface]
interface_port = 2061
# input the unique number in all search nodes
start_qid = 1


[Echo_protocol]
# input neighbors IP or hostname with ,
neighbor_list = 
# input your host ip
hostname = localhost
message_list_capped = 10000
n_process = 1
capped_return = 100
```

4 Start Network Search
```
./opt/NetworkSearch/start_network_search
```
Stop Network Search
```
./opt/NetworkSearch/stop_network_search
```
Restart Network Search
```
./opt/NetworkSearch/reset_ns
```

You can access http://localhost:8080/

## License
