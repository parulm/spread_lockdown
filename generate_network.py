import networkx as nx
import itertools as it
import numpy as np
import random
import matplotlib.pyplot as plt

class Social_Net():

	def __init__(self, complete_net=False, n=1000):
		#initializes the graph and sets the parameters to default
		self.G = nx.Graph()
		self.set_parameters()
		if complete_net:
			self.start_network(n)
			self.workplace_BA()
			self.workplace_random()
			self.interaction()
			self.social()
			print 'Classic network of size', n, 'created'
		else:
			print 'Network initialized. Please use function start_network, workplace_BA, workplace_random, interaction, and social to make the network'

	def start_network(self, n):
		self.family_graph(n, self.G)
		#print 'Graph constructed'

	def return_graph(self):
		return self.G

	def family_graph(self, n, G):
		#print 'Size of the network is', n
		for j, val in enumerate([int(round(i*n)) for i in self.family_sizes]):
			#print 'Adding', int(round(val/(j+1))), 'cliques of size', j+1
			for k in range(int(round(val/(j+1)))):
				self.add_clique(j+1, G)

	def workplace_BA(self):
		#creates a scale-free network on non-essential workers
		n_work = 0
		working_nodes = []
		for n in self.G.nodes():
			if self.G.node[n]['working'] and not self.G.node[n]['essential']:
				n_work+=1
				working_nodes.append(n)
		BAG = nx.barabasi_albert_graph(n_work, self.ba_degree)
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
		ER = nx.erdos_renyi_graph(n_ess, self.essential_connection)
		#map the ER to the actual network edges
		for pair in list(ER.edges()):
			self.G.add_edge(essential_nodes[pair[0]], essential_nodes[pair[1]], lockdown=True)
		#print 'Printing edges of the workplace random network'
		#print ER.edges()

	def interaction(self):
		#add edges that represent interactions of everyone with essential workers
		essential_nodes = []
		for n in self.G.nodes():
			if self.G.node[n]['essential']:
				essential_nodes.append(n)

		for n in self.G.nodes():
			connects = np.random.choice(np.arange(0,2), p=[1-self.interaction_prob, self.interaction_prob])
			if connects:
				m = random.choice(essential_nodes)
				self.G.add_edge(n, m, lockdown=True)

	def social(self):
		allnodes = self.G.nodes()
		allpairs = list(it.combinations(allnodes, 2))
		select = random.sample(allpairs, k=int(self.social_prob*len(allpairs)))
		print 'Social interaction will add', len(select), 'edges'
		for i,j in select:
			self.G.add_edge(i, j, lockdown=False)

	def set_parameters(self, family_sizes=[0.3, 0.35, 0.18, 0.17], workrate=0.7, essential=0.2, 
							ba_degree=3, essential_connection=0.6, interaction_prob=0.20, social_prob=0.001):
		self.workrate = workrate
		self.essential = essential
		self.family_sizes = family_sizes
		self.ba_degree = ba_degree
		self.essential_connection = essential_connection
		self.interaction_prob = interaction_prob
		self.social_prob = social_prob

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


if __name__ == '__main__':
	My = Social_Net(complete_net=True)
	#My.set_parameters(essential=0.7)
	#My.start_network(50)
	#My.workplace_BA()
	#My.workplace_random()
	#My.interaction()
	#My.social()
	G = My.return_graph()
	#print G.nodes(data=True)
	#print G.edges()
	nx.draw(G, node_size=10)
	plt.show()