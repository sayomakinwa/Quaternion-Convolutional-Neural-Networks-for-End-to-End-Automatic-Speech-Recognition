#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Authors: Parcollet Titouan

import numpy                 as np

import keras                        
from   keras.optimizers      import Adam
from   models.example_model  import *
from   sklearn.preprocessing import normalize
import sys
import argparse              as Ap


##########################################
###### UTILS FOR THE EXAMPLE_SCRIPT ######
##########################################

def dataPrepDecodaQuaternion(filename, isquat=False):

    nbTopics         = 250
    quaternionFactor = 4
    nbClasses        = 8
    raw              = open(filename, 'r').readlines()
    x                = np.ndarray(shape=(len(raw), nbTopics*quaternionFactor))
    y                = np.ndarray(shape=(len(raw), nbClasses))
    elementCpt       = 0
    documentCpt      = 0

    for doc in raw:
        elements   = doc.split('\t')[0].split(" ")
        nbElements = len(elements)

        # DATA
        for element in elements:
            components                                    = element.split(',')

            if(isquat):
                x[documentCpt][elementCpt]                = components[0]
                x[documentCpt][elementCpt+(nbElements)]   = components[1]
                x[documentCpt][elementCpt+(2*nbElements)] = components[2]
                x[documentCpt][elementCpt+(3*nbElements)] = components[3]
            else:
                x[documentCpt][4*elementCpt]              = components[0]
                x[documentCpt][4*elementCpt+1]            = components[1]
                x[documentCpt][4*elementCpt+2]            = components[2]
                x[documentCpt][4*elementCpt+3]            = components[3]
            elementCpt += 1
        elementCpt = 0

        # LABELS
        labels   = doc.split('\t')[1].split(" ")
        labelCpt = 0
        for label in labels:
            values                   = label.split(',')
            y[documentCpt][labelCpt] = values[0]
            labelCpt                += 1
        labelCpt     = 0
        documentCpt += 1

    x = normalize(x)
    
    return x,y


def getArgParser():
    parser = Ap.ArgumentParser(description='Parameters for the Neural Networks')
    
    parser.add_argument("--lr",             default="0.001",      type=float)
    parser.add_argument("--model", "--m",   default="QCNN",       type=str,
            choices=["QCNN", "QDNN", "CNN", "DNN"])

    args = parser.parse_args()
    return args

##########################################
######         MAIN PROGRAM         ######
##########################################

print('####################################################')
print('#     Quaternion Convolutional Neural Networks     #')
print('#      Parcollet Titouan - ORKIS - LIA - 2018      #')
print('####################################################')

params = getArgParser()

print('Data loading  -----------------------------')
if(params.model in ['QCNN' , 'QDNN']):
    x_train, y_train = dataPrepDecodaQuaternion('decoda/250_TRAIN_Q.data',isquat=True)
    x_dev,   y_dev   = dataPrepDecodaQuaternion('decoda/250_DEV_Q.data',  isquat=True)
    x_test,  y_test  = dataPrepDecodaQuaternion('decoda/250_TEST_Q.data', isquat=True)
else:
    x_train, y_train = dataPrepDecodaQuaternion('decoda/250_TRAIN_Q.data',isquat=False)
    x_dev,   y_dev   = dataPrepDecodaQuaternion('decoda/250_DEV_Q.data',  isquat=False)
    x_test,  y_test  = dataPrepDecodaQuaternion('decoda/250_TEST_Q.data', isquat=False)

if(params.model in ['CNN' , 'QCNN']):
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
    x_dev   = np.reshape(x_dev,   (x_dev.shape[0],   x_dev.shape[1],   1))
    x_test  = np.reshape(x_test,  (x_test.shape[0],  x_test.shape[1],  1))

print('Train size : '+str(x_train.shape[0]))
print('Dev size   : '+str(x_dev.shape[0]))
print('Test size  : '+str(x_test.shape[0]))

print('Parameters    -------------------------------')
opt = Adam(lr = 0.0005)
print('learning rate   : '+str(params.lr))
print('Model type      : '+str(params.model))


#
# CLASSIFIER
#

if(params.model in ['CNN' , 'QCNN']):
    classifier = CNN(params)
else:
    classifier = DNN(params)

print(' ')
print('Model Summary ----------------------------')
print(classifier.summary())

#
# Training
#
classifier.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
classifier.fit(x_train, y_train,
                validation_data=(x_dev,y_dev),
                epochs=15,
                batch_size=3)

#
# Eval.
#
loss, acc = classifier.evaluate(x_test,y_test)
print('Test Loss = '+str(loss)+' | Test accuracy = '+str(acc))
print("That's All Folks :p ")
