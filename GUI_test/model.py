from sklearn import datasets
import math
import numpy as np
import os.path
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
from sklearn import preprocessing
import math
from minisom import MiniSom
from timeit import default_timer as timer
from collections import defaultdict
import itertools

class Model(object):
    
    def __init__(self):
        self.dataset = Dataset()
        self.testing_set = Dataset()
        self.datasets_location = dict()
        self.datasets_location['KDD99'] = 'inner'
        self.datasets_location['TEST'] = 'inner'
        self.algorithms = set() #available algorithms
        self.set_algorithms()
        self.results = [] #list of results
        self.current_algorithm = Algorithm()
    
    def set_algorithms(self):
        #KMEAN 
        kmean = Algorithm_Kmean(2)
        #kmean.set_properties({'n_cluster': 8}) #to finish
        self.algorithms.add(kmean)
        #SOM
        som = Algorithm_Som()
        #som.set_properties({'x': 6, 'y': 6, 'sigma': 1.0, 'learning_rate': 0.5, 'neighborhood_function': 'gaussian', 'random_seed' : None}) #adding them internally to the object
        som.set_properties_choices({som.neighborhood_function_print: ['gaussian','mexican_hat','bubble','triangle']})
        self.algorithms.add(som)
        #Fixed With Clust
        fixed_width = Fixed_Width_Clustering(width = 2.5)
        fixed_width.set_properties_choices({fixed_width.distance_alg_print: ['euclidean', 'manhattan']})
        self.algorithms.add(fixed_width)
    
    def set_current_algorithm(self, algorithm):
        """set the current algorithm as the one passed as argument with default settings"""
        for elem in self.algorithms: #find the algorithm required amongst the available ones and load it
            if elem.name == algorithm:
                alg = elem
                self.current_algorithm = alg
                break

    def apply_current_algorithm(self):
        if(self.dataset.size > 0):
            if(self.dataset.attr_size != self.testing_set.attr_size):
                print("different attributes between training and testing set")
                return {}
            alg = self.current_algorithm
            results = alg.apply_alg(self.dataset, self.testing_set)
            if(results.show_results()):
                self.results.append(results)
            return results.show_results()
            
        else:
            #show message box error
            print('no dataset loaded! Cannot perform algorithm')
            return {}

    
    def get_som_coord_clusters_normal(self):
        """return coordinates for normals and anomalies clusters created in the som
           [[normal],[anomaly]] 
           normal: [[x1,x2,..],[[y1,y2,..]]
        """ 
        map_labeled = self.get_som_map_label()
        if not(map_labeled):
            return
        outlier = [[] for x in range(2)] #[[x1,x2..],[y1,y2..]]
        inlier = [[] for x in range(2)]
        for key in map_labeled:
            if map_labeled[key][0] == 'normal.':
                inlier[0].append(key[0])
                inlier[1].append(key[1])
            elif map_labeled[key][0] == 'attack.':
                outlier[0].append(key[0])
                outlier[1].append(key[1])
        return [inlier, outlier]
    
    def clear_storage_new_load(self):
        """clear results and current algorithm"""
        self.results.clear()
        self.current_algorithm = Algorithm()

    def get_som_map_label(self):
        """get last som map label calculated"""
        if(self.results):
            result = self.results[len(self.results) - 1]
            if type(result) != Result_Som:
                print("Last result is not a SOM, there is no map label to show")
                return
            map_label = result.map_label
            return map_label
        else:
            print("No results stored yet, run algorithm at least once")
            return
    
    def get_result(self, index):
        print(self.results[index].algorithm_settings.name)#DEBUG
        return self.results[index].show_results()

    def get_results(self, indexes):
        results = []
        for index in indexes:
            results.append(self.results[index].show_results())
        print(results)
        return results
        
    def get_result_alg_properties(self, index):
        return self.results[index].algorithm_settings.get_properties()

    def get_results_alg_names(self):
        names = []
        for result in self.results:
            names.append(result.algorithm_settings.name_print)
        return names
    
    def get_results_alg_names_chosen(self, indexes):
        names = []
        for index in indexes:
            names.append(self.results[index].algorithm_settings.name_print)
        return names

    def get_last_result(self):
        return self.results[len(self.results) - 1].show_results()

    def get_current_alg_name(self):
        return self.current_algorithm.name

    def get_current_alg_properties(self):
        current_alg = self.current_algorithm
        return current_alg.get_properties()
    
    def get_current_alg_properties_choices(self):
        properties = self.get_current_alg_properties()
        choices = self.current_algorithm.get_properties_choices()
        for key in choices:
            if not(key in properties):
                print("mismatch between choice properties and properties for the current algorithm")
                return
        return choices

    def modify_properties_alg(self, properties):
        self.current_algorithm.set_properties(properties)

    def dataset_path_to_name(self, path):
        path_splitted = path.split('/')
        name = (path_splitted[len(path_splitted) - 1]).split('.')[0] #last part of directory, less the extension
        return name

    def set_dataset_location(self, path):
        """set the name and location of the dataset in the map"""
        name = self.dataset_path_to_name(path)
        if not(path in self.datasets_location):
            self.datasets_location[name] = path#name is key in dictionary
        else:
            print("dataset directory provided already contains a dataset, did not add it")
    
    def check_existence_dataset_file(self, path):
        """check that dataset path is a file, if not remove it from the datasets_directory if present"""
        if not(os.path.isfile(path)):
            print("No file matching the directory specified for ", path)
            name = self.dataset_path_to_name(path)
            if (self.datasets_location.get(name) != None and name != 'inner'):#do not delete inner elements (loaded interally like KDD99)
                del self.datasets_location[name]
            return False
        return True

    def transform_to_correct_type(self, str):
        type = self.attribute_single_type(str)
        if(type == "Categorical"):
            return str
        elif(type == "Continuous"):
            return float(str)
        elif(type == "Discrete"):
            return int(str)

    def get_dataset_names(self):
        return list(self.datasets_location.keys())

    def get_algorithm_names(self):
        l = []
        for alg in self.algorithms:
            l.append(alg.name)
        return l

    def get_dataset_current_name(self):
        print('current dataset:', self.dataset.name)
        return self.dataset.name

    def get_test_set_current_name(self):
        return self.testing_set.name

    def get_attr_size(self):
        return self.dataset.attr_size
    
    def show_test_set_properties(self):
        return self.testing_set.show_dataset()
    
    def show_train_set_properties(self):
        return self.dataset.show_dataset()

    def read_testing_set(self, path):
        if not(os.path.isfile(path)):
            print("No file matching the directory specified for ", path)
            return False
        testing_loaded = self.read_dataset(path)
        if(testing_loaded.attr_size == 0):
            return False
        self.testing_set = testing_loaded
        #not setting the dataset names (this is the testing, which cannot be loaded as a training usign the combobox)
        return True


    def read_training_set(self, path):
        print('Reading dataset')
        dataset_loaded = self.read_dataset(path)
        if(dataset_loaded.attr_size == 0): #if empty dataset, it has not been possible to load it
            return False
        self.dataset = dataset_loaded

        self.set_dataset_location(path)
        return True


    def read_dataset(self, path):
        if not(self.check_existence_dataset_file(path)): #skipping the open file, if this function already checked that file do not exists
            return Dataset()
        #use try catch, in case has been removed in the time being
        try:
            file = open(path, 'r')
        except IOError:
            print("No file present!")
            return Dataset() #return empty dataset
        #clear results and current algorithm when loading a new dataset
        self.clear_storage_new_load()
        dataset = []
        target = []
        attr_names = [] #could use a set
        #set attribute names in the dataset (only fist line taken)
        line = file.readline() #add: check that are all different
        line_split = line.replace('\n', '').split(',')
        print(line_split[len(line_split) -1])
        for attr in line_split:
            if attr in attr_names:
                print("There is a duplicate attribute name, or the first line is not attribute line")
                return Dataset()
            attr_names.append(attr)
        #set attributes values
        #should not assume that index for class label is the last column
        #index_label = (dataset.attr_num - 1) if index == -1 else index 
        for line in file.readlines():
            temp = line.replace('\n', '').split(',')
            target.append(temp.pop())
            dataset.append(temp)
        file.close()

        print(dataset[0])
        d_m = dataset.copy()
        start = timer()
        ##setting the type of input data following rules utilized to check type of attributes
        #for i in range(len(dataset)):
        #    #dataset[i] = [self.transform_to_correct_type(x) for x in dataset[i]] #very slow! might better just check if it is float or not
        #    for inn in range(len(dataset[i])):
        #        d_m[i][inn] = self.return_type_fast_safe(dataset[i][inn])
        #end = timer()
        #print("timer", str(end - start))
        #print(dataset[0])

        start = timer()
        #setting the type of input data following rules utilized to check type of attributes
        for i in range(len(dataset)):
            #dataset[i] = [self.transform_to_correct_type(x) for x in dataset[i]] #very slow! might better just check if it is float or not
            for inn in range(len(dataset[i])):
                d_m[i][inn] = self.return_type_fast(dataset[i][inn])
        end = timer()
        print("timer", str(end - start))
        print(dataset[0])

        #start = timer()
        ##setting the type of input data following rules utilized to check type of attributes
        #for i in range(len(dataset)):
        #    d_m[i] = [self.transform_to_correct_type(x) for x in dataset[i]] #very slow! might better just check if it is float or not
        #end = timer()
        #print("timer", str(end - start))
        #print(dataset[0])

        d = Dataset()

        d.target = np.asarray(target)
        d.data = np.asarray(dataset, dtype = np.dtype(object))
        d.set_properties() #some properties not set, still referring to old dataset
        d.set_name_path(self.dataset_path_to_name(path), path)
        d.set_attribute_names(attr_names)
        
        return d

    def return_type_fast(self, item : str):
        """improvement in the return_single_attribute. Assume passing string
           returns converted value into the correct type read from a string"""
        if(item == ""):
            print("Attribute value is incorrect: empty")
            return ""

        if (item.replace('.', '').replace('e', '').replace('-',"").isdecimal()):#working atm, very likely that string inputted do not follow only these paramethers
        #if(self.is_float(item)): #slower than checking manually
            if (item.find('.') == -1):
                    return int(item)
            else:
                return float(item)
        else:
            return item

    def return_type_fast_safe(self, item):
        if(item == ""):
            print("Attribute value is incorrect: empty")
            return ""

        if(self.is_float(item)): #slower than checking manually
            if (item.find('.') == -1):
                    return int(item)
            else:
                return float(item)
        else:
            return item

    def timer(self):
        s = "1.2e2"
        start = timer()
        for i in range(1000):
            s.isdecimal()
        end = timer()
        print(str(end - start))
        start = timer()
        for i in range(1000):
            s.isnumeric()
        end = timer()
        print(str(end - start))
        start = timer()
        for i in range(1000):
            s.isdigit()
        end = timer()
        print(str(end - start))

    def load_dataset(self, dataset_name):
        """retreives data and works on it"""
        #find dataset directory in map
        #DEBUG
        if(dataset_name.upper() == "TEST"):
            self.clear_storage_new_load()
            print('Reading dataset') #trainign and testing are the same
            self.dataset.data = np.asarray([[1,1.5],[2,2.5],[10,3.5],[25,9.5]])
            self.dataset.target = np.asarray(['normal.', 'normal.', 'attack.', 'attack.'])
            self.dataset.set_attribute_names(np.asarray(['a','b']))
            self.dataset.set_properties()
            self.dataset.set_name_path('TEST', 'inner')
            self.datasets_location['TEST'] = 'inner'
            self.testing_set.data = np.asarray([[1,1.5],[2,2.5],[10,3.5],[25,9.5]])
            self.testing_set.target = np.asarray(['normal.', 'normal.', 'attack.', 'attack.'])
            self.testing_set.set_attribute_names(np.asarray(['a','b']))
            self.testing_set.set_properties()

        elif(dataset_name.upper() == "KDD99"): #special case. Using sklearn lib to load it
            self.clear_storage_new_load()
            print('Reading dataset') #not loading testing, have to use import button
            kdd = datasets.fetch_kddcup99()
            self.dataset.data = kdd.data
            self.dataset.target = np.array([str(x, 'utf') for x in kdd.target])
            self.dataset.set_attribute_names(np.array(['duration','protocol_type','service','flag','src_bytes','dst_bytes','land','wrong_fragment','urgent','hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted','num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','is_host_login','is_guest_login','count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate'])) # no class attribute name
            self.dataset.set_properties()
            self.dataset.set_name_path('KDD99', 'inner')
            self.datasets_location['KDD99'] = 'inner'
            
        else:
            if(dataset_name in self.datasets_location): #only execute if the dataset name is present in the map
                return self.read_training_set(self.datasets_location[dataset_name])
                
        return True

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False     
    #def get_directory_dataset(self, name):
    #    if(name in self.datasets_location):
    #        return self.datasets_location[name]
    #    else:
    #        return ''

    def attributes_names(self):
        return self.dataset.attr_names

    def attributes_type(self):
        """attributes types are returned from current dataset"""
        self.dataset.attr_types = self.attributes_type_packing(self.dataset.data)
        return self.dataset.attr_types
        
    def attributes_type_packing(self, dataset):
        #using the '.' symbol to undestand if float or integer
        attribute_types = []
        for index, item in enumerate(dataset[0]): #only the first row
            attribute_types.append(self.attribute_single_type(item, index))
        return attribute_types

    
    def attribute_single_type(self, item, index = -1):
        #used to return each attribute as a single type. It can be reused in other functions. Can be utilized without binary return usign -1 index
        if(str(item) == ""):
            print("Attribute value is incorrect: empty")
            return ''

        #if ((str(item)).replace('.', '').isdigit()):
        if(self.is_float(item)):  
            #if(int(item) == 1 or int(item) == 0):
            if(index != -1 and self.attribute_check_if_binary(index)):
                #print('Binary')
                return ('Binary')

            if (str(item).find('.') == -1):
                    #print('Discrete')
                    return ('Discrete')
            else:
                #print('Continuous')
                return ('Continuous')
        else:
            #print('Categorical')
            return ('Categorical')
        
    def attribute_check_if_binary(self, index):
        if(type(self.dataset.data[0][index]) == float):
            f = 0.0
            t = 1.0
        elif(type(self.dataset.data[0][index]) == int):
            f = 0
            t = 1
        else:
            return False #only working for float and int

        for item in self.dataset.data:
            if(item[index] != f and item[index] != t):
                return False
        return True


    def calculate_info_attribute(self, index):
        #to do:check that first is not empty (missing) and find next proper one. Not sure if I should check against "" string only
        attr_type = self.attribute_single_type(self.dataset.data[0][index], index)
        if(attr_type == 'Categorical'):
            return self.calculate_info_categorical(index)
        elif(attr_type == 'Discrete' or attr_type == 'Continuous'):#trying with a discrete
            #set info in the right format (each inner list is one row in the view)
            continuous = self.calculate_info_continuous(index)
            l_formatted = [['Minimum value:', continuous[0]], ['Maximum value:', continuous[1]],['Mean:', continuous[2]],['Standard Deviation:', continuous[3]]]
            return l_formatted
        elif(attr_type == 'Binary'):
            return self.calculate_info_binary(index)
        else:
            print("Attribute is not supported")
            return ''

    def calculate_info_binary(self, index):
        categories = [['Value:', 'Frequency:', 'Percentage:']]
        
        if(self.dataset.data[0][index] != ""):
            categories.append([self.dataset.data[0][index], 1])
        for i in range(1, self.dataset.size):
            for item in categories:
                if(self.dataset.data[i][index] != "" and self.dataset.data[i][index] == item[0]):
                    item[1] += 1
                    break
            else:
                categories.append([self.dataset.data[i][index], 1])

        for i in range(1, len(categories)):
            categories[i].append(round(categories[i][1] / self.dataset.size * 100, 3))
        return categories
        

    def calculate_info_continuous(self, index):
        #min, max, mean, std deviation
        minimum, maximum, mean = self.calculate_minmaxmean(index)
        std_deviation = self.calculate_stddeviation(index, mean)
        return [minimum, maximum, mean, std_deviation]
        
    def calculate_stddeviation(self, index, mean):
        sigma = 0
        for i in range(self.dataset.size):
            sigma += (self.dataset.data[i][index] - mean) ** 2
        std_deviation = math.sqrt(sigma / self.dataset.size)
        return round(std_deviation, 2)

    def calculate_minmaxmean(self, index):
        m = self.dataset.data[0][index]
        h = self.dataset.data[0][index]
        sum = 0
        for i in range(1, self.dataset.size):
            sum += self.dataset.data[i][index]
            if(self.dataset.data[i][index] < m):
                m = self.dataset.data[i][index]
            if(self.dataset.data[i][index] > h):
                h = self.dataset.data[i][index]
        mean = sum / (self.dataset.size)
        
        return [round(m, 2), round(h, 2), round(mean, 2)]

    def calculate_info_categorical(self, index):
        """find different categories and their frequencies. returned list: [[name1, frequency], [name2, freq2]..]"""
        categories = [['Value:', 'Frequency:']]
        
        if(self.dataset.data[0][index] != ""):
            categories.append([self.dataset.data[0][index], 1])
        for i in range(1, self.dataset.size):
            for item in categories:
                if(self.dataset.data[i][index] != "" and self.dataset.data[i][index] == item[0]):
                    item[1] += 1
                    break
            else:
                categories.append([self.dataset.data[i][index], 1])
        return categories
            
    def remove_attributes_dataset(self, attributes):
        if isinstance(self.dataset.data, np.ndarray):
            self.dataset.data = np.delete(self.dataset.data, attributes, 1)
            self.dataset.attr_names = np.delete(self.dataset.attr_names, attributes, 0)
            self.dataset.set_properties()
            print('attributes :', attributes, 'deleted')
            print(self.dataset.attr_size, self.dataset.data[0])
            
        elif isinstance(self.dataset.data, list):
            print('list')
            new_dataset = [] 
            for record in self.dataset.data:
                new_dataset.append(np.delete(record, attributes)) #very slow method to create new dataset
            print(len(new_dataset[0]), new_dataset[0])
            self.dataset.data = new_dataset
            self.dataset.set_properties()

        else:
            print("Error - cant remove from empty dataset")
        return None

    def attr_nominal_to_binary(self, indexes):
        """transform nominal attributes given from the indexes into binaries, returns true if at least one attribute has been transformed"""
        categ_flag = False
        #take away the indexes of not categorical attributes
        no_categ_index = [] #stores the index of the indexes to be deleted
        print(indexes)
        for index in indexes[:]:
            if (self.attribute_single_type(self.dataset.data[0][index], index) == 'Categorical'):
                categ_flag = True #flag used to signal the execution of at least one transformation (view needs to be refreshed)
            else:
                indexes.remove(index)
                print("Attributes selected are not categorical types")
        
        print(indexes)
        if (categ_flag):
            sets = self.sets_of_nominal_attributes(indexes)
            self.attr_nominal_to_binary_add_attr(sets, indexes)
            self.remove_attributes_dataset(indexes)
        return categ_flag

    def set_attr_names_nominal_to_binary(self, indexes, sets):
        #indexes is used to retreive the name of the original attribute so it can be set as -> xes: port = http
        for attr in sets:
            for item in attr:
                self.dataset.attr_names = '= ' + str(item)

    def resize_dataset_add_attributes(self, list):
        """resize the dataset to add all the items in the list, works on jagged lists and list of lists"""
        elements = sum(len(item) for item in list)
        
        additional_elements = np.zeros((self.dataset.size, elements), dtype = int)
        self.dataset.data = np.concatenate((self.dataset.data, additional_elements), axis = 1)
        self.dataset.attr_size += elements
        
        
    def attr_nominal_to_binary_add_attr(self, sets, indexes):
        #sets is list of list: have to 
        #have to resize the array - problem: resize only takes from other close array and inglobe their data.
        sets_elements = sum(len(item) for item in sets)
        self.resize_dataset_add_attributes(sets)
        for i1 in range(self.dataset.size):
            current_index = self.dataset.attr_size - sets_elements
            for i_set, index in enumerate(indexes):
                #index where the new attribute will be placed: first set item will be after last element in old dataset (like append)
                for el_set in sets[i_set]:
                    if(self.dataset.data[i1][index] == el_set):
                        self.dataset.data[i1][current_index] = 1
                        
                    #no need to else, because new attributes have been set to 0 previously. Only switch the ones to 1.
                    #else:
                    #    self.dataset.data[i1][current_index] = 0
                    #current_index += 1

    def sets_of_nominal_attributes(self, indexes):
        """returns a list of sets of unique values are taken from each attributes passed (as indexes of the dataset)"""
        nominal_set = [set() for _ in range(len(indexes))]

        for i1 in range(self.dataset.size):
            for set_index, i2 in enumerate(indexes):
                nominal_set[set_index].add(self.dataset.data[i1][i2]) 
        return nominal_set

    def test(self):
        f = open(r"C:\Users\User\Downloads\kddcup.data_10_percent\fixed_alg_outcome.csv", "a")
        
        self.read_training_set(r"C:\Users\User\Downloads\kddcup.data_10_percent\filtered_freq_normmax_names.csv")
        self.read_testing_set(r"C:\Users\User\Downloads\kddcup.data_10_percent\tests\test_freq_filtered_maxnorm_names.csv")
        #self.read_testing_set(r"C:\Users\User\Downloads\kddcup.data_10_percent\test_test_names.csv")
        #self.read_training_set(r"C:\Users\User\Downloads\kddcup.data_10_percent\test_names.csv")
        for i in [2.5]:
            alg = Fixed_Width_Clustering(i)
            f.write("Threshold: "+ str(i))
            train_cluster_labels = alg.train_alg_labels(self.dataset.data, self.dataset.target)
            test_map_label = alg.test_alg_label(self.testing_set.data, self.testing_set.target)
            map_labels = list(zip(list(zip(*train_cluster_labels))[0],test_map_label))
            out = []
            for cluster in map_labels:#a giant mess, fix it using a proper structure
                temp = [cluster[0]]
                for index in range(len(cluster[1])):
                    temp.append(cluster[1][index])
                out.append(temp)

            detection_rate = alg.calculate_detection_rate(out)
            false_alarm = alg.calculate_false_alarm(out)
            print(detection_rate)
            print(false_alarm)
            f.write("TRAINING")
            for label in train_cluster_labels:
                temp = ""
                for elem in label:
                    temp = temp + str(elem) + ","
                temp += "\n"
                f.write(temp)
            f.write("TESTING")
            for label in test_map_label:
                temp = ""
                for elem in label:
                    temp = temp + str(elem) + ","
                temp += "\n"
                f.write(temp)
            f.write("******")
        f.close()
        #print(labels_)
        #print(len(alg.clusters))
        
            

class Dataset(object):
    def __init__(self):
        self.data = [[]]
        self.target = [] #labels
        self.attr_names = []
        self.attr_types = []
        self.attr_size = 0
        self.normal_n = 0 #number of normal connections
        self.attack_n = 0
        self.size = 0
        self.name = ''
        self.path = ''
        ##print variables
        self.name_print = "Name Dataset"
        self.attr_size_print = "Number of attributes"
        self.normal_n_print = "Normal connections"
        self.attack_n_print = "Attack connections"
        self.size_print = "Number of total connections"

    def show_dataset(self):
        """method returing a dictionary useful to the view to print all the relevant informations"""
        return {self.name_print : self.name, self.attr_size_print : self.attr_size, self.normal_n_print : self.normal_n, self.attack_n_print : self.attack_n, self.size_print : self.size}

    def set_properties(self, normal_label = 'normal.'):
        if len(self.data) != 0:
            self.attr_size = len(self.data[0])
            self.size = len(self.data)
            self._set_normal_attack_n(normal_label)

    def _set_normal_attack_n(self, normal_label = 'normal.'):
        """setting the number of normal and attack total connections in the dataset, it can use different index and normal label"""
        #not reliable on inner KDD
        c_normal = 0
        c_attack = 0
        for label in self.target:
            if label == normal_label:
                c_normal += 1
            else:
                c_attack += 1
        self.normal_n = c_normal
        self.attack_n = c_attack

    def set_name_path(self, name, path):
        self.name = name
        self.path = path

    def set_attribute_names(self, attr_names):
        self.attr_names = attr_names

    


class Algorithm(object): #abstract class
    def __init__(self):
        self.name = ''
        self.properties_choices = {} #dictionary of properties that the user can choose from
        
    #def set_properties(self, properties): #[properties: [[name1, value1], [name2, value2]]
        #add or modify existing property
        #for property, value in properties.items():
        #    self.properties[str.lower(str(property))] = value
    
    def get_properties_choices(self):
        return self.properties_choices

    def get_properties(self):
        raise NotImplementedError()

    def set_properties(self):
        return NotImplementedError()

    def copy(self):
        return NotImplementedError()

    def apply_alg(self, training_set, testing_set):
        return NotImplementedError()

    def set_properties_choices(self, choices : dict): #choices {property : [choices]}
        for key, value in choices.items():
            self.properties_choices[(str(key))] = value

class Algorithm_Som(Algorithm):
    def __init__(self, x = 6, y = 6, sigma = 1.0, learning_rate = 0.5, neighborhood_function = 'gaussian', random_seed = None): #intial settings
        super(Algorithm_Som, self).__init__()
        self.name = 'Self Organizing Map'
        self.x = x
        self.y = y
        self.sigma = sigma
        self.learning_rate = learning_rate
        self.neighborhood_function = neighborhood_function
        self.random_seed = random_seed

        #variables holding print names for internal settings
        self.name_print = 'som'
        self.x_print = 'Map Width'
        self.y_print = 'Map Height'
        self.sigma_print = 'Sigma'
        self.learning_rate_print = 'Learning rate'
        self.neighborhood_function_print = 'Neighborhood function'
        self.random_seed_print = 'Random seed'

    def set_properties(self, properties):
        """set properties from dictionary like structure (expecting correct type value in the dictionary"""
        self.x = properties[self.x_print]
        self.y = properties[self.y_print]
        self.sigma = properties[self.sigma_print]
        self.learning_rate = properties[self.learning_rate_print]
        self.neighborhood_function = properties[self.neighborhood_function_print]
        self.random_seed = None if properties[self.random_seed_print] == 'None' else properties[self.random_seed_print] #specifically check for None since it is default value and stored as a string


    def get_properties(self):
        properties = {self.x_print: self.x, self.y_print: self.y, self.sigma_print: self.sigma, self.learning_rate_print: self.learning_rate, self.neighborhood_function_print: self.neighborhood_function, self.random_seed_print : self.random_seed}
        return properties

    def copy(self):
        copy_alg = Algorithm_Som(self.x, self.y, self.sigma, self.learning_rate, self.neighborhood_function, self.random_seed)
        return copy_alg

    def apply_alg(self, dataset, testing):
        print('Running ', self.name)
        try:
            dataset.data = np.array(dataset.data, dtype = float)
            testing.data = np.array(testing.data, dtype = float)
        except ValueError:
            print('Not possible to apply SOM on categorical data, transform it')
            return Result_Som(self)

        #som = MiniSom(6, 6, dataset.attr_size, sigma=1, learning_rate=0.5, neighborhood_function='gaussian')
        som = MiniSom(self.x, self.y, dataset.attr_size, sigma = self.sigma, learning_rate = self.learning_rate, neighborhood_function = self.neighborhood_function, random_seed = self.random_seed)
        som.train_batch(dataset.data, 100, verbose=True)  

        #som.train_random(dataset.data, 100, verbose=True) # random training
        e = som.labels_map(dataset.data, dataset.target)
        print(e)
        
        map_labeled = self.normal_vs_attacks_detection(e)
        print(map_labeled)
        e_testing = som.labels_map(testing.data, testing.target)
        print(e_testing)
        results = self.calc_results(som, map_labeled, testing)
        

        #win_map = som.win_map(testing.data)
        #print(map_labeled)
        #print(win_map)

        #results = Result_Som(self)
        #results.map_label = map_labeled
        #results.detection_rate = self.calculate_detection_rate(map_labeled)
        #results.false_alarm = self.calculate_false_alarm(map_labeled)
        print(results.detection_rate)
        print(results.false_alarm)
        return results

    def calc_results(self, som : MiniSom, cluster_label, testing):
            attack = 0
            normal_as_attack = 0 #false negative
            for index, elem in enumerate(testing.data):
                coord = som.winner(elem)
                if(coord in cluster_label):
                    if(cluster_label[coord][0] == 'attack.'):
                        if(testing.target[index] == 'attack.'):
                            attack += 1
                        else:
                            normal_as_attack += 1
                else:
                    print("training elem not in cluster named")
            results = Result_Som(self)
            detection_rate = attack / testing.attack_n
            false_alarm = normal_as_attack / testing.normal_n
            results.detection_rate = detection_rate
            results.false_alarm = false_alarm
            return results

    def normal_vs_attacks_detection(self, labeled_map : defaultdict):
        clustered_map = dict() #stores the highest elem for each cluster ['type', normals#, attacks#] 
        for key in labeled_map:
            normal = 0
            attack = 0
            for d in labeled_map.get(key):
                if(d != 'normal.'):
                    attack += labeled_map.get(key).get(d)
                elif(d != ''):
                    normal += labeled_map.get(key).get(d)
            if(normal > attack):
                clustered_map[key] = ['normal.', normal, attack]
            elif(normal < attack):
                clustered_map[key] = ['attack.', normal, attack]
            else:
                print('normal and attack number is the same. messed up')
        return clustered_map

    def calculate_detection_rate(self, clusters_labeled):
        """ratio of the detected attack records to the total attack records 
            clusters_labeled: (x,y):['type', normals#, attacks#] ,.."""
        detected = 0
        total = 0
        for item in clusters_labeled.values():
            if(item[0] == 'attack.'):
                detected += item[2]
            total += item[2]
        return detected / total

    def calculate_false_alarm(self, clusters_labeled):
        """the ratio of the normal records detected as the attack record, to total normal records"""
        not_detected = 0
        total = 0
        for item in clusters_labeled.values():
            if(item == 'attack.'):
                not_detected += item[1]
            total += item[1]
        return not_detected / total

class Algorithm_Kmean(Algorithm):
    def __init__(self, cluster_n = 8, y = 1):
        super(Algorithm_Kmean, self).__init__()
        self.name = "K-Means Clustering"
        self.cluster_n = cluster_n #specify initial settings
        self.y_power = y
        #variables holding print names for internal settings
        self.name_print = "kmeans"
        self.cluster_n_print = "Number of clusters"
        self.y_power_print = "y"

    def get_properties(self):
        properties = {self.cluster_n_print : self.cluster_n, self.y_power_print: self.y_power}
        return properties

    def set_properties(self, properties):
        """set properties from dictionary like structure (expecting correct type value in the dictionary"""
        self.cluster_n = properties[self.cluster_n_print]
        self.y_power = properties[self.y_power_print]

    def copy(self):
        copy_alg = Algorithm_Kmean(self.cluster_n, self.y_power)
        return copy_alg

    def apply_alg(self, dataset, testing):
        print('Running ', self.name)
        try:
            np.array(dataset.data[0], dtype = float)
        except ValueError:
            print("Not possible utilize categorical values in this algorithm, transform them")
            return Result_Kmean(self)

        y = KMeans(n_clusters = self.cluster_n).fit(dataset.data)
        
        c = [[0 for x in range(2)] for y in range(self.cluster_n)]
    
        for index in range(0, len(dataset.target)):
            c[y.labels_[index]][0] += 1 #add 1 to the counter of elements in each cluster
            if dataset.target[index] in ['normal.', 'normal'] :
                c[y.labels_[index]][1] += 1
        
        print('Clusters:' + str(self.cluster_n))
        print(c) #print [total_n_elements per cluster, n_normals per cluster]
    
        #calculate_stdev(y.n_clusters, y, dataset.data, len(dataset.data[0]), len(dataset.data), list(zip(*c))[0])
        normal_instances = dataset.normal_n
        
        of = self.calculate_outlier_factor(y.cluster_centers_, self.y_power)
        labels_clusters = self.of_label_clusters(list(zip(*c))[0], of, normal_instances)
        labels = y.predict(testing.data)
        detection_rate = self.calculate_detection_rate(labels_clusters, labels, testing.target)
        false_alarm = self.calculate_false_alarm(labels_clusters, labels, testing.target)
        print(labels_clusters)
        print(of)
        print(detection_rate)
        print(false_alarm)
        results = Result_Kmean(self)
        results.detection_rate = detection_rate
        results.false_alarm = false_alarm
        return results

    def of_label_clusters(self, clusters_pop, of, normal_instances):
        """gives labels to clusters based on the of calculated. clusters_pop = population of each cluster, normal_instances = number of normal instances in the dataset"""
        labels = ['' for x in range(len(of))]
        centers_m = [[x] for x in of]
        total = 0.0
        for index, elem in enumerate(centers_m): #add index at the end of each center, so it can be retrieved if center_m is modified
            elem.append(index)

        while(total < normal_instances and len(centers_m) != 0):
            min = centers_m[0][0]
            min_index = 0 #index of minimum element (on centers_m)
            for index in range(1, len(centers_m)):
                if(centers_m[index][0] < min):
                    min_index = index
                    min = centers_m[index][0]
    
            total += clusters_pop[min_index]
    
            if(total < normal_instances):
                labels[centers_m[min_index][1]] = 'normal.'
            else:
                for elem in centers_m:
                    labels[elem[len(elem) - 1]] = 'attack.'
            #if(len(centers_m))
            del centers_m[min_index]
        return labels

    def calculate_outlier_factor(self, cluster_centers, y = None):
        """calculate the average distance from cluster to others"""
        if y == None: #in case user did not provide value, use default stored in member variable
            y = self.y_power
        distances = []
        for index in range(len(cluster_centers)):
            distance_clust = 0.0
            for inn in range(len(cluster_centers)):
                distance_attr = 0.0
                if (inn != index):
                
                    for index_attr in range(len(cluster_centers[index])):
                        distance_attr += abs(cluster_centers[index][index_attr] - cluster_centers[inn][index_attr])
                    distance_attr = pow(pow(distance_attr, 2) / len(cluster_centers[index]), 0.5)
                    distance_clust += pow(distance_attr, y)
            distances.append(pow(distance_clust / (len(cluster_centers) - 1), 1 / y))
        return distances

    def calculate_detection_rate(self, clusters_labeled, clusters, labels):
        """ratio of the detected attack records to the total attack records"""
        #clusters_attack = [] #[indexes of attacks]
        #for index in range(len(clusters_labeled)):
        #    if(clusters_labeled[index] != 'normal.'):
        #        clusters_attack.append(index)
    
        attacks_detected = 0
        attacks_total = 0
        for index in range(len(labels)):
            if labels[index] != 'normal.':
                attacks_total += 1
                if clusters_labeled[clusters[index]] != 'normal.':
                    attacks_detected += 1
        #return [attacks_detected, attacks_total]
        return attacks_detected / attacks_total

    def calculate_false_alarm(self, clusters_labeled, clusters, labels):
        """the ratio of the normal records detected as the attack record, to total normal records"""
        normal_total = 0
        normal_as_attack = 0 #detected attack, but it is actually a normal

        for index in range(len(labels)):
            if labels[index] == 'normal.':
                normal_total += 1
                if clusters_labeled[clusters[index]] != 'normal.':
                    normal_as_attack += 1
        #return [normal_as_attack, normal_total]
        return normal_as_attack / normal_total

    def calculate_stdev(self, n_clusters, y, dataset, attr_size, size, n_elem_clusters):
        #i = [0] * n_clusters #n. of total elements
        count = [[0 for x in range(attr_size)] for y in range(n_clusters)] #stdev for each feature
        for index in range(size):
            #i[y.labels_[index]] += 1
            for inn in range(attr_size):
                count[y.labels_[index]][inn] += pow(- y.cluster_centers_[y.labels_[index]][inn] + dataset[index][inn], 2) 
    
        for index in range(n_clusters):
            for inn in range(attr_size):
                count[index][inn] /= n_elem_clusters[index]
                count[index][inn] = math.sqrt(count[index][inn])

        #print(count)
        total = [0] * n_clusters
        for index in range(n_clusters): #useful in case the dataset has been normalized
            total[index] = sum(count[index])
        print(total)

class Fixed_Width_Clustering(Algorithm):
    def __init__(self, width, distance_alg = 'euclidean'):
        super(Fixed_Width_Clustering, self).__init__()
        #set intial clusters set
        self.name = "Fixed Width Clustering"
        self._clusters = []
        self._distance_func = self.calculate_distance_to_clusters_euclidean
        self.fixed_width = width
        self.distance_alg = distance_alg
        #Show properties
        self.name_print = 'fixed wcl'
        self.fixed_width_print = "Fixed width"
        self.distance_alg_print = "Distance algorithm"

    def get_properties(self):
        properties = {self.fixed_width_print : self.fixed_width, self.distance_alg_print : self.distance_alg}
        return properties

    def set_properties(self, properties):
        """set properties from dictionary like structure (expecting correct type value in the dictionary"""
        self.fixed_width = properties[self.fixed_width_print]
        self.distance_alg = properties[self.distance_alg_print]
        

    def copy(self):
        copy_alg = Fixed_Width_Clustering(self.fixed_width)
        return copy_alg
    
    def apply_alg(self, training, testing):
        print('Running ', self.name)
        train_cluster_labels = self.train_alg_labels(training.data, training.target)
        test_map_label = self.test_alg_label(testing.data, testing.target)
        map_labels = list(zip(list(zip(*train_cluster_labels))[0],test_map_label))
        out = []
        for cluster in map_labels:#a giant mess, fix it using a proper structure
            temp = [cluster[0]]
            for index in range(len(cluster[1])):
                temp.append(cluster[1][index])
            out.append(temp)
    
        results = Result_Fixed_Width_Clustering(self)
        detection_rate = self.calculate_detection_rate(out)
        false_alarm = self.calculate_false_alarm(out)
        results.detection_rate = detection_rate
        results.false_alarm = false_alarm
        print(detection_rate)
        print(false_alarm)
        return results

    def add_cluster(self, centroid):
        self._clusters.append(centroid)
    
    def calculate_distance_to_clusters_euclidean(self, record):
        return euclidean_distances(record, self._clusters)
    
    def calculate_distance_to_clusters_manhattan(self, record):
        return manhattan_distances(record, self._clusters)
    
    def calculate_distance_to_clusters(self, record):
        return self._distance_func(record)

    def get_closest_cluster(self, record):
        distances = self.calculate_distance_to_clusters([record])
        return self.get_smallest_index(distances[0]) #passing only [0] because there should be only 1 element in array since it has been calculated distance between 1 record vs centroids

    def get_smallest_index(self, distances):
        min_index = 0
        
        for index in range(1, len(distances)):
            if(distances[index] < distances[min_index]):
                min_index = index
        return min_index

    def set_distance_func(self):
        if(self.distance_alg == 'euclidean'):
            self._distance_func = self.calculate_distance_to_clusters_euclidean
        elif(self.distance_alg == 'manhattan'):
            self._distance_func = self.calculate_distance_to_clusters_manhattan


    def train_alg(self, training):
        print("Running Algorithm")
        self.set_distance_func()
        self.add_cluster(training[len(training) -1]) #better to pick it randomly | center_id = random_state.randint(n_samples)
        labels = [0]
        for index in range(len(training) - 1):
             distances = self.calculate_distance_to_clusters([training[index]])
             min_index = self.get_smallest_index(distances[0])
             if(distances[0][min_index] < self.fixed_width):
                 labels.append(min_index)
                 pass
             else:
                 self.add_cluster(training[index])
                 labels.append(len(self._clusters) - 1)
                 print("added: n.", len(self._clusters))
        return labels

    def train_alg_labels(self, training, labels):
        clusters_labels = self.train_alg(training)
        temp = [['',0,0] for x in range(len(self._clusters))] #['type', normal#, attack#]

        for index in range(len(clusters_labels)):
            if(labels[index] == "normal."):
                temp[clusters_labels[index]][1] += 1
            else:
                temp[clusters_labels[index]][2] += 1

        for elem in temp:
            if(elem[1] > elem[2]):
                elem[0] = 'normal.'
            elif(elem[1] < elem[2]):
                elem[0] = 'attack.'
            else:
                #print("number of attacks and normal connections are the same")
                elem[0] = 'attack.'
        return temp

    def test_alg(self, testing):
        clusters = []
        for elem in testing:
            clusters.append(self.get_closest_cluster(elem))
        return clusters
    
    def test_alg_label(self, testing, labels):
        clusters = self.test_alg(testing)
        map_labels = [[0,0] for x in range(len(self._clusters))] #[[normals#, attacks#], [..]]
        for index in range(len(clusters)):
            if(labels[index] == 'normal.'):
                map_labels[clusters[index]][0] += 1
            else:
                map_labels[clusters[index]][1] += 1
        return map_labels

    def calculate_detection_rate(self, map_labels):
        """ratio of the detected attack records to the total attack records
           map_labels: [['type', normals#, attacks#],[..]]"""
        detected = 0
        total = 0
        for elem in map_labels:
            if(elem[0] == 'attack.'):
                detected += elem[2]
            total += elem[2]
        return detected / total
        

    def calculate_false_alarm(self, map_labels):
        """the ratio of the normal records detected as the attack record, to total normal records"""
        not_detected = 0
        total = 0
        for elem in map_labels:
            if(elem[0] == 'attack.'):
                not_detected += elem[1]
            total += elem[1]
        print("normal as attack: ",not_detected)
        print("total normal: ",total)
        return not_detected / total

class Result_Alg(object):
    def __init__(self):
        self.detection_rate = -1
        self.false_alarm = -1
        #might add time taken to run alg

    def show_results(self):
        if(self.detection_rate != -1 and self.false_alarm != -1):
            common_results = {'detection rate' : self.detection_rate, 'false alarm' : self.false_alarm}
            return common_results
        else:
            return {}

class Result_Som(Result_Alg):
    def __init__(self, alg_som):
        super(Result_Som, self).__init__()
        self.map_label = []
        self.algorithm_settings = alg_som.copy()

    def show_results(self):
        """returning results to be shown on view using a dictionary"""
        results = super(Result_Som, self).show_results()
        #results.update({'map label' : self.map_label}) #not shown on view, so dont need to pass it
        return results


class Result_Kmean(Result_Alg):
    def __init__(self, alg_kmean):
        super(Result_Kmean, self).__init__()
        self.algorithm_settings = alg_kmean.copy()

    def show_results(self):
        """returning results to be shown on view using a dictionary"""
        results = super(Result_Kmean, self).show_results()
        #add other kmean results needed to be shown in view
        return results
    
class Result_Fixed_Width_Clustering(Result_Alg):
    def __init__(self, fixed_width_alg):
        super(Result_Fixed_Width_Clustering, self).__init__()
        self.algorithm_settings = fixed_width_alg.copy()

    def show_results(self):
        results = super(Result_Fixed_Width_Clustering, self).show_results()
        return results
