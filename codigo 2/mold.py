from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


def topology():

    net = Mininet(
        link=TCLink
    )

    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.2.3/24')
    h4 = net.addHost('h4', ip='10.0.2.4/24')
    h5 = net.addHost('h5', ip='10.0.2.5/24')

    s1 = net.addSwitch('s1', failMode='standalone')
    s2 = net.addSwitch('s2', failMode='standalone')

    net.addLink(
        h1, s1,
        bw=10,
        delay='20ms',
        loss=1
    )

    net.addLink(
        h2, s1,
        bw=5,
        delay='50ms',
        loss=3
    )

    net.addLink(
        h2, s2,
        bw=5,
        delay='50ms',
        loss=3
    )

    net.addLink(
        h3, s2,
        bw=2,
        delay='100ms',
        loss=5
    )

    net.addLink(
        h4, s2,
        bw=2,
        delay='200ms',
        loss=5
    )

    net.addLink(
        h5, s2,
        bw=2,
        delay='140ms',
        loss=5
    )

    net.start()
# ===========================================================
    h2.cmd(
        'ifconfig h2-eth1 10.0.2.1 netmask 255.255.255.0'
    )

    h2.cmd(
        'sysctl -w net.ipv4.ip_forward=1'
    )

    h3.cmd(
        'route add default gw 10.0.2.1'
    )

    h4.cmd(
        'route add default gw 10.0.2.1'
    )

    h5.cmd(
        'route add default gw 10.0.2.1'
    )
    h1.cmd(
        'route add -net 10.0.2.0 netmask 255.255.255.0 gw 10.0.0.2'
    )
# =========================================================
    CLI(net)

    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
