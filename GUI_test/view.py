from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QPushButton, QSlider, QScrollBar, QLayout, QLayoutItem, QCheckBox
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QSignalMapper
from PyQt5.QtGui import QPalette, QColor


class View(object):
    def __init__(self):
        print("init")
        self.listener = EventListener()
        self.app = QApplication([])
        self.window = QWidget()
      
    def test_(self):
        print('cmb_box signal')

    def startView(self):
        main_layout = QGridLayout()
        
        #upper top left
        cmb_box_dataset = QComboBox(objectName = 'cmb_box_dataset', currentIndexChanged = self.listener.dataset_chosen_changed)
        #cmb_box_dataset.currentIndexChanged.connect(self.test_cmb)
        cmb_box_dataset.addItems(['KDD99', 'KDD99'])
        label_dataset = QLabel('Datasets')
        label_dataset.setBuddy(cmb_box_dataset)
        btn_import = QPushButton('IMPORT')
        btn_del_attr = QPushButton('del attr', clicked = self.listener.remove_selected_attr)
        #
        #btn_import.setStyleSheet("background : yellow")
        pal = btn_import.palette()
        #pal.setColor(QPalette.Active, QPalette.Button, QColor(Qt.yellow))
        btn_import.setAutoFillBackground(True)
        
        btn_import.setPalette(pal)
        btn_import.update()

        #
        layout_top_upper = QHBoxLayout()
        layout_top_upper.addWidget(label_dataset)
        layout_top_upper.addWidget(cmb_box_dataset)
        layout_top_upper.addWidget(btn_import)
        layout_top_upper.addWidget(btn_del_attr)
        
        #Group top left
        top_left_group = QGroupBox('Top left group', objectName = 'top_left_group')
        
        layout_top1 = QVBoxLayout(objectName = "top_left_box")
        #layout_top_inner1 = QVBoxLayout(objectName = "top_left_box_inner1")
        #layout_top_inner2 = QVBoxLayout(objectName = "top_left_box_inner2")
        #layout_top2 = QVBoxLayout(objectName = "top_left_box2")
        
        #scrollBar = QScrollBar(Qt.Vertical, top_left_group)
        #scrollBar.setValue(20)
        #layout_top.addWidget(scrollBar)
        #layout_top1.addLayout(layout_top_inner1)
        #layout_top1.addLayout(layout_top_inner2)
        #layout_top.addLayout(layout_top1)
        #layout_top.addLayout(layout_top2)
        top_left_group.setLayout(layout_top1)

        

        #Group top right
        right_group = QGroupBox('Right group')

        layout_right = QHBoxLayout(objectName = 'right_outer')
            
        layout_right1 = QVBoxLayout(objectName = 'right1')
        layout_right2 = QVBoxLayout(objectName = 'right2')
        layout_right.addLayout(layout_right1)
        layout_right.addLayout(layout_right2)
        
        attr_name_lbl = QLabel('Attr. name1')
        attr_type_lbl = QLabel('*type1')
        #layout_right1.addWidget(attr_name_lbl)
        #layout_right2.addWidget(attr_type_lbl)
        
        right_group.setLayout(layout_right)
        


        #Group button right
        layout_button = QVBoxLayout()
        alg_menu = QComboBox(objectName = 'alg_menu')
        alg_menu.addItems(['KMean', 'SOM'])
        
        alg_label = QLabel('Algorithm to apply')
        alg_label.setBuddy(alg_menu)
        apply_btn = QPushButton('&APPLY')
        layout_button.addWidget(alg_label)
        layout_button.addWidget(alg_menu)
        layout_button.addWidget(apply_btn)
        #
       
        main_layout.addLayout(layout_top_upper, 0, 0, 1, 1)
        main_layout.addWidget(top_left_group, 1, 0)
        main_layout.addWidget(right_group, 1, 3)
        
        main_layout.addLayout(layout_button, 2, 3)
        self.window.setLayout(main_layout)
        
        self.window.show()
        self.app.exec_()
    

    def set_attr_group(self, dataset):
        layout = self.window.findChild(QVBoxLayout, name = "top_left_box")

        #layout_inner1 = self.window.findChild(QVBoxLayout, name = "top_left_box_inner1")
        #layout_inner2 = self.window.findChild(QVBoxLayout, name = "top_left_box_inner2")
        #layout2 = self.window.findChild(QVBoxLayout, name = "top_left_box2")
        for index, item in enumerate(dataset):
            layout_inner = QHBoxLayout(objectName = "top_left_box_inner")
            check = QCheckBox(checked = False)
            btn = QPushButton('attr.' + str(index + 1), objectName = 'attr.' + str(index), flat = True)#at the moment hardcoding name of attributes because no name on the dataset (KDD)
            #using lambda to pass an additional paramether. Have to use i = index or the last variable will be passed to all the lambdas
            btn.clicked.connect(lambda a, i = index : self.listener.attribute_selected(i)) #have to use additional a paramether because connect will pass a boolean variable and if not consumed will be assigned to i and then passed to listener function
            layout_inner.addWidget(check)
            check.setProperty('index', index) #setting a property index to be retreived when deleting attribute
            layout_inner.addWidget(btn)
            layout_inner.addWidget(QLabel(item))
            layout.addLayout(layout_inner) #CARE, if call twice it will add it twice! TODO: check if it is prensent and write over, or delete it completely and start again

            
           
        
    def add_lbl_test(self, widget, a, index = 2):
        """create labels - used for DEBUG purposes"""
        for i in range(index):
            widget.addWidget(QLabel(' ' * index + a))
        
    def get_dataset_chosen(self):
        dataset = self.window.findChild(QComboBox, name = 'cmb_box_dataset')
        if(dataset != None):
            return dataset.currentText()
        else:
            return 'None'

    def set_attribute_info(self, infos):
        right1 = self.window.findChild(QVBoxLayout, name = 'right1')
        right2 = self.window.findChild(QVBoxLayout, name = 'right2')
        self.clean_widget(right1)
        self.clean_widget(right2)
        
        for item in infos:
            right1.addWidget(QLabel(str(item[0])))
            right2.addWidget(QLabel(str(item[1])))

    
    def clean_widget(self, layout : QLayout):
        while(True):
            item = layout.takeAt(0)
            
            if(item == None):
                break
            child_l = item.layout() #if item is a layout, it is returned as layout. if not as None => is a widget
            if(child_l != None):
                self.clean_layout(child_l)
                
            widget = item.widget()
            if(widget != None):
                print(widget.text())
                widget.deleteLater()
                
            del item
       
    def get_unselected_attributes(self):
        pass

    def get_attribute_selected(self):
        indexes = []
        layout = self.window.findChild(QGroupBox, name = 'top_left_group')
        check_boxs = layout.findChildren(QCheckBox)
        for item in check_boxs:
            if(item.isChecked()):
                indexes.append(item.property('index'))
        return indexes

from controller import *

class EventListener(object):
    
    def __init__(self):
        print('event intiated')
        control : Controller = None

    def dataset_chosen_changed(self):
        self.control.set_dataset()        
    
    
    def attribute_selected(self, i : int):
        self.control.attribute_chosen(i)
        
    def submit_window(self):
        self.control.submit_window()
        
    def remove_selected_attr(self):
        self.control.attr_removed()
   
        



    
