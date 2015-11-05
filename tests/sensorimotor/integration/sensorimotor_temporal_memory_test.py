#!/usr/bin/env python
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

import unittest2 as unittest

from sensorimotor.one_d_world import OneDWorld
from sensorimotor.one_d_universe import OneDUniverse
from sensorimotor.random_one_d_agent import RandomOneDAgent

from sensorimotor.test.abstract_sensorimotor_test import (
  AbstractSensorimotorTest)



class SensorimotorTemporalMemoryTest(AbstractSensorimotorTest):

  VERBOSITY = 1
  DEFAULT_TM_PARAMS = {
    "columnDimensions": [100],
    "cellsPerColumn": 8,
    "initialPermanence": 0.5,
    "connectedPermanence": 0.6,
    "minThreshold": 20,
    "activationThreshold": 20,
    "maxNewSynapseCount": 50,
    "permanenceIncrement": 0.1,
    "permanenceDecrement": 0.02
  }


  def testSingleWorldOneBitPerPattern(self):
    """Test Sensorimotor Temporal Memory learning in a single world.
    Patterns (sensor and motor) are represented with one active bit per pattern.
    """
    self._init({"columnDimensions": [4],
                "minThreshold": 2,
                "activationThreshold": 2})

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=4, wSensor=1,
                            nMotor=3, wMotor=1)
    world = OneDWorld(universe, [0, 1, 2, 3])
    agent = RandomOneDAgent(world, 2, possibleMotorValues=set(xrange(-1, 2)))

    sequence = self._generateSensorimotorSequences(100, [agent])
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(20, [agent])
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    self._assertAllInactiveWereUnpredicted()
    self._assertSequencesOnePredictedActiveCellPerColumn()


  def testSingleWorldBasic(self):
    """Test Sensorimotor Temporal Memory learning in a single world.
    Patterns are represented as complete SDRs. No patterns are repeated.
    Prediction should be perfect.
    """
    self._init()

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)
    world = OneDWorld(universe, [0, 1, 2, 3])
    agent = RandomOneDAgent(world, 2, possibleMotorValues=set(xrange(-3, 4)))

    sequence = self._generateSensorimotorSequences(100, [agent])
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, [agent])
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    self._assertAllInactiveWereUnpredicted()
    self._assertSequencesOnePredictedActiveCellPerColumn()


  def testMultipleWorldsBasic(self):
    """Test Sensorimotor Temporal Memory learning in multiple separate worlds.
    Patterns are represented as complete SDRs. No patterns are repeated.
    Prediction should be perfect.
    """
    self._init()

    universe = OneDUniverse(debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)

    agents = []
    numWorlds = 4
    sequenceLength = 4

    for i in xrange(numWorlds):
      start = i * sequenceLength
      patterns = range(start, start + sequenceLength)
      world = OneDWorld(universe, patterns)
      agent = RandomOneDAgent(world, 2, possibleMotorValues=set(xrange(-3, 4)))
      agents.append(agent)

    sequence = self._generateSensorimotorSequences(150, agents)
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, agents)
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    self._assertAllInactiveWereUnpredicted()
    self._assertSequencesOnePredictedActiveCellPerColumn()


  def testMultipleWorldsSharedPatterns(self):
    """Test Sensorimotor Temporal Memory learning in multiple separate worlds.
    Patterns are represented as complete SDRs. Patterns are shared between
    worlds.
    All active columns should have been predicted.
    """
    self._init()

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)

    agents = []
    patternSets = [
      [3,2,1,0],
      [0,2,1,3],
      [1,2,0,3],
      [3,0,2,1],
      [1,0,2,3]
    ]

    for patterns in patternSets:
      world = OneDWorld(universe, patterns)
      agent = RandomOneDAgent(world, 2, possibleMotorValues=set([-3, -2, -1,
                                                                 1,  2, 3]))
      agents.append(agent)

    sequence = self._generateSensorimotorSequences(150, agents)
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, agents)
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    predictedInactiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedInactiveColumns())
    self.assertTrue(0 < predictedInactiveColumnsMetric.mean < 5)


  def testMultipleWorldsSharedPatternsWithSelfMovement(self):
    """Test Sensorimotor Temporal Memory learning in multiple separate worlds.
    Patterns are represented as complete SDRs. Patterns are shared between
    worlds. Allows movements with value 0 (self-movements).
    All active columns should have been predicted.
    """
    self._init()

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)

    agents = []
    patternSets = [
      [3,2,1,0],
      [0,2,1,3],
      [1,2,0,3],
      [3,0,2,1],
      [1,0,2,3]
    ]

    for patterns in patternSets:
      world = OneDWorld(universe, patterns)
      agent = RandomOneDAgent(world, 2, possibleMotorValues=set(xrange(-3, 4)))
      agents.append(agent)

    sequence = self._generateSensorimotorSequences(250, agents)
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, agents)
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    predictedInactiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedInactiveColumns())
    self.assertTrue(0 < predictedInactiveColumnsMetric.mean < 5)


  def testMultipleWorldsSharedPatternsNoSharedSubsequences(self):
    """Test Sensorimotor Temporal Memory learning in multiple separate worlds.
    Patterns are represented as complete SDRs. Patterns are shared between
    worlds. Worlds have no shared subsequences.
    All active columns should have been predicted.
    All inactive columns should have been unpredicted.
    Patterns in different worlds should have different cell representations.
    """
    self._init()

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)

    agents = []
    patterns = range(4)
    for _ in xrange(2):
      world = OneDWorld(universe, patterns)
      agent = RandomOneDAgent(world, 2, possibleMotorValues=set([-3, -2, -1,
                                                                 1,  2, 3]))
      agents.append(agent)
      patterns = list(patterns)  # copy
      patterns.reverse()

    sequence = self._generateSensorimotorSequences(150, agents)
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, agents)
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    predictedInactiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedInactiveColumns())
    self._assertAllInactiveWereUnpredicted()
    self._assertSequencesOnePredictedActiveCellPerColumn()
    self._assertOneSequencePerPredictedActiveCell()


  def testMultipleWorldsSharedPatternsNoSharedSubsequencesWithSelfMovement(self):
    """Test Sensorimotor Temporal Memory learning in multiple separate worlds.
    Patterns are represented as complete SDRs. Patterns are shared between
    worlds. Worlds have no shared subsequences. Allows movements with value 0
    (self-movements).
    All active columns should have been predicted.
    All inactive columns should have been unpredicted.
    Patterns in different worlds should have different cell representations.
    """
    self._init()

    universe = OneDUniverse(debugSensor=True, debugMotor=True,
                            nSensor=100, wSensor=10,
                            nMotor=70, wMotor=10)

    agents = []
    patterns = range(4)
    for _ in xrange(2):
      world = OneDWorld(universe, patterns)
      agent = RandomOneDAgent(world, 2, possibleMotorValues=set(xrange(-3, 4)))
      agents.append(agent)
      patterns = list(patterns)  # copy
      patterns.reverse()

    sequence = self._generateSensorimotorSequences(150, agents)
    self._feedTM(sequence)

    sequence = self._generateSensorimotorSequences(100, agents)
    self._testTM(sequence)

    self._assertAllActiveWerePredicted(universe)
    predictedInactiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedInactiveColumns())
    # Note: There will be extra predictions because transitions are shared
    # between the worlds (the self-movements)
    self.assertTrue(0 < predictedInactiveColumnsMetric.mean < 5)
    self._assertSequencesOnePredictedActiveCellPerColumn()
    self._assertOneSequencePerPredictedActiveCell()


  # ==============================
  # Helper functions
  # ==============================

  def _assertAllActiveWerePredicted(self, universe):
    unpredictedActiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTraceUnpredictedActiveColumns())
    predictedActiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedActiveColumns())

    self.assertEqual(unpredictedActiveColumnsMetric.sum, 0)

    self.assertEqual(predictedActiveColumnsMetric.min, universe.wSensor)
    self.assertEqual(predictedActiveColumnsMetric.max, universe.wSensor)


  def _assertAllInactiveWereUnpredicted(self):
    predictedInactiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedInactiveColumns())

    self.assertEqual(predictedInactiveColumnsMetric.sum, 0)


  def _assertAllActiveWereUnpredicted(self, universe):
    unpredictedActiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTraceUnpredictedActiveColumns())
    predictedActiveColumnsMetric = self.tm.mmGetMetricFromTrace(
      self.tm.mmGetTracePredictedActiveColumns())

    self.assertEqual(predictedActiveColumnsMetric.sum, 0)

    self.assertEqual(unpredictedActiveColumnsMetric.min, universe.wSensor)
    self.assertEqual(unpredictedActiveColumnsMetric.max, universe.wSensor)


  def _assertSequencesOnePredictedActiveCellPerColumn(self):
    metric = self.tm.mmGetMetricSequencesPredictedActiveCellsPerColumn()
    self.assertEqual(metric.min, 1)
    self.assertEqual(metric.max, 1)


  def _assertOneSequencePerPredictedActiveCell(self):
    metric = self.tm.mmGetMetricSequencesPredictedActiveCellsShared()
    self.assertEqual(metric.min, 1)
    self.assertEqual(metric.max, 1)


if __name__ == "__main__":
  unittest.main()

