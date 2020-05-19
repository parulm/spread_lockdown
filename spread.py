import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
import json
import math

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
				self.G.node[n]['future'] = 'immunity'
				self.G.node[n]['symptoms'] = False
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
		#kills people by a probability distribution of their sick time
		dead = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['future']=='death':
					d = self.G.node[n]['day']
					if d>6:
						dprob = self.death_dist[d]
						die = np.random.choice(np.arange(0,2), p=[1-dprob, dprob])
						if die:
							dead.append(n)
		#a person dies as per probability calculated from their day of sickness
		for n in dead:
			self.G.node[n]['status'] = 'dead'
		#returns the number of people killed
		return len(dead)

	def immune_susceptible(self):
		#scans all nodes that do not have future as dead and probabilistically decides by the day if they recover today
		to_update = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['future']!='death':
					dayval = self.G.node[n]['day']
					probtoday = self.recover_func(float(dayval))
					today = np.random.choice(np.arange(0,2), p=[1-probtoday, probtoday])
					if today:
						to_update.append(n)

		for n in to_update:
			if self.G.node[n]['future']=='immunity':
				self.G.node[n]['status'] = 'immune'
			elif self.G.node[n]['future']=='health':
				self.G.node[n]['status'] = 'healthy'
			else:
				print 'Unexpected future/status on node', n, self.G.node[n]
		

	def recover_func(self, x):
		return (float(1)/12)*math.exp(-(3.14)*((x-17)/12)**2)

	def spread_infection(self, is_lockdown=False):
		to_infect = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['symptoms']:
					tval = self.trans_symp
				else:
					tval = self.trans_asymp
				neighbors = list(self.G.neighbors(n))
				if is_lockdown:
					vulnerable = []
					for neigh in neighbors:
						if self.G.get_edge_data(n, neigh)['lockdown']:
							vulnerable.append(neigh)
				else:
					vulnerable = neighbors
				affected_neighbors = random.sample(vulnerable, int(round(tval*len(vulnerable))))
				to_infect.extend(affected_neighbors)
		infected_today = []
		for n in to_infect:
			if self.G.node[n]['status']=='healthy':
				self.G.node[n]['status'] = 'infected'
				self.G.node[n]['day'] = 0
				infected_today.append(n)
		#print infected_today, 'people were newly infected today'
		self.cases_count+=len(infected_today)
		asymp = random.sample(infected_today, int(round(self.asymp_ratio*len(infected_today))))
		symp = list(set(infected_today) - set(asymp))
		#mark whether the person is symptomatic or not
		symp_set = set(symp)
		for n in infected_today:
			if n in symp_set:
				self.G.node[n]['symptoms'] = True
			else:
				self.G.node[n]['symptoms'] = False
		f = self.death_rate/(1-self.asymp_ratio)
		to_die = random.sample(symp, int(round(f*len(symp))))
		for n in to_die:
			self.G.node[n]['future'] = 'death'
		rest = list(set(infected_today) - set(to_die))
		#immune and make the rest of rest susceptible
		fi = self.immune_rate/(1-self.death_rate)
		to_imm = random.sample(rest, int(round(fi*len(rest))))
		immset = set(to_imm)
		for n in rest:
			if n in immset:
				self.G.node[n]['future'] = 'immunity'
			else:
				self.G.node[n]['future'] = 'health'

	def set_parameters(self, trans_symp=0.01, trans_asymp=0.08, death_rate=0.05, immune_rate=0.85, sick_time=6, recover_time=14, asymp_ratio=0.8):
		self.trans_asymp = trans_asymp
		self.trans_symp = trans_symp
		self.death_rate = death_rate
		self.immune_rate = immune_rate
		self.sick_time = sick_time
		self.recover_time = recover_time
		self.asymp_ratio = asymp_ratio
		#the following variables are hardfixed
		death_list = [1, 1.5, 4.5, 6, 8, 10, 12, 14, 12, 10, 8, 6, 4.5, 1.5, 1]
		self.death_dist = {i+7:death_list[i] for i in range(len(death_list))}