# Background
Network search makes operational data available in real-time to management applications. In contrast to traditional monitoring, neither the data location nor the data format needs to be known to the invoking process, which simplifies application development, but requires an efficient search plane inside the managed system. The search plane is realized as a network of search nodes that process search queries in a peer to peer fashion fashion. Each search node maintains a real-time database of operational information and allows for parallel processing of search queries. This project provides the code that runs in a search node. 

### Directory Structure of the Codes

The top directory (NetworkSearch) includes a subdirectory (NetworkSearch2) that contains the source codes to implement a network search prototype and scripts to manage (install, clean up the logs, start/stop/restart a search node) the prototype. 

NetworkSearch2 folder includes source codes and some configuration files. The configuration file includes: (i) config.cfg, which is used to configure a search node, e.g., peers of a search node, etc., and (ii) to configure caching protocol to compute distances from the peers. 

The source codes are primarily organized in five sub-categories:

1. web --> includes modules that realizes a restful api for network search and a GUI that uses the API
2. interfaces --> includes modules that realizes a search interface to management applications
2. interpreter --> includes modules that tokenizes, parses, and translates a query
3. QuerySubsystem --> includes modules that realizes the search query processing based on the echo protocol
4. IndexingSubsystem --> include modules that realizes indexing of search object that are in the real-time search database
4. SensorSubsystem --> include modules that collects and formats raw data and populates the search database with the formatted data 

A key module that resides outside the above subdirectories is 'manager.py' and responsible for managing the QuerySubsystem to run multiple threads for concurrent query processing, queueing, logging, etc. 

### Installation
##### Required libraries
Python 2.7, MongoDB > 2.4, ZeroMQ 3.2.4

##### Required Python modules 
bottle 0.12.5, distribute 0.7.3, tornado 3.2, pymongo 2.7, pyzmq 14.1.1

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
### Configuration

Edit NetworkSearch2/config.cfg as follows (<val> indicates sample parameter)

```
[Interface]
interface_port = 2061
# input the unique number in all search nodes
start_qid = <1>

[Echo_protocol]
# input neighbors IP or hostname with ,
neighbor_list = <10.10.10.10>, <20.20.20.20> 
# input your host ip
hostname = <30.30.30.30>
n_process = <1>
```

### Run

Start Network Search
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

### Debug

Process that has to run

manager.py, indexManager.py, sensorManager.py, web_server.py, mongodb

NetworkSearch2/NetworkSearch2.log  (query processing)
NetworkSearch2/SensorSubsystem/SensorManager2.log (Data Handling)
NetworkSearch2/IndexingSubsystem/IndexManager.log (Indexing)
nohup.log (restful API)


## License


## Copyright
@LCN
