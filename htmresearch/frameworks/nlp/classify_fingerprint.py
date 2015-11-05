# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
# Numenta, Inc. a separate commercial license for this software code, the
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
import os

from htmresearch.encoders import EncoderTypes
from htmresearch.encoders.cio_encoder import CioEncoder
from htmresearch.frameworks.nlp.classification_model import ClassificationModel
from nupic.algorithms.KNNClassifier import KNNClassifier



class ClassificationModelFingerprint(ClassificationModel):
  """
  Class to run the survey response classification task with Coritcal.io
  fingerprint encodings.

  From the experiment runner, the methods expect to be fed one sample at a time.
  """

  def __init__(self,
               verbosity=1,
               numLabels=3,
               modelDir="ClassificationModelFingerprint",
               fingerprintType=EncoderTypes.word,
               unionSparsity=20.0,
               retinaScaling=1.0,
               retina="en_associative",
               apiKey=None):

    super(ClassificationModelFingerprint, self).__init__(
      verbosity=verbosity, numLabels=numLabels, modelDir=modelDir)

    # Init kNN classifier and Cortical.io encoder; need valid API key (see
    # CioEncoder init for details).
    self.classifier = KNNClassifier(k=numLabels,
                                    distanceMethod='rawOverlap',
                                    exact=False,
                                    verbosity=verbosity-1)

    if fingerprintType is (not EncoderTypes.document or not EncoderTypes.word):
      raise ValueError("Invaid type of fingerprint encoding; see the "
                       "EncoderTypes class for eligble types.")
    root = os.path.dirname(os.path.realpath(__file__))
    self.encoder = CioEncoder(retinaScaling=retinaScaling,
                              cacheDir=os.path.join(root, "CioCache"),
                              fingerprintType=fingerprintType,
                              unionSparsity=unionSparsity,
                              retina=retina,
                              apiKey=apiKey)


  def encodeSample(self, sample):
    """
    Encode an SDR of the input string by querying the Cortical.io API. If the
    client returns None, we create a random SDR with the model's dimensions n
    and w.

    @param sample     (list)        Tokenized sample, where each item is a str.
    @return fp        (dict)        The sample text, sparsity, and bitmap.
    Example return dict:
      {
        "text": "Example text",
        "sparsity": 0.03,
        "bitmap": numpy.array([])
      }
    """
    sample = " ".join(sample)
    fpInfo = self.encoder.encode(sample)
    if fpInfo:
      fp = {"text":fpInfo["text"] if "text" in fpInfo else fpInfo["term"],
            "sparsity":fpInfo["sparsity"],
            "bitmap":numpy.array(fpInfo["fingerprint"]["positions"])}
    else:
      fp = {"text":sample,
            "sparsity":float(self.encoder.w)/self.encoder.n,
            "bitmap":self.encodeRandomly(
              sample, self.encoder.n, self.encoder.w)}

    return fp


  def trainModel(self, i):
    # TODO: add batch training, where i is a list
    """
    Train the classifier on the sample and labels for record i. The list
    sampleReference is populated to correlate classifier prototypes to sample
    IDs.
    """
    bitmap = self.patterns[i]["pattern"]["bitmap"]
    if bitmap.any():
      for label in self.patterns[i]["labels"]:
        self.classifier.learn(bitmap, label, isSparse=self.encoder.n)
        self.sampleReference.append(self.patterns[i]["ID"])


  def testModel(self, i, seed=42):
    """
    Test the model on record i. The random seed is used in getWinningLabels().

    @return           (numpy array)   numLabels most-frequent classifications
                                      for the data samples; int or empty.
    """
    (_, inferenceResult, _, _) = self.classifier.infer(self.sparsifyPattern(
      self.patterns[i]["pattern"]["bitmap"], self.encoder.n))
    return self.getWinningLabels(inferenceResult, seed)
