# UDP Based Service Discovery System
## 1.Project Overview
This is implemented using python mininet and open vSwitch (OVS)
It is done by communication with broker using Open vSwitch
## 2.Objective
Implement dynamic traffic blocking and unblocking using open flow rules
Measure service and latency
## 3.Technology used
Python
UDP Socket Programming
Mininet
Open vSwitch (OVS)
Ubuntu
OpenFlow 1.3
## 4.System Architecture
Consist of 7 mininet host h1-h7
h1 is broker
h2->h6 is worker that provide services
h7 is client
## 5.Available service
Calculator (h2): Perform basic operation
Messaging (h3): Recive and return message
File Information (h4):Provide file details
Network monitor: Gives Basic network information
Time Service: Provide Date and time
## 6.Working Principle
Worker register service with UDP
worker sent periodic message saying it is active(heartbeat) and broker remove service when heartbeat stops
Client request for service
Client communicate to worker through broker
It uses Openflow rules
## 7.Project Structure
```text
broker.py
worker.py
client.py
simple_controller.py
topology.py
README.md
```
## 8.Installation and Execution
Install dependancy
```bash
sudo apt update
sudo apt install -y mininet openvswitch-switch xterm python3
```
start openswitch
```bash
sudo service openvswitch-switch start
```
start mininet 
```bash
sudo mc -c
sudo python3 topology.py
```
```bash
sudo python3 simple_controller.py
```
open host terminal in mininet
```bash
xterm h1 h2 h3 h4 h5 h6 h7
```
run the program in the host
h1
python3 broker.py
h2
python3 worker.py calculator 6001
h3
python3 worker.py messaging 6002
h4
python3 worker.py file_info 6003
h5
python3 worker.py network_monitor 6004
h6
python3 worker.py time_service 6005
h7
python3 client.py
## 9.Testing and Performance
It tested:
Regestery and discovery of service
Successful communication
Dynamic traffic blocking and unblocking
Service recovery after worker start
Open flow rules can be inspected by using
```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```
## 10.Limitation
Designed only for local deployment
UDP dosen't guarentee delivary

## Conclusion
THE Project combine UDP Socket programming and SDN to provide dynamic service discovery,failure detection and network traffic control  
