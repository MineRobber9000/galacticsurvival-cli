"""A simple implementation of the PCG32 random number generator."""
import random, os

class PCG32(random.Random):
	# The multiplicative constant for the internal state.
	CONSTANT = 6364136223846793005
	# A 64-bit bitmask, used to enforce integer overflow.
	BITMASK = (2**64)-1
	# A 32-bit bitmask, also used to enforce integer overflow (but for `uint32_t` in the C source).
	BITMASK32 = (2**32)-1
	# The amount of bits in the seed that should be dedicated to determining a stream.
	STREAM_BITS = 8
	# The state version. Used in case internals need changing.
	VERSION = 1
	def seed(self,initseed=None,version=None):
		"""Seeds the PCG32 instance."""
		# If a seed wasn't provided, take one from os.urandom.
		if initseed is None: initseed = os.urandom(8)
		# Get a number seed from whatever we just took in
		assert isinstance(initseed,(int,str,bytes,bytearray)), "Cannot use seed of type other than int, str, bytes, or bytearray."
		if isinstance(initseed,(str,bytes,bytearray)):
			if isinstance(initseed,str):
				initseed = initseed.encode()
			initseed = int.from_bytes(initseed,'big')
		initseed = initseed & self.BITMASK
		# Since Python only lets us take in a seed, use said seed to initialize a stream
		initseq = initseed & (2**self.STREAM_BITS)-1
		initseed = (initseed >> self.STREAM_BITS)^initseed
		# now call the direct_seed function, which handles seed and stream
		self.direct_seed(initseed,initseq)
	def direct_seed(self, initseed, initseq=0):
		"""If you want more control over seed and stream, this is the function to call."""
		self._buffer = 0
		self._buffer_bits = 0
		self.state = 0
		self.inc = (initseq << 1 | 1) & self.BITMASK
		self.rand_raw()
		self.state = (self.state + initseed) & self.BITMASK
		self.rand_raw()
	def getstate(self):
		return (self.VERSION,self.state,self.inc,self._buffer,self._buffer_bits)
	def setstate(self,state):
		if state[0]==1:
			self.state, self.inc, self._buffer, self._buffer_bits = state[1:]
		else:
			raise ValueError(f"Passed state of version {state[0]} into PCG32 object of version {self.VERSION}")
	def rand_raw(self):
		"""Generates a random 32-bit number. Used by the other functions."""
		oldstate = self.state
		self.state = (oldstate * self.CONSTANT + self.inc) & self.BITMASK
		xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & self.BITMASK32
		rot = oldstate>>59 # also technically a uint32_t in the C source code but I think I'm safe
		return ((xorshifted >> rot) | (xorshifted << ((-rot)&31))) & self.BITMASK32
	def random(self):
		"""Returns a random floating-point number."""
		return self.rand_raw()/self.BITMASK32
	def getrandbits(self,k):
		if self._buffer_bits < k:
			self._buffer = (self.rand_raw()<<self._buffer_bits)+self._buffer
			self._buffer_bits += 32
		retval = self._buffer & (2**k)-1
		self._buffer >>= k
		self._buffer_bits -= k
		return retval
