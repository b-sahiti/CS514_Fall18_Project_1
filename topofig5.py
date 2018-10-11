#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
import re
import numpy
import matplotlib.pyplot as plt
import math
import os


class customTopo(Topo):

	def __init__(self, bandwidth, loss, queue):
 		Topo.__init__(self)

		host1 = self.addHost('h1', cpu = 0.5)
		host2 = self.addHost('h2', cpu= 0.5)
		switch =self.addSwitch('s1')
		
		self.addLink( host1, switch, bw=bandwidth, delay='15ms', loss=loss,max_queue_size=queue, use_htb=True)
		self.addLink( host2, switch, bw=bandwidth, delay='15ms', loss=loss,max_queue_size=queue, use_htb=True)
		


def perfTest(bandwidth, loss, queue):
	"Create network and run simple performance test"
	topo = customTopo(bandwidth, loss, queue)
	net = Mininet(topo=topo, link=TCLink)
	net.start()
	
	h1, h2 = net.get('h1', 'h2')	
	h1.cmd('ping -c 15 %s' %h2.IP())
	h2.cmd('ping -c 15 %s' %h1.IP())
	
	#print "RTT between h1 and h2"
	f = open('output_fig5.txt', 'a')	
	
	h1rtt=h1.cmd('ping -c 100 %s' %h2.IP())
	match=re.search('time=([\d.]+)(\w+)',h1rtt)
	if match is not None:
		rtt1=str(match.group(1)+match.group(2))
	else:
		rtt1=0
	f.write(", {}".format(rtt1))
	
	#print "RTT between h2 and h1"
	h2rtt=h2.cmd('ping -c 100 %s' %h1.IP())
	match=re.search('time=([\d.]+)(\w+)',h2rtt)
	if match is not None:
		rtt2=str(match.group(1)+match.group(2))
	else:
		rtt2=0
	f.write(", {}, ".format(rtt2))
		
	bandwidth = net.iperf((h1,h2),fmt='-M 1074 -f M')
	f.write(str(bandwidth))
	bw1=bandwidth[0].split()
	b1=bw1[0]
	bw2=bandwidth[1].split()
	b2=bw2[0]
	cwnd=((float(rtt1)*float(b1)*1000)+(float(rtt2)*float(b2)*1000))/2
	cwnd=float(cwnd/1024)
	f.close()
	net.stop()
	return cwnd

if __name__ == '__main__':
	setLogLevel('error')
	os.system("sysctl -w net.ipv4.tcp_congestion_control=reno")
	
	bandwidth=[10,9,8]
	queue = [30,20]
	
	loss=numpy.logspace(-1.5,0.69,num=30,base=10.0)
	
	x=[]
	y=[]
	c=[]
	count=1 
	for q in queue:	
		for b in bandwidth:
			for l in loss:
				f=open('output_fig5.txt', 'a')
				print("============================ count = {}, loss={}".format(count,l))				
				f.write("\n  {}, ".format(q))
				f.write(" {}".format(l))
				f.close()
				cwnd=perfTest(b, l, q)
				x.append(l)
				y.append(cwnd)
				count+=1
				
				
	f=open('output_fig5_plot_values.txt', 'a')	
	for i in range(0,len(x),1):
		print("{loss},{cwnd}".format(loss=x[i],cwnd=y[i]))
		f.write("\n {loss} , {cwnd}".format(loss=x[i],cwnd=y[i]))
	f.close()

	x1=numpy.log(x)
	y1=numpy.log(y)

	slope,intercept=numpy.polyfit(x1,y1,1)
	
	for x2 in x1:
		c.append(math.exp(slope*x2+intercept))
	
	plt.plot(x,y,'o',x,c,'--')
	plt.xlabel('Loss(p)')
	plt.ylabel('BW*RTT/MSS')
	plt.title('Fig 6: Estimated Window vs Loss')
	plt.yscale('log')
	plt.xscale('log')
	plt.savefig('output_fig5.pdf')
	plt.show()
	

	
	

	

	
