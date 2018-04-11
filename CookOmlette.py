import re
class CookOmlette(object):

	"""
        These class level variables are used to store pddl file
        states - store list of literal at each stae
        actions - store actions defined in pddl
        goal - store the goal state
        action_state - store list of actions at each state
        Variables are getting populate in populatePDDL() function
    """	
	states = {}
	actions = {}
	goal = {}
	action_state = {}

	"""
        These class level variables are used to store pddl file
        states - store list of literal at each stae
        actions - store actions defined in pddl
        goal - store the goal state
        action_state - store list of actions at each state
        Variables are getting populate in populatePDDL() function
    """	
	nl_mutex = {}
	ie_mutex = {}
	i_mutex = {}
	cn_mutex = {}
	is_mutex = {}

	"""docstring for CookOmlette"""
	def __init__(self):
		super(CookOmlette, self).__init__()

	"""
        This fucntion reads and populate the entire pddl in the data structure from road.txt
    """	
	def populatePDDL(self):
		file = open("pddl.txt","r")
		line = file.read()
		
		regex = r"\((.*?)\)"
		matches = re.finditer(regex, line, re.MULTILINE | re.DOTALL)
		literals = []

		for matchNum, match in enumerate(matches):
			literals.append(match.group(1))

		#populating initial state
		initial_s = {literals[0]:1, "FriedEggs":-1, "BoiledVegetables":-1, "Dinner": -1}
		self.states[1] = initial_s

		#populating goal
		goals = literals[1].split(",")
		for goal in goals:
			if "~" in goal:
				self.goal[goal.replace("~", "")] = -1
			else:
				self.goal[goal] = 1

		#populating actions
		for action in literals[2:]:

			temp_action_data = []
			action_data = action.split("\n")
			
			action_name = action_data[0].replace(",","")
			
			#populating pre conditions
			fluents = action_data[1].replace("PRECOND:","").split(",")
			pre_map = {}
			for fluent in fluents:
				if "~" in fluent:
					pre_map[fluent.replace("~", "")] = -1
				else:
					pre_map[fluent] = 1
			temp_action_data.append(pre_map)

			#populating effects
			fluents = action_data[2].replace("EFFECT:","").split(",")
			effect_map = {}
			for fluent in fluents:
				if "~" in fluent:
					effect_map[fluent.replace("~", "")] = -1
				else:
					effect_map[fluent] = 1
			temp_action_data.append(effect_map)
			
			self.actions[action_name] = temp_action_data

		file.close()


	"""
        This fucntion expand planning graph to cook omelette
    """	
	def cookOmlette(self):
		current_state = 1

		#check if the goal state exist in the graph plan otherwise extend the graph
		while self.checkGoal(current_state):
			temp_state = self.states[current_state].copy()
			action_state = []
			for action in self.actions:
				action_flag = True
				pre_cond = self.actions[action][0]
				for fluent in pre_cond:
					if pre_cond[fluent] != self.states[current_state][fluent] and self.states[current_state][fluent]!=2:
						action_flag = False
				if action_flag:
					action_state.append(action) 
					effects = self.actions[action][1]
					for fluent in effects:
						if self.states[current_state][fluent] + effects[fluent] == 0:
							temp_state[fluent] = 2
						elif fluent not in temp_state:
							temp_state[fluent] = effects[fluent]
			self.states[current_state+1] = temp_state
			self.action_state[current_state] = action_state
			self.printStates(current_state)
			print "------------"
			current_state+=1
			self.printAction(current_state-1)
			print "------------"
			self.printStates(current_state)
			print "------------"
			self.mutexes(current_state)

	def checkGoal(self, state):
		goals = []
		for goal in self.goal:
			if(self.goal[goal]==-1):
				goals.append("~"+goal)
			else:
				goals.append(goal)
		goal_act = {}
		state_goal = ['CleanPan', '~FriedEggs', '~Dinner', '~BoiledVegetables']
		current_state = self.states[state]
		for goal in self.goal:
			if self.goal[goal] != current_state[goal] and current_state[goal] !=2:
				return True
		if self.is_mutex[state]:
			return True

		c_st = 1
		actions = self.action_state
		while c_st < state:
			for action in actions:
				#print ",,,,,,,,,,,,,,",actions[action]
				for lit in actions[action]:
					is_mutex = self.i_mutex[c_st]
					if lit in is_mutex and set(is_mutex[lit]).issubset(actions[action]):
						if not goal_act:
							goal_act[c_st] = lit
							effects = self.actions[lit][1]
							for eff in effects:
								if(effects[eff]==-1):
									state_goal.remove(eff)
									state_goal.append("~"+eff)
								else:
									state_goal.remove("~"+eff)
									state_goal.append(eff)
						elif c_st!=1:
							#goal_act[c_st] = None
							for key in goal_act.keys():
								if goal_act[key] != lit:
									pre_cond = self.actions[lit][0]
									temp_pre = []
									for eff in pre_cond:
										if(pre_cond[eff]==-1):
											temp_pre.append("~"+eff)
										else:
											temp_pre.append(eff)
									#print "pre", temp_pre
									if set(temp_pre).issubset(state_goal):
										if not c_st in goal_act:
											goal_act[c_st] = lit
										#print temp_pre, state_goal, "---------xoxoxoxoxoxox----------------"
										#return
											effects = self.actions[lit][1]
											for eff in effects:
												if(effects[eff]==-1):
													state_goal.remove(eff)
													state_goal.append("~"+eff)	
												else:
													state_goal.remove("~"+eff)
													state_goal.append(eff)
										#print effects, state_goal, "---------jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjb----------------"
										#if goal_act[c_st] is None:
										#print "update Washhhhhhh...",goal_act[c_st]
										
						
				c_st+=1
		#print goal_act
		#print goals
		#print state_goal
		#print "----b-------------------------------------------------------------------------------------------------"
		if not set(goals).issubset(state_goal):
			return True
		else:
			print "Solution Path",goal_act




	def mutexes(self, state):
		self.negatedLiteral(state)
		self.inconsistentEffect(state-1)
		self.interference(state-1)
		self.comptetingNeeds(state-1)
		self.inconsistentSupport(state)
		print "------------"

	def negatedLiteral(self,state):
		nl_mutex = []
		current_state = self.states[state]
		for key in current_state:
			if current_state[key] == 2:
				nl_mutex.append([key,"~"+key])
		self.nl_mutex[state] = nl_mutex
		print "NL mutex at literal state", state,"--",nl_mutex

	def inconsistentEffect(self,state):
		ie_mutexes = {}
		current_action = self.action_state[state]
		next_state = self.states[state+1]
		for action in current_action:
			temp_ie = []
			effects = self.actions[action][1]
			for effect in effects:
				if(next_state[effect] == 2):	
					#temp_ie.append(action)
					for i_action in current_action:
						if i_action != action:
							i_effects = self.actions[i_action][1]
							if effect in i_effects and i_effects[effect]+effects[effect]==0:
								temp_ie.append(i_action)
					if(effects[effect] == 1):
						temp_ie.append("no-op(~" + effect +")")
					else:
						temp_ie.append("no-op("+effect+")")
			ie_mutexes[action] = temp_ie

		self.ie_mutex[state] = ie_mutexes
		#print self.actions
		print "IE mutex at action state",state, "--", ie_mutexes
	
	def interference(self,state):
		i_mutexes = {}
		current_action = self.action_state[state]
		for action in current_action:
			temp_i = []
			effects = self.actions[action][1]
			for effect in effects:
				for i_action in current_action:
					if i_action != action:
						pre_cond = self.actions[i_action][0]
						if effect in pre_cond and pre_cond[effect]+effects[effect]==0:
							temp_i.append(i_action)
			i_mutexes[action] = temp_i

		self.i_mutex[state] = i_mutexes
		print "I mutex at action state",state, "--", i_mutexes

	def comptetingNeeds(self,state):
		cn_mutexes = {}
		current_action = self.action_state[state]
		for action in current_action:
			temp_i = []
			effects = self.actions[action][0]
			for effect in effects:
				for i_action in current_action:
					if i_action != action:
						pre_cond = self.actions[i_action][0]
						if effect in pre_cond and pre_cond[effect]+effects[effect]==0:
							temp_i.append(i_action)
			cn_mutexes[action] = temp_i
		self.cn_mutex[state] = cn_mutexes
		print "CN mutex at action state",state, "--", cn_mutexes

	
	def inconsistentSupport(self,c_state):
		states = self.states[c_state]
		#self.actionEffet(c_state,{"FriedEggs":1, "BoiledVegetables":1})
		for state in states:
			for p_state in states:
				if p_state !=state:
					x = 2
					if states[state] == 2:
						if states[p_state] == 1:
							self.actionEffet(c_state,{state:1, p_state:1})
							self.actionEffet(c_state,{state:-1, p_state:1})
						elif states[p_state] == -1:
							self.actionEffet(c_state,{state:1, p_state:-1})
							self.actionEffet(c_state,{state:-1, p_state:-1})
						else:
							self.actionEffet(c_state,{state:1, p_state:1})
							self.actionEffet(c_state,{state:-1, p_state:1})
							self.actionEffet(c_state,{state:1, p_state:-1})
							self.actionEffet(c_state,{state:-1, p_state:-1})
					elif states[state] == 1:
						if states[p_state] == 1:
							self.actionEffet(c_state,{state:1, p_state:1})
						elif states[p_state] == -1:
							self.actionEffet(c_state,{state:1, p_state:-1})
						else:
							self.actionEffet(c_state,{state:1, p_state:1})
							self.actionEffet(c_state,{state:1, p_state:-1})
					else:
						if states[p_state] == 1:
							self.actionEffet(c_state,{state:-1, p_state:1})
						elif states[p_state] == -1:
							self.actionEffet(c_state,{state:-1, p_state:-1})
						else:
							self.actionEffet(c_state,{state:-1, p_state:1})
							self.actionEffet(c_state,{state:-1, p_state:-1})
		print "IS mutex at literal state",c_state, "--", self.is_mutex[c_state]	

	def actionEffet(self, state, literal):
		is_mutexes = []
		actions = self.action_state[state-1]
		pair_action = []
		for key in literal:
			if self.states[state-1][key] == literal[key]:
				return
		for action in actions:
			effect = self.actions[action][1]
			for key,value in effect.iteritems():
				if key in literal and literal[key] == value:
					pair_action.append(action)
		for action in pair_action:
			if action in self.i_mutex[state-1]:
				for i in self.i_mutex[state-1][action]:
						if i in pair_action:
							pair_action.remove(i)
							pair_action.remove(action)
							if not pair_action:
								temp = []
								for key in literal:
									if key == -1:
										temp.append("~"+key)
									else:
										temp.append(key)
								is_mutexes.append(temp)
		self.is_mutex[state] = is_mutexes										
		

	def printAction(self, state):
		print "Action at state -",state,":"
		c_actions = self.action_state[state]
		states = self.states[state]
		for state in states:
			if(states[state] == 2):
				print state,"--> no-op -->",state
				state = "~"+state
				print state,"--> no-op -->",state
			elif states[state] == -1:
				state = "~"+state
				print state,"--> no-op -->",state
			else:
				print state,"--> no-op -->",state
		for action in c_actions:
			pre_cond = []
			effects = []
			for x in self.actions[action][0]:
				if self.actions[action][0][x] == -1:
					pre_cond.append("~"+x)
				else:
					pre_cond.append(x)
			for x in self.actions[action][1]:
				if self.actions[action][1][x] == -1:
					effects.append("~"+x)
				else:
					effects.append(x)

			print pre_cond,"-->", action,"-->",effects

	def printStates(self,state):
		print "Literals at state -",state,":"
		c_states = self.states[state]
		st = []
		for x in c_states:
			if c_states[x] == 2:
				st.append("~"+x)
				st.append(x)
			elif c_states[x] == -1:
				st.append("~"+x)
			else:
				st.append(x)
		print st
		

"""
    Main method : CookOmelette.py
    Arguments: filPath
"""  
if __name__ == "__main__":
        # param = sys.argv
        # pddl = param[1]

        omlette = CookOmlette()
        omlette.populatePDDL()
        omlette.cookOmlette()
		