class Stardate:
	GREEK_LETTERS = "Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Lamda Mu Nu Xi Omicron Pi Rho Sigma Tau Upsilon Phi Chi Psi Omega".split()
	def __init__(self,year=1,month=1,day=1,cycle=1):
		self.year = year
		self.month = month
		self.day = day
		self.cycle = cycle
		self.normalize()
	def normalize(self):
		while self.day > 30:
			self.day -= 30
			self.month += 1
		while self.month > 24:
			self.month -= 24
			self.year += 1
		while self.year > 24:
			self.year -= 24
			self.cycle += 1
	@property
	def next(self):
		return self.__class__(self.year,self.month,self.day+1,self.cycle)
	def format(self):
		return "{} {} {!s} {}".format(self.GREEK_LETTERS[self.year-1],self.GREEK_LETTERS[self.month-1],self.day,self.GREEK_LETTERS[self.cycle-1])
	def __str__(self):
		return self.format()
	@classmethod
	def from_string(cls,s):
		s = s.strip().split()
		s = [int(x) if x.isdigit() else cls.GREEK_LETTERS.index(x)+1 for x in s]
		return cls(*s)
	def days_until(self,sd):
		return sd.days_since(self)
	def days_since(self,sd):
		now = ((self.cycle-1) * 24 * 24 * 30) + ((self.year-1) * 24 * 30) + ((self.month-1) * 30) + self.day - 1
		then = ((sd.cycle-1) * 24 * 24 * 30) + ((sd.year-1) * 24 * 30) + ((sd.month-1) * 30) + sd.day - 1
		return now - then

MAX_STARDATE = Stardate(len(Stardate.GREEK_LETTERS),len(Stardate.GREEK_LETTERS),30,len(Stardate.GREEK_LETTERS))
