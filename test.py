import networkx as nx 
import matplotlib.pyplot as plt 
from generate_network import Social_Net
from spread import Spread_Net
import time


#Create the social network and save it in graphml for representation and in gml for reading later
print 'Starting graph creation'
start = time.time()
SN = Social_Net(complete_net=False)
SN.set_parameters(ba_degree=2, social_prob=0.0005)
SN.start_network(10000)
G = SN.return_graph()
#networkfile = 'results/structure_10k_1.graphml'
#gmlfile = 'results/structure_10k_1.gml'
#nx.write_graphml(G, networkfile)
#nx.write_gml(G, gmlfile)
print 'Graph creation completed in', time.time()-start, 'seconds'


#read from file if the file is already saved
#print 'Starting the reading'
#gmlreadfile = 'results/structure_1k_1.gml'
#G = nx.read_gml(gmlreadfile)
#print 'Network read'

spreading = Spread_Net(G=G, infected_init=5, setval=True)
#spreading.set_parameters(trans_asymp=0.03)
#spreading.many_dayrun(num_days=120, curve=True)
#spreading.many_dayrun(num_days=120, curve=True, img_file = 'results/time_100k_1.png', datafile='results/data_100k_1.json')
spreading.many_dayrun(num_days=240, lockstart=5, lockend=65, postlock=True, complete_norm=75, curve=True)
#spreading.many_dayrun(num_days=120, lockstart=5, lockend=50, curve=True, img_file = 'results/time_10k_1_15.png', datafile='results/data_10k_1_15.json')