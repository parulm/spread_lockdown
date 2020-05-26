import networkx as nx 
import time
from generate_network import Social_Net
from spread import Spread_Net
import json
import statistics

#graphs x runs will be the number of simulations. And the results will be on the average of those
graphs = 30
runs = 100
#number of days each simulation will run for
ndays = 120
#number of nodes in the network
N = 10000

avgdict = {'healthy':[0 for i in range(ndays)], 'immune':[0 for i in range(ndays)], 'total':[0 for i in range(ndays)], 'infected':[0 for i in range(ndays)], 'dead':[0 for i in range(ndays)]}

mindict = {'healthy':[N for i in range(ndays)], 'immune':[N for i in range(ndays)], 'total':[N for i in range(ndays)], 'infected':[N for i in range(ndays)], 'dead':[N for i in range(ndays)]}

stdevdict = {'healthy':[0 for i in range(ndays)], 'immune':[0 for i in range(ndays)], 'total':[0 for i in range(ndays)], 'infected':[0 for i in range(ndays)], 'dead':[0 for i in range(ndays)]}

cumdict = {'healthy':[[] for i in range(ndays)], 'immune':[[] for i in range(ndays)], 'total':[[] for i in range(ndays)], 'infected':[[] for i in range(ndays)], 'dead':[[] for i in range(ndays)]}

for graphno in range(graphs):
	start = time.time()
	for runno in range(runs):
		startlocal = time.time()
		print 'Running for graph no', graphno+1, 'run no', runno+1
		if runno==0:
			#create graph and store it
			SN = Social_Net(complete_net=False)
			SN.set_parameters(ba_degree=2, social_prob=0.00025, rand_degree=25)
			SN.start_network(N)
			G = SN.return_graph()
			#networkfile = 'results_rand25/network_10k_'+str(graphno+1)+'.graphml'
			gmlfile = 'results_rand25/network_10k_'+str(graphno+1)+'.gml'
			#nx.write_graphml(G, networkfile)
			nx.write_gml(G, gmlfile)
		else:
			#read graph from file
			gmlreadfile = 'results_rand25/network_10k_'+str(graphno+1)+'.gml'
			G = nx.read_gml(gmlreadfile)

		#run the spread on this graph
		spreading = Spread_Net(G=G, setval=True)
		datadict = spreading.many_dayrun(num_days=ndays, curve=False)
		#print 'datadict', datadict
		for k in datadict.keys():
			for ind in range(ndays):
				cumdict[k][ind].append(datadict[k][ind])
		#for k in avgdict.keys():
		#	avgdict[k] = [i+j for i,j in zip(avgdict[k], datadict[k])]
		#for k in datadict.keys():
		#	for ind in range(ndays):
		#		if datadict[k][ind]<mindict[k][ind]:
		#			mindict[k][ind] = datadict[k][ind]
		#		if datadict[k][ind]>maxdict[k][ind]:
		#			maxdict[k][ind] = datadict[k][ind]
		print 'Run completed in', time.time()-startlocal, 'seconds'
	print 'Run for one graph completed in', time.time()-start, 'seconds'

#print 'cumdict is', cumdict

allruns = graphs*runs
for k in cumdict.keys():
	for ind in range(ndays):
		avgdict[k][ind] = statistics.mean(cumdict[k][ind])
		stdevdict[k][ind] = statistics.stdev(cumdict[k][ind])
#print 'avgdict is', avgdict
#print 'stdevdict is', stdevdict
#for k in avgdict.keys():
#	avgdict[k] = [float(j)/allruns for j in avgdict[k]]
#print 'avgdict', avgdict
spreading.draw_curve(datadict=avgdict, N=N, num_days=ndays, confidence=True, stdevdict=stdevdict, img_file='results_rand25/time_nolock.png')

with open('results_rand25/data_nolock.json', 'w+') as fp:
	#json.dump(avgdict, fp)
	json.dump(cumdict, fp)
	#json.dump(mindict, fp)
	#json.dump(maxdict, fp)
