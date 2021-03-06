import subprocess
import os
from sklearn.datasets import load_svmlight_file
import numpy as np
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
testing_file = os.path.join(current_dir, "digits/digits.test")
X_test, Y_test = load_svmlight_file(testing_file)

C = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1]
all_acc = [[] for i in xrange(10)]
best_cs = [0]*10
best_models = [0]*10
highest_predictions = []

#return a table of validation accuracies for each c for each digit and return best c for each digit
def find_best_classifier():
    for digit in xrange(10):
        for c in C:
            train_model(digit, c)
            val_acc = validate(digit, c)

    for digit in xrange(10):
        highest_acc = max(all_acc[digit])
        best_c = C[all_acc[digit].index(highest_acc)]
        best_cs[digit] = best_c
        best_models[digit] = './1c_files/model%s_%s' %(digit, best_c)

    multi_classify()


#return a model file
def train_model(digit, c):
    p = subprocess.check_call('./svm_light/svm_learn -t 0 -c %s ./digits/digits%s.train ./1c_files/model%s_%s' %(c, digit, digit, c), shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


#store accuracy for c on validation set
def validate(digit, c):
    print 'digit %s and c %s' %(digit, c)
    p = subprocess.Popen('./svm_light/svm_classify ./digits/digits%s.val ./1c_files/model%s_%s ./1c_files/validations%s_%s' %(digit, digit, c, digit, c), shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for l in p.stdout:
        if 'Accuracy' in l:
            print 'Found accuracy'
            acc = l[l.find(':')+2:l.find('%')]
    all_acc[digit].append(float(acc))


#use each model to find the best class for each test instance and print overall accuracy
def multi_classify():
    #create the 10 predictions for each instance
    for digit in xrange(10):
        model = best_models[digit]
        predict(model, digit)
    
    #assign class to instance according to highest prediction
    highest_predictions = classify()
    #calculate and print out the overall test accuracy
    overall_acc = calc_acc(highest_predictions, Y_test)
    final_print(overall_acc)


#use 10 models to create 10 predictions for each instance and print accuracies
def predict(model, digit):
    #format test examples
    test = format_classes(digit)
    p = subprocess.Popen('./svm_light/svm_classify '+test+' '+model+' ./1c_predictions/predictions%s' %digit, shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for l in p.stdout:
        if 'Accuracy' in l:
            acc = l[l.find(':')+2:l.find('%')]
    print acc


#create new test set with changed labels of set to either +1/-1 depending on the classifier
def format_classes(digit):
    with open('./1c_predictions/test%d' %digit, 'w') as fp:
        for index in xrange(len(Y_test)):                  #for each test instance
            if (Y_test[index] == digit) or (Y_test[index] == 10 and digit == 0):
                y_label = '+1'
            else:
                y_label = '-1'
            line = y_label
            feat = X_test[index].indices
            feat_values = X_test[index].data
            for f in range(len(feat)):
                feature = str(feat[f]+1)
                value = str(int(feat_values[f]))
                line = line+" "+feature+':'+value
            fp.write(line+"\n")
    return './1c_predictions/test%d' %digit


#return array of best guesses for each instance, None if there was no positive prediction for that instance
def classify():
    instances = [None]*len(Y_test)     #in each index store the class of the highest prediction
    best_preds = [None]*len(Y_test)    #in each index store the highest prediction
    #iterate through the predictions and tracking for each instance the highest prediction so far
    for digit in range(10):
        with open('./1c_predictions/predictions%d' %digit, 'r') as fp:
            i = 0
            while i < len(instances):
                for line in fp:
                    if float(line) > best_preds[i]:
                        best_preds[i] = float(line)
                        if digit == 0:
                            instances[i] = 10
                        else:
                            instances[i] = digit
                    i = i+1
    return instances


#return the accuracy on overall test set by comparing highest_predictions with actual test labels
def calc_acc(predictions, tests):
    correct = 0.0
    total = len(predictions)
    for i in range(len(predictions)):
        if predictions[i] == tests[i]:
            correct = correct+1.0
    overall_acc = str((correct/total)*100)+'%'
    return overall_acc


def final_print(overall_acc):
    print "\nAll accuracies during validation for each digit while varying C:"
    for digit in xrange(len(all_acc)):
        if digit == 0:
            string = '10'
        else:
            string = str(digit)+' '
        for i, v in enumerate(all_acc[digit]):
            string = string+' '+str(v)
        print string
        
    print "\nThe best C value for each digit is:"
    for i, v in enumerate(best_cs):
        if i == 0:
            print '10: '+str(v)
        else:
            print str(i)+' : '+str(v)
            
    print "\nThe accuracy on the overall test set is: "+overall_acc

find_best_classifier()




