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

"""
Plot temporal noise experiment result
"""
import os
from matplotlib import pyplot
import matplotlib as mpl

from plot import plotAccuracy
from plot import computeAccuracy
from plot import readExperiment
mpl.rcParams['pdf.fonttype'] = 42
pyplot.ion()
pyplot.close('all')


if __name__ == '__main__':

  experiments = [os.path.join("lstm/results", "high-order-noise",
                              "inject_noise_after0.0", "0.log"),
                 os.path.join("tm/results", "high-order-noise",
                              "inject_noise_after0.0", "0.log")]

  for experiment in experiments:
    data = readExperiment(experiment)
    (accuracy, x) = computeAccuracy(data['predictions'],
                                    data['truths'],
                                    data['iterations'],
                                    resets=data['resets'],
                                    randoms=data['randoms'])

    plotAccuracy((accuracy, x),
                 data['trains'],
                 window=100,
                 type=type,
                 label='NoiseExperiment',
                 hideTraining=True,
                 lineSize=1.0)
    pyplot.xlim([10500, 14500])
    pyplot.xlabel('Number of elements seen')
    pyplot.ylabel(' Accuracy ')

  pyplot.legend(['LSTM', 'HTM'])
  pyplot.savefig('./result/temporal_noise_train_with_noise.pdf')


  experiments = [os.path.join("lstm/results", "high-order-noise",
                              "inject_noise_after12000.0", "0.log"),
                 os.path.join("tm/results", "high-order-noise",
                              "inject_noise_after12000.0", "0.log")]

  pyplot.close('all')
  for experiment in experiments:
    data = readExperiment(experiment)
    (accuracy, x) = computeAccuracy(data['predictions'],
                                    data['truths'],
                                    data['iterations'],
                                    resets=data['resets'],
                                    randoms=data['randoms'])
    # injectNoiseAt = data['sequenceCounter'][12000]
    # x = numpy.array(x) - injectNoiseAt + 1400
    plotAccuracy((accuracy, x),
                 data['trains'],
                 window=100,
                 type=type,
                 label='NoiseExperiment',
                 hideTraining=True,
                 lineSize=1.0)
    pyplot.xlim([10500, 14500])
    pyplot.xlabel('Number of elements seen')
    pyplot.ylabel(' Accuracy ')

  pyplot.axvline(x=12000, color='k')
  pyplot.legend(['LSTM', 'HTM'])
  pyplot.savefig('./result/temporal_noise_train_without_noise.pdf')

  experiments = [
    os.path.join("lstm/results", "high-order-noise-test-without-noise", "0.log"),
    os.path.join("tm/results", "high-order-noise-test-without-noise", "0.log"),
  ]
  pyplot.close('all')
  for experiment in experiments:
    data = readExperiment(experiment)
    (accuracy, x) = computeAccuracy(data['predictions'],
                                    data['truths'],
                                    data['iterations'],
                                    resets=data['resets'],
                                    randoms=data['randoms'])
    plotAccuracy((accuracy, x),
                 data['trains'],
                 window=100,
                 type=type,
                 label='NoiseExperiment',
                 hideTraining=True,
                 lineSize=1.0)
    pyplot.xlim([10500, 15000])
    pyplot.axvline(x=12000, color='k')
    pyplot.xlabel('Number of elements seen')
    pyplot.ylabel(' Accuracy ')
  pyplot.legend(['LSTM', 'HTM'])
  pyplot.savefig('./result/temporal_noise_test_without_noise.pdf')