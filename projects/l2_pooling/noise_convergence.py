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
This file plots the convergence of L4-L2 as you increase the amount of noise.

"""

import os
import numpy
import cPickle
from multiprocessing import cpu_count
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42

from htmresearch.frameworks.layers.multi_column_convergence_experiment import (
  runExperiment, runExperimentPool
)


def plotConvergenceByObjectMultiColumn(results, objectRange, columnRange):
  """
  Plots the convergence graph: iterations vs number of objects.
  Each curve shows the convergence for a given number of columns.
  """
  ########################################################################
  #
  # Accumulate all the results per column in a convergence array.
  #
  # Convergence[c,o] = how long it took it to converge with f unique features
  # and c columns.

  convergence = numpy.zeros((max(columnRange), max(objectRange) + 1))
  for r in results:
    if r["numColumns"] in columnRange:
      convergence[r["numColumns"] - 1, r["numObjects"]] += r["convergencePoint"]

  convergence /= numTrials

  # print "Average convergence array=", convergence

  ########################################################################
  #
  # Create the plot. x-axis=
  plt.figure()
  plotPath = os.path.join("plots", "convergence_by_object_multicolumn.jpg")

  # Plot each curve
  legendList = []
  colorList = ['r', 'b', 'g', 'm', 'c', 'k', 'y']

  for i in range(len(columnRange)):
    c = columnRange[i]
    print "columns={} objectRange={} convergence={}".format(
      c, objectRange, convergence[c-1,objectRange])
    if c == 1:
      legendList.append('1 column')
    else:
      legendList.append('{} columns'.format(c))
    plt.plot(objectRange, convergence[c-1,objectRange],
             color=colorList[i])

  # format
  plt.legend(legendList, loc="upper left", prop={'size':10})
  plt.xlabel("Number of objects in training set")
  plt.xticks(range(0,max(objectRange)+1,10))
  plt.yticks(range(0,int(convergence.max())+2))
  plt.ylabel("Average number of touches")
  plt.title("Object recognition with multiple columns (unique features = 5)")

    # save
  plt.savefig(plotPath)
  plt.close()

def plotAccuracyByNoiseLevelAndColumnRange(results,noiseRange,columnRange):
  plt.figure()
  plotPath = os.path.join("plots", "classification_accuracy_by_noiselevelAndColumnNum.jpg")

  # Plot each curve
  accuracyList = []
  legendList = []
  colorList = ['r', 'b', 'g', 'm', 'c', 'k', 'y']

  for k in range(len(columnRange)):
    c = columnRange[k]
    for i in range(len(noiseRange)):
      accuracyList.append(results[k*len(noiseRange)+i].get('classificationAccuracy'))
    if c == len(columnRange):
      legendList.append('1 column')
    else:
      legendList.append('{} columns'.format(len(columnRange)-k))
    plt.plot(noiseRange, accuracyList, colorList[k])
    accuracyList = []

  # format
  plt.legend(legendList, loc="upper left", prop={'size': 10})
  plt.xlabel("Noise level added")
  plt.ylabel("classification accuracy")
  plt.title("Classification accuracy VS. noise level")

  # save
  plt.savefig(plotPath)
  plt.close()

def plotAccuracyByActivationThreshold(results_by_thresholds, activation_thresholds):
  plt.figure()
  plotPath = os.path.join("plots", "classification_accuracy_by_activationThreshold.jpg")

  plt.plot(activation_thresholds, results_by_thresholds)


  # format
  plt.xlabel("activationThresholdDistal")
  plt.ylabel("classification accuracy")
  plt.title("Classification accuracy VS. activationThresholdDistal")

  # save
  plt.savefig(plotPath)
  plt.close()

if __name__ == "__main__":

  # This is how you run a specific experiment in single process mode. Useful
  # for debugging, profiling, etc.
  if False:
    results = runExperiment(
                  {
                    "numObjects": 100,
                    "numPoints": 10,
                    "numLocations": 10,
                    "numFeatures": 10,
                    "numColumns": 1,
                    "trialNum": 4,
                    "featureNoise": 0.6,
                    "plotInferenceStats": False,  # Outputs detailed graphs
                    "settlingTime": 3,
                    "includeRandomLocation": False,
                    "l2Params": {"cellCount": 4096*4, "sdrSize": 40*2, "activationThresholdDistal": 14}
                  }
    )

  # This is for specifically testing how the distal activation threshold affect
  # the classification results
  if True:
    activationThresholdDistalRange = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    results_by_thresholds = []
    for i in range(len(activationThresholdDistalRange)):
        results = runExperiment(
                  {
                    "numObjects": 100,
                    "numPoints": 10,
                    "numLocations": 10,
                    "numFeatures": 10,
                    "numColumns": 1,
                    "trialNum": 4,
                    "featureNoise": 0.6,
                    "plotInferenceStats": False,  # Outputs detailed graphs
                    "settlingTime": 3,
                    "includeRandomLocation": False,
                    "l2Params": {"cellCount": 4096 * 4, "sdrSize": 40 * 2, "activationThresholdDistal": i+1}
                  }
        )
        results_by_thresholds.append(results.get('classificationAccuracy'))

    plotAccuracyByActivationThreshold(results_by_thresholds,activationThresholdDistalRange)

  # Here we want to see how the number of objects affects convergence for
  # multiple columns.
  if False:
    # We run 10 trials for each column number and then analyze results
    numTrials = 1
    columnRange = [1,2,3]
    noiseRange = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
    featureRange = [10]
    objectRange = [100]

    # Comment this out if you are re-running analysis on already saved results.
    # Very useful for debugging the plots
    runExperimentPool(
                      numObjects=objectRange,
                      numLocations=[10],
                      numFeatures=featureRange,
                      numColumns=columnRange,
                      numPoints=10,
                      featureNoiseRange=noiseRange,
                      numWorkers=cpu_count() - 1,
                      #numWorkers=1,
                      nTrials=numTrials,
                      resultsName="object_convergence_noise_results.pkl")

    # Analyze results
    with open("object_convergence_noise_results.pkl","rb") as f:
      results = cPickle.load(f)
    # print results

    plotAccuracyByNoiseLevelAndColumnRange(results, noiseRange, columnRange)
    # plotConvergenceByObjectMultiColumn(results, objectRange, columnRange)
