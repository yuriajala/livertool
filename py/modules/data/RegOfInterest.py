import numpy as np
from modules.ff import dixon, multi, triple, ann50, ann100
import pyqtgraph

class RegOfInterest ():

    def __init__(self, type, n, center_pos):
        self.slice_idx = None  # matrix, starting zero
        self.roi_number = n + 1
        self.name = None
        self.list_SI = None
        self.results = None
        self.visibility = None
        self.plot = []
        self.deleted = False
        self.center_pos = None
        self.type = type
        self.area_px = None

        color_table = ['r', 'g', 'b', 'c', 'm', 'y']
        idx_color = n % 6 #remainder of division
        self.pen = color_table[idx_color]
        self.type = type
        if (type == "Rectangle"):
            self.specs = pyqtgraph.RectROI(center_pos, [15, 15], pen=self.pen)
        elif (type == "Ellipse"):
            self.specs = pyqtgraph.EllipseROI(center_pos, [15, 15], pen=self.pen)
        elif (type == "Polygon"):
            self.specs = pyqtgraph.PolyLineROI([center_pos, [center_pos.x()+15, center_pos.y()],
                                                [center_pos.x(), center_pos.y()+15]], pen=self.pen, closed=True)

    def set_roi_id(self, slice_idx):
        self.slice_idx = slice_idx
        self.name = "ROI " + str(self.roi_number) + ", Slice " + str(self.slice_idx + 1)
        self.visibility = True
        # lock it in position:
        self.specs.translatable = False
        self.specs.rotateAllowed = False

        handles = [h for h in self.specs.getHandles()]
        if self.type != 'Polygon':
            for idx, hdl in enumerate(handles):
                self.specs.removeHandle(hdl)
                #missing polygons
        return

    def get_roi_points(self, images_list, pcv_img):
        """
            Triggered by act_ROI_done.
        """

        nb_slices, nb_echos, n_rows, n_cols = images_list.shape
        img_slice = np.copy(images_list[self.slice_idx]) + 1.0
        SI_avg = np.zeros(nb_echos)
        for echo_index in range(nb_echos):
            img = img_slice[echo_index]
            region = self.specs.getArrayRegion(np.array(img), pcv_img.getImageItem(), axes=(1,0)) #get ROI, "axes" transposes the img
            region_valid = [SI for SI in region.flatten() if SI != 0] #eliminate zeros
            SI_avg[echo_index] = np.average(region_valid) #calculate average
            self.area_px = len(region_valid)
        self.list_SI = SI_avg
        print(self.area_px)
        return

    def calculate_results(self, header, model=None, model_path=None):
        functions = [dixon, triple, multi]
        results_list = []
        methods = ["Dixon", "Triple", "Multi", "ANN50", "ANN100"]
        if len(self.list_SI) < 3:
            results_list = dixon.compute(self.list_SI, 0.001 * header['list_TE'], header['imaging_frequency'])
            self.results = {"Dixon": results_list}
        else:
            for func in functions:
                results_list.append(func.compute(self.list_SI, 0.001 * header['list_TE'], header['imaging_frequency']))
                self.results = dict(zip(methods, results_list))
        if len(self.list_SI) == 7:
            model, model_path = ann50.initialize()
            results_list.append(ann50.compute(self.list_SI, model, model_path)[0][0])
            model, model_path = ann100.initialize()
            results_list.append(ann100.compute(self.list_SI, model, model_path)[0][0])
            self.results = dict(zip(methods, results_list))
        print(self.results)
        return

    def toggle_visibility(self):
        self.visibility = not self.visibility
        return
    def delete_ROI (self):
        #performed by window manager
        return
    def select_ROI (self):
        #not implemented yet
        return
    def cancel_new_roi(self):
        #performed by window manager
        return
