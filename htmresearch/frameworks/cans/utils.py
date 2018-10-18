# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2018, Numenta, Inc.  Unless you have an agreement
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
from scipy import signal
import os



def mexican_hat(x, sigma=1.):
  a = 2./ ( np.sqrt(3*sigma) * np.power(np.pi,0.25 ) )
  b = (1. - (x/sigma)**2 )
  c = np.exp( - x**2/(2.*sigma**2))
  return a*b*c



def W_zero(x):
  a = 1.0
  lambda_net = 4.0
  beta = 3.0 / lambda_net**2
  gamma = 1.05 * beta

  x_length_squared = x**2

  return a*np.exp(-gamma*x_length_squared) - np.exp(-beta*x_length_squared)



def create_W(J, D):
  n = D.shape[0]
  W = np.zeros(D.shape)
  W = J(D)

  np.fill_diagonal(W, 0.0)

  for i in range(n):
    W[i,:] -= np.mean(W[i,:])

  return W



def normalize(x):
  x_   = x - np.amin(x)
  amax = np.amax(x_)

  if amax != 0.:
    x_ = x_/amax

  return x_



def compute_scales(W):
  num_gc = W.shape[1]
  scales = np.zeros(num_gc)
  for i in range(num_gc):
    f   = (W[:,i] > .1).astype(float)
    df  = f[1:] - f[:-1]
    ind = np.where(df == -1.)[0]
    ind = ind.astype(float)

    if len(ind) > 1:
      scales[i] = np.mean(ind[1:] - ind[:-1])

    else:
      scales[i] = -1.

  return scales
