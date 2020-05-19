import networkx as nx 
import matplotlib.pyplot as plt 
from generate_network import Social_Net
from spread import Spread_Net


#Create the social network and save it in graphml for representation and in gml for reading later
SN = Social_Net(complete_net=True, n=10000)
G = SN.return_graph()
#networkfile = 'results/structure_10k_1.graphml'
#gmlfile = 'results/structure_10k_1.gml'
#nx.write_graphml(G, networkfile)
#nx.write_gml(G, gmlfile)


#read from file if the file is already saved
#print 'Starting the reading'
#gmlreadfile = 'results/structure_1k_1.gml'
#G = nx.read_gml(gmlreadfile)
#print 'Network read'

spreading = Spread_Net(G=G, setval=False)
spreading.set_parameters(trans_asymp=0.05)
spreading.many_dayrun(num_days=120, curve=True)
#spreading.many_dayrun(num_days=60, curve=True, img_file = 'results/time_10k_1_3.png', datafile='results/data_10k_1_3.json')
#spreading.many_dayrun(num_days=120, lockstart=5, lockend=50, curve=True, img_file = 'results/time_10k_1_15.png', datafile='results/data_10k_1_15.json')