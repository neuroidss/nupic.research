# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2016, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

import numpy as np
import math


class ScalarEncoder(object):
	"""
	Quick implementation of a scalar encoder, that is, a map that
	encodes a real valued vector x as a binary vector as outlined below.

	Idea
	----               
                       				   x							   y
	   					|--------------|----|		|------------------||           

       				   min                 max     min				   max
                    
                      
	    f(x,y)     =    [. . . . . 1 1 1 . .]	+	[. . . . . . . 1 1 1]

	"""
	def __init__(self, dimensions=1, max_values = [[0., 1.]], bits_per_axis=[1000], weight_per_axis=[20], wrap_around = False):
		self.max_values      = max_values
		self.dimensions      = dimensions
		self.bits_per_axis   = bits_per_axis
		self.weight_per_axis = weight_per_axis
		self.output_size     = np.sum(self.bits_per_axis)
		self.wrap_around     = wrap_around

	def __call__(self, x):
		return self.encode(x)

	def encode(self, x):
		y = np.zeros(self.output_size)

		for i in range(self.dimensions):
			activeBits = []
			if x[i] <= self.max_values[i][0]:
				start = 0

			elif x[i] >= self.max_values[i][1]:
				if self.wrap_around == False:
					start = self.bits_per_axis[i] - self.weight_per_axis[i]
				else:
					start = self.bits_per_axis[i]

			else:
				domainSize = self.max_values[i][1] - self.max_values[i][0]

				if self.wrap_around == False:
					binSize = domainSize/(self.bits_per_axis[i] - self.weight_per_axis[i])
				else:
					binSize = domainSize/(self.bits_per_axis[i])

				start   = int(math.floor( (x[i] - self.max_values[i][0]) /binSize))			

			activeBits = int(np.sum(self.bits_per_axis[:i])) + np.arange(start, start + self.weight_per_axis[i])%self.bits_per_axis[i]
			y[activeBits] = 1.

		return y

