#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have an agreement
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
import json
import operator
import os
import random
import sys
import time

import numpy

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.research.monitor_mixin.trace import CountsTrace

from htmresearch.data.sequence_generator import SequenceGenerator
from htmresearch.support.sequence_prediction_dataset import HighOrderDataset


MIN_ORDER = 6
MAX_ORDER = 7
NUM_PREDICTIONS = [4]
NUM_RANDOM = 1
PERTURB_AFTER = 10000
TEMPORAL_NOISE_AFTER = float('inf')
TOTAL_ITERATION = 20000

# MIN_ORDER = 6
# MAX_ORDER = 7
# NUM_PREDICTIONS = [1]
# NUM_RANDOM = 1
# PERTURB_AFTER = 20000
# TEMPORAL_NOISE_AFTER = 6000
# TOTAL_ITERATION = 8000

NUM_SYMBOLS = SequenceGenerator.numSymbols(MAX_ORDER, max(NUM_PREDICTIONS))
RANDOM_START = NUM_SYMBOLS
RANDOM_END = NUM_SYMBOLS + 5000

MODEL_PARAMS = {
  "model": "CLA",
  "version": 1,
  "predictAheadTime": None,
  "modelParams": {
    "inferenceType": "TemporalMultiStep",
    "sensorParams": {
      "verbosity" : 0,
      "encoders": {
        "element": {
          "fieldname": u"element",
          "name": u"element",
          "type": "SDRCategoryEncoder",
          "categoryList": range(max(RANDOM_END, NUM_SYMBOLS)),
          "n": 2048,
          "w": 41
        }
      },
      "sensorAutoReset" : None,
    },
      "spEnable": False,
      "spParams": {
        "spVerbosity" : 0,
        "globalInhibition": 1,
        "columnCount": 2048,
        "inputWidth": 0,
        "numActiveColumnsPerInhArea": 40,
        "seed": 1956,
        "columnDimensions": 0.5,
        "synPermConnected": 0.1,
        "synPermActiveInc": 0.1,
        "synPermInactiveDec": 0.01,
        "maxBoost": 0.0
    },
    "tpEnable" : True,
    "tpParams": {
      "verbosity": 0,
        "columnCount": 2048,
        "cellsPerColumn": 32,
        "inputWidth": 2048,
        "seed": 1960,
        "temporalImp": "monitored_tm_py",
        "newSynapseCount": 32,
        "maxSynapsesPerSegment": 128,
        "maxSegmentsPerCell": 128,
        "initialPerm": 0.21,
        "connectedPerm": 0.50,
        "permanenceInc": 0.1,
        "permanenceDec": 0.1,
        "predictedSegmentDecrement": 0.01,
        "globalDecay": 0.0,
        "maxAge": 0,
        "minThreshold": 15,
        "activationThreshold": 15,
        "outputType": "normal",
        "pamLength": 1,
      },
      "clParams": {
        "implementation": "cpp",
        "regionName" : "CLAClassifierRegion",
        "clVerbosity" : 0,
        "alpha": 0.0001,
        "steps": "1",
      },
      "trainSPNetOnlyIfRequested": False,
    },
}



def generateSequences(numPredictions, perturbed=False):
  sequences = []

  # # Generated sequences
  # generator = SequenceGenerator(seed=42)

  # for order in xrange(MIN_ORDER, MAX_ORDER+1):
  #   sequences += generator.generate(order, numPredictions)

  # # Subutai's sequences
  # """
  # Make sure to change parameter 'categoryList' above to: "categoryList": range(18)
  # """
  # sequences = [
  #   [0, 1, 2, 3, 4, 5],
  #   [6, 3, 2, 5, 1, 7],
  #   [8, 9, 10, 11, 12, 13],
  #   [14, 1, 2, 3, 15, 16],
  #   [17, 4, 2, 3, 1, 5]
  # ]

  # # Two orders of sequences
  # sequences = [
  #   [4, 2, 5, 0],
  #   [4, 5, 2, 3],
  #   [1, 2, 5, 3],
  #   [1, 5, 2, 0],
  #   [5, 3, 6, 2, 0],
  #   [5, 2, 6, 3, 4],
  #   [1, 3, 6, 2, 4],
  #   [1, 2, 6, 3, 0]
  # ]

  # # Two orders of sequences (easier)
  # # """
  # # Make sure to change parameter 'categoryList' above to: "categoryList": range(13)
  # # """
  # sequences = [
  #   [4, 2, 5, 0],
  #   [4, 5, 2, 3],
  #   [1, 2, 5, 3],
  #   [1, 5, 2, 0],
  #   [11, 9, 12, 8, 6],
  #   [11, 8, 12, 9, 10],
  #   [7, 9, 12, 8, 10],
  #   [7, 8, 12, 9, 6]
  # ]

  # # Two orders of sequences (isolating the problem)
  # sequences = [
  #   [1, 5, 2, 0],
  #   [5, 2, 6, 3, 4]
  # ]
  # random.seed(100) # 100 fails, 300 works (results depend on order of training)

  if numPredictions == 1:
    # Hardcoded set of sequences
    if perturbed:
      sequences = [
        [6, 8, 7, 4, 2, 3, 5],
        [1, 8, 7, 4, 2, 3, 0],
        [6, 3, 4, 2, 7, 8, 0],
        [1, 3, 4, 2, 7, 8, 5],
        [0, 9, 7, 8, 5, 3, 4, 6],
        [2, 9, 7, 8, 5, 3, 4, 1],
        [0, 4, 3, 5, 8, 7, 9, 1],
        [2, 4, 3, 5, 8, 7, 9, 6]
      ]
    else:
      sequences = [
        [6, 8, 7, 4, 2, 3, 0],
        [1, 8, 7, 4, 2, 3, 5],
        [6, 3, 4, 2, 7, 8, 5],
        [1, 3, 4, 2, 7, 8, 0],
        [0, 9, 7, 8, 5, 3, 4, 1],
        [2, 9, 7, 8, 5, 3, 4, 6],
        [0, 4, 3, 5, 8, 7, 9, 6],
        [2, 4, 3, 5, 8, 7, 9, 1]
      ]

  if numPredictions == 2:
    # Hardcoded set of sequences with multiple predictions (2)
    # Make sure to set NUM_PREDICTIONS = 2 above
    if perturbed:
      sequences = [
        [4, 8, 3, 10, 9, 6, 0],
        [4, 8, 3, 10, 9, 6, 7],
        [5, 8, 3, 10, 9, 6, 1],
        [5, 8, 3, 10, 9, 6, 2],
        [4, 6, 9, 10, 3, 8, 2],
        [4, 6, 9, 10, 3, 8, 1],
        [5, 6, 9, 10, 3, 8, 7],
        [5, 6, 9, 10, 3, 8, 0],
        [4, 3, 8, 6, 1, 10, 11, 0],
        [4, 3, 8, 6, 1, 10, 11, 7],
        [5, 3, 8, 6, 1, 10, 11, 9],
        [5, 3, 8, 6, 1, 10, 11, 2],
        [4, 11, 10, 1, 6, 8, 3, 2],
        [4, 11, 10, 1, 6, 8, 3, 9],
        [5, 11, 10, 1, 6, 8, 3, 7],
        [5, 11, 10, 1, 6, 8, 3, 0]
      ]
    else:
      sequences = [
        [4, 8, 3, 10, 9, 6, 1],
        [4, 8, 3, 10, 9, 6, 2],
        [5, 8, 3, 10, 9, 6, 0],
        [5, 8, 3, 10, 9, 6, 7],
        [4, 6, 9, 10, 3, 8, 7],
        [4, 6, 9, 10, 3, 8, 0],
        [5, 6, 9, 10, 3, 8, 2],
        [5, 6, 9, 10, 3, 8, 1],
        [4, 3, 8, 6, 1, 10, 11, 9],
        [4, 3, 8, 6, 1, 10, 11, 2],
        [5, 3, 8, 6, 1, 10, 11, 0],
        [5, 3, 8, 6, 1, 10, 11, 7],
        [4, 11, 10, 1, 6, 8, 3, 7],
        [4, 11, 10, 1, 6, 8, 3, 0],
        [5, 11, 10, 1, 6, 8, 3, 2],
        [5, 11, 10, 1, 6, 8, 3, 9]
      ]

  if numPredictions == 4:
    # Hardcoded set of sequences with multiple predictions (4)
    # Make sure to set NUM_PREDICTIONS = 4 above
    if perturbed:
      sequences = [
        [7, 4, 12, 5, 14, 1, 13],
        [7, 4, 12, 5, 14, 1, 10],
        [7, 4, 12, 5, 14, 1, 6],
        [7, 4, 12, 5, 14, 1, 8],
        [11, 4, 12, 5, 14, 1, 2],
        [11, 4, 12, 5, 14, 1, 3],
        [11, 4, 12, 5, 14, 1, 0],
        [11, 4, 12, 5, 14, 1, 9],
        [7, 1, 14, 5, 12, 4, 9],
        [7, 1, 14, 5, 12, 4, 0],
        [7, 1, 14, 5, 12, 4, 3],
        [7, 1, 14, 5, 12, 4, 2],
        [11, 1, 14, 5, 12, 4, 8],
        [11, 1, 14, 5, 12, 4, 6],
        [11, 1, 14, 5, 12, 4, 10],
        [11, 1, 14, 5, 12, 4, 13],
        [9, 4, 5, 15, 6, 1, 12, 14],
        [9, 4, 5, 15, 6, 1, 12, 11],
        [9, 4, 5, 15, 6, 1, 12, 7],
        [9, 4, 5, 15, 6, 1, 12, 8],
        [13, 4, 5, 15, 6, 1, 12, 2],
        [13, 4, 5, 15, 6, 1, 12, 3],
        [13, 4, 5, 15, 6, 1, 12, 0],
        [13, 4, 5, 15, 6, 1, 12, 10],
        [9, 1, 12, 6, 15, 4, 5, 10],
        [9, 1, 12, 6, 15, 4, 5, 0],
        [9, 1, 12, 6, 15, 4, 5, 3],
        [9, 1, 12, 6, 15, 4, 5, 2],
        [13, 1, 12, 6, 15, 4, 5, 8],
        [13, 1, 12, 6, 15, 4, 5, 7],
        [13, 1, 12, 6, 15, 4, 5, 11],
        [13, 1, 12, 6, 15, 4, 5, 14]
      ]
    else:
      sequences = [
        [7, 4, 12, 5, 14, 1, 2],
        [7, 4, 12, 5, 14, 1, 3],
        [7, 4, 12, 5, 14, 1, 0],
        [7, 4, 12, 5, 14, 1, 9],
        [11, 4, 12, 5, 14, 1, 13],
        [11, 4, 12, 5, 14, 1, 10],
        [11, 4, 12, 5, 14, 1, 6],
        [11, 4, 12, 5, 14, 1, 8],
        [7, 1, 14, 5, 12, 4, 8],
        [7, 1, 14, 5, 12, 4, 6],
        [7, 1, 14, 5, 12, 4, 10],
        [7, 1, 14, 5, 12, 4, 13],
        [11, 1, 14, 5, 12, 4, 9],
        [11, 1, 14, 5, 12, 4, 0],
        [11, 1, 14, 5, 12, 4, 3],
        [11, 1, 14, 5, 12, 4, 2],
        [9, 4, 5, 15, 6, 1, 12, 2],
        [9, 4, 5, 15, 6, 1, 12, 3],
        [9, 4, 5, 15, 6, 1, 12, 0],
        [9, 4, 5, 15, 6, 1, 12, 10],
        [13, 4, 5, 15, 6, 1, 12, 14],
        [13, 4, 5, 15, 6, 1, 12, 11],
        [13, 4, 5, 15, 6, 1, 12, 7],
        [13, 4, 5, 15, 6, 1, 12, 8],
        [9, 1, 12, 6, 15, 4, 5, 8],
        [9, 1, 12, 6, 15, 4, 5, 7],
        [9, 1, 12, 6, 15, 4, 5, 11],
        [9, 1, 12, 6, 15, 4, 5, 14],
        [13, 1, 12, 6, 15, 4, 5, 10],
        [13, 1, 12, 6, 15, 4, 5, 0],
        [13, 1, 12, 6, 15, 4, 5, 3],
        [13, 1, 12, 6, 15, 4, 5, 2]
      ]

  # print "Sequences generated:"
  # for sequence in sequences:
  #   print sequence
  # print

  return sequences



def getEncoderMapping(model):
  encoder = model._getEncoder().encoders[0][1]
  mapping = dict()

  for i in range(NUM_SYMBOLS):
    mapping[i] = set(encoder.encode(i).nonzero()[0])

  return mapping



def classify(mapping, activeColumns, numPredictions):
  scores = [(len(encoding & activeColumns), i) for i, encoding in mapping.iteritems()]
  random.shuffle(scores)  # break ties randomly
  return [i for _, i in sorted(scores, reverse=True)[:numPredictions]]



class Runner(object):

  def __init__(self, numPredictions, resultsDir):
    random.seed(43)
    self.numPredictions = numPredictions

    if not os.path.exists(resultsDir):
      os.makedirs(resultsDir)

    self.resultsFile = open(os.path.join(resultsDir, "0.log"), 'w')

    self.model = ModelFactory.create(MODEL_PARAMS)
    self.model.enableInference({"predictedField": "element"})
    self.shifter = InferenceShifter()
    self.mapping = getEncoderMapping(self.model)

    self.correct = []
    self.numPredictedActiveCells = []
    self.numPredictedInactiveCells = []
    self.numUnpredictedActiveColumns = []

    self.iteration = 0
    self.perturbed = False
    self.randoms = []
    self.verbosity = 1

    self.dataset = HighOrderDataset(numPredictions=self.numPredictions)
    self.sequences = []
    self.currentSequence = []
    self.replenish_sequence()


  def replenish_sequence(self):
    if self.iteration > PERTURB_AFTER and not self.perturbed:
      print "PERTURBING"
      # self.sequences = generateSequences(self.numPredictions, perturbed=True)
      sequence, target = self.dataset.generateSequence(self.iteration, perturbed=True)
      self.perturbed = True
    else:
      sequence, target = self.dataset.generateSequence(self.iteration)
      # self.sequences = generateSequences(self.numPredictions, perturbed=False)

    # sequence = random.choice(self.sequences)

    if self.iteration > TEMPORAL_NOISE_AFTER:
      injectNoiseAt = random.randint(1, 3)
      sequence[injectNoiseAt] = random.randrange(RANDOM_START, RANDOM_END)

    # append noise element at end of sequence
    random.seed(self.iteration)
    print "seed {} start {} end {}".format(self.iteration, RANDOM_START, RANDOM_END)
    sequence.append(random.randrange(RANDOM_START, RANDOM_END))

    print "next sequence: ", sequence
    self.currentSequence += sequence


  def step(self):
    element = self.currentSequence.pop(0)

    randomFlag = (len(self.currentSequence) == 1)
    self.randoms.append(randomFlag)

    result = self.shifter.shift(self.model.run({"element": element}))
    tm = self.model._getTPRegion().getSelf()._tfdr

    tm.mmClearHistory()
    # Use custom classifier (uses predicted cells to make predictions)
    predictiveColumns = set([tm.columnForCell(cell) for cell in tm.predictiveCells])
    topPredictions = classify(self.mapping, predictiveColumns, self.numPredictions)

    truth = None if (self.randoms[-1] or
                     len(self.randoms) >= 2 and self.randoms[-2]) else self.currentSequence[0]

    correct = None if truth is None else (truth in topPredictions)

    data = {"iteration": self.iteration,
            "current": element,
            "reset": False,
            "random": randomFlag,
            "train": True,
            "predictions": topPredictions,
            "truth": truth}

    self.resultsFile.write(json.dumps(data) + '\n')
    self.resultsFile.flush()

    if self.verbosity > 0:
      print ("iteration: {0} \t"
             "current: {1} \t"
             "predictions: {2} \t"
             "truth: {3} \t"
             "correct: {4} \t").format(
        self.iteration, element, topPredictions, truth, correct)

    # replenish sequence
    if len(self.currentSequence) == 0:
      self.replenish_sequence()

    self.iteration += 1


if __name__ == "__main__":
  outdir = sys.argv[1]

  if not os.path.exists(outdir):
    os.makedirs(outdir)

  runners = []

  for numPredictions in NUM_PREDICTIONS:
    resultsDir = os.path.join(outdir,
                              "num_predictions{0}".format(numPredictions),
                              "noise_at{0}".format(TEMPORAL_NOISE_AFTER))
    runners.append(Runner(numPredictions, resultsDir))

  for i in xrange(TOTAL_ITERATION):
    for runner in runners:
      runner.step()
