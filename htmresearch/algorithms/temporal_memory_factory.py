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

"""Module providing a factory for instantiating a temporal memory instance."""

from nupic.research.temporal_memory import TemporalMemory
from htmresearch.algorithms.general_temporal_memory import (
  GeneralTemporalMemory)
from nupic.research.monitor_mixin.temporal_memory_monitor_mixin import (
  TemporalMemoryMonitorMixin)

class MonitoredTemporalMemory(TemporalMemoryMonitorMixin, TemporalMemory): pass

class TemporalMemoryTypes(object):
  """ Enumeration of supported classification model types, mapping userland
  identifier to constructor.  See createModel() for actual factory method
  implementation.
  """
  general = GeneralTemporalMemory
  tm = TemporalMemory
  tmMixin = MonitoredTemporalMemory


  @classmethod
  def getTypes(cls):
    """ Get sequence of acceptable model types.  Iterates through class
    attributes and separates the user-defined enumerations from the default
    attributes implicit to Python classes. i.e. this function returns the names
    of the attributes explicitly defined above.
    """

    for attrName in dir(cls):
      attrValue = getattr(cls, attrName)
      if (isinstance(attrValue, type)):
        yield attrName # attrName is an acceptable model name and


def createModel(modelName, **kwargs):
  """
  Return a classification model of the appropriate type. The model could be any
  supported subclass of ClassficationModel based on modelName.

  @param modelName (str)  A supported temporal memory type

  @param kwargs    (dict) Constructor argument for the class that will be
                          instantiated. Keyword parameters specific to each
                          model type should be passed in here.
  """

  if modelName not in TemporalMemoryTypes.getTypes():
    raise RuntimeError("Unknown model type: " + modelName)

  return getattr(TemporalMemoryTypes, modelName)(**kwargs)


def getConstructorArguments(modelName):
  """
  Return a list of strings corresponding to constructor arguments for the
  given model type.

  @param modelName (str)  A supported temporal memory type

  """

  if modelName not in TemporalMemoryTypes.getTypes():
    raise RuntimeError("Unknown model type: " + modelName)

  return getattr(TemporalMemoryTypes, modelName)(**kwargs)
