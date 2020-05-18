import networkx as nx
import random
import matplotlib.pyplot as plt
import json

class Spread_Net():
	def __init__(self, G, infected_init=5, setval=True):
		#initialize the spreading for given network G
		#nodes of G must have attributes working and is_essential and edges of G must have attribute lockdown
		self.G = G
		infected = set(random.sample(self.G.nodes(), infected_init))
		for n in self.G.nodes():
			if n in infected:
				self.G.node[n]['status'] = 'infected'
				self.G.node[n]['day'] = 0
			else:
				self.G.node[n]['status'] = 'healthy'
		self.cases_count = infected_init
		#self.inf_count, self.health_count, self.immune_count, self.dead_count = 0, 0, 0, 0
		self.cases_data = [infected_init] 
		self.inf_data, self.health_data, self.dead_data, self.immune_data = [], [], [], []
		if setval:
			self.set_parameters()
		print 'Spread initialized. Run daily spread functions to continue the spread'

	def many_dayrun(self, num_days, lockstart=None, lockend=None, curve=False, img_file='temp.png', datafile='temp.json'):
		#self.set_parameters()
		for i in range(num_days):
			if i%10==0:
				print 'Running simulation for day', i+1
			if i+1>=lockstart and i+1<=lockend:
				self.dayrun(is_lockdown=True)
			else:
				self.dayrun(is_lockdown=False)
			self.inf_data.append(self.inf_count)
			self.health_data.append(self.health_count)
			self.dead_data.append(self.dead_count)
			self.immune_data.append(self.immune_count)
			#self.cases_count = sum(self.inf_data)
			self.cases_data.append(self.cases_count)
		self.cases_data = self.cases_data[:-1]
		#save data to datafile
		dict_tosave = {'infected':self.inf_data, 'healthy':self.health_data, 'dead': self.dead_data, 'immune':self.immune_data, 'total':self.cases_data}
		with open(datafile, 'w+') as fp:
			json.dump(dict_tosave, fp)
		if curve:
			N = self.G.number_of_nodes()
			x = [i+1 for i in range(num_days)]
			plt.plot(x, self.health_data, 'go-', markersize=3.5, linewidth=0.5)
			plt.plot(x, self.inf_data, 'ro-', markersize=3.5, linewidth=0.5)
			plt.plot(x, self.immune_data, 'bo-', markersize=3.5, linewidth=0.5)
			plt.plot(x, self.dead_data, 'ko-', markersize=3.5, linewidth=0.5)
			plt.plot(x, self.cases_data, 'yo-', markersize=3.5, linewidth=0.5)
			print 'checking before plotting', N
			if lockstart:
				plt.plot([lockstart]*3, [0, N/2, N], color='0.5')
			if lockend:
				plt.plot([lockend]*3, [0, N/2, N], color='0.5')
			plt.legend(['healthy', 'infected', 'immune', 'dead', 'total cases'], loc='best', fontsize='x-small')
			plt.xticks(fontsize='x-small')
			plt.yticks(fontsize='x-small')
			plt.savefig(img_file, dpi=500)
			plt.close()

	def dayrun(self, is_lockdown=False):
		self.kill()
		self.immune_susceptible()
		self.inf_count, self.health_count, self.immune_count, self.dead_count = 0, 0, 0, 0
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				self.inf_count+=1
				self.G.node[n]['day']+=1
			elif self.G.node[n]['status']=='healthy':
				self.health_count+=1
			elif self.G.node[n]['status']=='dead':
				self.dead_count+=1
			elif self.G.node[n]['status']=='immune':
				self.immune_count+=1
			else:
				print 'node', n, 'has unidentifiable status'
		self.spread_infection(is_lockdown)

	def kill(self):
		#kills death_rate fraction of the infected people
		inf_todie = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['day']==self.sick_time:
					inf_todie.append(n)
		dead = list(random.sample(inf_todie, int(round(self.death_rate*len(inf_todie)))))
		for n in dead:
			self.G.node[n]['status'] = 'dead'
		#returns the number of people killed
		return len(dead)

	def immune_susceptible(self):
		#immunizes some fraction and makes the rest susceptible again
		inf_toimm = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['day']>=self.recover_time:
					inf_toimm.append(n)
		immune = set(random.sample(inf_toimm, int(round(self.immune_rate*len(inf_toimm)))))
		for n in inf_toimm:
			if n in immune:
				self.G.node[n]['status'] = 'immune'
			else:
				self.G.node[n]['status'] = 'healthy'
		#return the number of people that gained immunity
		return len(list(immune))

	def spread_infection(self, is_lockdown=False):
		to_infect = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				neighbors = list(self.G.neighbors(n))
				if is_lockdown:
					vulnerable = []
					for neigh in neighbors:
						if self.G.get_edge_data(n, neigh)['lockdown']:
							vulnerable.append(neigh)
				else:
					vulnerable = neighbors
				affected_neighbors = random.sample(vulnerable, int(round(self.transmission*len(vulnerable))))
				to_infect.extend(affected_neighbors)
		infected_today = 0
		for n in to_infect:
			if self.G.node[n]['status']=='healthy':
				self.G.node[n]['status'] = 'infected'
				self.G.node[n]['day'] = 0
				infected_today+=1
		#print infected_today, 'people were newly infected today'
		self.cases_count+=infected_today

	def set_parameters(self, transmission=0.1, death_rate=0.05, immune_rate=0.85, sick_time=6, recover_time=14):
		self.transmission = transmission
		self.death_rate = death_rate
		self.immune_rate = immune_rate
		self.sick_time = sick_time
		self.recover_time = recover_time