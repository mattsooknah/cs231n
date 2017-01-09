import numpy as np

from cs231n.layers import *
from cs231n.fast_layers import *
from cs231n.layer_utils import *


class ThreeLayerConvNet(object):
  """
  A three-layer convolutional network with the following architecture:

  conv - relu - 2x2 max pool - affine - relu - affine - softmax

  The network operates on minibatches of data that have shape (N, C, H, W)
  consisting of N images, each with height H and width W and with C input
  channels.
  """

  def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
               hidden_dim=100, num_classes=10, weight_scale=1e-3, reg=0.0,
               dtype=np.float32):
    """
    Initialize a new network.

    Inputs:
    - input_dim: Tuple (C, H, W) giving size of input data
    - num_filters: Number of filters to use in the convolutional layer
    - filter_size: Size of filters to use in the convolutional layer
    - hidden_dim: Number of units to use in the fully-connected hidden layer
    - num_classes: Number of scores to produce from the final affine layer.
    - weight_scale: Scalar giving standard deviation for random initialization
      of weights.
    - reg: Scalar giving L2 regularization strength
    - dtype: numpy datatype to use for computation.
    """
    self.params = {}
    self.reg = reg
    self.dtype = dtype

    C, H, W = input_dim
    F = num_filters

    # assuming max pool stride = 2
    max_pool_height = 1 + (H - 2) / 2
    max_pool_width  = 1 + (W - 2) / 2
    max_pool_dim = max_pool_height * max_pool_width * num_filters

    self.params['W1'] = weight_scale * np.random.randn(F, C, filter_size, filter_size)
    self.params['b1'] = np.zeros((F,))
    self.params['W2'] = weight_scale * np.random.randn(max_pool_dim, hidden_dim)
    self.params['b2'] = np.zeros((hidden_dim,))
    self.params['W3'] = weight_scale * np.random.randn(hidden_dim, num_classes)
    self.params['b3'] = np.zeros((num_classes,))

    for k, v in self.params.iteritems():
      self.params[k] = v.astype(dtype)


  def loss(self, X, y=None):
    """
    Evaluate loss and gradient for the three-layer convolutional network.

    Input / output: Same API as TwoLayerNet in fc_net.py.
    """
    reg = self.reg
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    W3, b3 = self.params['W3'], self.params['b3']

    # pass conv_param to the forward pass for the convolutional layer
    filter_size = W1.shape[2]
    conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

    # pass pool_param to the forward pass for the max-pooling layer
    pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

    # ------------------------------ FORWARD PASS ------------------------------
    # conv - relu - 2x2 max pool - affine - relu - affine - softmax

    conv, conv_cache = conv_relu_pool_forward(X, W1, b1, conv_param, pool_param)
    # squash dims to make affine easier
    conv_dims = conv.shape
    conv = conv.reshape(conv_dims[0], -1)
    hidden, hidden_cache = affine_relu_forward(conv, W2, b2)
    scores, scores_cache = affine_forward(hidden, W3, b3)

    if y is None:
      return scores

    # ------------------------------ BACKWARD PASS -----------------------------

    grads = {}
    loss, dScores = softmax_loss(scores, y)

    (dHidden, dW3, db3) = affine_backward(dScores, scores_cache)
    (dConv, dW2, db2) = affine_relu_backward(dHidden, hidden_cache)
    # unsquash dims
    dConv = dConv.reshape(conv_dims)
    (dX, dW1, db1) = conv_relu_pool_backward(dConv, conv_cache)

    # remember to add regularization
    loss += 0.5 * reg * sum([np.sum(p * p) for p in (W1,W2,W3,b1,b2,b3)])
    grads['W1'] = dW1 + reg * W1
    grads['b1'] = db1 + reg * b1
    grads['W2'] = dW2 + reg * W2
    grads['b2'] = db2 + reg * b2
    grads['W3'] = dW3 + reg * W3
    grads['b3'] = db3 + reg * b3

    return loss, grads
