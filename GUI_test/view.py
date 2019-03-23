from PyQt5.QtWidgets import QApplication, QLabel, QComboBox, QHBoxLayout, QWidget, QVBoxLayout, QGroupBox, QGridLayout, QPushButton, QSlider, QScrollBar, QLayout, QLayoutItem, QCheckBox, QScrollArea, QSizePolicy, QFileDialog, QInputDialog, QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt5.QtCore import Qt, QObject, pyqtSlot, QSignalMapper, QStringListModel, QModelIndex, QRect
from PyQt5.QtGui import QPalette, QColor, QStandardItemModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import numpy as np
from collections import deque

class View(object):
    def __init__(self):
        print("init")
        self.listener = EventListener()
        self.app = QApplication([])
        self.window = QWidget()
        self.window.setMinimumSize(400,400)
        self.second_window = QWidget()
        self.second_window.setAttribute(Qt.WA_DeleteOnClose)
        self.additional_windows = []
        self.attribute_checked = 0
        self.active_window = QWidget()
      
    def startView(self, dataset_names, algorithm_names):
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
        btn_import_training = QPushButton('IMPORT', clicked = self.listener.import_dataset)
        btn_import_test = QPushButton('Import testset', clicked = self.listener.import_test_set)
        btn_del_attr = QPushButton('del attr', objectName = 'delbtn', clicked = self.listener.remove_selected_attr, enabled = False)
        btn_ntb = QPushButton('Transform to binary', objectName = 'ntbbtn', clicked = self.listener.nominal_to_binary, enabled = False)
        
        #btn_import.setStyleSheet("background : yellow")
        pal = btn_import_training.palette()
        #pal.setColor(QPalette.Active, QPalette.Button, QColor(Qt.yellow))
        btn_import_training.setAutoFillBackground(True)
        
        btn_import_training.setPalette(pal)
        btn_import_training.update()

        #
        layout_top_upper = QHBoxLayout()
        layout_top_upper.addWidget(label_dataset)
        layout_top_upper.addWidget(cmb_box_dataset)
        layout_top_upper.addWidget(btn_import_training)
        layout_top_upper.addWidget(btn_import_test)
        layout_top_upper.addWidget(btn_del_attr)
        layout_top_upper.addWidget(btn_ntb)
        
        #debugging
        btn_test = QPushButton('test', clicked = self.test)
        layout_top_upper.addWidget(btn_test)
        #
        
        #layout testing dataset
        layout_testing = QHBoxLayout()
        testing = QLabel('Selected testing set: None', objectName = "label_testing")
        testing.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout_testing.addWidget(testing)
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
        alg_menu = QComboBox(objectName = 'alg_menu', maximumWidth = 200)
        alg_menu.addItems(algorithm_names)
        
        alg_label = QLabel('Algorithm to apply')
        alg_label.setBuddy(alg_menu)
        apply_btn = QPushButton('&APPLY', clicked = self.listener.submit_window, maximumWidth = 200)
        layout_button.addWidget(alg_label)
        layout_button.addWidget(alg_menu)
        layout_button.addWidget(apply_btn)
        #
       
        main_layout.addLayout(layout_top_upper, 0, 0, 1, 1) #from row, from col, widthspan, to hightspan (1 is no span)
        main_layout.addWidget(top_left_group, 1, 0, 2, 1)
        main_layout.addWidget(right_group, 1, 1)
        
        main_layout.addLayout(layout_button, 2, 1, Qt.AlignBottom)
        main_layout.addLayout(layout_testing, 3, 0, 1, 1)
        self.window.setLayout(main_layout)
        self.active_window = self.window #setting the active window so it is possible to retreive information about the actual showing window
        
    
    def execute(self):
        self.window.show()
        #self.new_window('som')
        self.app.exec_()

    def set_attr_group(self, dataset, names):
        layout = self.window.findChild(QVBoxLayout, name = "top_left_box")
        self.clean_layout(layout)

        for index, item in enumerate(dataset):
            layout_inner = QHBoxLayout(objectName = "top_left_box_inner")
            check = QCheckBox(checked = False, stateChanged = self.listener.attribute_checked)
            name_attr = names[index] if len(names) != 0 else 'attr.' + str(index + 1) 
            btn = QPushButton(name_attr, objectName = 'attr.' + str(index), flat = False)#at the moment hardcoding name of attributes because no name on the dataset (KDD)
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

    def get_checkbox_selected(self):
        indexes = []
        #layout = self.actual_window.findChild(QGroupBox, name = 'top_left_group') using the window as parent
        check_boxs = self.active_window.findChildren(QCheckBox)
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
        window = QWidget(destroyed = self.closed_second_window)
        window.setAttribute(Qt.WA_DeleteOnClose)
        main_layout = QGridLayout()
        layout_top_upper = QHBoxLayout()
        layout_top_upper.addWidget(QLabel(str.upper(algorithm)))
        btn_settings = QPushButton('Modify settings', clicked = self.listener.show_settings_algorithm)
        btn_settings.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        layout_top_upper.addWidget(btn_settings)
        if(algorithm == 'som'): #dirty
            btn_som = QPushButton('View clusters created', clicked = self.listener.view_som_map_clusters)
            btn_som.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
            layout_top_upper.addWidget(btn_som)
        
        group_box_results = QGroupBox('Results')
        
        layout_results_wrapper = QVBoxLayout()
        layout_results = QVBoxLayout(objectName = 'layout_results')
        layout_results.setAlignment(Qt.AlignTop)
        btn_compare = QPushButton('COMPARE', clicked = self.listener.compare_results)
        
        layout_results_wrapper.addLayout(layout_results)
        layout_results_wrapper.addWidget(btn_compare)
        layout_results_wrapper.setAlignment(btn_compare, Qt.AlignBottom)
        
        group_box_results.setLayout(layout_results_wrapper)
        
        layout_mid = QVBoxLayout(objectName = 'layout_mid')
        layout_datasets_info = QVBoxLayout(objectName = 'layout_datasets_info')
        layout_result_table = QVBoxLayout(objectName = 'layout_result_table')
        layout_result_alg_prop = QVBoxLayout(objectName = 'layout_result_alg_prop')
        layout_charts = QHBoxLayout()
        m = PlotCanvas(window) #width , height changes the size of the plot 
        m1 = PlotCanvas(window)
        layout_charts.addWidget(m)
        layout_charts.addWidget(m1)
        layout_mid.addLayout(layout_datasets_info)
        layout_mid.addLayout(layout_charts)
        layout_mid.addLayout(layout_result_table)
        layout_mid.addLayout(layout_result_alg_prop)
        layout_bottom = QVBoxLayout()
        btn_rerun = QPushButton('RERUN', clicked = self.listener.rerun_algorithm, maximumWidth = 100)
        layout_bottom.addWidget(btn_rerun)
        layout_bottom.setAlignment(btn_rerun, Qt.AlignCenter)
        
        main_layout.addLayout(layout_top_upper,0,0, 1, 2)
        main_layout.addWidget(group_box_results,1,0,1,1)
        main_layout.addLayout(layout_mid, 1, 1)
        main_layout.addLayout(layout_bottom, 2, 1)
        main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        window.setLayout(main_layout)
        
        #self.second_window.setWindowModality(Qt.ApplicationModal)
        del self.active_window
        
        self.second_window = window
        self.active_window = window
        print("active_window = second")
        self.active_window.show()
        
     
    def show_algorithm_results(self, train_set_properties, test_set_properties, algorithm, results, names_results, compare_results = [], compare_names = [], indexes = []):
        """indexes: index of the chosen results to compare [array] it can be empty"""
        self.new_window(algorithm) #work on second window
              
        #set the results names 
        layout_results : QVBoxLayout = self.second_window.findChild(QVBoxLayout, name = "layout_results")
        for index in range(len(names_results)):
            layout_inner = QHBoxLayout()
            check = QCheckBox(checked = False, stateChanged = self.listener.attribute_checked)
            check.setProperty('index', index)
            btn = QPushButton(names_results[index])
            #widget.setProperty('index', index) not need because index is stored in the lambda
            btn.clicked.connect(lambda a, i = index : self.listener.result_chosen(i)) #a paramether used to consume the boolean that clicked would pass to function
            layout_inner.addWidget(check)
            layout_inner.addWidget(btn)
            layout_results.addLayout(layout_inner)
            layout_results.setAlignment(layout_inner,Qt.AlignTop)

        #set datasets info
        layout_datasets_info = self.second_window.findChild(QVBoxLayout, name = 'layout_datasets_info')
        table_datasets = QTableWidget(2, len(train_set_properties)) #rows, columns
        table_datasets.setHorizontalHeaderLabels(list(train_set_properties.keys()))
        table_datasets.setVerticalHeaderLabels(['Trainset', 'Testset'])
        table_datasets.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table_datasets.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_datasets.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        
        #table_datasets.layout().setSizeConstraint(QLayout.SetMinimumSize)
        #table_datasets.setGeometry(QApplication.desktop().screenGeometry())
        #set the train set info
        for index, val in enumerate(train_set_properties.values()):
             table_datasets.setItem(0, index, QTableWidgetItem(str(val)))
        #set the test set info
        for index, val in enumerate(test_set_properties.values()):
             table_datasets.setItem(1, index, QTableWidgetItem(str(val)))
        table_datasets.resizeColumnsToContents()
        table_datasets.updateGeometries()
        width = 0.0
        for i in range(table_datasets.columnCount()):
            width += table_datasets.columnWidth(i)
        width += table_datasets.verticalHeader().width()  
        height = 0.0
        for i in range(table_datasets.rowCount()):
            height += table_datasets.rowHeight(i)
        height += table_datasets.horizontalHeader().height()
        #table.setFixedSize(table.horizontalHeader()->length()+table.verticalHeader()->width(), table.verticalHeader()->length()+table.horizontalHeader()->height())
        
        table_datasets.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed);
        table_datasets.setMaximumSize(width, height)
        
        layout_datasets_info.addWidget(table_datasets)
        #plot the charts
        plots = self.second_window.findChildren(PlotCanvas)   
        #plot.plot_bar([detection_rate],[name])
        results_list = []
        results_titles = []
        results_names = []
        if(compare_results):
            results_list = [[] for x in range(len(compare_results[0]))]
            for index in range(len(compare_results)):
                for inn, (key, val) in enumerate(compare_results[index].items()):
                    results_list[inn].append(val * 100) 
                    results_titles.append(key)
            results_titles = results_titles[0:len(compare_results[0])] #all the keys were added. Only keep the unique ones
            results_names = compare_names
        else:
            results_list = [[val * 100] for val in results.values()] #multiply by 100 to get the percentage
            results_titles = [key for key in results.keys()]
            results_names = [algorithm]
        for index in range(len(results_list)):
            plots[index].plot_bar(results_list[index], results_names, results_titles[index])

       
        layout_result_table = self.active_window.findChild(QVBoxLayout, name = 'layout_result_table')
        #table results
        if not(compare_results):
            table_results = QTableWidget(1, len(results), objectName = 'table_results')
            table_results.setHorizontalHeaderLabels(list(results.keys()))
            table_results.setVerticalHeaderLabels([algorithm])
            vheader = table_results.verticalHeader()
            vheader.sectionPressed.connect(lambda table_index, i = indexes : self.listener.table_alg_chosen(table_index, i))
            
            
            table_results.setEditTriggers(QAbstractItemView.NoEditTriggers);
            table_results.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            table_results.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            

            for index, val in enumerate(results.values()):
                table_results.setItem(0,index, QTableWidgetItem(str(val)))
        else:
            
            table_results = QTableWidget(len(compare_names), len(compare_results), objectName = 'table_results') #rows, columns
            table_results.setHorizontalHeaderLabels(list(compare_results[0].keys()))
            compare_names = [compare_names[index] + str(index + 1) for index in range(len(compare_names))] #add index after the name
            table_results.setVerticalHeaderLabels(compare_names)
            vheader = table_results.verticalHeader()
            vheader.sectionPressed.connect(lambda table_index, i = indexes : self.listener.table_alg_chosen(table_index, i))
            
            table_results.setEditTriggers(QAbstractItemView.NoEditTriggers);
            table_results.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            table_results.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            for index in range(len(compare_results)):
                    for inn, val in enumerate(compare_results[index].values()):
                        table_results.setItem(index, inn, QTableWidgetItem(str(val)))
            table_results.resizeColumnsToContents()
        table_results.updateGeometries()
        table_results.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        table_results.setFixedSize(table_results.horizontalHeader().length()+table_results.verticalHeader().width(), table_results.verticalHeader().length()+table_results.horizontalHeader().height())
            
        
        layout_result_table.addWidget(table_results)
        layout_result_table.update()
        #show properties algorithms 

        #set the window size bigger
        geom = self.second_window.geometry()
        geom.setWidth(1000)
        self.second_window.setGeometry(geom)
        
    def show_alg_properties_chosen(self, name_alg, properties):
        #clear layout
        
        layout = self.active_window.findChild(QVBoxLayout, name = "layout_result_alg_prop")
        if(layout == None):
            return
        table = QTableWidget(1,len(properties))
        self.clean_layout(layout)
        
        table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table.setHorizontalHeaderLabels(list(properties.keys()))
        
        
        table.setVerticalHeaderLabels([name_alg])
        for index, val in enumerate(properties.values()):
            table.setItem(0, index, QTableWidgetItem(str(val)))

        table.resizeColumnsToContents()
        table.updateGeometries()
        #width = 0.0
        #for i in range(table.columnCount()):
        #    width += table.columnWidth(i)
        #width += table.verticalHeader().width()  
        #height = 0.0
        #for i in range(table.rowCount()):
        #    height += table.rowHeight(i)
        #height += table.horizontalHeader().height()
        
        #layout.addWidget(table)
        table.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed);
        #table.setMaximumSize(width, height)


        #table.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        
        
        #table.resizeRowsToContents()
        #print(width)
        #print(height)
        #print(table.horizontalHeader().length()+table.verticalHeader().width())
        #print(table.verticalHeader().length()+table.horizontalHeader().height())
        
        table.setMaximumSize(table.horizontalHeader().length()+table.verticalHeader().width(), table.verticalHeader().length()+table.horizontalHeader().height())
        
        layout.addWidget(table)
        

    def show_new_window_scatterplot(self, labels_element, x_coords, y_coords, name = None):
        if len(x_coords) != len(y_coords):
            print("missing coordinates for categories to represent in the scatterplot")
            return
        if len(x_coords) != len(labels_element):
            print("mismatching number of labels and categories coordinates")
            return
        plt.figure(num = name)
        for index in range(len(x_coords)):
            plt.scatter(x_coords[index], y_coords[index],
                label=labels_element[index])
        plt.legend()
        plt.show()
        
    
    def create_new_submit_form_window(self, info, fields : dict, options_fields : dict):
        """will create a new window with specified fields and default input preloaded in the view
        info: text to dispay at the top of the window (bold)"""
        window = QWidget(destroyed = self.closed_additional_window)
        window.setAttribute(Qt.WA_DeleteOnClose)
        main_grid = QGridLayout()
        layout_info = QHBoxLayout()
        info = QLabel(info)
        info.setStyleSheet("font-weight: bold")
        layout_info.addWidget(info)
        outer_layout = QVBoxLayout()
        for key, value in fields.items():
            #layout = QVBoxLayout()
            #layout.addWidget(QLabel(key))
            input = QInputDialog()
            if(key in options_fields): 
                input.setComboBoxItems(options_fields[key])    
                #input.setMaximumWidth(500)
                input.setTextValue(str(value))
            else:
                if type(value) == float:
                    input.setDoubleValue(float(value))
                elif type(value) == int:
                    input.setIntValue(int(value))
                else:
                    input.setTextValue(str(value))
                
            input.setOption(QInputDialog.NoButtons)
            input.setLabelText(key)
            input.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
            outer_layout.addWidget(input)
        
        bottom_layout = QHBoxLayout()
        set_btn = QPushButton('SET', objectName = 'btn_set_form', clicked = self.listener.form_submitted)
        set_btn.setMaximumWidth(100)
        bottom_layout.addWidget(set_btn)
        
        main_grid.addLayout(layout_info, 0, 0)
        main_grid.addLayout(outer_layout, 1, 0)
        main_grid.addLayout(bottom_layout, 2, 0)
        window.setLayout(main_grid)
        self.additional_windows.append(window)
        self.additional_windows[0].show()    
    
    def closed_additional_window(self):
        #remove window from list
        print("removed window")
        self.additional_windows.pop()
    
    def closed_second_window(self):
        print("closed second window")
        self.active_window = self.window

    def get_properties_modified(self):
        window = self.additional_windows[len(self.additional_windows) - 1] #get last additional window
        inputs = window.findChildren(QInputDialog)
        properties = {}
        for input in inputs:
            input_type = input.inputMode()
            label = input.labelText()
            if input_type == QInputDialog.TextInput:
                properties[label] = input.textValue()
            elif input_type == QInputDialog.IntInput:
                properties[label] = input.intValue()
            elif input_type == QInputDialog.DoubleInput:
                properties[label] = input.doubleValue()
        window.close()
        print(properties)
        return properties

    def set_training_set(self, name):
        train : QLabel = self.window.findChild(QLabel, name = "label_testing")
        train.setText("Selected testing set: \"" + name + "\"")

    def test(self):
        pass
    def itemClicked(self, i):
        table = self.active_window.findChild(QTableWidget, name = 'table_results')
        print(table.verticalHeaderItem(i).text())
class PlotCanvas(FigureCanvas):
 
    def __init__(self, parent=None, width=2, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)
        fig.patch.set_facecolor("None")
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.setStyleSheet("background-color:transparent;")
        
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
    def plot_bar(self, heights, labels, title):
        #pm, pc, pn = plt.bar(ind, get_stats(0))
        #pm.set_facecolor('r') #can change color in this way
        chart = self.figure.subplots()
        chart.bar(np.arange(len(heights)), heights, width = 0.35)
        chart.set_ylim([0,100])
        chart.set_xticks(np.arange(len(heights) + 1))#adding extra tick because in case there is only 1, the bar will occupy the whole chart resulting in a big fat bar
        chart.set_xticklabels(labels)
        chart.set_ylabel('%')
        chart.set_title(title)
        #chart.patch.set_alpha(0.5)
        
        self.draw()
        #matplotlib.pyplot.bar(x, height, width=0.8, bottom=None, *, align='center', data=None, **kwargs)[source]
        #https://matplotlib.org/api/_as_gen/matplotlib.pyplot.bar.html

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
        self.control.set_run_algorithm()
        
    def remove_selected_attr(self):
        self.control.attr_removed()
    
    def nominal_to_binary(self):
        self.control.nominal_to_binary()
   
    def import_dataset(self):
        print('import btn pressed')
        self.control.import_training_set()
    
    def import_test_set(self):
        self.control.import_test_set()

    def view_som_map_clusters(self):
        self.control.view_som_map_clusters()

    def show_settings_algorithm(self):
        self.control.show_settings_algorithm()
    
    def rerun_algorithm(self):
        self.control.run_algorithm()

    def form_submitted(self):
        self.control.modify_properties_alg()
    
    def result_chosen(self, index):
        self.control.set_chosen_result(index)

    def compare_results(self):
        self.control.compare_results()

    def table_alg_chosen(self,table_index, indexes_model):
        self.control.show_alg_properties(table_index, indexes_model)
        
        
