'''
@author: dapowan
@file: position_estimation.py
@time: 2019-05-21 20:09
@desc: The neural network structure of position estimation model in AdaRF. The codes are referenced from https://github.com/tensorflow/models. The version of tensorflow-gpu is 1.9.0.
'''


import tensorflow as tf

DATA_TYPE = tf.float32
DEVICE = '/gpu:0'


class NeuralNetworkStucture():

    def __init__(self):
        # number of channel
        self.NUM_CHANNELS = 2
        # regularization term of convolution layers
        self.REGULARIZATION_RATE = None
        # regularization term of fully-connected layers
        self.LOCAL_REGULARIZATION_RATE = None


    def inference(self, data, training=True):
        '''

        :param data:  4-dimension ndarray. The generated holograms. [sample_number][100][100][2]
            The first dimension is the index of sample.
            The second dimension is the size of grids along the x-axis.
            The third dimension is the size of grids along the y-axis.
            The fourth dimension is the index of channel, which is 2 in AdaRF (L1 and L2).
        :param training: boolean. create model for training or test.
        :return: tensor. The position estimation model in AdaRF.
        '''
        # conv1
        with tf.variable_scope('conv1') as scope:
            kernel = self.variable_with_weight_decay('weights',
                                                     shape=[5, 5, self.NUM_CHANNELS, 16],
                                                     stddev=0.1,
                                                     wd=self.REGULARIZATION_RATE, scope=scope)
            conv = tf.nn.conv2d(data, kernel, [1, 1, 1, 1], padding='VALID')
            biases = self.variable_on_device('biases', [16], tf.constant_initializer(0.0), scope=scope)
            pre_activation = tf.nn.bias_add(conv, biases)
            conv1 = tf.nn.tanh(pre_activation, name=scope.name)

        # pool1
        pool1 = tf.nn.max_pool(conv1, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1],
                               padding='VALID', name='pool1')

        # norm1
        norm1 = tf.nn.lrn(pool1, name='norm1')#

        # conv2
        with tf.variable_scope('conv2') as scope:
            kernel = self.variable_with_weight_decay('weights',
                                                     shape=[5, 5, 16, 32],
                                                     stddev=0.1,
                                                     wd=self.REGULARIZATION_RATE, scope=scope)
            conv = tf.nn.conv2d(norm1, kernel, [1, 1, 1, 1], padding='VALID')
            biases = self.variable_on_device('biases', [32], tf.constant_initializer(0.0), scope=scope)
            pre_activation = tf.nn.bias_add(conv, biases)
            conv2 = tf.nn.tanh(pre_activation, name=scope.name)

        # pool2
        pool2 = tf.nn.max_pool(conv2, ksize=[1, 3, 3, 1],
                               strides=[1, 2, 2, 1], padding='VALID', name='pool2')

        # norm2
        norm2 = tf.nn.lrn(pool2, name='norm2')

        #conv3
        with tf.variable_scope('conv3') as scope:
            kernel = self.variable_with_weight_decay('weights',
                                                     shape=[3, 3, 32, 16],
                                                     stddev=0.1,
                                                     wd=self.REGULARIZATION_RATE, scope=scope)
            conv = tf.nn.conv2d(norm2, kernel, [1, 1, 1, 1], padding='VALID')
            biases = self.variable_on_device('biases', [16], tf.constant_initializer(0.0), scope=scope)
            pre_activation = tf.nn.bias_add(conv, biases)
            conv3 = tf.nn.tanh(pre_activation, name=scope.name)

        # pool3
        pool3 = tf.nn.max_pool(conv3, ksize=[1, 3, 3, 1],
                               strides=[1, 1, 1, 1], padding='SAME', name='pool3')

        # norm3
        norm3 = tf.nn.lrn(pool3, name='norm3')

        dropout = tf.layers.dropout(norm3, rate=0.2, training=training, name='dropout')

        # local4
        with tf.variable_scope('local4') as scope:
            reshape = tf.reshape(dropout, [data.get_shape().as_list()[0], -1])
            dim = reshape.get_shape()[1].value
            weights = self.variable_with_weight_decay('weights', shape=[dim, 100],
                                                      stddev=0.1,
                                                      wd=self.LOCAL_REGULARIZATION_RATE, scope=scope)
            biases = self.variable_on_device('biases', [100], tf.constant_initializer(0.0), scope=scope)
            local4 = tf.nn.tanh(tf.matmul(reshape, weights) + biases, name=scope.name)


        # local5
        with tf.variable_scope('local5') as scope:
            weights = self.variable_with_weight_decay('weights', shape=[100, 32],
                                                      stddev=0.1, wd=self.LOCAL_REGULARIZATION_RATE, scope=scope)
            biases = self.variable_on_device('biases', [32], tf.constant_initializer(0.0), scope=scope)
            local5 = tf.nn.tanh(tf.matmul(local4, weights) + biases, name=scope.name)

        with tf.variable_scope('local6') as scope:
            weights = self.variable_with_weight_decay('weights', shape=[32, 10],
                                                      stddev=0.1, wd=self.LOCAL_REGULARIZATION_RATE, scope=scope)
            biases = self.variable_on_device('biases', [10], tf.constant_initializer(0.0), scope=scope)
            local6 = tf.nn.tanh(tf.matmul(local5, weights) + biases, name=scope.name)


        with tf.variable_scope('local7') as scope:
            weights = self.variable_with_weight_decay('weights', shape=[10, 2],
                                                      stddev=0.1, wd=self.LOCAL_REGULARIZATION_RATE, scope=scope)
            biases = self.variable_on_device('biases', [2], tf.constant_initializer(0.0), scope=scope)
            local7 = tf.nn.tanh(tf.matmul(local6, weights) + biases, name=scope.name)

        return local7

    def variable_with_weight_decay(self, name, shape, stddev, wd, scope):
      var = self.variable_on_device(
          name,
          shape,
          tf.truncated_normal_initializer(stddev=stddev, dtype=DATA_TYPE), scope)
      if wd is not None:
        weight_decay = tf.multiply(tf.nn.l2_loss(var), wd, name='weight_loss')
        tf.add_to_collection('losses', weight_decay)
      return var

    def variable_on_device(self, name, shape, initializer, scope):
      with tf.device(DEVICE):
        try:
            var = tf.get_variable(name, shape, initializer=initializer, dtype=DATA_TYPE)
        except ValueError:
            scope.reuse_variables()
            var = tf.get_variable(name, shape, initializer=initializer, dtype=DATA_TYPE)
      return var
