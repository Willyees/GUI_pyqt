from sklearn import datasets
import math
import numpy as np

class Model(object):
    
    def __init__(self):
        self.dataset = []
        self.dataset_length = 0
        self.dataset_attr_info = []
        self.attributes_number = 0

    
    def load_dataset(self, dataset):
        """retreives data and works on it"""
        if(dataset == "KDD99"):
            kdd = datasets.fetch_kddcup99()
            self.dataset_length = len(kdd.data)
            self.attributes_number = len(kdd.data[0])
            self.dataset = kdd.data
            print(self.dataset[0])
            return kdd.data
        else:
            print("Error in retreiving dataset: " + dataset)
            return ""
        

    def attributes_type(self, dataset_name, new):
        """attributes types are returned from dataset_name provided if new is set to True. Otherwise are returned from already stored dataset"""
        if(new):
            #load new dataset if new is set to true
            dataset = self.load_dataset(dataset_name)
        attribute_types = self.attributes_type_packing(self.dataset)
        return attribute_types
        
    def attributes_type_packing(self, dataset):
        #using the '.' symbol to undestand if float or integer
        attribute_types = []
        for item in dataset[0]: #only the first row
            attribute_types.append(self.attribute_single_type(item))
            #print(item)
        return attribute_types

    
    def attribute_single_type(self, item):
        #used to return each attribute as a single type. It can be reused in other functions
        if ((str(item)).replace('.', '').isdigit()):
            if (str(item).find('.') == -1):
                return ('Discrete')
            else:
                return ('Continuous')
        else:
            return ('Categorical')
        

    def calculate_info_attribute(self, index):
        #todo:check that first is not empty (missing) and find next proper one. Not sure if I should check against "" string only
        if(self.attribute_single_type(self.dataset[0][index]) == 'Categorical'):
            return self.calculate_info_categorical(index)
        if(self.attribute_single_type(self.dataset[0][index]) == 'Discrete'):#trying with a discrete
            #set info in the right format (each inner list is one row in the view)
            continuous = self.calculate_info_continuous(index)
            l_formatted = [['minimum', continuous[0]], ['maximum', continuous[1]],['mean', continuous[2]],['standard deviation', continuous[3]]]
            return l_formatted

    def calculate_info_continuous(self, index):
        #min, max, mean, std deviation
        minimum, maximum, mean = self.calculate_minmaxmean(index)#MEAN not working, TODO check!
        std_deviation = self.calculate_stddeviation(index, mean)
        return [minimum, maximum, mean, std_deviation]
        
    def calculate_stddeviation(self, index, mean):
        sigma = 0
        for i in range(len(self.dataset)):
            sigma += (self.dataset[i][index] - mean) ** 2
        std_deviation = math.sqrt(sigma / len(self.dataset))
        return round(std_deviation, 2)

    def calculate_minmaxmean(self, index):
        m = self.dataset[0][index]
        h = self.dataset[0][index]
        sum = 0
        for i in range(1, len(self.dataset)):
            sum += self.dataset[i][index]
            if(self.dataset[i][index] < m):
                m = self.dataset[i][index]
            if(self.dataset[i][index] > h):
                h = self.dataset[i][index]
        mean = sum / (len(self.dataset))
        
        return [round(m, 2), round(h, 2), round(mean, 2)]

    def calculate_info_categorical(self, index):
        """find different categories and their frequencies. returned list: [[name1, frequency], [name2, freq2]..]"""
        categories = []
        print(self.dataset[0][index])
        if(self.dataset[0][index] != ""):
            categories.append([self.dataset[0][index], 1])
        for i in range(1, len(self.dataset)):
            for item in categories:
                if(self.dataset[i][index] != "" and self.dataset[i][index] == item[0]):
                    item[1] += 1
                    break
            else:
                categories.append([self.dataset[i][index], 1])
        return categories
            
    def remove_attributes_dataset(self, attributes):
        print(attributes)
        if isinstance(self.dataset, np.ndarray) and self.dataset.size:
            new_dataset = []
            for record in self.dataset:
                new_dataset.append(np.delete(record, attributes))
            print(len(new_dataset[0]), new_dataset[0])
            self.dataset = new_dataset
        elif isinstance(self.dataset, list) and self.dataset:
            print('list')
            new_dataset = []
            for record in self.dataset:
                new_dataset.append(np.delete(record, attributes))
            print(len(new_dataset[0]), new_dataset[0]) #Implement case for built in list
            self.dataset = new_dataset
        else:
            print("Error - cant remove from empty dataset")
        return None