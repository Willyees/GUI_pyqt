from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QPushButton, QSlider, QScrollBar, QLayout, QLayoutItem, QCheckBox, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QSignalMapper
from PyQt5.QtGui import QPalette, QColor


class View(object):
    def __init__(self):
        print("init")
        self.listener = EventListener()
        self.app = QApplication([])
        self.window = QWidget()
        self.attribute_checked = 0
      
    def startView(self):
        main_layout = QGridLayout()
        
        #upper top left
        cmb_box_dataset = QComboBox(objectName = 'cmb_box_dataset', currentIndexChanged = self.listener.dataset_chosen_changed)
        #cmb_box_dataset.currentIndexChanged.connect(self.test_cmb)
        cmb_box_dataset.addItems(['KDD99', 'KDD99'])
        label_dataset = QLabel('Datasets')
        label_dataset.setBuddy(cmb_box_dataset)
        btn_import = QPushButton('IMPORT')
        btn_del_attr = QPushButton('del attr', objectName = 'delbtn', clicked = self.listener.remove_selected_attr, enabled = False)
        btn_ntb = QPushButton('Transform to binary', objectName = 'ntbbtn', clicked = self.listener.nominal_to_binary, enabled = False)
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
        layout_top_upper.addWidget(btn_ntb)
        
        #Group top left
        top_left_group = QGroupBox('Attributes', objectName = 'top_left_group')
        layout_top = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding) #horizontal policy -follows size_hint(), vertical policy - takes as much as possible space
        
        widget_scroll = QWidget()
        
        layout_top1 = QVBoxLayout(objectName = "top_left_box")
        
        widget_scroll.setLayout(layout_top1)
        scroll.setWidget(widget_scroll)
        scroll.setWidgetResizable(True)
        layout_top.addWidget(scroll)
        top_left_group.setLayout(layout_top)
        
        #Group top right
        right_group = QGroupBox('Attribute Details')
        
        layout_right = QHBoxLayout(objectName = 'right_outer')
        #layout_right1 = QVBoxLayout(objectName = 'right1')
        #layout_right2 = QVBoxLayout(objectName = 'right2')
        #layout_right.addLayout(layout_right1)
        #layout_right.addLayout(layout_right2)
        
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
       
        main_layout.addLayout(layout_top_upper, 0, 0, 1, 1) #from row, from col, widthspan, to hightspan (1 is no span)
        main_layout.addWidget(top_left_group, 1, 0, 2, 1)
        main_layout.addWidget(right_group, 1, 1)
        main_layout.addLayout(layout_button, 2, 1, Qt.AlignBottom)

        self.window.setLayout(main_layout)
        
        self.window.show()
        self.app.exec_()
    

    def set_attr_group(self, dataset):
        layout = self.window.findChild(QVBoxLayout, name = "top_left_box")
        self.clean_layout(layout)

        for index, item in enumerate(dataset):
            layout_inner = QHBoxLayout(objectName = "top_left_box_inner")
            check = QCheckBox(checked = False, stateChanged = self.listener.attribute_checked)
            btn = QPushButton('attr.' + str(index + 1), objectName = 'attr.' + str(index), flat = False)#at the moment hardcoding name of attributes because no name on the dataset (KDD)
            #using lambda to pass an additional paramether. Have to use i = index or the last variable will be passed to all the lambdas
            btn.clicked.connect(lambda a, i = index : self.listener.attribute_selected(i)) #have to use additional a paramether because connect will pass a boolean variable and if not consumed will be assigned to i and then passed to listener function
            layout_inner.addWidget(check)
            check.setProperty('index', index) #setting a property index to be retreived when deleting attribute
            layout_inner.addWidget(btn)
            layout_inner.addWidget(QLabel(item, objectName = 'type_attr.' + str(index)))
            layout.addLayout(layout_inner)

            
           
        
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
        right = self.window.findChild(QHBoxLayout, name = 'right_outer')
        #right1 = self.window.findChild(QVBoxLayout, name = 'right1')
        #right2 = self.window.findChild(QVBoxLayout, name = 'right2')
        #self.clean_layout(right1)
        #self.clean_layout(right2)
        self.clean_layout(right)
        
        for i_in in range(len(infos[0])):
            layout = QVBoxLayout()
            for i_out in range(len(infos)):
                layout.addWidget(QLabel(str(infos[i_out][i_in])))
                #right2.addWidget(QLabel(str(item[1])))
            right.addLayout(layout)

    
    def clean_layout(self, layout : QLayout):
        print('clear layout')
        while(True):
            item = layout.takeAt(0)
            
            if(item == None):
                break
            child_l = item.layout() #if item is a layout, it is returned as layout. if not as None => is a widget
            if(child_l != None):
                self.clean_layout(child_l)
                del child_l
                
            widget = item.widget()
            if(widget != None):
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
    
    def attr_checked(self, status):
        if(status == Qt.Checked):
            self.attribute_checked += 1
        elif(status == Qt.Unchecked):
            self.attribute_checked -= 1
    
    def set_delbtn_state(self):
        delbtn = self.window.findChild(QPushButton, name = 'delbtn')
        if(self.attribute_checked == 0):
            delbtn.setEnabled(False)
        else:
            delbtn.setEnabled(True)

    def set_ntbbtn_state(self):
        delbtn = self.window.findChild(QPushButton, name = 'ntbbtn')
        if(self.attribute_checked == 0):
            delbtn.setEnabled(False)
        else:
            delbtn.setEnabled(True)
    
from controller import *

class EventListener(object):
    
    def __init__(self):
        print('event intiated')
        control : Controller = None

    def dataset_chosen_changed(self):
        self.control.set_dataset()        
    
    
    def attribute_selected(self, i : int):
        self.control.attribute_chosen(i)

    def attribute_checked(self, state):
        self.control.attribute_checked(state)
        
    def submit_window(self):
        self.control.submit_window()
        
    def remove_selected_attr(self):
        self.control.attr_removed()
    
    def nominal_to_binary(self):
        self.control.nominal_to_binary()
   
        



    
