from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QPushButton, QSlider, QScrollBar, QLayout, QLayoutItem, QCheckBox, QScrollArea, QSizePolicy, QFileDialog
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QSignalMapper, QStringListModel, QModelIndex
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
class View(object):
    def __init__(self):
        print("init")
        self.listener = EventListener()
        self.app = QApplication([])
        self.window = QWidget()
        self.second_window : QWidget()
        self.attribute_checked = 0
      
    def startView(self, dataset_names):
        main_layout = QGridLayout()
        
        #upper top left
        cmb_box_dataset = QComboBox(objectName = 'cmb_box_dataset')
        cmb_box_dataset.addItem('')
        model : QStandardItemModel = cmb_box_dataset.model()
        firstIndex : QModelIndex = model.index(0, cmb_box_dataset.modelColumn(), cmb_box_dataset.rootModelIndex())
        firstItem = model.itemFromIndex(firstIndex)
        firstItem.setSelectable(False)
        cmb_box_dataset.addItems(dataset_names)
        cmb_box_dataset.currentIndexChanged.connect(self.listener.dataset_chosen_changed)#connecting after adding items, so it wont trigger the signal
        label_dataset = QLabel('Datasets')
        label_dataset.setBuddy(cmb_box_dataset)
        btn_import = QPushButton('IMPORT', clicked = self.listener.import_dataset)
        btn_del_attr = QPushButton('del attr', objectName = 'delbtn', clicked = self.listener.remove_selected_attr, enabled = False)
        btn_ntb = QPushButton('Transform to binary', objectName = 'ntbbtn', clicked = self.listener.nominal_to_binary, enabled = False)
        
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
        
        #debugging
        btn_test = QPushButton('test', clicked = self.test)
        layout_top_upper.addWidget(btn_test)
        #
        
        
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
        apply_btn = QPushButton('&APPLY', clicked = self.listener.submit_window)
        layout_button.addWidget(alg_label)
        layout_button.addWidget(alg_menu)
        layout_button.addWidget(apply_btn)
        #
       
        main_layout.addLayout(layout_top_upper, 0, 0, 1, 1) #from row, from col, widthspan, to hightspan (1 is no span)
        main_layout.addWidget(top_left_group, 1, 0, 2, 1)
        main_layout.addWidget(right_group, 1, 1)
        main_layout.addLayout(layout_button, 2, 1, Qt.AlignBottom)

        self.window.setLayout(main_layout)
        
    
    def execute(self):
        self.window.show()
        #self.new_window('som')
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

            
    def set_cmbbox_datasets(self, dataset_names, name_current):
        cmbbox : QComboBox = self.window.findChild(QComboBox, name = 'cmb_box_dataset')
        cmbbox.clear()
        #keeping the empty as first, so it is guaranteed that it will be the currentIndex after clearing the cmbbox and can be excepted from dataset name to be loaded
        cmbbox.addItem('')
        model : QStandardItemModel = cmbbox.model()
        firstIndex : QModelIndex = model.index(0, cmbbox.modelColumn(), cmbbox.rootModelIndex())
        firstItem = model.itemFromIndex(firstIndex)
        firstItem.setSelectable(False)
        cmbbox.addItems(dataset_names)
        cmbbox.setCurrentText(name_current)
        
    def add_lbl_test(self, widget, a, index = 2):
        """create labels - used for DEBUG purposes"""
        for i in range(index):
            widget.addWidget(QLabel(' ' * index + a))
        
    def get_dataset_chosen(self):
        dataset : QComboBox = self.window.findChild(QComboBox, name = 'cmb_box_dataset')
        if(dataset != None):
            print(dataset.currentText())
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
    
    def get_file_selected(self, caption = 'Select dataset', filter = '', directory = ''):
        file_dialog = QFileDialog(caption = caption, filter = filter, directory = directory)
        #.getOpenFileName(caption = 'Select dataset', directory = "C:\\", filter = 'Dataset files (*.csv)') 
        file_selected = []
        if(file_dialog.exec()):
            file_selected = file_dialog.selectedFiles()
        print(file_selected)
        return file_selected

    def get_algorithm_active(self):
        algorithm : QComboBox = self.window.findChild(QComboBox, name = "alg_menu")
        return algorithm.currentText()

    def new_window(self, algorithm):
        self.second_window = QWidget()
        main_layout = QGridLayout()
        layout_top_upper = QVBoxLayout()
        layout_top_upper.addWidget(QLabel(str.upper(algorithm)))
        layout_top_upper.addWidget(QPushButton('modify settings', clicked = self.listener.show_settings_algorithm))
        layout_top_upper.addWidget(QPushButton('View clusters created', clicked = self.listener.view_som_map_clusters))
        m = PlotCanvas(self.second_window, width=5, height=4)
        layout_top_upper.addWidget(m)
        layout_mid = QVBoxLayout()
        layout_bottom = QVBoxLayout()
        layout_bottom.addWidget(QPushButton('RERUN', clicked = self.listener.rerun_algorithm))
        main_layout.addLayout(layout_top_upper,0,0)
        main_layout.addLayout(layout_mid, 1, 0)
        main_layout.addLayout(layout_bottom, 2, 0)
        self.second_window.setLayout(main_layout)
        
        self.second_window.show()
       
    def test(self):
        self.window.close()
        
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
 
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()
        
 
    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        ax.set_title('PyQt Matplotlib Example')
        self.draw()

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
        self.control.run_algorithm()
        
    def remove_selected_attr(self):
        self.control.attr_removed()
    
    def nominal_to_binary(self):
        self.control.nominal_to_binary()
   
    def import_dataset(self):
        print('import btn pressed')
        self.control.import_dataset()

    def view_som_map_clusters(self):
        self.control.view_som_map_clusters()

    def show_settings_algorithm(self):
        self.control.show_settings_algorithm()
    
    def rerun_algorithm(self):
        self.control.rerun_algorithm()
    
