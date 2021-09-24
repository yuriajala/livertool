import numpy as np
from PyQt5.QtWidgets import QFileDialog
from nibabel import parrec as prc
import matplotlib.pyplot as plt

def browse_file_parrec(app_window):
    file_dialog = QFileDialog(app_window)
    file_dialog.setNameFilter("PAR/REC files (*.PAR *.REC)")
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_path = None
    if (file_dialog.exec()):
        selected = file_dialog.selectedFiles()
        if (len(selected) > 0):
            file_path = selected[0]

    return file_path

def normalize(signal):

    return signal / np.linalg.norm(signal)

def load_parrec(file_path):
    subject = prc.PARRECImage.load(file_path)
    raw_images_list = subject.dataobj  # original shape: (nb_columns, nb_rows, nb_slices, nb_echoes)
    
    #data_scaling_slope, data_scaling_intercept = subject.header.get_data_scaling(method='dv') # scale factor
    #print(data_scaling_slope)
    #print()
    #print(data_scaling_intercept)
    
    nb_slices = subject.header.general_info['max_slices']
    nb_echoes = subject.header.general_info['max_echoes']
    nb_rows = subject.shape[1]
    nb_columns = subject.shape[0]
    images_list = np.transpose(np.array(raw_images_list), (2, 3, 1, 0))  # (nb_slices, nb_echoes, nb_rows, nb_columns)
    
    #images_list = images_list*data_scaling_slope[0,0,0,0] # image reescaled by the scale factor
    images_list = normalize(images_list) # normalizing the signal
    
    patient_name = subject.header.general_info['patient_name']
    repetition_time = subject.header.general_info['repetition_time']
    flip_angle = subject.header.image_defs[0][29]
    echo_times = np.zeros(nb_echoes)
    for n in range(0, nb_echoes):
        echo_times[n] = subject.header.image_defs[n][24]
    half_period = (echo_times[1] - echo_times[0]) * 0.001
    ppm = 3.4e-6
    hydroGyro = np.array(42.577e6)  # Hydrogen gyromagnetic ratio, Hz/T
    imaging_frequency = 1 / (2 * half_period * ppm)
    magnetic_field = np.round(imaging_frequency / hydroGyro, 2)
    slice_thickness = subject.header.image_defs[0][17]
    slice_dimensions = subject.header.image_defs[0][23]
    voxel_size = [slice_dimensions[0], slice_dimensions[1], slice_thickness]
    water_chem_shift = 4.68
    header_file = subject.header.__dict__
    header = {
        "patient_name": patient_name,
        "magnetic_field": magnetic_field,
        "list_TE": echo_times,
        "repetition_time": repetition_time,
        "flip_angle": flip_angle,
        "image_dimensions_px": np.array([nb_rows, nb_columns]),
        "voxel_size_mm": voxel_size,
        "water_chem_shift": water_chem_shift,
        "imaging_frequency": imaging_frequency,
        "path": file_path,
        "header_file": header_file
    }
    
    return header, images_list
