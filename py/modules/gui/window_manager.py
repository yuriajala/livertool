'''
Este arquivo contém as funções associadas aos elementos da interface.
no começo são definidas as principais variáveis
*current_file
*current_fatmaps
(e futuramente)
*current_rois (ou algo do tipo)
elas são objetos que serão instanciados ao abrir um arquivo válido
objetos das classes definidas em ../data
current_file é DicomFile, que contém o header e a matriz de imagens, o que precisar o window_manager vai pegar de lá
current_fatmaps é da classe... FatMaps. Ela contém os mapas inteiros e/ou parciais que foram gerados
(assim quando gera um, não perde o que foi gerado anteriormente, mesmo que mude de método)
Isso vai facilitar na hora de exportar
A classe roi ainda não foi adaptada para o mesmo molde (mas já existe de antes)

os métodos:

ui_init seta os valores iniciais ao abrir o software. Ao carregar um arquivo, eles são alterados

set_events determina a função de trigger chamada por cada botão na interface, é geralmente por ela que uma ação vai começar quando
vc se perder no código

os trigger methods são os chamados pelos set_events. São funções para cada interação do usuário. Essas função em geral
vão só preparar os dados para chamar funções mais complexas.
    Ao carregar um arquivo com trigger_load_single/multiple_dicom, será chamada update_dicom_img
    ela vai ajustar os botões, mostrar a imagem (trigger_change_slice_img, que por sua vez já chama a que mostra o fatmap
     e pega as ROI, ambas se houver) e por fim chamar uma função que troca as info do header (trigger_change_info)

    Ao realizar uma operação de mapa de ff, trigger_compute_fatmaps chama o método compute_fatmaps que pertence ao
    ao objeto current_fatmaps que havia sido instanciado (então é a outra classe que faz a operação)
    lá na classe, vemos que o método chama outros internos e etc, mas é simples. No final, é possível ter mais de um
    mapa, completo ou parcial ao mesmo tempo. Para mudar a visualização, basta mudar a escolha no comboBox (que ativa
    trigger_change_fatmap). Foi implementado também a função mouseMoved para mostrar a intensidade do pixel do mapa que
    o mouse está apontando.

    Faltando apenas ajustar o gerenciamento de ROIs e finalizar com a exportação no formato DICOM.

'''

import sys;

# import numpy as np;
# PyQt Modules
from PyQt5 import QtWidgets

# Project Modules
import modules.gui.qt_mainwindow
# from modules.data.current_file import DicomFile as dcm, FatMaps as fmp, RegOfInterest as ROI
from modules.data.DicomFile import DicomFile as dcm
from modules.data.FatMaps import FatMaps as fmp
from modules.data.ParRecFile import PARRECfile as parrec
from modules.data.RegOfInterest import RegOfInterest as ROI
from modules.io import dicom_opener as dcmop, parrec_opener as parrecop, export



# > https://stackoverflow.com/questions/36399381/whats-the-fastest-way-of-checking-if-a-point-is-inside-a-polygon-in-python
# from shapely.geometry import Point;
# from shapely.geometry.polygon import Polygon;

class MainWindowManager(modules.gui.qt_mainwindow.Ui_MainWindow):

    # SETUP
    ################################################

    def __init__(self, show = True):
        """
        Description: definition and initialization of self variables.
        """
        # > super Init
        self.app_window = QtWidgets.QMainWindow()
        super(MainWindowManager, self).__init__()

        # > Class elements definition
        self.current_File = None
        self.current_fatmaps = None
        self.rois = []

        # > UI Management
        self.setupUi(self.app_window)  # > Inserts all the window elements
        self.ui_init()
        self.set_events()

        # > Visual Output
        if(show):
            self.show()
        return

    def ui_init(self):
        """
        Description: Defines the initial values from each UI element on
        program startup.
        """

        #> Component Definiton
        self.spb_slice.setMaximum(1)
        self.spb_echo.setMaximum(1)
        self.sld_slice.setMaximum(1)
        self.sld_echo.setMaximum(1)
        self.spb_slice.setMinimum(1)
        self.spb_echo.setMinimum(1)
        self.sld_slice.setMinimum(1)
        self.sld_echo.setMinimum(1)
        self.cbx_methods.addItems(["Dixon", "Triple", "Multi", "ANN50", "ANN100"])
        self.btn_cfatmap.setEnabled(False)
        self.act_rectangle.setEnabled(False)
        self.act_ellipse.setEnabled(False)
        self.act_polygon.setEnabled(False)
        self.act_ROI_done.setEnabled(False)
        self.act_ROI_cancel.setEnabled(False)
        self.actionExport.setEnabled(False)

        # # > Graphs Vizualization
        # self.pcv_img = self.qlb_img # > Legacy Name
        # self.pcv_fatmap = self.qlb_fatmap # > Legacy Name
        # self.pcv_signal = self.qlb_signal # > Legacy Name

        # > Global PyQtGraph Config
        #pyqtgraph.setConfigOptions(imageAxisOrder='row-major')
        #pyqtgraph.setConfigOptions(imageAxisOrder='col-major')
        self.pcv_img.setPredefinedGradient('grey')
        self.pcv_fatmap.setPredefinedGradient('yellowy')
        self.pcv_img.ui.roiBtn.hide()
        self.pcv_img.ui.menuBtn.hide()
        self.pcv_fatmap.ui.roiBtn.hide()
        self.pcv_fatmap.ui.menuBtn.hide()
        return


    def set_events(self):
        """
        Description: assigns methods to signals from UI elements.
        """
        self.act_open_single.triggered.connect(self.trigger_load_single_dicom)
        self.act_open_multiple.triggered.connect(self.trigger_load_multiple_dicom)
        self.act_open_parrec.triggered.connect(self.trigger_load_parrec)
        self.spb_slice.valueChanged.connect(self.trigger_change_slice_img)  # 0 for slice change
        self.spb_echo.valueChanged.connect(self.trigger_change_slice_img)  # 1 for echo change
        self.btn_cfatmap.clicked.connect(self.trigger_compute_fatmaps)
        self.radio_summary_header.toggled.connect(self.trigger_change_info)
        self.cbx_methods.currentIndexChanged.connect(self.trigger_change_fatmap)
        self.pcv_fatmap.scene.sigMouseMoved.connect(self.mouseMovedFat)
        self.pcv_img.scene.sigMouseMoved.connect(self.mouseMovedImg)
        self.cbox_rois.currentIndexChanged.connect(self.trigger_change_ROI_info)
        self.btn_roi_delete.clicked.connect(self.trigger_delete_ROI)
        self.btn_export.clicked.connect(self.trigger_export)

        self.act_rectangle.triggered.connect(self.trigger_roi_started)
        self.act_ellipse.triggered.connect(self.trigger_roi_started)
        self.act_polygon.triggered.connect(self.trigger_roi_started)
        self.act_ROI_done.triggered.connect(self.trigger_roi_done)
        self.act_ROI_cancel.triggered.connect(self.trigger_roi_cancelled)


        return

    def show(self):
        self.app_window.show()
        return

    ################################################

    # METHODS CALLED BY TRIGGERS
    ################################################





    def update_dicom_img(self, img_list):
        """
            Called by trigger_load_single_dicom() and trigger_load_multiple_dicom().
        """
        self.spb_echo.setMaximum(img_list.shape[1])
        self.sld_echo.setMaximum(img_list.shape[1])
        self.spb_slice.setMaximum(len(img_list))
        self.sld_slice.setMaximum(len(img_list))
        self.btn_cfatmap.setEnabled(True)
        self.act_rectangle.setEnabled(True)
        self.act_ellipse.setEnabled(True)
        self.act_polygon.setEnabled(True)
        for roi in self.rois:
            self.pcv_img.removeItem(roi.specs)
        self.rois = []
        self.pcv_img.clear()
        self.pcv_signal.clear()
        self.pcv_fatmap.clear()
        self.cbox_rois.clear()
        self.cbx_methods.clear()

        self.trigger_change_slice_img()
        self.trigger_change_fatmap()
        self.trigger_change_info()

        if img_list.shape[1] < 3:
            self.cbx_methods.addItems(["Dixon"])
        else:
            self.cbx_methods.addItems(["Dixon", "Triple", "Multi"])
        if img_list.shape[1] == 7:
            self.cbx_methods.addItems(["ANN50", "ANN100"])
        return



    ################################################

    # TRIGGER METHODS
    ################################################

    def trigger_load_single_dicom(self):
        """
            Triggered by act_open_single.triggered .
        """
        file_path = dcmop.browse_single_dicom(self.app_window)
        if(file_path != None):
            self.current_File = None
            self.current_File = dcm(dcmop.load_single(file_path)[0], dcmop.load_single(file_path)[1]) #header, image array
            dim = (self.current_File.img_list.shape[0], self.current_File.img_list.shape[2], self.current_File.img_list.shape[3])
            self.current_fatmaps = fmp(dim)
            if len(self.current_File.img_list) > 0:
                self.update_dicom_img(self.current_File.img_list)
        return

    def trigger_load_multiple_dicom(self):
        """
            Triggered by act_open_multiple.triggered .
        """
        dir_path = dcmop.browse_dir_dicom(self.app_window)
        if(dir_path != None):
            self.current_File = None
            self.current_File = dcm(dcmop.load_multiple(dir_path)[0], dcmop.load_multiple(dir_path)[1])
            dim = (self.current_File.img_list.shape[0], self.current_File.img_list.shape[2],
                   self.current_File.img_list.shape[3])
            self.current_fatmaps = fmp(dim)
            if len(self.current_File.img_list) > 0:
                self.update_dicom_img(self.current_File.img_list)
        return

    def trigger_load_parrec(self):
        """
            Triggered by act_open_parrec.triggered .
        """
        file_path = parrecop.browse_file_parrec(self.app_window)
        if(file_path != None):
            self.current_File = None
            # build object with returns from open, which are header, img_list
            self.current_File = parrec(parrecop.load_parrec(file_path)[0], parrecop.load_parrec(file_path)[1])
            #### check below ###
            dim = (self.current_File.img_list.shape[0], self.current_File.img_list.shape[2],
                   self.current_File.img_list.shape[3])
            self.current_fatmaps = fmp(dim)
            if len(self.current_File.img_list) > 0:
                self.update_dicom_img(self.current_File.img_list)
        return

    def trigger_change_info(self):
        """
            Triggered by radio_summary_header.toggled()
        :return:
        """
        if self.current_File.header_summary != None:
            if self.radio_summary_header.isChecked():
                self.textedit_header.clear()
                for row, key in enumerate(self.current_File.header_summary):
                    self.textedit_header.append(key +': ' + str(self.current_File.header_summary[key]) + '\n')
            else:
                self.textedit_header.clear()
                self.textedit_header.append(str(self.current_File.header['header_file']))
        else:
            pass

    def trigger_change_slice_img(self):
        """
            Triggered by spb_slice.valueChanged
            Triggered by spb_echo.valueChanged
            Called by update_dicom_img
            Called by trigger_compute_fatmaps
        """
        slice_val = self.spb_slice.value() - 1
        echo_val = self.spb_echo.value() - 1
        slices_nb = len(self.current_File.img_list)
        if slice_val < slices_nb:
            current_img = self.current_File.img_list[slice_val, echo_val]
            self.pcv_img.setImage(current_img.T, autoRange=False)

            self.trigger_change_fatmap()
            if self.rois:  # check if there is something in the list (i.e. not empty)
                for roi in self.rois: #for each roi
                    if roi.slice_idx != slice_val and roi.visibility is True or roi.deleted is True:
                        self.pcv_img.removeItem(roi.specs)
                        roi.visibility = False
                    elif roi.slice_idx == slice_val and roi.visibility is False and roi.deleted is False:
                        self.pcv_img.addItem(roi.specs)
                        roi.visibility = True
        return

    def trigger_compute_fatmaps(self):
        """
            Triggered by btn_cfatmap.clicked.
        """
        self.current_fatmaps.compute_fatmaps(self.current_File.header, self.current_File.img_list,
                                          self.cbx_methods.currentText(), self.check_current_slice.isChecked(), self.spb_slice.value())
        #args = header, images, method, state of current slice button, spb slice value

        self.pcv_fatmap.getView().setXLink(self.pcv_img.view)
        self.pcv_fatmap.getView().setYLink(self.pcv_img.view)
        self.trigger_change_fatmap()
        self.trigger_change_slice_img()

        # connect zoom of both windows
        return

    def trigger_change_fatmap(self):
        """
            Triggered by cbx_methods.currentIndexChanged.
        """
        method = self.cbx_methods.currentText()

        if method == 'Dixon':
            ffmap = self.current_fatmaps.map_dixon

        elif method == 'Triple':
            ffmap = self.current_fatmaps.map_triple

        elif method == 'Multi':
            ffmap = self.current_fatmaps.map_multi

        elif method == 'ANN50':
            ffmap = self.current_fatmaps.map_ann50

        elif method == 'ANN100':
            ffmap = self.current_fatmaps.map_ann100
        else:   #para inicialização
            ffmap = self.current_fatmaps.map_dixon

        slice_val = self.spb_slice.value() - 1
        if self.spb_slice.value() < len(ffmap):
            ffmap_show = ffmap[slice_val, :, :]
            self.pcv_fatmap.setImage(ffmap_show.T, levels=(0, 1), autoRange=False)  # it must be transposed

        return

    def trigger_roi_started(self):
        """
            Triggered by act_rectangle, act_ellipse, act_polygon
        """
        self.act_rectangle.setEnabled(False)
        self.act_ellipse.setEnabled(False)
        self.act_polygon.setEnabled(False) #do not create more than one ROI at the same time
        self.act_ROI_done.setEnabled(True)
        self.act_ROI_cancel.setEnabled(True)

        rect = self.pcv_img.getImageItem().viewRect()
        view_pos = self.pcv_img.getImageItem().mapFromScene(rect)
        center_pos = view_pos.boundingRect().center()
        type = self.app_window.sender().text()
        number = len(self.rois)
        roi = ROI(type, number, center_pos)
        self.rois.append(roi)
        self.pcv_img.addItem(roi.specs)
        return

    def trigger_roi_done(self):
        """
            Triggered by act_ROI_done.
        """
        self.act_rectangle.setEnabled(True)
        self.act_ellipse.setEnabled(True)
        self.act_polygon.setEnabled(True)
        self.act_ROI_done.setEnabled(False)
        self.act_ROI_cancel.setEnabled(False)

        slice_index = self.spb_slice.value() - 1
        self.rois[len(self.rois)-1].set_roi_id(slice_index) #update slice index after finished drawing
        self.rois[len(self.rois)-1].get_roi_points(self.current_File.img_list, self.pcv_img) #get signal from ROI
        self.pcv_signal.plot(self.current_File.header['list_TE'], self.rois[len(self.rois) - 1].list_SI,
                             pen=self.rois[len(self.rois) - 1].pen)  # plot signal
        self.rois[len(self.rois) - 1].calculate_results(self.current_File.header) #calculate results
        self.cbox_rois.addItem(self.rois[len(self.rois)-1].name) #adds new roi to combo box
        self.cbox_rois.setCurrentIndex(len(self.rois)-1) #changes current roi in combo box to new one
        self.trigger_change_ROI_info()
        return

    def trigger_change_ROI_info(self):
        """
            Triggered by roi_done and cbox_roi changed
        :return:
        """
        # print results to text area - may code as another method
        self.textEdit_roi.clear()
        if self.rois:
            self.textEdit_roi.clear()
            self.textEdit_roi.append('Fat fraction analysis of the selected region of interest:' + '\n')
            self.textEdit_roi.append('-----------------------------' + '\n')
            for key in self.rois[self.cbox_rois.currentIndex()].results:
                self.textEdit_roi.append(key + ' : ' + str(self.rois[self.cbox_rois.currentIndex()].results[key]*100)+'%' + '\n')

        return

    def trigger_roi_cancelled(self):
        self.act_rectangle.setEnabled(True)
        self.act_ellipse.setEnabled(True)
        self.act_polygon.setEnabled(True)
        self.act_ROI_done.setEnabled(False)
        self.act_ROI_cancel.setEnabled(False)

        self.pcv_img.removeItem(self.rois[len(self.rois)-1].specs)
        self.rois = self.rois[0:len(self.rois)-1]
        return

    def trigger_delete_ROI(self):
        if self.rois:
            self.rois[self.cbox_rois.currentIndex()].deleted = True
            self.pcv_img.removeItem(self.rois[self.cbox_rois.currentIndex()].specs)
            self.rois.pop(self.cbox_rois.currentIndex())
            self.cbox_rois.clear()
            self.pcv_signal.clear()
            for idx, roi in enumerate(self.rois):
                self.cbox_rois.addItem(self.rois[idx].name)
                self.pcv_signal.plot(self.current_File.header['list_TE'], self.rois[idx].list_SI,
                                     pen=self.rois[idx].pen)  # re-plot signals
            self.cbox_rois.setCurrentIndex(0)
        return

    def mouseMovedFat(self, evt):
        if self.current_fatmaps is not None:
            data = self.pcv_fatmap.image #get image matrix
            nRows, nCols = data.shape   #get original dimensions
            scenePos = self.pcv_fatmap.getImageItem().mapFromScene(evt)
            col, row = int(scenePos.x()), int(scenePos.y())
            if (0 <= row < nRows) and (0 <= col < nCols):
                value = data[col, row]
                QtWidgets.QToolTip.showText(self.pcv_fatmap.mapToGlobal(evt.toPoint()), str(value)
                                            + ' ('+str(col)+', '+str(row)+')')
            else:
                pass
        else:
            pass

    def mouseMovedImg(self, evt):
        if self.current_fatmaps is not None:
            data = self.pcv_img.image #get image matrix
            nRows, nCols = data.shape   #get original dimensions
            scenePos = self.pcv_img.getImageItem().mapFromScene(evt)
            col, row = int(scenePos.x()), int(scenePos.y())
            if (0 <= row < nRows) and (0 <= col < nCols):
                value = data[col, row]
                QtWidgets.QToolTip.showText(self.pcv_img.mapToGlobal(evt.toPoint()), str(value)
                                            + ' ('+str(col)+', '+str(row)+')')
            else:
                pass
        else:
            pass

    def trigger_export(self):
        if self.check_export_csv.isChecked():
            if self.rois:
                export.export_csv(self.current_File.header_summary["Patient ID"],
                                  self.current_File.header['voxel_size_mm'],
                                  self.rois, self.check_include_csv_hdr.isChecked()) #patient ID, ROI list, include csv header

#,





################################################
# MAIN FLOW
################################################

def start():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindowManager()
    app.exec_()
    return

################################################
