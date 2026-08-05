import tensorflow as tf
#import tensorflow_probability as tfp


def mae_O(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,0] - y_pred[:,0]))

def mae_C(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,1] - y_pred[:,1]))

def mae_N(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,2] - y_pred[:,2]))

def mae_H(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,3] - y_pred[:,3]))

def mae_Ca(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,4] - y_pred[:,4]))

def mae_P(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,5] - y_pred[:,5]))

# For one vs all
def mae_one(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,0] - y_pred[:,0]))

def mae_all(y_true, y_pred):
    return tf.reduce_mean(tf.abs(y_true[:,1] - y_pred[:,1]))

'''
def median_ae_O(y_true, y_pred):
    ae = tf.abs(y_true[:,0] - y_pred[:,0])
    return tfp.stats.percentile(ae, 50.0)

def median_ae_C(y_true, y_pred):
    ae = tf.abs(y_true[:,1] - y_pred[:,1])
    return tfp.stats.percentile(ae, 50.0)

def median_ae_N(y_true, y_pred):
    ae = tf.abs(y_true[:,2] - y_pred[:,2])
    return tfp.stats.percentile(ae, 50.0)'''


