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
            dataset_attributes = self.model.attributes_type(dataset_str)
            if(dataset_attributes != [""]):
                self.view.set_attr_group(dataset_attributes)
    
    def attribute_chosen(self, index):
        #index = self.transform_to_attribute_index(attribute)
        #if(index == -1):
        #    print("problem in finding index from label attribute name")
        #    return None
        attribute_info = self.model.calculate_info_attribute(index)
        self.view.set_attribute_info(attribute_info)

    def transform_to_attribute_index(attribute : str):
        digit_index = -1
        for index, char in enumerate(attribute):
            if char.isdigit():
                digit_index = index
        attribute_num = attribute[index : ]
        return attribute_num
            


