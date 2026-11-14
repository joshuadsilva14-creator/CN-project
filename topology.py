import subprocess

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel


class ServiceDiscoveryTopology(Topo):
    def build(self):
        hosts = []

        for i in range(1, 8):
            host = self.addHost(
                "h" + str(i),
                ip="10.0.0." + str(i) + "/24"
            )
            hosts.append(host)

        switch = self.addSwitch(
            "s1",
            protocols="OpenFlow13",
            failMode="standalone"
        )

        for host in hosts:
            self.addLink(host, switch)


def create_topology():
    topo = ServiceDiscoveryTopology()

    net = Mininet(
        topo=topo,
        controller=None,
        switch=OVSSwitch,
        autoSetMacs=True,
        autoStaticArp=True
    )

    net.start()

    # Give the host-side switch bridge an IP so h1 can reach the
    # Python controller process running in the Ubuntu host namespace.
    subprocess.run(
        ["ip", "addr", "replace", "10.0.0.100/24", "dev", "s1"],
        check=True
    )

    print("Service Discovery Network Started")
    print("Hosts: h1-h7 | Switch: s1 | Controller host IP: 10.0.0.100")

    try:
        CLI(net)
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()
