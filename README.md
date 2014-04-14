# Network Search
Network search makes operational data available in real-time to management applications. In contrast to traditional monitoring, neither the data location nor the data format needs to be known to the invoking process, which simplifies application development, but requires an efficient search plane inside the managed system. The search plane is realized as a network of search nodes that process search queries in a distributed fashion. This presentation focuses on the design of a search node, which maintains a real-time database of operational information and allows for parallel processing of search queries.

### How to install
##### Requirement
* Python 2.7
* MongoDB
* ZeroMQ 3.2.4


1. Move NetworkSeach dir to /opt
```
cp -rf NetworkSeach /opt
```
2. Install dependency
```
#if you use ubuntu
./install-ubuntu
#if you use Centos
./install-centos
```

## License
