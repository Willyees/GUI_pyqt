from sklearn import datasets
import math
import numpy as np

class Model(object):
    
    def __init__(self):
        self.dataset = Dataset()
        
    #def encode_bytes_to_string(self, dataset): #Too slow, going to encode only the needed ones in the controller (~MVC)
    #    for item in dataset:
    #        for index in range(len(dataset[0])):
    #            if(type(item[index]) == bytes):
    #                dataset[str(item[index], "utf-8")


    def load_dataset(self, dataset):
        """retreives data and works on it"""
        if(dataset == "KDD99"):
            kdd = datasets.fetch_kddcup99()
            self.dataset.size = len(kdd.data)
            self.attr_size = len(kdd.data[0])
            self.dataset.data = kdd.data
            self.dataset.set_properties()
            #self.attr_nominal_to_binary([1,3])
            
            return self.dataset.data
        else:
            print("Error in retreiving dataset: " + dataset)
            return ""
        

    def attributes_type(self, dataset_name, new):
        """attributes types are returned from dataset_name provided if new is set to True. Otherwise are returned from already stored dataset"""
        if(new):
            #load new dataset if new is set to true
            self.dataset.data = self.load_dataset(dataset_name)
            self.dataset.set_properties()
        self.dataset.attr_types = self.attributes_type_packing(self.dataset.data)
        return self.dataset.attr_types
        
    def attributes_type_packing(self, dataset):
        #using the '.' symbol to undestand if float or integer
        attribute_types = []
        for index, item in enumerate(dataset[0]): #only the first row
            attribute_types.append(self.attribute_single_type(item, index))
        return attribute_types

    
    def attribute_single_type(self, item, index):
        #used to return each attribute as a single type. It can be reused in other functions
        if(str(item) == ""):
            print("Attribute value is incorrect: empty")
            return ''

        if ((str(item)).replace('.', '').isdigit()):
            print(index)
            if(int(item) == 1 or int(item) == 0):
                if(self.attribute_check_if_binary(index)):
                    return ('Binary')

            if (str(item).find('.') == -1):
                return ('Discrete')
            else:
                return ('Continuous')
        else:
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
        #todo:check that first is not empty (missing) and find next proper one. Not sure if I should check against "" string only
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
        """transform nominal attributes given from the indexes into binaries"""
        #for index in indexes:
        #if (self.attribute_single_type(self.dataset.data[0][indexes], index) == 'Categorical'):
        sets = self.sets_of_nominal_attributes(indexes)
        self.attr_nominal_to_binary_add_attr(sets, indexes)
        self.remove_attributes_dataset(indexes)
        

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
        self.attr_names = []
        self.attr_types = []
        self.attr_size = 0
        self.size = 0

    def set_properties(self):
        if len(self.data) != 0:
            self.attr_size = len(self.data[0])
            self.size = len(self.data)
            #todo add methods to fit attrnames and types
