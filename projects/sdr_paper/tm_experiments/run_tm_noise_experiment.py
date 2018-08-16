# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2017, Numenta, Inc.  Unless you have an agreement
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

import numpy
import copy
from itertools import izip as zip, count
from nupic.bindings.algorithms import TemporalMemory as TM
from scipy.spatial.distance import cosine
from htmresearch.frameworks.poirazi_neuron_model.data_tools import generate_evenly_distributed_data_sparse, apply_noise
numpy.random.seed(19)

def convert_cell_lists_to_dense(dim, cell_list, add_1 = False):
  if add_1:
    dense_cell_list = numpy.zeros((len(cell_list), dim + 1))
  else:
    dense_cell_list = numpy.zeros((len(cell_list), dim))
  for i, datapoint in enumerate(cell_list):
    for cell in datapoint:
      dense_cell_list[i, int(cell)] = 1
    if add_1:
      dense_cell_list[i, dim] = 1

  return dense_cell_list


def run_tm_noise_experiment(dim = 2048,
                            cellsPerColumn=1,
                            num_active = 40,
                            activationThreshold=16,
                            initialPermanence=0.8,
                            connectedPermanence=0.50,
                            minThreshold=16,
                            maxNewSynapseCount=20,
                            permanenceIncrement=0.05,
                            permanenceDecrement=0.00,
                            predictedSegmentDecrement=0.000,
                            maxSegmentsPerCell=255,
                            maxSynapsesPerSegment=255,
                            seed=42,
                            num_samples = 1,
                            num_trials = 1000,
                            sequence_length = 20,
                            training_iters = 1,
                            automatic_threshold = False,
                            noise_range = range(0, 100, 5)):

  """
  Run an experiment tracking the performance of the temporal memory given
  noise.  The number of active cells and the dimensions of the TM are
  fixed. We track performance by comparing the cells predicted to be
  active with the cells actually active in the sequence without noise at
  every timestep, and averaging across timesteps. Three metrics are used,
  correlation (Pearson's r, by numpy.corrcoef), set similarity (Jaccard
  index) and cosine similarity (using scipy.spatial.distance.cosine). The
  Jaccard set similarity is the canonical metric used in the paper, but
  all three metrics tend to produce very similar results.

  Typically, this experiment is run to test the influence of activation
  threshold on noise tolerance, with multiple different thresholds tested.
  However, this experiment could also be used to examine the influence of
  factors such as sparsity and sequence length.

  Output is written to tm_noise_{threshold}}.txt, including sample size.

  We used three different activation threshold settings, 8, 12 and 16, mirroring
  the parameters used in the Poirazi neuron model experiment.
  """
  if automatic_threshold:
    activationThreshold = min(num_active/2, maxNewSynapseCount/2)
    minThreshold = min(num_active/2, maxNewSynapseCount/2)

  for noise in noise_range:
    print noise
    for trial in range(num_trials):
      tm = TM(columnDimensions=(dim,),
          cellsPerColumn=cellsPerColumn,
          activationThreshold=activationThreshold,
          initialPermanence=initialPermanence,
          connectedPermanence=connectedPermanence,
          minThreshold=minThreshold,
          maxNewSynapseCount=maxNewSynapseCount,
          permanenceIncrement=permanenceIncrement,
          permanenceDecrement=permanenceDecrement,
          predictedSegmentDecrement=predictedSegmentDecrement,
          maxSegmentsPerCell=maxSegmentsPerCell,
          maxSynapsesPerSegment=maxSynapsesPerSegment,
          )#seed=seed)

      datapoints = []
      canonical_active_cells = []

      for sample in range(num_samples):
        data = generate_evenly_distributed_data_sparse(dim = dim, num_active = num_active, num_samples = sequence_length)
        datapoints.append(data)
        for i in range(training_iters):
          for j in range(data.nRows()):
            activeColumns = set(data.rowNonZeros(j)[0])
            tm.compute(activeColumns, learn = True)
          tm.reset()

        current_active_cells = []
        for j in range(data.nRows()):
          activeColumns = set(data.rowNonZeros(j)[0])
          tm.compute(activeColumns, learn = True)
          current_active_cells.append(tm.getActiveCells())
        canonical_active_cells.append(current_active_cells)
        tm.reset()

      # Now that the TM has been trained, check its performance on each sequence with noise added.
      correlations = []
      similarities = []
      csims = []
      for datapoint, active_cells in zip(datapoints, canonical_active_cells):
        data = copy.deepcopy(datapoint)
        apply_noise(data, noise)

        predicted_cells = []

        for j in range(data.nRows()):
          activeColumns = set(data.rowNonZeros(j)[0])
          tm.compute(activeColumns, learn = False)
          predicted_cells.append(tm.getPredictiveCells())

        similarity = [(0.+len(set(predicted) & set(active)))/len((set(predicted) | set(active))) for predicted, active in zip (predicted_cells[:-1], active_cells[1:])]
        dense_predicted_cells = convert_cell_lists_to_dense(2048*32, predicted_cells[:-1])
        dense_active_cells = convert_cell_lists_to_dense(2048*32, active_cells[1:])
        correlation = [numpy.corrcoef(numpy.asarray([predicted, active]))[0, 1] for predicted, active in zip(dense_predicted_cells, dense_active_cells)]
        csim = [1 - cosine(predicted, active) for predicted, active in zip(dense_predicted_cells, dense_active_cells)]

        correlation = numpy.nan_to_num(correlation)
        csim = numpy.nan_to_num(csim)
        correlations.append(numpy.mean(correlation))
        similarities.append(numpy.mean(similarity))
        csims.append(numpy.mean(csim))

    correlation = numpy.mean(correlations)
    similarity = numpy.mean(similarities)
    csim = numpy.mean(csims)
    with open("tm_noise_{}.txt".format(activationThreshold), "a") as f:
      f.write(str(noise)+", " + str(correlation) + ", " + str(similarity) + ", " + str(csim) + ", " + str(num_trials) + "\n")

if __name__ == "__main__":
  run_tm_noise_experiment()
