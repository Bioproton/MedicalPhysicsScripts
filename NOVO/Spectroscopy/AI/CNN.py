import numpy as np
import os
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.layers import ( 
    Input, Conv1D, Concatenate, BatchNormalization, ReLU, 
    Add, GlobalAveragePooling1D, Dense, Dropout, MultiHeadAttention, LayerNormalization, Lambda, Activation) 
from tensorflow.keras.models import Model 
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint
from tensorflow.keras.losses import KLDivergence
from tensorflow.keras.optimizers import Adam

import datetime
from helper_functions import read_composition


# Multi-scale CNN block 
def inception_block(x, filters=32): 
    b1 = Conv1D(filters, 3, padding="same", activation="relu")(x) # 3
    b2 = Conv1D(filters, 7, padding="same", activation="relu")(x)  # 7 
    b3 = Conv1D(filters, 15, padding="same", activation="relu")(x) # 15
    return Concatenate()([b1, b2, b3]) 

# Dilated CNN block 
def dilated_block(x, filters=64): 
    d1 = Conv1D(filters, 7, dilation_rate=1, padding="same", activation="relu")(x) 
    d2 = Conv1D(filters, 7, dilation_rate=2, padding="same", activation="relu")(x) 
    d3 = Conv1D(filters, 7, dilation_rate=4, padding="same", activation="relu")(x) 
    return Concatenate()([d1, d2, d3]) 

# Self-attention block 
def attention_block(x, num_heads=4, key_dim=32): 
    # Layer normalization before attention (Transformer style) 
    ln = LayerNormalization()(x) 

    # Multi-head self-attention 
    attn_out, attn_scores = MultiHeadAttention(num_heads=num_heads, key_dim=key_dim, dropout=0.1, name = "attention_layer")(ln, ln, return_attention_scores=True)

    # Residual connection 
    x = Add()([x, attn_out]) 

    # Feed-forward network (MLP) 
    ln2 = LayerNormalization()(x) 
    ff = Dense(128, activation="relu")(ln2) 
    ff = Dense(x.shape[-1])(ff) 

    # Second residual connection 
    x = Add()([x, ff]) 

    return x, attn_scores

# Må sjekke arkitekturen mer. Denne kan sikkert forbedres med flere attention layers. Sparr med co-pilot, sjekk andre modeller. 
# finn også ut om attention maps
def build_CNN(input_length=350, output_dim=3, num_channels = 2,with_attention = False, num_filters_1 = 32, num_filters_2 = 64, auxillary_output = False,rho_min = 0.8, rho_max = 1.9, add_spes = False): 
    inp = Input(shape=(input_length, num_channels)) 
    #proton_inp = Input(shape=(1,), name = "num_of_primaries")

    # initial CNN
    x = Conv1D(32, 7, padding="same")(inp) 
    x = BatchNormalization()(x) 
    x = ReLU()(x) 

    # inception block
    inc = inception_block(x, filters=num_filters_1) 
    res = Conv1D(96,1, padding = "same")(x) # Her var det ganget med 2 tidligere, husker ikke hvorfor
    x = Add()([res, inc])    # residual 

    # dilution block
    dil = dilated_block(x, filters=num_filters_2) 
    res2 = Conv1D(192,1, padding = "same")(x) # her og
    x = Add()([res2, dil])    # residual 

    if with_attention == False:
        # add another inception_block
        inc_2 = inception_block(x, filters=64) 
        x = Add()([x, inc_2])    # residual 

    if with_attention == True:
        # add attention block
        x, attn_scores = attention_block(x, num_heads=4, key_dim=32)

    # burde sjekke hvordan denne funker
    x = GlobalAveragePooling1D()(x) 

    # concatenate scalar value here? 

    x = Dense(64, activation="relu")(x) 
    x = Dropout(0.2)(x)  

    if add_spes:
        shared = x
        class_logits = []

        for i in range(output_dim):
            h = Dense(32, activation = "relu", name=f"class_{i}_hidden")(shared)
            logit = Dense(1, activation=None, name=f"class_{i}_logit")(h)

            class_logits.append(logit)
        
        logits = Concatenate(name = "logits")(class_logits)
        out = Activation("softmax", name = "composition")(logits)
    
    else:
        out = Dense(output_dim, activation="softmax", name = "composition")(x) 

    if auxillary_output:
        aux_output = Dense(1, activation="sigmoid", name = "auxillary_output_before_scaling")(x) 
        aux_output = Lambda(lambda t: rho_min + (rho_max - rho_min) * t, name = "auxillary_output")(aux_output)
        model = Model(inputs=inp, outputs = [out, aux_output])
    else:
        model = Model(inputs=inp, outputs = out)

    if with_attention == True:
        attention_model = Model(inputs=inp, outputs = attn_scores)
    else:
        attention_model = None
        
    return model, attention_model
