import networkx as nx 
import time
from generate_network import Social_Net
from spread import Spread_Net

#graphs x runs will be the number of simulations. And the results will be on the average of those
graphs = 5
runs = 10
#number of days each simulation will run for
ndays = 240
#number of nodes in the network
N = 10000

avgdict = {'healthy':[0 for i in range(ndays)], 'immune':[0 for i in range(ndays)], 'total':[0 for i in range(ndays)], 'infected':[0 for i in range(ndays)], 'dead':[0 for i in range(ndays)]}

for graphno in range(graphs):
	start = time.time()
	for runno in range(runs):
		startlocal = time.time()
		print 'Running for graph no', graphno+1, 'run no', runno+1
		if runno==0:
			#create graph and store it
			SN = Social_Net(complete_net=False)
			SN.set_parameters(ba_degree=2, social_prob=0.0005)
			SN.start_network(N)
			G = SN.return_graph()
			networkfile = 'results/network_10k_'+str(graphno+1)+'.graphml'
			gmlfile = 'results/network_10k_'+str(graphno+1)+'.gml'
			nx.write_graphml(G, networkfile)
			nx.write_gml(G, gmlfile)
		else:
			#read graph from file
			gmlreadfile = 'results/network_10k_'+str(graphno+1)+'.gml'
			G = nx.read_gml(gmlreadfile)

		#run the spread on this graph
		spreading = Spread_Net(G=G, setval=True)
		datadict = spreading.many_dayrun(num_days=ndays, curve=False, lockstart=3, lockend=93)
		#print 'datadict', datadict
		for k in avgdict.keys():
			avgdict[k] = [i+j for i,j in zip(avgdict[k], datadict[k])]
		print 'Run completed in', time.time()-startlocal, 'seconds'
	print 'Run for one graph completed in', time.time()-start, 'seconds'

allruns = graphs*runs
for k in avgdict.keys():
	avgdict[k] = [j/allruns for j in avgdict[k]]
print 'avgdict', avgdict
spreading.draw_curve(avgdict, N, ndays, lockstart=3, lockend=93, img_file='results/time_10k_50runs_lock_3-93.png')