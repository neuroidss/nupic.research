## Grid Cell Learning

This project contains code implementing some of the continuous attractor
grid cell learning models from Widloski & Fiete, 2014.  CAN.py, in the
grid_cell_learning frameworks package, contains a straightforward implementation
of a learning grid cell module, which employs rate-coded neurons to learn an
approximate CAN network across a 1D environment.

1D CAN Learning.ipynb contains code to run and visualize this network, including
a confirmation that it generates a CAN network with gridlike firing, and an
evaluation of its accuracy at path integration.

Finally, compute_hardwired_weights.py contains code directly adapted from
code provided by Fiete to initialize the network's weights to a desirable
target.  This can be used for sanity checking.

In the future, this work may be extended to include 2D learning, and may also
be used in other, related learning problems.
