from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn import neighbors
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier

import scipy.io as sio
from sklearn import preprocessing
import numpy as np
from sklearn import metrics
import h5py
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2, f_classif, mutual_info_classif
from sklearn.feature_selection import RFE

subNum = 32
trialNum = 40
featureDim = 2360

# 0 valence 1 arousal
emodim = 1

#load data Y
file1 = sio.loadmat('.//trial_labels_personal_valence_arousal_dominance.mat')
Y = file1['trial_labels']

#results ndarray bestk:10, feature_sel_method:3, subjects:32, classifiers:6
f1_scores = np.zeros((236,32))
acc_scores = np.zeros((236,32))

subX_all = np.zeros((subNum*trialNum, featureDim))
subY_all = np.zeros((subNum*trialNum))


## combine all subjects' samples...
for subNo in range(0, subNum):
    file2 = h5py.File(
        'D://LX//Processed DEAP DATA//FeatureEngineering//EEG//Frontiers//NoScaleRawData_RhythmExtraction//BetaRhythm//WindowTime4_sub' + str(
            subNo + 1) + '.mat', 'r')
    file3 = h5py.File(
        'D://LX//Processed DEAP DATA//FeatureEngineering//EEG//Frontiers//NoScaleRawData_RhythmExtraction//GammaRhythm//WindowTime4_sub' + str(
            subNo + 1) + '.mat', 'r')
    file4 = h5py.File(
        'D://LX//Processed DEAP DATA//FeatureEngineering//EEG//Frontiers//NoScaleRawData_RhythmExtraction//AlphaRhythm//WindowTime4_sub' + str(
            subNo + 1) + '.mat', 'r')
    file5 = h5py.File(
        'D://LX//Processed DEAP DATA//FeatureEngineering//EEG//Frontiers//NoScaleRawData_RhythmExtraction//ThetaRhythm//WindowTime4_sub' + str(
            subNo + 1) + '.mat', 'r')
    subX1 = file2['EEG_Features']
    subX1 = np.transpose(subX1)
    subX2 = file3['EEG_Features']
    subX2 = np.transpose(subX2)
    subX3 = file4['EEG_Features']
    subX3 = np.transpose(subX3)
    subX4 = file5['EEG_Features']
    subX4 = np.transpose(subX4)
    subX = np.hstack((subX4, subX3, subX1, subX2)) # with order of : theta alpha beta gamma
    subY = Y[subNo*trialNum:(subNo+1)*trialNum, emodim]

    subX_all[subNo*trialNum:(subNo+1)*trialNum,:] = subX
    subY_all[subNo*trialNum:(subNo+1)*trialNum] = subY


## scale data
min_max_scaler = preprocessing.MinMaxScaler()
X = min_max_scaler.fit_transform(subX_all)
Y = subY_all


for no_k in range(0, 236):
    num_k = (no_k + 1) * 10
    for subNo in range(0, subNum):
            print("Building model and test for ------------------------------------------------------------------------------------------------ sub " + str(subNo + 1))
            if subNo == 0:
                testX = X[0:40,:]
                testY = Y[0:40]
                trainX = X[40:subNum*trialNum,:]
                trainY = Y[40:subNum*trialNum]
            elif subNo == 31:
                testX = X[1240:1280,:]
                testY = Y[1240:1280]
                trainX = X[0:1240,:]
                trainY = Y[0:1240]
            else:
                testX = X[subNo*trialNum:(subNo+1)*trialNum, :]
                testY = Y[subNo*trialNum:(subNo+1)*trialNum]
                trainX = np.vstack((X[0:subNo*trialNum, :], X[(subNo+1)*trialNum:subNum*trialNum, :]))
                trainY = np.concatenate((Y[0:subNo*trialNum], Y[(subNo+1)*trialNum:subNum*trialNum]))

            clf = svm.SVC(kernel='linear')
            sel_criteria = RFE(estimator=clf, n_features_to_select=num_k, step=0.5).fit(trainX, trainY)
            sel_indx_mask = sel_criteria.get_support()
            sel_indx = np.where(sel_indx_mask == True)
            sel_indx = sel_indx[0]
            trainX = trainX[:,sel_indx]
            testX = testX[:,sel_indx]

            #svm
            clf1 = svm.SVC(kernel='linear')
            clf1.fit(trainX, trainY)
            predict_testY = clf1.predict(testX)
            f1_scores[no_k,subNo]=metrics.f1_score(testY, predict_testY)
            acc_scores[no_k,subNo]=metrics.accuracy_score(testY, predict_testY)


            print('current sub performance:', acc_scores[no_k,subNo], ' kbest:', num_k)


#save results
if emodim==0:
    #save results
    sio.savemat('f1_scores_valence_subcross_236steps_wrapper_revision.mat', {'results': f1_scores})
    sio.savemat('acc_scores_valence_subcross_236steps_wrapper_revision.mat', {'results': acc_scores})
else:
    sio.savemat('f1_scores_arousal_subcross_236steps_wrapper_revision.mat', {'results': f1_scores})
    sio.savemat('acc_scores_arousal_subcross_236steps_wrapper_revision.mat', {'results': acc_scores})