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
        

    def attributes_type_point(self, dataset_name):
        dataset = self.load_dataset(dataset_name)
        attribute_types = self.attributes_type_modulus(dataset)
        return attribute_types
        
       
    def attributes_type_point(self, dataset):
        #using modulus to understand kind of item
        attribute_types = []
        for item in dataset[0]: #only the first row
            
            if ((str(item)).replace('.', '').isdigit()):
                if (str(item).find('.') == -1):
                    attribute_types.append('Discrete')
                else:
                    attribute_types.append('Continuous')
            else:
                attribute_types.append('Categorical')
                print(item)
        return attribute_types

    def attributes_type_type(self, dataset):
        #using the type function to understand kind of item. Only works if dataset contains different types (if they are all strings, when converted will lose their type)
        attribute_types = []
        for item in dataset[0]: #only the first row
            if str(item).isdigit():
                if type(item) == int:
                    attribute_types.append('Discrete')
                elif type(item) == float:
                    attribute_types.append('Continuous')
            else:
                attribute_types.append('Categorical')
        return attribute_types

    def calculate_info_attribute(self, index):
        #todo:check that first is not empty (missing) and find next proper one. Not sure if I should check against "" string only
        if(type(self.dataset[0][index]) == str):
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
            