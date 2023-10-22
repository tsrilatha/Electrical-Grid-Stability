# -*- coding: utf-8 -*-
"""tmp (2) (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14ecYXL-b4uXcxY1CHycq_tXQgXwsH8ue

a) Datat Set description
"""

#import librairies and read the csv file using pandas
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

dataset = pd.read_csv("Electrical_Grid_Stability_Stimulated_Dataset.csv")
dataset.head() # #displays 5 observations.

# We display the summary statistics of our data set.
dataset.describe()

dataset.info() # information of the dataset.

"""b) Data Set Visualization  """

#Creating a scatterplot matrix for all the variables using seaborn.
sns.set_style("whitegrid");
# Plot pairwise relationships in a dataset.
sns.pairplot(dataset, hue="stabf", height=2);
plt.show()

"""From the pair plot above, the blue color indicate the distribution of observation with unstable response while orange indicate distribution of observations with stable response. By observing the scatter matrix the predictor variables datapoints are uniformaly distributed so we can conclude the predictor variables are independent to each other. The scatter matrix with the output variable and the predictors indicate that when predictor value increase the output tends to be unstable."""

#Correlation plot using seaborn heatmap
plt.figure(figsize=(16, 6))
heatmap = sns.heatmap(dataset.corr(),cmap='coolwarm', vmin=-1, vmax=1, annot=True)

"""It is important to verify the correlation between each numerical feature and the dependent variable stab, as well as correlation among numerical features leading to potential undesired collinearity. Correlation provides an overview of correlation between the dependent variable ('stab') and the 12 numerical features. Also, correlation between 'p1' and its components 'p2', 'p3' and 'p4' is above average, as expected, which as discussed in dataset description we will not use P1 for the prediction as it is the sum of P2 ,P3 and P4."""

#Ploting the histogram using seaborn histplot for the variables.
columns = set(dataset.columns) - set(['stab', 'stabf'])
fig, axes = plt.subplots(3, 4, figsize=(20,20))
for i, col in enumerate(columns):
    x, y = i//4, i % 4
    # 'Multiple' is approach to resolving multiple elements when semantic mapping creates subsets.
    p=sns.histplot(dataset, x=col, hue="stabf",multiple="stack", ax=axes[x, y])
    p.set_ylabel("Frequency", fontsize = 15)

plt.show()

"""From the above plots, We can see the density distribution of each attribute broken down by class value. Like the scatterplot matrix, the density plot by class can show the separation of classes. It can also help to us understand the overlap in class values for an attribute."""

# Visual representation of the histogram statistic.
#plots shows the desity plot of the variables in our data set.
fig, axes = plt.subplots(3, 4, figsize=(20,20))
for i, col in enumerate(columns):
    x, y = i//4, i % 4
    p=sns.histplot(dataset, x=col, hue="stabf", element="poly", ax=axes[x, y])
    p.set_ylabel("Density", fontsize = 15)
plt.show()

#ploting all the variables in a single visualization that contain all the boxplots.
sns.set()
fig, axes = plt.subplots(3, 4, figsize=(20,20))

for i, col in enumerate(columns):
    x, y = i//4, i % 4
    sns.boxplot(data=dataset, x=col, y='stabf', ax=axes[x, y])

plt.show()

print(f'Split of "unstable" (0) and "stable" (1) observations in the original dataset:')
print(dataset['stabf'].value_counts(normalize=True))
#The proportion of observations related to 'unstable' and 'stable' scenarios is mapped.

"""We therefore plot all the variables in a single visualization that contain all the boxplots.
Above boxplots indicate that there is not any case of outliers within our data set.

c) DATA CLEANING
"""

dataset_new=dataset.dropna() # Remove missing values.
dataset_new

"""Splitting our dataset into training, valadiation and testing."""

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import time
import itertools

required_dataset = dataset[['tau1','tau2','tau3','tau4','p2','p3','p4','g1','g2','g3','g4', 'stabf']]
train, test = train_test_split(required_dataset, test_size=0.2 , random_state=50)
train, val = train_test_split(train, test_size=0.1 , random_state=50)

features = ['tau1','tau2','tau3','tau4','p2','p3','p4','g1','g2','g3','g4']
train_X, train_y = train[features], train['stabf']
val_X, val_y = val[features], val['stabf']
test_X,test_y = test[features], test['stabf']

"""e) feature extraction and feature selection"""

def processSubset(feature_set):
    # Fit model on feature_set and calculate accuracy
    x = train_X[list(feature_set)].values
    LogReg=LogisticRegression(random_state=50)
    regr = LogReg.fit(x, train_y.values)
    accuracy = LogReg.score(val_X[list(feature_set)].values, val_y)
    return {"model":regr, "accuracy":accuracy, "feature_set": feature_set}

def getBest(k):
    tic = time.time()
    results = []
    for combo in itertools.combinations(features, k):
        results.append(processSubset(combo))
    # Wrap everything up in a nice dataframe
    models = pd.DataFrame(results)
    # Choose the model with the highest RSS
    best_model = models.loc[models['accuracy'].argmax()]
    toc = time.time()
    print("Processed", models.shape[0], "models on", k, "predictors in", (toc-tic), "seconds.")
    # Return the best model, along with some other useful information about the model
    return best_model

models_best = pd.DataFrame(columns=["accuracy", "model", "feature_set"])
tic = time.time()
for i in range(1,12):
    models_best.loc[i] = getBest(i)
toc = time.time()
print("Total elapsed time:", (toc-tic), "seconds.")

models_best

feature_columns_final = models_best['feature_set'][9]
models_best['model'][9].score(test_X[list(feature_columns_final)].values, test_y.values)

"""forward subset"""

def forward(predictors):
    # Pull out predictors we still need to process
    remaining_predictors = [p for p in features if p not in predictors]
    tic = time.time()
    results = []
    for p in remaining_predictors:
        results.append(processSubset(predictors+[p]))
    # Wrap everything up in a nice dataframe
    models = pd.DataFrame(results)
    # Choose the model with the highest accuracy
    best_model = models.loc[models['accuracy'].argmin()]
    toc = time.time()
    print("Processed ", models.shape[0], "models on", len(predictors)+1, "predictors in", (toc-tic), "seconds.")
    # Return the best model, along with some other useful information about the model
    return best_model

models_fwd = pd.DataFrame(columns=["accuracy", "model", "feature_set"])
tic = time.time()
predictors = []
for i in range(1,len(features)+1):
    models_fwd.loc[i] = forward(predictors)
    predictors = models_fwd.loc[i]["feature_set"]
toc = time.time()
print("Total elapsed time:", (toc-tic), "seconds.")

models_fwd

feature_columns_final = models_fwd['feature_set'][11]
models_fwd['model'][11].score(test_X[list(feature_columns_final)].values, test_y.values)

"""Backwards subset selection"""

def backward(predictors):
    tic = time.time()
    results = []
    for combo in itertools.combinations(predictors, len(predictors)-1):
        results.append(processSubset(combo))
    # Wrap everything up in a nice dataframe
    models = pd.DataFrame(results)
    # Choose the model with the highest RSS
    best_model = models.loc[models['accuracy'].argmin()]
    toc = time.time()
    print("Processed ", models.shape[0], "models on", len(predictors)-1, "predictors in", (toc-tic), "seconds.")
    # Return the best model, along with some other useful information about the model
    return best_model

models_bwd = pd.DataFrame(columns=["accuracy", "model" ,"feature_set"], index = range(1,len(features)))
tic = time.time()
predictors = features
while(len(predictors) > 1):
    models_bwd.loc[len(predictors)-1] = backward(predictors)
    predictors = models_bwd.loc[len(predictors)-1]["feature_set"]
toc = time.time()
print("Total elapsed time:", (toc-tic), "seconds.")

models_bwd

feature_columns_final = models_bwd['feature_set'][10]
models_bwd['model'][10].score(test_X[list(feature_columns_final)].values, test_y.values)

"""PCA"""

# construct a dataframe using pandas
import numpy as np
feature_dataset= dataset[list(features)]

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
# Scale data before applying PCA
scaling=StandardScaler()

# Use fit and transform method
scaling.fit(feature_dataset)
Scaled_data=scaling.transform(feature_dataset)

# Set the n_components=3
principal=PCA(n_components=6)
principal.fit(Scaled_data)
x_pca=principal.transform(Scaled_data)

# Check the dimensions of data after PCA
print(x_pca.shape)

#plot for explanied variance ratio
plt.plot(np.cumsum(principal.explained_variance_ratio_))
plt.xlabel('number of components')
plt.ylabel('cumulative explained variance');

# printing 6 principal components.
pc_df = pd.DataFrame(x_pca, columns = ['pc1', 'pc2','pc3','pc4','pc5','pc6'])
finalDf = pd.concat([pc_df, dataset[['stabf']]], axis = 1)
pc_df

# plot for 2 component PCA
fig = plt.figure(figsize = (8,8))
ax = fig.add_subplot(1,1,1)
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize = 20)
targets = ['stable','unstable']
colors = ['r', 'g', 'b']
for target, color in zip(targets,colors):
    indicesToKeep = finalDf['stabf'] == target
    ax.scatter(finalDf.loc[indicesToKeep, 'pc1']
               , finalDf.loc[indicesToKeep, 'pc2']
               , c = color
               , s = 50)
ax.legend(targets)
ax.grid()

principal.explained_variance_ratio_  # varience ratio of 6 principal compontnents

var=np.cumsum(np.round(principal.explained_variance_ratio_, decimals=3)*100)
var #cumulative sum of variance explained with [n] features

# import relevant libraries for 3d graph
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(figsize=(10,10))

# choose projection 3d for creating a 3d graph
axis = fig.add_subplot(111, projection='3d')

# x[:,0]is pc1,x[:,1] is pc2 while x[:,2] is pc3
axis.scatter(x_pca[:,0],x_pca[:,1],x_pca[:,1], c=dataset['tau1'],cmap='plasma')
axis.set_xlabel("PC1", fontsize=10)
axis.set_ylabel("PC2", fontsize=10)

print ("Proportion of Variance Explained : ", principal.explained_variance_ratio_)
out_sum = np.cumsum(principal.explained_variance_ratio_)
print ("Cumulative Prop. Variance Explained: ", out_sum)
# check how much variance is explained by each principal component
print("variance of principal component:" , principal.explained_variance_ratio_)

"""f) Model development  """

#Import the libraries and fit all the model with training set.
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import  QuadraticDiscriminantAnalysis

LogReg=LogisticRegression(random_state=50)
LogReg.fit(train_X,train_y)

knn = KNeighborsClassifier(n_jobs=-1, n_neighbors=5)
knn.fit(train_X,train_y)

lda = LinearDiscriminantAnalysis(solver='svd')
lda.fit(train_X,train_y)

qda = QuadraticDiscriminantAnalysis()
qda.fit(train_X,train_y)

svc = svm.SVC(kernel='rbf')
svc.fit(train_X, train_y)

dtc = DecisionTreeClassifier(criterion="entropy", max_depth=3)
dtc.fit(train_X,train_y)

rfc=RandomForestClassifier(random_state=1)
rfc.fit(train_X, train_y)

import seaborn as sns
from sklearn.metrics import confusion_matrix

# defining an funtion to perform the required classification metrix
def compute_performance_metrics(model, input_dataset, labels, header):
    y_pred = model.predict(input_dataset)
    report = classification_report(labels,y_pred, target_names = ['stable','unstable'])
    acc_score = model.score(input_dataset, labels )
    print(header)
    print(report)
    print(f"accuracy of the model {acc_score}")

    cf=confusion_matrix(labels, y_pred)

    ax = sns.heatmap(cf, annot=True, cmap='Blues', fmt='g')

    ax.set_title('Seaborn Confusion Matrix with labels\n\n');
    ax.set_xlabel('\nPredicted Values')
    ax.set_ylabel('Actual Values ');

    ## Ticket labels - List must be in alphabetical order
    ax.xaxis.set_ticklabels(['False','True'])
    ax.yaxis.set_ticklabels(['False','True'])

    ## Display the visualization of the Confusion Matrix.
    plt.show()

datasets = {
    "train": {"input": train_X, "output": train_y},
    "test": {"input": test_X, "output": test_y},
    "val": {"input": val_X, "output": val_y}
}

models = [{"model": LogReg, "model_name": "Logistic regression"},
          {"model": knn, "model_name": "KNN"},
          {"model": lda, "model_name": "LinearDiscriminantAnalysis"},
          {"model": qda, "model_name": "QuadraticDiscriminantAnalysis"},
          {"model": svc, "model_name": "SVM"},
          {"model": dtc, "model_name": "Decision Tree"},
          {"model": rfc, "model_name": "randomForest"},
         ]

for model in models:
    for dataset_type, value in datasets.items():
        compute_performance_metrics(model["model"], value["input"], value["output"], f"{model['model_name']} on {dataset_type} set")

# get the coceffients and intercecpt of logistic regression model
print('classes: ',LogReg.classes_)
print('coefficient: ',LogReg.coef_)
print('intercept: ',LogReg.intercept_)

# plot the important features used for rfc and dtc
Importance = pd.DataFrame({'Importance':rfc.feature_importances_*100}, index=features)
Importance.sort_values('Importance', axis=0, ascending=True).plot(kind='barh', color='b', )
plt.xlabel('Variable Importance')
plt.gca().legend_ = None

# Get the desicion tree plot with the max depth mentioned in the model for fitting.
import graphviz
from sklearn import tree
dot_data = tree.export_graphviz(dtc, out_file=None)
graph = graphviz.Source(dot_data)
graph.render("features")
tree.plot_tree(dtc)

#Plot the tree with the terminal nodes as stable or unstable
dot_data = tree.export_graphviz(dtc, out_file=None, feature_names=features,
                      class_names=True,
                      filled=True, rounded=True,
                      special_characters=True)
graph = graphviz.Source(dot_data)
graph

"""g) Fine-tune your models & Feature Set"""

#using random forest classifier for tuning the hyperparameters
from pprint import pprint
pprint(rfc.get_params())

import numpy as np
from sklearn.model_selection import RandomizedSearchCV
# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 100, stop = 200, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 80, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
print(random_grid)

rf_random = RandomizedSearchCV(estimator = rfc, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
# Fit the random search model
rf_random.fit(train_X, train_y)

rf_random.score(test_X, test_y)

from sklearn.model_selection import validation_curve

param_range = np.arange(1, 250, 2)

train_scoreNum, test_scoreNum = validation_curve(
                                RandomForestClassifier(),
                                X = train_X, y = train_y,
                                param_name = 'n_estimators',
                                param_range = param_range, cv = 3)

# Calculate mean and standard deviation for training set scores
train_mean = np.mean(train_scoreNum, axis=1)
train_std = np.std(train_scoreNum, axis=1)

# Calculate mean and standard deviation for test set scores
test_mean = np.mean(test_scoreNum, axis=1)
test_std = np.std(test_scoreNum, axis=1)

# Plot mean accuracy scores for training and test sets
plt.plot(param_range, train_mean, label="Training score", color="black")
plt.plot(param_range, test_mean, label="Cross-validation score", color="dimgrey")

# Plot accurancy bands for training and test sets
plt.fill_between(param_range, train_mean - train_std, train_mean + train_std, color="gray")
plt.fill_between(param_range, test_mean - test_std, test_mean + test_std, color="gainsboro")

# Create plot
plt.title("Validation Curve With Random Forest")
plt.xlabel("Number Of Trees")
plt.ylabel("Accuracy Score")
plt.tight_layout()
plt.legend(loc="best")
plt.show()

def evaluate(model, test_features, test_labels):
    predictions = model.predict(test_features)
    errors = abs(predictions - test_labels)
    mape = 100 * np.mean(errors / test_labels)
    accuracy = 100 - mape
    print('Model Performance')
    print('Average Error: {:0.4f} degrees.'.format(np.mean(errors)))
    print('Accuracy = {:0.2f}%.'.format(accuracy))

    return accuracy


from sklearn.model_selection import GridSearchCV
# Create the parameter grid based on the results of random search
param_grid = {
    'bootstrap': [True, False],
    'max_depth': [10, 20, 30, 40],
    'max_features': [2, 3],
    'min_samples_leaf': [1, 2, 4],
    'min_samples_split': [2, 5, 10],
    'n_estimators': [100, 200, 300, 1000]
}
# Create a based model
rf = RandomForestClassifier()
# Instantiate the grid search model
grid_search = GridSearchCV(estimator = rf, param_grid = param_grid,
                          cv = 3, n_jobs = -1, verbose = 2)

grid_search.fit(train_X, train_y.factorize()[0])

grid_search.best_params_

best_grid = grid_search.best_estimator_

best_grid.score(test_X, test_y.factorize()[0])

"""SVM hyperparameter tuning"""

kernels = ['Polynomial', 'RBF', 'Sigmoid','Linear']#A function which returns the corresponding SVC model
def getClassifier(ktype):
    if ktype == 0:
        # Polynomial kernal
        return SVC(kernel='poly', degree=8, gamma="auto")
    elif ktype == 1:
        # Radial Basis Function kernal
        return SVC(kernel='rbf', gamma="auto")
    elif ktype == 2:
        # Sigmoid kernal
        return SVC(kernel='sigmoid', gamma="auto")
    elif ktype == 3:
        # Linear kernal
        return SVC(kernel='linear', gamma="auto")

from sklearn.svm import SVC
for i in range(4):
    svclassifier = getClassifier(i)
    svclassifier.fit(train_X, train_y.factorize()[0])# Make prediction
    y_pred = svclassifier.predict(test_X)# Evaluate our model
    print("Evaluation:", kernals[i], "kernel")
    print(classification_report(test_y,y_pred))

"""Lasso regression using logistic regression"""

coefficient_values = []
powers = []
for c in np.arange(-10, 10):
    lasso=LogisticRegression( penalty ='l1', solver='liblinear',random_state=50, C=np.power(10.0, c))
    lasso.fit(train_X,train_y.factorize()[0])
    lasso.score(train_X,train_y.factorize()[0])
    coefficient_values.append(lasso.coef_.flatten())
    powers.append(np.power(10.0, c))

ax = plt.gca()
ax.plot(powers, coefficient_values)
ax.set_xscale('log')
plt.axis('tight')
plt.xlabel('alpha')
plt.ylabel('weights')
plt.title('Lasso coefficients as a function of the regularization');

coefficient_values

#log regression
from sklearn.linear_model import LogisticRegressionCV

lasso=LogisticRegressionCV( penalty ='l1', solver='liblinear',random_state=50, Cs=list(np.power(10.0, np.arange(-10, 10)))
)
lasso.fit(train_X,train_y.factorize()[0])
lasso.score(train_X,train_y.factorize()[0])

lasso.fit(test_X,test_y.factorize()[0])
lasso.score(test_X,test_y.factorize()[0])

pd.Series(lasso.coef_.flatten(), index=features)

"""Deciscion tree hyperparameter tuning"""

from sklearn.model_selection import GridSearchCV
dt = DecisionTreeClassifier(random_state=42)
# Create the parameter grid based on the results of random search
params = {
    'max_depth': [2, 3, 5, 10, 20],
    'min_samples_leaf': [5, 10, 20, 50, 100],
    'criterion': ["gini", "entropy"]
}

# Instantiate the grid search model
grid_search = GridSearchCV(estimator=dt,
                           param_grid=params,
                           cv=4, n_jobs=-1, verbose=1, scoring = "accuracy")

grid_search.fit(train_X, train_y.factorize()[0])

score_df = pd.DataFrame(grid_search.cv_results_)
score_df.head()

score_df.nlargest(5,"mean_test_score")

grid_search.best_estimator_

dt_best = grid_search.best_estimator_

def evaluate_model(dt_classifier):
    print("Train Accuracy :", accuracy_score(train_y.factorize()[0], dt_classifier.predict(train_X)))
    print("Train Confusion Matrix:")
    print(confusion_matrix(train_y.factorize()[0], dt_classifier.predict(train_X)))
    print("-"*50)
    print("Test Accuracy :", accuracy_score(test_y.factorize()[0], dt_classifier.predict(test_X)))
    print("Test Confusion Matrix:")
    print(confusion_matrix(test_y.factorize()[0], dt_classifier.predict(test_X)))

from sklearn.metrics import confusion_matrix, accuracy_score
evaluate_model(dt_best)

def get_dt_graph(dt_classifier):
    fig = plt.figure(figsize=(25,20))
    _ = tree.plot_tree(dt_classifier,
                       feature_names=features,
                       class_names=['No Disease', "Disease"],
                       filled=True)

get_dt_graph(dt_best)

print(classification_report(test_y.factorize()[0], dt_best.predict(test_X)))