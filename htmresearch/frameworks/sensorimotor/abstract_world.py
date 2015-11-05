# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2014, Numenta, Inc.  Unless you have an agreement
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

import abc



class AbstractWorld(object):
  """
  A World represents a particular (static) configuration of sensory parameters.
  Every instance of a World belongs to a single Universe, which in turn defines
  the space of possible sensory patterns and motor commands.
  """
  __metaclass__ = abc.ABCMeta


  def __init__(self, universe):
    """
    @param universe (AbstractUniverse) Universe that the world belongs to.
    """
    self.universe = universe


  def toString(self):
    """
    Human readable representation of the world
    """
    return "AbstractWorld"
