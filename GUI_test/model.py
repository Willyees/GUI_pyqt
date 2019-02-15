from sklearn import datasets
class Model(object):
    
    def __init__(self):
        self.dataset = None
        self.dataset_length = 0
        self.dataset_attr_info = []
        self.attributes_number = 0

    """retreives data and works on it"""
    def load_dataset(self, dataset):
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
        

    def attributes_type(self, dataset_name):
        dataset = self.load_dataset(dataset_name)
        attribute_types = self.attributes_type_packing(dataset)
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
            self.calculate_info_categorical(index)
    
    def calculate_info_numerical_(self, index):
        #min, max, mean, std deviation
        pass


    def calculate_info_categorical(self, index):
    
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
        print(categories)
            