import tensorflow as tf

def make_weighted_loss(w_O, w_C, w_N, w_H, w_Ca,w_P):
    def weighted_loss(y_true, y_pred):
        kl = tf.keras.losses.kullback_leibler_divergence(y_true[:,:6], y_pred[:,:6])

        err_O = tf.abs(y_true[:,0] - y_pred[:,0]) * w_O
        err_C = tf.abs(y_true[:,1] - y_pred[:,1]) * w_C
        err_N = tf.abs(y_true[:,2] - y_pred[:,2]) * w_N
        err_H = tf.abs(y_true[:,3] - y_pred[:,3]) * w_H
        err_Ca = tf.abs(y_true[:,4] - y_pred[:,4]) * w_Ca
        err_P = tf.abs(y_true[:,5] - y_pred[:,5]) * w_P

        mae_weighted = tf.reduce_mean(err_O + err_C + err_N + err_H + err_Ca + err_P)

        return kl + 0.2 * mae_weighted
    return weighted_loss

def make_compositional_and_density_loss(lambda_comp,lambda_density):
    def compositional_and_density_loss(y_true,y_pred): 
        composition_loss = tf.keras.losses.kullback_leibler_divergence(y_true[:,:6], y_pred[:,:6])
        density_loss = tf.abs(y_true[:,6] - y_pred[:,6])

        return lambda_comp*composition_loss + lambda_density*density_loss
    return compositional_and_density_loss






    








