import numpy as np
#import cv2;
import glob
import os
import pydicom
from PyQt5.QtWidgets import QFileDialog, QMainWindow

def browse_single_dicom(app_window):
    file_dialog = QFileDialog(app_window)
    file_dialog.setNameFilter("DICOM Images (*.dcm)")
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_path = None
    if (file_dialog.exec()):
        selected = file_dialog.selectedFiles()
        if (len(selected) > 0):
            file_path = selected[0]

    return file_path

def browse_dir_dicom(app_window):
    file_dialog = QFileDialog(app_window)
    #file_dialog.setFileMode(QFileDialog.Directory);
    file_dialog.setFileMode(QFileDialog.DirectoryOnly)
    file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    file_dialog.setOption(QFileDialog.ShowDirsOnly, False)

    dir_path = None
    if (file_dialog.exec()):
        selected = file_dialog.selectedFiles()
        if (len(selected) > 0):
            dir_path = selected[0]
    return dir_path

def load_multiple(dir_path):
    subject = []
    raw_images_list = []
    os.chdir(dir_path)
    files_list = glob.glob('*.dcm')
    files_list.sort()
    for file_path in files_list:
        subject.append(pydicom.read_file(file_path))
    for img in range(len(subject)):
        raw_images_list.append(subject[img].pixel_array)
    #print(subject[0])
    nb_frames = len(subject)
    nb_echoes = subject[0][0x018, 0x091].value
    nb_slices = int(nb_frames / nb_echoes)
    nb_rows = subject[0][0x028, 0x010].value
    nb_columns = subject[0][0x028, 0x011].value
    # prepare 4D image matrix [slice, echo, rows, columns];
    images_list = np.reshape(np.array(raw_images_list), (nb_slices, nb_echoes, nb_rows, nb_columns))
    # get more header information to build header dictionary
    patient_name = subject[0][0x10, 0x10].value
    magnetic_field = subject[0][0x018, 0x087].value
    # list of time to echo values
    echo_times = np.zeros(nb_echoes)
    for n in range(0, nb_echoes):
        echo_times[n] = subject[n][0x018, 0x081].value
    rep_time = subject[0][0x018, 0x080].value
    flip_angle = subject[0][0x018, 0x1314].value
    pixel_spacing = subject[0][0x028, 0x030].value
    slice_thickness = subject[0][0x18, 0x050].value
    voxel_size = np.array([pixel_spacing[0], pixel_spacing[1], slice_thickness])
    water_chem_shift = subject[0][0x2005, 0x140f][0][0x0018, 0x9053].value
    imaging_frequency = subject[0][0x018, 0x084].value
    # build header
    header = {
        "patient_name": patient_name,
        "magnetic_field": magnetic_field,
        "list_TE": echo_times,
        "repetition_time": rep_time,
        "flip_angle": flip_angle,
        "image_dimensions_px": np.array([nb_rows, nb_columns]),
        "voxel_size_mm": voxel_size,
        "water_chem_shift": water_chem_shift,
        "imaging_frequency": imaging_frequency,
        "path": dir_path,
        "header_file": subject
    }
    return header, images_list;


def load_single(file_path):
    subject = pydicom.read_file(file_path);
    # initialization
    raw_images_list = subject.pixel_array;
    nb_frames = subject[0x028, 0x008].value;
    nb_echoes = subject[0x5200, 0x9229][0][0x18, 0x9112][0][0x18, 0x91].value;
    nb_slices = int(nb_frames / nb_echoes);
    nb_rows = subject[0x028, 0x010].value;
    nb_columns = subject[0x028, 0x011].value;
    # prepare 4D image matrix [slice, echo, rows, columns];
    images_list = np.reshape(raw_images_list, (nb_slices, nb_echoes, nb_rows, nb_columns));
    # get more header information to build header dictionary
    patient_name = subject[0x10, 0x10].value
    magnetic_field = subject[0x018, 0x087].value
    # list of time to echo values
    echo_times = np.zeros(nb_echoes)
    for n in range(nb_echoes):
        echo_times[n] = subject[0x5200, 0x9230][n][0x2005, 0x140f][0][0x018, 0x081].value
    rep_time = subject[0x5200, 0x9229][0][0x0018, 0x9112][0][0x018, 0x080].value
    flip_angle = subject[0x5200, 0x9229][0][0x18, 0x9112][0][0x18, 0x1314].value
    pixel_spacing = subject[0x5200, 0x9230][0][0x028, 0x9110][0][0x028, 0x030].value
    slice_thickness = subject[0x5200, 0x9230][0][0x028, 0x9110][0][0x018, 0x050].value
    voxel_size = np.array([pixel_spacing[0], pixel_spacing[1], slice_thickness])
    water_chem_shift = subject[0x0018, 0x9053].value
    imaging_frequency = subject[0x5200, 0x9229][0][0x018, 0x9006][0][0x0018, 0x9098].value
    # build header
    header = {
        "patient_name": patient_name,
        "magnetic_field": magnetic_field,
        "list_TE": echo_times,
        "repetition_time": rep_time,
        "flip_angle": flip_angle,
        "image_dimensions_px": np.array([nb_rows, nb_columns]),
        "voxel_size_mm": voxel_size,
        "water_chem_shift": water_chem_shift,
        "imaging_frequency": imaging_frequency,
        "path": file_path,
        "header_file": subject
    }
    return header, images_list