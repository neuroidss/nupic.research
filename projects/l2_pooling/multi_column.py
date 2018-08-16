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

"""
This file creates simple experiment to test a single column L4-L2 network.
"""

import random

from htmresearch.frameworks.layers.object_machine_factory import (
  createObjectMachine
)
from htmresearch.frameworks.layers.l2_l4_inference import L4L2Experiment



def runLateralDisambiguation(noiseLevel=None, profile=False):
  """
  Runs a simple experiment where two objects share a (location, feature) pair.
  At inference, one column sees that ambiguous pair, and the other sees a
  unique one. We should see the first column rapidly converge to a
  unique representation.

  Parameters:
  ----------------------------
  @param    noiseLevel (float)
            Noise level to add to the locations and features during inference

  @param    profile (bool)
            If True, the network will be profiled after learning and inference

  """
  exp = L4L2Experiment(
    "lateral_disambiguation",
    numCorticalColumns=2,
  )

  objects = createObjectMachine(
    machineType="simple",
    numInputBits=20,
    sensorInputSize=1024,
    externalInputSize=1024,
    numCorticalColumns=2,
  )
  objects.addObject([(1, 1), (2, 2)])
  objects.addObject([(1, 1), (3, 2)])

  exp.learnObjects(objects.provideObjectsToLearn())
  if profile:
    exp.printProfile()

  inferConfig = {
    "noiseLevel": noiseLevel,
    "numSteps": 6,
    "pairs": {
      # this should activate 0 and 1
      0: [(1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)],
      # this should activate 1
      1: [(3, 2), (3, 2), (3, 2), (3, 2), (3, 2), (3, 2)]
    }
  }

  exp.infer(objects.provideObjectToInfer(inferConfig), objectName=1)
  if profile:
    exp.printProfile()

  exp.plotInferenceStats(
    fields=["L2 Representation",
            "Overlap L2 with object",
            "L4 Representation"],
    onePlot=False,
  )



def runDisambiguationByUnions(noiseLevel=None, profile=False):
  """
  Runs a simple experiment where an object is disambiguated as each column
  recognizes a union of two objects, and the real object is the only
  common one.

  Parameters:
  ----------------------------
  @param    noiseLevel (float)
            Noise level to add to the locations and features during inference

  @param    profile (bool)
            If True, the network will be profiled after learning and inference

  """
  exp = L4L2Experiment(
    "disambiguation_unions",
    numCorticalColumns=2,
  )

  objects = createObjectMachine(
    machineType="simple",
    numInputBits=20,
    sensorInputSize=1024,
    externalInputSize=1024,
    numCorticalColumns=2,
  )
  objects.addObject([(1, 1), (2, 2)])
  objects.addObject([(2, 2), (3, 3)])
  objects.addObject([(3, 3), (4, 4)])

  exp.learnObjects(objects.provideObjectsToLearn())
  if profile:
    exp.printProfile()

  inferConfig = {
    "numSteps": 6,
    "noiseLevel": noiseLevel,
    "pairs": {
      # this should activate 1 and 2
      0: [(2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2)],
      # this should activate 2 and 3
      1: [(3, 3), (3, 3), (3, 3), (3, 3), (3, 3), (3, 3)]
    }
  }

  exp.infer(objects.provideObjectToInfer(inferConfig), objectName=1)
  if profile:
    exp.printProfile()

  exp.plotInferenceStats(
    fields=["L2 Representation",
            "Overlap L2 with object",
            "L4 Representation"],
    onePlot=False,
  )



def runStretch(noiseLevel=None, profile=False):
  """
  Stretch test that learns a lot of objects.

  Parameters:
  ----------------------------
  @param    noiseLevel (float)
            Noise level to add to the locations and features during inference

  @param    profile (bool)
            If True, the network will be profiled after learning and inference

  """
  exp = L4L2Experiment(
    "stretch_L10_F10_C2",
    numCorticalColumns=2,
  )

  objects = createObjectMachine(
    machineType="simple",
    numInputBits=20,
    sensorInputSize=1024,
    externalInputSize=1024,
    numCorticalColumns=2,
  )
  objects.createRandomObjects(10, 10, numLocations=10, numFeatures=10)
  print "Objects are:"
  for object, pairs in objects.objects.iteritems():
    print str(object) + ": " + str(pairs)

  exp.learnObjects(objects.provideObjectsToLearn())
  if profile:
    exp.printProfile(reset=True)

  # For inference, we will check and plot convergence for object 0. We create a
  # sequence of random sensations for each column.  We will present each
  # sensation for 4 time steps to let it settle and ensure it converges.
  objectCopy1 = [pair for pair in objects[0]]
  objectCopy2 = [pair for pair in objects[0]]
  objectCopy3 = [pair for pair in objects[0]]
  random.shuffle(objectCopy1)
  random.shuffle(objectCopy2)
  random.shuffle(objectCopy3)

  # stay multiple steps on each sensation
  objectSensations1 = []
  for pair in objectCopy1:
    for _ in xrange(4):
      objectSensations1.append(pair)

  # stay multiple steps on each sensation
  objectSensations2 = []
  for pair in objectCopy2:
    for _ in xrange(4):
      objectSensations2.append(pair)

  # stay multiple steps on each sensation
  objectSensations3 = []
  for pair in objectCopy3:
    for _ in xrange(4):
      objectSensations3.append(pair)

  inferConfig = {
    "numSteps": len(objectSensations1),
    "noiseLevel": noiseLevel,
    "pairs": {
      0: objectSensations1,
      1: objectSensations2,
      # 2: objectSensations3,  # Uncomment for 3 columns
    }
  }

  exp.infer(objects.provideObjectToInfer(inferConfig), objectName=0)
  if profile:
    exp.printProfile()

  exp.plotInferenceStats(
    fields=["L2 Representation",
            "Overlap L2 with object",
            "L4 Representation"],
    onePlot=False,
  )



def runAmbiguities(noiseLevel=None, profile=False):
  """
  Runs an experiment where three objects are being learnt, but share many
  patterns. At inference, only one object is being moved over, and we should
  see quick convergence.

  Parameters:
  ----------------------------
  @param    noiseLevel (float)
            Noise level to add to the locations and features during inference

  @param    profile (bool)
            If True, the network will be profiled after learning and inference

  """
  exp = L4L2Experiment(
    "ambiguities",
    numCorticalColumns=2,
  )

  objects = createObjectMachine(
    machineType="simple",
    numInputBits=20,
    sensorInputSize=1024,
    externalInputSize=1024,
    numCorticalColumns=2,
  )
  objects.addObject([(1, 1), (2, 1), (3, 3)])
  objects.addObject([(2, 2), (3, 3), (2, 1)])
  objects.addObject([(3, 1), (2, 1), (1, 2)])

  exp.learnObjects(objects.provideObjectsToLearn())
  if profile:
    exp.printProfile()

  inferConfig = {
    "numSteps": 6,
    "noiseLevel": noiseLevel,
    "pairs": {
      0: [(2, 1), (2, 1), (3, 3), (2, 2), (2, 2), (2, 2)],
      1: [(3, 3), (3, 3), (3, 3), (2, 2), (2, 1), (2, 1)]
    }
  }

  exp.infer(objects.provideObjectToInfer(inferConfig), objectName=1)
  if profile:
    exp.printProfile()

  exp.plotInferenceStats(
    fields=["L2 Representation",
            "Overlap L2 with object",
            "L4 Representation"],
    onePlot=False,
  )



if __name__ == "__main__":
  # simple disambiguation by another cortical column
  runLateralDisambiguation()

  # disambiguation between two cortical columns on ambiguous patterns
  runDisambiguationByUnions()

  # stretch experiment with a lot of objects
  runStretch()

  # experiment with a lot of ambiguities between patterns and objects
  runAmbiguities()
