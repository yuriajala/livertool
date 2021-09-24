import datetime
import numpy as np
from modules.ff import dixon, multi, triple, ann50, ann100

class FatMaps ():

    def __init__(self, dim): #dim = (nb_slices, nb_rows, nb_columns)

        self.map_dixon = np.zeros(dim)
        self.map_triple = np.zeros(dim)
        self.map_multi = np.zeros(dim)
        self.map_ann50 = np.zeros(dim)
        self.map_ann100 = np.zeros(dim)

        # > Methods parameters - cut air values
        self.air_thresh = 50



    def compute_fatmaps(self, dicom_header, images_list, method, only_current_slice, spb_slice):
        """
            Called by trigger_compute_fatmaps().
        """
        print(spb_slice)

        model = None
        model_path = None

        # teste de tempo para calcular um corte
        currentDT = datetime.datetime.now()
        print(str(currentDT))

        if(method == 'Dixon'):
            func = dixon
            self.map_dixon = self.check_and_run(self.map_dixon, dicom_header, model, model_path, images_list, func,
                                                only_current_slice, spb_slice)
        elif(method == 'Triple'):
            func = triple
            self.map_triple = self.check_and_run(self.map_triple, dicom_header, model, model_path, images_list, func,
                                                only_current_slice, spb_slice)
        elif(method == 'Multi'):
            func = multi
            self.map_multi = self.check_and_run(self.map_multi, dicom_header, model, model_path, images_list, func,
                                                only_current_slice, spb_slice)
        elif (method == 'ANN50'):
            model, model_path = ann50.initialize()
            func = ann50
            self.map_ann50 = self.check_and_run(self.map_ann50, dicom_header, model, model_path, images_list, func,
                                                 only_current_slice, spb_slice)
        elif (method == 'ANN100'):
            model, model_path = ann100.initialize()
            func = ann100
            self.map_ann100 = self.check_and_run(self.map_ann100, dicom_header, model, model_path, images_list, func,
                                                 only_current_slice, spb_slice)
        else:
            return


    def check_and_run(self, fatmap, dicom_header, model, model_path, images_list, func, only_current_slice, spb_slice):

        echo_times = dicom_header['list_TE']
        imaging_frequency = dicom_header['imaging_frequency']
        if only_current_slice:    #if checked runs only current slice
            im_slice = images_list[spb_slice - 1, :, :]
            fatmap[spb_slice - 1, :, :] = self.run_fatmap(images_list.shape, im_slice, func, echo_times, imaging_frequency, model, model_path)
        else:
            full_map = []
            # with pyqtgraph.ProgressDialog("Processing...", 0, len(images_list)) as dlg:
            for im_slice in images_list:
                full_map.append(self.run_fatmap(images_list.shape, im_slice, func, echo_times, imaging_frequency, model, model_path))
                fatmap = np.array(full_map)


        #teste de tempo
        currentDT = datetime.datetime.now()
        print(str(currentDT))
        return fatmap

    def run_fatmap(self, im_list_dims, im_slice, func, echo_times, imaging_frequency, model, model_path):

        print('running image')
        single_map = np.zeros((im_list_dims[2], im_list_dims[3]));
        for row in range(im_list_dims[2]):
            #print('calculating row ', row, im_list_dims[2])
            for col in range(im_list_dims[3]):
                p_list = im_slice[:, row, col];
                if p_list[0] >= self.air_thresh:
                    if func == ann50:
                        val = func.compute(p_list, model, model_path)
                    elif func == ann100:
                        val = func.compute(p_list, model, model_path)
                    else:
                        val = func.compute(p_list, 0.001 * echo_times, imaging_frequency)
                    single_map[row, col] = val
        return single_map
