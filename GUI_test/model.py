from sklearn import datasets
import math
import numpy as np
import os.path
from sklearn.cluster import KMeans
from sklearn import preprocessing
import math
from minisom import MiniSom
from timeit import default_timer as timer
from collections import defaultdict

class Model(object):
    
    def __init__(self):
        self.dataset = Dataset()
        self.datasets_location = dict()
        self.datasets_location['KDD99'] = 'inner'
        self.datasets_location['TEST'] = 'inner'
        self.algorithms = set() #available algorithms
        self.set_algorithms()
        self.results = [] #list of results
        self.actual_algorithm = Algorithm()
    
    def set_algorithms(self):
        #KMEAN 
        kmean = Algorithm_Kmean()
        #kmean.set_properties({'n_cluster': 8}) #to finish
        self.algorithms.add(kmean)
        #SOM
        som = Algorithm_Som()
        #som.set_properties({'x': 6, 'y': 6, 'sigma': 1.0, 'learning_rate': 0.5, 'neighborhood_function': 'gaussian', 'random_seed' : None})
        som.set_properties_choices({'neighborhood_function': ['gaussian','mexican_hat','bubble','triangle']})
        self.algorithms.add(som)
    #def encode_bytes_to_string(self, dataset): #Too slow, going to encode only the needed ones in the controller (~MVC)
    #    for item in dataset:
    #        for index in range(len(dataset[0])):
    #            if(type(item[index]) == bytes):
    #                dataset[str(item[index], "utf-8")
    
    def apply_algorithm(self, algorithm):
        if(self.dataset.size > 0):
            if str.lower(algorithm) == 'som':
                return self.som_algorithm()
            elif str.lower(algorithm) == 'kmean':
                pass #kmean()
        else:
            #show message box error
            return {}
            print('no dataset loaded! Cannot perform algorithm')

    def som_algorithm(self):
        alg : Algorithm
        
        if self.actual_algorithm.name != '':
            alg = self.actual_algorithm
        else:
            for elem in self.algorithms:
                if elem.name == 'som':
                    alg = elem
                    break
        try:
            data = np.array(self.dataset.data, dtype = float)
        except ValueError:
            print('Not possible to apply SOM on categorical data, transform it')
            return results

        #som = MiniSom(6, 6, self.dataset.attr_size, sigma=1, learning_rate=0.5, neighborhood_function='gaussian')
        som = MiniSom(alg.x, alg.y, self.dataset.attr_size, sigma = alg.sigma, learning_rate = alg.learning_rate, neighborhood_function = alg.neighborhood_function, random_seed = alg.random_seed)
        som.train_batch(data, 100, verbose=True)  
        #som.train_random(self.dataset.data, 100, verbose=True) # random training
        e = som.labels_map(data, self.dataset.target)
        print(e)
        map_labeled = self.normal_vs_attacks_detection_som(e)
        
        print(map_labeled)

        results = Result_Som(alg)
        results.map_label
        results.detection_rate = self.calculate_detection_rate_som(map_labeled)
        results.false_alarm = self.calculate_false_alarm_som(map_labeled)
        print(results.detection_rate)
        print(results.false_alarm)
        self.results.append(results)
        return results.show_results()

    def normal_vs_attacks_detection_som(self, labeled_map : defaultdict):
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

    def calculate_detection_rate_som(self, clusters_labeled):
        """ratio of the detected attack records to the total attack records"""
        detected = 0
        total = 0
        for item in clusters_labeled.values():
            if(item[0] == 'attack.'):
                detected += item[2]
            total += item[2]
        return detected / total

    def calculate_false_alarm_som(self, clusters_labeled):
        """the ratio of the normal records detected as the attack record, to total normal records"""
        not_detected = 0
        total = 0
        for item in clusters_labeled.values():
            if(item == 'attack.'):
                not_detected += item[1]
            total += item[1]
        return not_detected / total

    def get_som_coord_clusters_normal(self):
        """return coordinates for normals and anomalies clusters created in the som
           [[normal],[anomaly]] 
           normal: [[x1,x2,..],[[y1,y2,..]]
        """ 
        map_label = get_som_map_label()
        if not(map_label):
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

    def get_dataset_current_name(self):
        print('current dataset:', self.dataset.name)
        return self.dataset.name

    def read_dataset(self, path):
        if not(self.check_existence_dataset_file(path)): #skipping the open file, if this function already checked that file do not exists
            return False
        #use try catch, in case has been removed in the time being
        try:
            file = open(path, 'r')
        except IOError:
            print("No file present!")
            return False
        print('Reading dataset')
        dataset = []
        target = []
        attr_names = [] #could use a set
        #set attribute names in the dataset (only fist line taken)
        line = file.readline() #add: check that are all different
        line_split = line.replace('\n', '').split(',')
        for attr in line_split:
            if attr in attr_names:
                print("There is a duplicate attribute name, or the first line is not attribute line")
                return False
            attr_names.append(attr)

        #set attributes values
        for line in file.readlines():
            temp = line.replace('\n', '').split(',')
            target.append(temp.pop())
            dataset.append(temp)
        file.close()
        #start = timer()
        #setting the type of input data following rules utilized to check type of attributes
        for i in range(len(dataset)):
            dataset[i] = [self.transform_to_correct_type(x) for x in dataset[i]] #very slow! might better just check if it is float or not
            #for inn in range(len(dataset[i])):
            #    if(self.is_float(dataset[i][inn])):
            #        dataset[i][inn] = float(dataset[i][inn])
        #end = timer()
        #print("timer", str(end - start))

        self.dataset.target = np.asarray(target)
        self.dataset.data = np.asarray(dataset, dtype = np.dtype(object))
        self.dataset.set_properties() #some properties not set, still referring to old dataset
        self.dataset.set_name_path(self.dataset_path_to_name(path), path)
        self.dataset.set_attribute_names(attr_names)
        
        self.set_dataset_location(path)
        print(self.datasets_location)
        print(self.dataset.data[0])
        print(self.dataset.attr_names)
        return True

    def load_dataset(self, dataset_name):
        """retreives data and works on it"""
        #find dataset directory in map
        #DEBUG
        if(dataset_name.upper() == "TEST"):
            print('Reading dataset')
            self.dataset.data = np.asarray([[1,1.5],[2,2.5],[10,3.5],[25,9.5]])
            self.dataset.target = np.asarray(['normal.', 'normal.', 'attack.', 'attack.'])
            self.dataset.set_attribute_names = np.asarray(['a','b'])
            self.dataset.set_properties()
            self.dataset.set_name_path('TEST', 'inner')
            self.datasets_location['TEST'] = 'inner'


        elif(dataset_name.upper() == "KDD99"): #special case. Using sklearn lib to load it
            print('Reading dataset')
            kdd = datasets.fetch_kddcup99()
            #self.dataset.size = len(kdd.data)
            #self.attr_size = len(kdd.data[0])
            self.dataset.data = np.asarray(kdd.data)
            self.dataset.target = np.array(kdd.target, str)
            print(self.dataset.target[0])
            self.dataset.set_attribute_names = np.asarray(['duration','src_bytes','dst_bytes','land,wrong_fragment','urgent','hot','num_failed_logins','logged_in','num_compromised','root_shell','su_attempted','num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','is_host_login','is_guest_login','count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate']) # no class attribute name
            self.dataset.set_properties()
            self.dataset.set_name_path('KDD99', 'inner')

            self.datasets_location['KDD99'] = 'inner'
            
        else:
            if(dataset_name in self.datasets_location): #only execute if the dataset name is present in the map
                return self.read_dataset(self.datasets_location[dataset_name])
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

        if ((str(item)).replace('.', '').isdigit()):
            
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

class Dataset(object):
    def __init__(self):
        self.data = [[]]
        self.target = [] #labels
        self.attr_names = []
        self.attr_types = []
        self.attr_size = 0
        self.size = 0
        self.name = ''
        self.path = ''

    def set_properties(self):
        if len(self.data) != 0:
            self.attr_size = len(self.data[0])
            self.size = len(self.data)
            #to do add methods to fit attrnames and types

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
    
    def get_properties(self):
        raise NotImplementedError()

    def set_properties_choices(self, choices : dict): #choices {property : [choices]}
        for key, value in choices.items():
            self.properties_choices[str.lower(str(key))] = value

class Algorithm_Som(Algorithm):
    def __init__(self, x = 6, y = 6, sigma = 1.0, learning_rate = 0.5, neighborhood_function = 'gaussian', random_seed = None): #intial settings
        super(Algorithm_Som, self).__init__()
        self.name = 'som'
        self.x = x
        self.y = y
        self.sigma = sigma
        self.learning_rate = learning_rate
        self.neighborhood_function = neighborhood_function
        self.random_seed = random_seed

    def get_properties():
        properties = {'x': self.x, 'y': self.y, 'sigma': self.sigma, 'learning_rate': self.learning_rate, 'neighborhood_function': self.neighborhood_function, 'random_seed' : self.random_seed}
        return properties

    def copy(self):
        copy_alg = Algorithm_Som(self.x, self.y, self.sigma, self.learning_rate, self.neighborhood_function, self.random_seed)
        return copy_alg

class Algorithm_Kmean(Algorithm):
    def __init__(self):
        super(Algorithm_Kmean, self).__init__()
        self.cluster_n = 8 #specify initial settings


class Result_Alg(object):
    def __init__(self):
        self.detection_rate = -1
        self.false_alarm = -1

    def show_results(self):
        common_results = {'detection rate' : self.detection_rate, 'false alarm' : self.false_alarm}
        return common_results

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
    def __init__(self):
        super(Result_Kmean, self).__init__()
        self.algorith_settings = Algorithm_Kmean()

    def show_results():
        results = super(Result_Som, self).show_results()
        #add other kmean results needed to be shown in view
        return results
    