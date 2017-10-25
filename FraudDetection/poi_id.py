#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from poi_email_addresses import poiEmails
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from tester import test_classifier

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list1 = ['poi', 'total_stock_value','total_payments','restricted_stock','exercised_stock_options','expenses',\
                  'salary','bonus','from_messages','from_poi_to_this_person',\
                  'from_this_person_to_poi','shared_receipt_with_poi','to_messages']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

# data description    
import pandas as pd
df = pd.DataFrame(data_dict).T    
print 'total number of data points: ' + str(len(df))
print 'allocation across classes (POI/non-POI): ' 
print  df.poi.value_counts()
print 'number of features in total: ' + str(len(df.columns))
# number of missing values in each features
nan_value = pd.DataFrame(df.apply(lambda x: sum(x=='NaN'),axis=0))
nan_value.sort(0)

### Task 2: Remove outliers
data = featureFormat(data_dict, features_list1)
for point in data:
    expenses = point[5]
    salary = point[6]
    plt.scatter( expenses, salary )

plt.xlabel("expenses")
plt.ylabel("salary")
plt.show()

for i in data_dict:
    if data_dict[i]['salary'] > 2.5 * 10**7 and data_dict[i]['salary'] != 'NaN':
        print i

print df[(df.salary > 2 * 10 ** 7) & (df.salary != 'NaN')].salary
data_dict.pop( 'TOTAL', 0 )        

# double check whether ther are outliers
data = featureFormat(data_dict, features_list1, sort_keys = True)
for point in data:
    expenses = point[5]
    salary = point[6]
    plt.scatter( expenses, salary )

plt.xlabel("expenses")
plt.ylabel("salary")
plt.show()

for i in data_dict:
    if data_dict[i]['salary'] > 10**6 and data_dict[i]['salary']  != 'NaN':
        print i
        
for i in data_dict:
    if data_dict[i]['expenses'] > 2 * 10**5 and data_dict[i]['expenses']  != 'NaN':
        print i, data_dict[i]

### Task 3: Create new feature(s)
# allocation across classes (POI/non-POI)
def Poi_non_poi_ratio(data):
    return sum(data[:,0]==1) / float(sum(data[:,0]==0))
print len(data)  # total number of data points
print Poi_non_poi_ratio(data)


### Extract features and labels from dataset for local testing
data = featureFormat(data_dict, features_list1, sort_keys = True)
labels, features = targetFeatureSplit(data)
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score

names = ["Decision Tree", "Random Forest", "AdaBoost","Naive Bayes"]
classifiers = [
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB()
]

# iterate over classifiers
accuracy = []
precision = []
recall= []
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    print test_classifier(clf, data_dict, features_list1, folds = 1000)
    # AdaBoost classifier has the highest precision and recall 

# K nearest neighbour - result is too bad to continue using this algorithm
min_max_scaler = preprocessing.MinMaxScaler()
X_train_minmax = min_max_scaler.fit_transform(X_train)
X_test_minmax = min_max_scaler.transform(X_test)

# parameter tuning for k nearest neighbour
alphas = np.array([1,0.1,0.01,0.001,0.0001,0])
algorithm = ['auto', 'ball_tree', 'kd_tree', 'brute']
metrics       = ['minkowski','euclidean','manhattan'] 
weights       = ['uniform','distance'] #10.0**np.arange(-5,4)
numNeighbors  = np.arange(2,5)
param_grid    = dict(metric=metrics,weights=weights,n_neighbors=numNeighbors)
cv            = cross_validation.StratifiedKFold(y_train,4)
grid = GridSearchCV(KNeighborsClassifier(),param_grid=param_grid,cv=cv)
grid.fit(X_train_minmax, y_train)
print(grid)
print(grid.best_score_)

clf =grid.best_estimator_
clf.fit(X_train_minmax, y_train)
pred =  clf.predict(X_test_minmax)
print sum(pred == y_test)/float((len(y_test)))
print precision_score(y_test, pred)
print recall_score(y_test, pred)
print clf.get_params()

# AdaBoost parameter tuning
param_grid = {"learning_rate" : [0.5,1,1.5,2],
              "n_estimators": [20,30,40,50,60]
             }
cv            = cross_validation.StratifiedKFold(y_train,4)
grid = GridSearchCV(AdaBoostClassifier(),param_grid=param_grid,cv=cv)
grid.fit(X_train, y_train)
grid.best_estimator_

clf = grid.best_estimator_
clf.fit(X_train, y_train)
print test_classifier(clf, data_dict, features_list1, folds = 1000)
print clf.feature_importances_

# choose another set of features based on feature importance
features_list2 = list( features_list1[i] for i in [0, 3, 4,5,6, 7,10 ] )
print features_list2

# repeate the process of comparing different algorithms
names = ["Decision Tree", "Random Forest", "AdaBoost","Naive Bayes"]

classifiers = [
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    AdaBoostClassifier(),
    GaussianNB()
]

# iterate over classifiers
accuracy = []
precision = []
recall= []
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    print test_classifier(clf, data_dict, features_list2, folds = 1000)

    
# Again, adaboost is the best classifier. repeate the process of parameter tuning
param_grid = {"learning_rate" : [0.5,1,1.5,2],
              "n_estimators": [20,30,40,50,60]
             }
cv            = cross_validation.StratifiedKFold(y_train,4)
grid = GridSearchCV(AdaBoostClassifier(),param_grid=param_grid,cv=cv)
grid.fit(X_train, y_train)
print grid.best_estimator_

clf = grid.best_estimator_
clf.fit(X_train, y_train)
print test_classifier(clf, data_dict, features_list2, folds = 1000)
print clf.feature_importances_

# the best estimator obtained from grid search has lower recall score while higher precision and accuracy score.
# Since the assignment requires both precision and recall larger than 0.3, I chose to use the classifier that meet this critiria
clf = AdaBoostClassifier()
clf.fit(X_train, y_train)
print test_classifier(clf, data_dict, features_list2, folds = 1000)
print clf.feature_importances_

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
test_classifier(clf, data_dict, features_list2, folds = 1000)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, data_dict, features_list2)