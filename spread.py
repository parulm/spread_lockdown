import networkx as nx
import random
import numpy as np
import matplotlib.pyplot as plt
import json
import math
import statistics

class Spread_Net():
	def __init__(self, G, infected_init=5, setval=True):
		#initialize the spreading for given network G
		#nodes of G must have attributes working and is_essential and edges of G must have attribute lockdown
		self.G = G
		infected = set(random.sample(self.G.nodes(), infected_init))
		self.infected_init = infected_init
		self.infect_dict = {0:infected}
		for n in self.G.nodes():
			if n in infected:
				self.G.node[n]['status'] = 'infected'
				self.G.node[n]['day'] = 0
				self.G.node[n]['future'] = 'immunity'
				self.G.node[n]['symptoms'] = False
				self.G.node[n]['recover_day'] = 14
				self.G.node[n]['repno'] = 0
			else:
				self.G.node[n]['status'] = 'healthy'
				self.G.node[n]['repno'] = -1
		self.cases_count = infected_init
		#self.inf_count, self.health_count, self.immune_count, self.dead_count = 0, 0, 0, 0
		self.cases_data = [infected_init] 
		self.inf_data, self.health_data, self.dead_data, self.immune_data = [], [], [], []
		if setval:
			self.set_parameters()
		#print 'Spread initialized. Run daily spread functions to continue the spread'

	def many_dayrun(self, num_days, lockstart=None, lockend=None, postlock=False, complete_norm=None, curve=False, img_file='temp.png', datafile='temp.json'):
		self.complete_norm = complete_norm
		self.lockend = lockend
		#self.set_parameters()
		for i in range(num_days):
			#if i%10==0:
			#	print 'Running simulation for day', i+1
			if i+1>=lockstart and i+1<=lockend:
				self.dayrun(is_lockdown=True, is_postlock=False, daynum=i+1)
			elif postlock and i+1>lockend:
				if i+1<=complete_norm:
					#print 'Will run dayrun with postlock'
					self.dayrun(is_lockdown=False, is_postlock=True, daynum=i+1)
				else:
					self.dayrun(is_lockdown=False, is_postlock=False, daynum=i+1)
			else:
				self.dayrun(is_lockdown=False, is_postlock=False, daynum=i+1)
			self.inf_data.append(self.inf_count)
			self.health_data.append(self.health_count)
			self.dead_data.append(self.dead_count)
			self.immune_data.append(self.immune_count)
			#self.cases_count = sum(self.inf_data)
			self.cases_data.append(self.cases_count)
		self.cases_data = self.cases_data[:-1]
		#save data to datafile
		dict_tosave = {'infected':self.inf_data, 'healthy':self.health_data, 'dead': self.dead_data, 'immune':self.immune_data, 'total':self.cases_data}
		tempdict = self.reproduction_number(givedata=False)
		dict_tosave['repno'] = []
		for tempkey in sorted(tempdict.keys())[:-1]:
			dict_tosave['repno'].append(tempdict[tempkey])
		with open(datafile, 'w+') as fp:
			json.dump(dict_tosave, fp)
		if curve:
			N = self.G.number_of_nodes()
			self.draw_curve(dict_tosave, N, num_days, lockstart=lockstart, lockend=lockend, complete_norm=complete_norm, img_file=img_file)
		return dict_tosave

	def draw_curve(self, datadict, N, num_days, lockstart=None, lockend=None, complete_norm=None, confidence=False, stdevdict={}, img_file='temp.png', rep_file='rep_temp.png'):
		x = [i+1 for i in range(num_days)]
		fig, ax = plt.subplots()
		ax.plot(x, datadict['healthy'], 'g',linewidth=0.5)
		ax.plot(x, datadict['infected'], 'r', linewidth=0.5)
		ax.plot(x, datadict['immune'], 'b', linewidth=0.5)
		ax.plot(x, datadict['dead'], 'k', linewidth=0.5)
		ax.plot(x, datadict['total'], 'y', linewidth=0.5)
		#print 'checking before plotting', N
		if lockstart:
			ax.plot([lockstart]*3, [0, N/2, N], color='0.5')
		if lockend:
			ax.plot([lockend]*3, [0, N/2, N], color='0.5')
		if complete_norm:
			ax.plot([complete_norm]*3, [0, N/2, N], color='pink')
		if confidence:
			if not stdevdict:
				print 'stdevdict not specified. Skipping drawing intervals'
			else:
				ax.fill_between(x, [b-a for a,b in zip(stdevdict['healthy'], datadict['healthy'])], [b+a for a,b in zip(stdevdict['healthy'], datadict['healthy'])], color='g', alpha=0.1)
				ax.fill_between(x, [b-a for a,b in zip(stdevdict['infected'], datadict['infected'])], [b+a for a,b in zip(stdevdict['infected'], datadict['infected'])], color='r', alpha=0.1)
				ax.fill_between(x, [b-a for a,b in zip(stdevdict['immune'], datadict['immune'])], [b+a for a,b in zip(stdevdict['immune'], datadict['immune'])], color='b', alpha=0.1)
				ax.fill_between(x, [b-a for a,b in zip(stdevdict['dead'], datadict['dead'])], [b+a for a,b in zip(stdevdict['dead'], datadict['dead'])], color='k', alpha=0.1)
				ax.fill_between(x, [b-a for a,b in zip(stdevdict['total'], datadict['total'])], [b+a for a,b in zip(stdevdict['total'], datadict['total'])], color='y', alpha=0.1)
		ax.legend(['healthy', 'infected', 'immune', 'dead', 'total cases'], loc='best', fontsize='x-small')
		plt.xticks(fontsize='x-small')
		plt.yticks(fontsize='x-small')
		plt.savefig(img_file, dpi=500)
		plt.close()
		#create another plot for the reproduction number (range is different)
		fig, ax = plt.subplots()
		ax.plot(x, datadict['repno'], 'bo-', markersize=1, linewidth=0.5)
		if confidence:
			ax.fill_between(x, [b-a for a,b in zip(stdevdict['repno'], datadict['repno'])], [b+a for a,b in zip(stdevdict['repno'], datadict['repno'])], color='b', alpha=0.1)
		ax.plot(x, [1]*len(x), 'k', linewidth=0.5)
		plt.savefig(rep_file, dpi=500)
		plt.close()


	def filter_data(self, datadict):
		#reads a dictionary of simulation results over certain number of days and returns a cleaner dictionary which does not contain the simulations where the disease did not spread at all
		inf = datadict['infected']
		num_sims = len(inf[0])
		num_days = len(inf)
		no_spread = set([])

		for k in range(num_sims):
			this = [inf[i][k] for i in range(num_days)]
			if set(this)=={0,self.infected_init}:
				no_spread.add(k)

		print len(list(no_spread)), 'of the', num_sims, 'simulations did not show any spread'

		newdata = {key:[] for key in datadict.keys()}

		for k in datadict.keys():
			for i in range(num_days):
				curday = datadict[k][i]
				newday = [curday[j] for j in range(num_sims) if j not in no_spread]
				newdata[k].append(newday)

		return newdata
		

	def dayrun(self, is_lockdown=False, is_postlock=False, daynum=None):
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
		self.spread_infection(is_lockdown=is_lockdown, is_postlock=is_postlock, daynum=daynum)

	def kill(self):
		#kills people by a probability distribution of their sick time
		dead = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['future']=='death':
					if self.G.node[n]['day']==self.G.node[n]['death_day']:
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
					if self.G.node[n]['day']==self.G.node[n]['recover_day']:
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

	def spread_infection(self, is_lockdown=False, is_postlock=False, daynum=None):
		to_infect = []
		for n in self.G.nodes():
			if self.G.node[n]['status']=='infected':
				if self.G.node[n]['symptoms']:
					tval = self.trans_symp
				elif is_postlock:
					factor = float(self.complete_norm-daynum)/(self.complete_norm - self.lockend)
					tval = self.trans_asymp - factor*(self.trans_asymp-self.trans_post)
					#print 'In postlock, daynum is', daynum, 'tval is', tval
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
				#separate essential and non-essential neighbors for symptomatic patients
				k = len(vulnerable)
				essential_vulnerable = []
				non_ess_vul = []
				for vulnode in vulnerable:
					if self.G.node[vulnode]['essential']:
						essential_vulnerable.append(vulnode)
					else:
						non_ess_vul.append(vulnode)
				kprime = len(essential_vulnerable)
				if k==kprime:
					ess_factor = 0
				else:
					ess_factor = (self.trans_symp*k - self.trans_asymp*kprime)/(k - kprime)
				if ess_factor<0:
					ess_factor = 0
				#print 'ess_factor is', ess_factor
				#print 'k is', k, 'kprime is', kprime
				if essential_vulnerable:
					affected_ess = random.sample(essential_vulnerable, int(round(self.trans_symp*len(essential_vulnerable))))
				else:
					affected_ess = []
				if non_ess_vul:
					affected_noness = random.sample(non_ess_vul, int(round(ess_factor*len(non_ess_vul))))
				else:
					affected_noness = []
				if self.G.node[n]['symptoms']:
					affected_neighbors = affected_noness+affected_ess
				else:
					affected_neighbors = random.sample(vulnerable, int(round(tval*len(vulnerable))))
				#print 'Will infect', len(affected_neighbors), 'would have infected', int(round(tval*len(vulnerable)))
				#affected_neighbors = random.sample(vulnerable, int(round(tval*len(vulnerable))))
				#see how many of affected neighbors are susceptible. Those add to the reproduction number of this node
				repnum = 0
				for aff in affected_neighbors:
					if self.G.node[aff]['status']=='healthy':
						repnum+=1
				self.G.node[n]['repno']+=repnum
				to_infect.extend(affected_neighbors)
		infected_today = []
		for n in to_infect:
			if self.G.node[n]['status']=='healthy':
				self.G.node[n]['status'] = 'infected'
				self.G.node[n]['day'] = 0
				self.G.node[n]['repno'] = 0
				infected_today.append(n)
		#print infected_today, 'people were newly infected today'
		self.infect_dict[daynum] = infected_today
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
			self.G.node[n]['death_day'] = np.random.choice(np.arange(5,25), p = self.death_list)
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
			self.G.node[n]['recover_day'] = np.random.choice(np.arange(1,36), p = self.recover_list)


	def reproduction_number(self, givedata = True, nodelevel = False, draw = False, img_file = 'temp_reprno.png', datafile = 'temp_reprs.json'):
		#function that returns the data on reproduction number
		#this function must be run after multiple day run is complete
		repdict = {}
		reps = []
		std = []
		rep_by_day = {}
		list_of_days = sorted(self.infect_dict.keys())
		#print 'the dict is', self.infect_dict
		for this_day in list_of_days:
			day_nodes = self.infect_dict[this_day]
			repr_list = [float(self.G.node[n]['repno']) for n in day_nodes]
			repdict[this_day] = repr_list
			#print 'repr_list is', repr_list
			if not repr_list:
				avg_rep = 0
				std_rep = 0
			elif len(repr_list)>1:
				avg_rep = statistics.mean(repr_list)
				std_rep = statistics.stdev(repr_list)
			else:
				avg_rep = repr_list[0]
				std_rep = 0
			reps.append(avg_rep)
			std.append(std_rep)
			rep_by_day[this_day] = round(avg_rep,4)
		if givedata:
			if nodelevel:
				with open(datafile, 'w+') as fp:
					json.dump(repdict, fp)
			else:
				with open(datafile, 'w+') as fp:
					json.dump(rep_by_day, fp)
		if draw:
			fig, ax = plt.subplots()
			ax.plot(list_of_days, reps, 'go-', markersize=1, linewidth=0.5)
			ax.plot(list_of_days, [1]*len(list_of_days), 'k', linewidth=0.5)
			#ax.fill_between(list_of_days, [b-a for a,b in zip(std, reps)], [b+a for a,b in zip(std, reps)], color='g', alpha=0.1)
			plt.savefig(img_file, dpi=500)
			plt.close()
		return rep_by_day


	def set_parameters(self, trans_symp=0.005, trans_asymp=0.05, death_rate=0.05, immune_rate=0.85, asymp_ratio=0.8, trans_post=0.01, transition=15):
		self.trans_asymp = trans_asymp
		self.trans_symp = trans_symp
		self.death_rate = death_rate
		self.immune_rate = immune_rate
		self.asymp_ratio = asymp_ratio
		self.trans_post = trans_post
		self.transition = transition
		#the following variables are hardfixed
		#death list is picked from a gaussian around 14. ranges from 5 days to 24 days.
		self.death_list = [0.0024, 0.0037, 0.0081, 0.0159, 0.0285, 0.0465, 0.0686, 0.0918, 0.1116, 0.1229, 0.1229, 0.1116, 0.0918, 0.0686, 0.0465, 0.0285, 0.0159, 0.0081, 0.0037, 0.0024]
		#death_list = [1, 1.5, 4.5, 6, 8, 10, 12, 14, 12, 10, 8, 6, 4.5, 1.5, 1]
		#self.death_dist = {i+7:death_list[i] for i in range(len(death_list))}
		#recover list is picked from a gaussian distribution around 17. Recovery ranges from 1 day to 35 days.
		self.recover_list = [0.0002, 0.0005, 0.0009, 0.0016, 0.0028, 0.0047, 0.0076, 0.0117, 0.0173, 0.0245, 0.0332, 0.0431, 0.0536, 0.0637, 0.0726, 0.0792, 0.0828, 0.0827, 0.0792, 0.0726, 0.0637, 0.0536, 0.0431, 0.0332, 0.0245, 0.0173, 0.0117, 0.0076, 0.0047, 0.0028, 0.0016, 0.0009, 0.0005, 0.0002, 0.0001]

	def return_parameters(self):
		pardict = {}
		pardict['trans_asymp'] = self.trans_asymp
		pardict['trans_symp'] = self.trans_symp
		pardict['death_rate'] = self.death_rate
		pardict['immune_rate'] = self.immune_rate
		pardict['sick_time'] = self.sick_time
		pardict['recover_time'] = self.recover_time
		pardict['asymp_ratio'] = self.asymp_ratio
		pardict['death_list'] = self.death_list
		pardict['recover_list'] = self.recover_list
		return pardict