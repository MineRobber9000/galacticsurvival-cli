import stardate, utils

class Saveable:
	"""Superclass that provides to_dict and from_dict. Configured by class attributes."""
	# Values that can just be stored.
	SIMPLE_STORABLES = []
	# Values that need transforming to store.
	TRANSFORMS = {}
	# The transforms, but in reverse (for loading).
	REV_TRANSFORMS = {}

	def to_dict(self):
		ret = dict()
		for attr in self.SIMPLE_STORABLES:
			ret[attr]=getattr(self,attr)
		for attr in self.TRANSFORMS.keys():
			ret[attr]=self.TRANSFORMS[attr](getattr(self,attr))
		return ret

	@classmethod
	def from_dict(cls,d):
		ret = cls()
		for attr in cls.SIMPLE_STORABLES:
			setattr(ret,attr,d[attr])
		for attr in cls.REV_TRANSFORMS.keys():
			setattr(ret,attr,cls.REV_TRANSFORMS[attr](d[attr]))
		return ret

class Camp(Saveable):
	SIMPLE_STORABLES = ["name","survivors","rations","water","coins","approval_rating"]
	TRANSFORMS = {"date": stardate.Stardate.format}
	REV_TRANSFORMS = {"date": stardate.Stardate.from_string}
	GOOD_APPROVAL = ["Everyone is in high spirits. We'll make it through this."]
	MEH_APPROVAL = ["There are murmurs of discontent."]
	BAD_APPROVAL = ["The murmurs of discontent have become a roar. You'd better watch your back."]
	def __init__(self):
		self.name = ""
		self.date = stardate.Stardate()
		self.survivors = 0
		self.rations = 0
		self.water = 0
		self.coins = 0
		self.approval_rating = 100
	def initialize(self,rng):
		randint = rng.randint
		self.name = " ".join(["GSD",str(randint(1,999999)).zfill(6)+rng.choice("abcdefghijklmnopqrstuvwxyz")])
		# Stardate is some time during the Alpha cycle
		self.date.cycle = 1
		self.date.year = randint(1,24)
		self.date.month = randint(1,24)
		self.date.day = randint(1,30)
		# Start with anywhere from 5 to 20 survivors
		self.survivors = randint(5,20)
		# Enough rations and water to last a month
		self.rations = 30 * 3 * self.survivors # 3 rations a day
		self.water = (80 + self.survivors) * 30 # 80 gallons a day + 1 gallon per survivor worst case scenario
		if self.date.month<13: # dry season starts get 3 times as much water because water is harder to come by in the dry season
			self.water *= 3
		# 100 coins to start you off
		self.coins = 100
		# assume an approval rating of 80 to 100 to start
		self.approval_rating = randint(80,100)
	def get_approval_message(self,rng):
		if self.approval_rating >= 75:
			return rng.choice(self.GOOD_APPROVAL)
		if self.approval_rating >= 45:
			return rng.choice(self.MEH_APPROVAL)
		return rng.choice(self.BAD_APPROVAL)
	def probability_mutiny_ending(self):
		if self.approval_rating >= 45:
			return 0 # no chance of mutiny if everyone's at most non-plussed
		# formula for the probability of a mutiny is the approval rating, divided by 45, raised to the fourth
		return ((45-self.approval_rating)/45)**4
	def affect_approval(self,d):
		self.approval_rating+=d
		if self.approval_rating<0: self.approval_rating=0
		if self.approval_rating>100: self.approval_rating=100

class Scout(Saveable):
	SIMPLE_STORABLES = ["rations","water","artifacts","attack_avoidance","carrying","mission_started","mission_length","focus","difficulty"]
	def __init__(self):
		self.rations = 50
		self.water = 50
		self.artifacts = 50
		self.attack_avoidance = 50
		self.carrying = dict()
		self.mission_started = False
		self.mission_length = 0
		self.focus = None
		self.difficulty = "medium"
	def chances(self,focus=None,is_wet_season=False):
		rations = self.rations
		water = self.water
		artifacts = self.artifacts
		attacked = 100 - self.attack_avoidance
		if focus=="rations": # Focus on finding rations: +15 Rations rating
			rations += 15
		elif focus=="water": # Focus on finding water: +15 Water rating
			water += 15
		elif focus=="artifacts": # Focus on finding artifacts: +15 Artifacts rating
			artifacts += 15
		elif focus=="not_attacked": # Focus on not getting attacked: Halves chance of being attacked at cost of -20 to Rations, Water, and Artifacts ratings
			rations -= 20
			water -= 20
			artifacts -= 20
			attacked = attacked // 2
		# you get the water focus bonus permanently during the wet season
		if is_wet_season: water += 15
		# chance of nothing happening is 100 - average of the other choices
		calm = 100 - (rations+water+artifacts+attacked)/4
		if calm<1: calm = 1
		return ["rations", "water", "artifacts", "attacked", "nothing"], [rations, water, artifacts, attacked, calm]
	def handle_rations(self,rng,is_wet_season):
		# Finding rations: in easy modes, 10 to 20 rations at a time
		if self.difficulty in ("very_easy","easy"):
			return {"rations":rng.randint(10,20)}
		elif self.difficulty == "medium": # 5 to 10
			return {"rations":rng.randint(5,10)}
		elif self.difficulty == "hard": # 1 to 5
			return {"rations":rng.randint(1,5)}
		elif self.difficulty == "very_hard": # 1 to 3
			return {"rations":rng.randint(1,3)}
	def handle_water(self,rng,is_wet_season):
		# Finding water: in easy modes, 40 to 100 gallons at a time (doubled in wet season)
		if self.difficulty in ("very_easy","easy"):
			return {"water":rng.randint(40,100) * (2 if is_wet_season else 1)}
		elif self.difficulty=="very_hard":
			return {"water":rng.randint(10,25) * (2 if is_wet_season else 1)}
		else:
			return {"water":rng.randint(20,50) * (2 if is_wet_season else 1)}
	def handle_artifacts(self,rng,is_wet_season):
		# Finding artifacts: in easy modes, 1 to 100 with a mode of 10
		if self.difficulty in ("very_easy","easy"):
			return {"coins":int(rng.triangular(1,100,10))}
		elif self.difficulty == "medium": # 1 to 10 with a mode of 2
			return {"coins":int(rng.triangular(1,10,2))}
		elif self.difficulty == "hard": # 1 to 5 with a mode of 2
			return {"coins":int(rng.triangular(1,5,2))}
		elif self.difficulty == "very_hard": # just 1
			return {"coins":1}
	def handle_attacked(self,rng,is_wet_season):
		# Getting attacked: .01% chance of killing the attacking beast; otherwise, lose anywhere from 25 to 50% of what we were carrying
		# On very easy mode, 1% chance of killing the attacking beast
		if rng.random()<(0.0001 if self.difficulty!="very_easy" else .01):
			return {"rations":rng.randint(500,1000)} # 500-1000 rations for a dead beast
		if self.difficulty=="very_hard": # on very hard mode, lose 75 to 100% of what you're carrying
			lost_percentage = rng.triangular(0.25,0.5,0.3) + 0.5
			if lost_percentage > 1: lost_percentage = 1 # should never happen but who knows
			return {"rations":int(self.carrying.get("rations",0)*-lost_percentage),"water":int(self.carrying.get("water",0)*-lost_percentage),"coins":int(self.carrying.get("coins",0)*-lost_percentage)}
		else: # otherwise, lose 5 to 20 of everything you're carrying
			outcome = dict()
			for key in "rations water coins".split():
				outcome[key] = -min(rng.randint(5,20),self.carrying.get(key,0))
			return outcome
	def handle_nothing(self,rng,is_wet_season):
		# Does nothing.
		return {}
	def set_mission(self,length,focus):
		self.mission_started = False
		self.mission_length = length
		self.focus = focus
	def events(self,date,rng):
		if self.mission_length==0: return {720:dict(type="nothing")}
		self.mission_length-=1
		start, end = 0, 1440
		retval = dict()
		if not self.mission_started: # first day starts at 0600
			start = 361
			retval[360]=dict(type="start_mission")
			self.mission_started = True
		if self.mission_length==0: # last day ends at 1800
			end = 1080
			retval[1080]=dict(type="end_mission")
		is_wet_season = date.month>12
		for minute in range(start,end):
			event = rng.choices(*self.chances(self.focus,is_wet_season))[0]
			if not hasattr(self,"handle_"+event): raise AttributeError(f"The RNG somehow returned unimplemented event {event}")
			outcome = getattr(self,"handle_"+event)(rng,is_wet_season)
			for k in outcome:
				self.carrying[k] = self.carrying.get(k,0)+outcome[k]
			retval[minute]=dict(type=event,outcome=outcome)
		return retval
	def report(self):
		print("Rations:",utils.letter_grade(self.rations))
		print("Water:",utils.letter_grade(self.water))
		print("Artifacts:",utils.letter_grade(self.artifacts))
		print("Attack Avoidance:",utils.letter_grade(self.attack_avoidance))
		if self.mission_length>0:
			print("Currently on a mission")
			print(f"{self.mission_length} day(s) until end of mission")
			print("Focus: {}".format({"rations":"Rations","water":"Water","artifacts":"Artifacts","not_attacked":"Not getting attacked",None:"None"}[self.focus]))
		else:
			print("Not currently on a mission")
