from objs import Camp, Scout, Saveable
from pcg32 import PCG32

def _set_pcg32_state(x):
	ret = PCG32(0)
	ret.setstate(x)
	return ret

class Save(Saveable):
	SIMPLE_STORABLES = ["game_over","days_without_food","days_without_water"]
	TRANSFORMS = {"camp": Camp.to_dict, "scout_a": Scout.to_dict, "scout_b": Scout.to_dict, "scout_c": Scout.to_dict, "rng": PCG32.getstate}
	REV_TRANSFORMS = {"camp": Camp.from_dict, "scout_a": Scout.from_dict, "scout_b": Scout.from_dict, "scout_c": Scout.from_dict, "rng": _set_pcg32_state}
	def __init__(self):
		self.camp = Camp()
		self.scout_a = Scout()
		self.scout_b = Scout()
		self.scout_c = Scout()
		self.rng = PCG32()
		self.game_over = False
		self.days_without_food = 0
		self.days_without_water = 0
		self.set_difficulty("medium")
	def initialize(self):
		self.camp.initialize(self.rng)
	def set_difficulty(self,difficulty):
		self.difficulty = difficulty
		self.scout_a.difficulty = difficulty
		self.scout_b.difficulty = difficulty
		self.scout_c.difficulty = difficulty
