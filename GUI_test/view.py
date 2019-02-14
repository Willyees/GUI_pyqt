from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QPushButton, QSlider, QScrollBar, QLayout
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QSignalMapper



class View(object):
     
    def btn_pressed(self):
        print('btn poressed')

    def __init__(self):
        print("init")
        self.listener = EventListener()
        self.app = QApplication([])
        self.window = QWidget()
       
        
    
    
    def startView(self):
        print("start view")
        
        main_layout = QGridLayout()
        
        #upper top left
        cmb_box_dataset = QComboBox(objectName = 'cmb_box_dataset')
        #cmb_box_dataset.currentIndexChanged.connect(self.test_cmb)
        cmb_box_dataset.addItems(['KDD99', 'D2'])
        label_dataset = QLabel('Datasets')
        label_dataset.setBuddy(cmb_box_dataset)
        btn_import = QPushButton('IMPORT')
        layout_top_upper = QHBoxLayout()
        layout_top_upper.addWidget(label_dataset)
        layout_top_upper.addWidget(cmb_box_dataset)
        layout_top_upper.addWidget(btn_import)
        
        #Group top left
        top_left_group = QGroupBox('Top left group')
        #top_left_group.setMaximumHeight(100)
        layout_top = QHBoxLayout()
        layout_top1 = QVBoxLayout(objectName = "top_left_box1")
        layout_top2 = QVBoxLayout(objectName = "top_left_box2")
        
        
        

        #scrollBar = QScrollBar(Qt.Vertical, top_left_group)
        #scrollBar.setValue(20)
        #layout_top.addWidget(scrollBar)

        layout_top.addLayout(layout_top1)
        layout_top.addLayout(layout_top2)
        top_left_group.setLayout(layout_top)

        

        #Group top right
        right_group = QGroupBox('Right group')

        layout_right = QHBoxLayout()
            
        layout_right1 = QVBoxLayout()
        layout_right2 = QVBoxLayout()
        layout_right.addLayout(layout_right1)
        layout_right.addLayout(layout_right2)

        attr_name_lbl = QLabel('Attr. name')
        attr_type_lbl = QLabel('type')
        layout_right1.addWidget(attr_name_lbl)
        layout_right1.addWidget(QLabel('right!!!!!!!!!!!!!!!!!!!'))
        layout_right1.addWidget(QLabel('right'))
        layout_right1.addWidget(QLabel('right'))
        layout_right2.addWidget(attr_type_lbl)
        layout_right2.addWidget(QLabel('left'))
        layout_right2.addWidget(QLabel('left'))
        layout_right2.addWidget(QLabel('left'))
        right_group.setLayout(layout_right)
     
        
        #Group button right

        layout_button = QVBoxLayout()
        alg_menu = QComboBox(objectName = 'alg_menu')
        alg_menu.addItems(['KMean', 'SOM'])
        
        alg_label = QLabel('Algorithm to apply')
        alg_label.setBuddy(alg_menu)
        apply_btn = QPushButton('&APPLY', clicked = self.listener.dataset_chosen_changed)
        
        
        #self.apply_btn.clicked.connect()
        layout_button.addWidget(alg_label)
        layout_button.addWidget(alg_menu)
        layout_button.addWidget(apply_btn)
        #
       
        main_layout.addLayout(layout_top_upper, 0, 0, 1, 1)
        main_layout.addWidget(top_left_group, 1, 0)
        main_layout.addWidget(right_group, 1, 3)
        main_layout.addWidget(right_group, 1, 3)
        main_layout.addLayout(layout_button, 2, 3)
        self.window.setLayout(main_layout)
        
        self.window.show()
        #print(alg_label.objectName())
        #print(self.window.findChild(QLabel, name = "asd" ).text())
        self.app.exec_()
    

    def set_attr_group(self, dataset):
        layout1 = self.window.findChild(QVBoxLayout, name = "top_left_box1")
        layout2 = self.window.findChild(QVBoxLayout, name = "top_left_box2")
        for index, item in enumerate(dataset):
            btn = QPushButton('attr.' + str(index + 1), objectName = 'attr.' + str(index), flat = True)#at the moment hardcoding name of attributes because no name on the dataset (KDD)
            #using lambda to pass an additional paramether. Have to use i = index or the last variable will be passed to all the lambdas
            btn.clicked.connect(lambda a, i = index : self.listener.attribute_selected(i)) #have to use additional a paramether because connect will pass a boolean variable and if not consumed will be assigned to i and then passed to listener function
            layout1.addWidget(btn)
            layout2.addWidget(QLabel(item))
            
           
        

    

    def get_info(self):
        return "info"
    
    def get_dataset_chosen(self):
        dataset = self.window.findChild(QComboBox, name = 'cmb_box_dataset')
        if(dataset != None):
            return dataset.currentText()
        else:
            return 'None'
        
from controller import *

class EventListener(object):
    def btn_pressed(self):
        print('btn pressed')
        self.control.submit_form()

    def __init__(self):
        print('event intiated')
        control : Controller = None

    def print(self):
        control.print()
    
    def dataset_chosen_changed(self):
        self.control.set_dataset()        
    
    
    def attribute_selected(self, i : int):
        print("attribute_selected")
        print(i)
        self.control.attribute_chosen(i)
        

        
        
   
        



    
