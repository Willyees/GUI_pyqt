from view import *

class Controller(object):
    """MVC controller, lets view and model indirectly communicate"""
    

    def __init__(self, model, view):
        self.model = model
        self.listener = view.listener
        self.listener.control = self
        self.listener.control.print()
        self.view = view
        
        self.startView()


    def startView(self):
        self.view.startView()

    def submit_form(self):
        print(self.view.get_info())

    def print(self):
        print("SUP?")

    def set_dataset(self):
        dataset_str = self.view.get_dataset_chosen()
        if(dataset_str != 'None'):
            dataset_attributes = self.model.attributes_type(True, dataset_str)
            if(dataset_attributes != [""]):
                self.view.set_attr_group(dataset_attributes)
    
    def attribute_chosen(self, index):
        #index = self.transform_to_attribute_index(attribute)
        #if(index == -1):
        #    print("problem in finding index from label attribute name")
        #    return None
        attribute_info = self.model.calculate_info_attribute(index)
        if(attribute_info != ''):
            self.encode_bytes_to_str(attribute_info)
            self.view.set_attribute_info(attribute_info)#info modified in previous function

    def transform_to_attribute_index(attribute : str):
        digit_index = -1
        for index, char in enumerate(attribute):
            if char.isdigit():
                digit_index = index
        attribute_num = attribute[index : ]
        return attribute_num
            
    def submit_window(self):
        attr_unselected = self.view.get_unselected_attributes()
        pass

    def attr_removed(self):
        attrs_selected = self.view.get_attribute_selected()
        self.model.remove_attributes_dataset(attrs_selected)
        dataset_attributes = self.model.attributes_type(False)
        if(dataset_attributes != [""]):
            self.view.set_attr_group(dataset_attributes)

    def attribute_checked(self, state):
        self.view.attr_checked(state)
        self.view.set_delbtn_state()
        self.view.set_ntbbtn_state()

    def encode_bytes_to_str(self, items): #not flexible, works only for list of lists
        print(items)
        for i1 in range(len(items)):
            for i2 in range(len(items[i1])):
                if(type(items[i1][i2]) == bytes):
                    items[i1][i2] = str(items[i1][i2], 'utf-8')


    def nominal_to_binary(self):
        attr_checked = self.view.get_attribute_selected()
        if(self.model.attr_nominal_to_binary(attr_checked)): #also removing attribute interally (in model) if it is a category attribute
            dataset_attributes = self.model.attributes_type(False)
            if(dataset_attributes != [""]):
                self.view.set_attr_group(dataset_attributes)

    def import_dataset(self):
        dataset_path = self.view.get_file_selected(filter = 'Dataset files (*.csv)', directory = 'C:\\Users\\User\\Documents')
        if(dataset_path): #check that user selected a file
            self.model.read_dataset(dataset_path[0])
            #read the file in the model and set it as dataset
            #store file location along with the name in model
            #update cmbbox view with the new dataset name