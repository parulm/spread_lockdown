import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt
import collections

class Social_Net():

	def __init__(self, complete_net=False, n=1000):
		#initializes the graph and sets the parameters to default
		self.G = nx.Graph()
		self.set_parameters()
		if complete_net:
			self.start_network(n)
			#self.workplace_BA()
			#self.workplace_random()
			#self.interaction()
			#self.social()
			#print 'Classic network of size', n, 'created'
		else:
			#print 'Network initialized. Please use function start_network to make the network'
			pass

	def start_network(self, n):
		self.family_graph(n, self.G)
		self.workplace_BA()
		self.workplace_random()
		self.interaction()
		self.social()
		#print 'Graph constructed'

	def return_graph(self):
		return self.G

	def family_graph(self, n, G):
		#print 'Size of the network is', n
		for j, val in enumerate([int(round(i*n)) for i in self.family_sizes]):
			#print 'Adding', int(round(val/(j+1))), 'cliques of size', j+1
			for k in range(int(round(val/(j+1)))):
				self.add_clique(j+1, G)
		print 'Family!'
		self.degree_histogram(G=self.G, hist_file='family_hist.png', loglog_file='family_log.png')

	def workplace_BA(self):
		#creates a scale-free network on non-essential workers
		n_work = 0
		working_nodes = []
		for n in self.G.nodes():
			if self.G.node[n]['working'] and not self.G.node[n]['essential']:
				n_work+=1
				working_nodes.append(n)
		BAG = nx.barabasi_albert_graph(n_work, self.ba_degree)
		print 'Workplace BA!'
		self.degree_histogram(G=BAG, hist_file='workBA_hist.png', loglog_file='workBA_log.png')
		#map the BAG to the actual network edges
		for pair in list(BAG.edges()):
			self.G.add_edge(working_nodes[pair[0]], working_nodes[pair[1]], lockdown=False)
		#print 'Printing edges of the workplace BA network'
		#print BAG.edges()
		return None

	def workplace_random(self):
		#creates a random network on essential workers
		n_ess = 0
		essential_nodes = []
		for n in self.G.nodes():
			if self.G.node[n]['essential']:
				n_ess+=1
				essential_nodes.append(n)
		#print 'Number of essential people is', n_ess
		#ER = nx.erdos_renyi_graph(n_ess, self.essential_connection)
		m = int(float(n_ess*self.rand_degree)/2)
		print 'm is', m
		ER = nx.gnm_random_graph(n_ess, m)
		print 'Workplace Random!'
		self.degree_histogram(G=ER, hist_file='workRand_hist.png', loglog_file='workRand_log.png')
		#map the ER to the actual network edges
		for pair in list(ER.edges()):
			self.G.add_edge(essential_nodes[pair[0]], essential_nodes[pair[1]], lockdown=True)
		#print 'Printing edges of the workplace random network'
		#print ER.edges()

	def interaction(self):
		#add edges that represent interactions of everyone with essential workers
		newG = nx.Graph()
		newG.add_nodes_from([i for i in range(len(self.G.nodes()))])
		essential_nodes = []
		for n in self.G.nodes():
			if self.G.node[n]['essential']:
				essential_nodes.append(n)

		for n in self.G.nodes():
			connects = np.random.choice(np.arange(0,2), p=[1-self.interaction_prob, self.interaction_prob])
			if connects:
				m = random.choice(essential_nodes)
				self.G.add_edge(n, m, lockdown=True)
				newG.add_edge(n, m)

		print 'interaction!'
		self.degree_histogram(G=newG, hist_file='inter_hist.png', loglog_file='inter_log.png')

	def social(self):
		socG = nx.Graph()
		socG.add_nodes_from([i for i in range(len(self.G.nodes()))])
		allnodes = self.G.nodes()
		allpairs = list(it.combinations(allnodes, 2))
		select = random.sample(allpairs, k=int(self.social_prob*len(allpairs)))
		print 'Social interaction will add', len(select), 'edges'
		for i,j in select:
			self.G.add_edge(i, j, lockdown=False)
			socG.add_edge(i, j)
		print 'Social!'
		self.degree_histogram(G=socG, hist_file='soc_hist.png', loglog_file='soc_log.png')

	def set_parameters(self, family_sizes=[0.3, 0.35, 0.18, 0.17], workrate=0.7, essential=0.2, ba_degree=3, essential_connection=0.6, interaction_prob=0.20, social_prob=0.001, rand_degree=5):
		self.workrate = workrate
		self.essential = essential
		self.family_sizes = family_sizes
		self.ba_degree = ba_degree
		self.essential_connection = essential_connection
		self.interaction_prob = interaction_prob
		self.social_prob = social_prob
		self.rand_degree = rand_degree

	def return_parameters(self):
		pardict = {}
		pardict['workrate'] = self.workrate
		pardict['essential'] = self.essential
		pardict['family_sizes'] = self.family_sizes
		pardict['ba_degree'] = self.ba_degree
		pardict['essential_connection'] = self.essential_connection
		pardict['interaction_prob'] = self.interaction_prob
		pardict['social_prob'] = self.social_prob
		pardict['rand_degree'] = self.rand_degree
		return pardict

	def add_clique(self, clique_size, G):
		#adds a clique of size n to graph G
		if G.nodes():
			l = max(G.nodes)+1
		else:
			l = 0
		#print 'l is', l 
		works = []
		for k in range(clique_size):
			works.append(np.random.choice(np.arange(0,2), p=[1-self.workrate, self.workrate]))
		nodes_to_add = [l+i for i in range(clique_size)]
		for i in range(clique_size):
			if works[i]:
				ess = np.random.choice(np.arange(0,2), p=[1-self.essential, self.essential])
			else:
				ess = 0
			#print 'ess is', ess
			G.add_node(l+i, working=works[i], essential=ess)
		#G.add_nodes_from(nodes_to_add)		#add nodes l, l+1, l+2, l+3 (for n=4) to the graph
		#add edges between all these pairs
		for i,j in list(it.combinations(nodes_to_add, 2)):
			#print 'adding edge between', i, 'and', j
			G.add_edge(i,j, lockdown=True)


	def degree_histogram(self, G=None, hist_file='temp_hist.png', loglog_file=None):
		if not G:
			G = self.G
		degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
		#print "Degree sequence", degree_sequence
		degreeCount = collections.Counter(degree_sequence)
		degreeCount = sorted(degreeCount.items())
		print type(degreeCount)
		deg, cnt = zip(*degreeCount)
		print 'deg', deg
		print 'cnt', cnt

		fig, ax = plt.subplots()
		plt.bar(deg, cnt)

		plt.title("Degree Histogram")
		plt.ylabel("Count")
		plt.xlabel("Degree")
		#ax.set_xticks([d + 0.4 for d in deg])
		#ax.set_xticklabels(deg)
		plt.savefig(hist_file, dpi=500)
		plt.close()

		if loglog_file:
			fig, ax = plt.subplots()
			#plt.loglog(deg, cnt)
			plt.plot(deg, cnt, 'ko', markersize=2)
			ax.set_xscale('log')
			ax.set_yscale('log')
			plt.title("Degree loglog plot")
			plt.ylabel("P(k)")
			plt.xlabel("Degree (k)")
			plt.savefig(loglog_file, dpi=500)
			plt.close()


if __name__ == '__main__':
	My = Social_Net(complete_net=False)
	My.set_parameters(ba_degree=2, social_prob=0.00025, rand_degree=25)
	My.start_network(10000)
	#My.workplace_BA()
	#My.workplace_random()
	#My.interaction()
	#My.social()
	G = My.return_graph()
	print 'Overall'
	My.degree_histogram(loglog_file='temp_log.png')
	#print G.nodes(data=True)
	#print G.edges()
	#nx.draw(G, node_size=10)
	#plt.show()
	#nx.write_graphml(G, 'tenk_net.graphml')