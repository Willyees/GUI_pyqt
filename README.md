**Honours project - Napier University - 2018/2019**
Comparison of unsupervised and supervised machine learning techniques in network anomaly detection

## Aim
The project is focused in applying different machine learning techniques to the problem of network intrusion detection. Amongst the available approaches, anomaly detection is used to find deviations from normal network traffic, discovering possible attacks.

A desktop application has been created that let the user import datasets to be analyzed. Different types of algorithms can be applied, creating models that would be able to predict attack connections in the network.

Users can compare different algorithms results, understanding which performs better and what might be the shortcomings.


## Overview
The application present itself with a clean user interface able to perform initial operations on datasets as:
- load a preloaded dataset
- import a new dataset
- import a new testset
- view attributes detail of the dataset selected
- delete attributes from the dataset loaded
- apply algorithm

![GUI_initial](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/GUI_front.png)

The GUI has been created by utilizing [PyQt5](https://pypi.org/project/PyQt5/) module.

The application has preloaded two datasets that can be used to view its capabilities quickly, without the need to create and import any dataset.

The first is "KDD99", a dataset used in Third International Knowledge Discovery and Data Mining Tools Competition, available at [http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html](http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html). The competition was aimed to build network intrusion detectors.

It is a very large csv file, loaded directly from the sklearn module, so it must be installed in order to load the dataset.

The second is a very small dataset "TEST" mostly used for debugging purposes because it can load very quickly.

Once dataset has been imported, information about each attribute can be viewed on the right panel and the "algorithm to apply" button is enabled.

Important: user must import a test set in order to be able to proceed and apply an algorithm to the dataset! Otherwise the console will inform the user by outputting the error information.

The preloaded KDD99 will import automatically a test set which has removed categorical attributes.

=======

Once user starts off the algorithm will be presented with a new window, showing the results of the algorithm run.

![settings_rerun](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/settings_rerun.png)

Detection rate and false alarm rate are plotted on a bar chart for quick comparison. Below, a table outputs more precisely the results.

It is possible to compare multiple runs of algorithms by selecting the run on the right panel and clicking the "compare" button.

Additionally, it is possible to modify the last algorithm run's properties and rerun it again. Below are presented the available properties modifiable.

### GUI implementation
MVC architectural has been utilised to create a flexible and low decoupled structure

![mvc](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/mvc.png)

The business logic is only present in the model part, the controller is the head of the application which calls the features needed to perform specific operations. The view, only receives data to be shown graphically on the application and decides how to arrange visual components.


## ML Algorithms
- **K-Means clustering**

![kmeans](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/kmeans.png)

K-Means is low computational complexity, since usually is implemented with fixed maximum iterations, resulting in linear complexity

The major drawbacks of the k-means algorithms are the fixed number of clusters k that needs to be presented at beginning of the algorithm. 

Lastly, it is not possible to utilize categorical features in a k-means algorithm. A suitable transformation is needed to be applied, converting into numerical values.

- **Self Organising Map**

![som](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/som.png)

SOM is an artificial neural network utilizing unsupervised learning to organize input data in to a set of classes created by two-dimensional neurons lattice. Its main purpose is then to group similar data instances into two- or three-dimensional neurons, regardless of the data dimensionality.

SOM is based on multiple iterations of training in which the updates on the units are gradually smaller, resulting in map of stable zones.


- **Fixed Width clustering**

![fixed_width](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/fixed_width.png)

Also called single linkage clustering is similar to the k-means algorithm, but the advantage is the dynamic creation of clusters number based on cluster’s width parameter.

This algorithm is very susceptible to not-normalized data: it has to utilize a distance metric that takes into account the different range of data features or take advantage of normalized training data. In the application two distances are available: Euclidian and Manhattan

## Dataset modification
As found out during the literature review and by exploring the KDD99 dataset, it is evident that the records were artificially created because the number of attacks are 80% which is unusually high for a normal network traffic.

The trainset has been modified to be more similar at real networks.

- Categorical attributes transformed with frequency technique
- Attributes normalized using min-max normalization
- Removed some types of attacks that were dominating the whole dataset

## Testingset
Two type of testing sets have been adopted: the first will be used to test against the same type of attacks, instead the second will have novel type of attacks that were not present in the training set. This is a usual set up in network anomaly detection.

## Results

![original_kd99_results](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/original_kd99_results.png)

These results are obtained utilizing the original KDD99 10% training data with full KDD test data. The best result for each algorithm is presented.

K-Means and simple-linkage perform uniformly even though the first is unsupervised trained.

SOM has the highest detection rate, but its false alarm is extreme. Related to novel attacks, SOM perform best with almost all the attacks detected. The other two scored low novel attacks.

On the other hand, when applied to the filtered dataset, the results were unsatisfactory. Especially the SOM seems that it will not be able to perform well with vey unbalanced datasets.

K-means only reaches 20% for 20 clusters before starting to drop off, most likely because of overfitting generated from high number of clusters. 

![nsl_kdd99_results](https://github.com/Willyees/GUI_pyqt/blob/assets/assets/nsl_kdd_results.png)

The above results were obtained with the standardized NSL-KDD99 filtered trainset. It can be seen that the detection rate is noticeably lower. This is caused by the different ratio of attack#/normal#. In fact in the second having less attacks, the models are under-trained for anomaly connections, resulting in a less detection rate.

Overall, there is not much difference in performances registered between the unsupervised K-Means and supervised single-linkage. In case of high cost on determining the labels for the training set, it should be chosen the unsupervised algorithm.

The overall detection rate performance is very dependent on the training data distribution. This is especially visible on the SOM, where the high number of attacks will create a map highly specialized for anomalies and misplace normal connections.

The experiment performed were much more extended than the only ones proposed here. If you want to get bored, I might provide the dissertation if contacted by e-mail.

