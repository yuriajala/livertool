import numpy as np
from nibabel import parrec as prc
import matplotlib.pyplot as plt
import datetime
import tensorflow as tf

subject = prc.PARRECImage.load('C:/Users/Yuri/Documentos/M2/Datasets/parrec/PAC001_7_ECOS.PAR')
raw_images_list = subject.dataobj
nb_slices = subject.header.general_info['max_slices']
nb_echoes = subject.header.general_info['max_echoes']
nb_rows = subject.shape[0]
nb_columns = subject.shape[1]
images_list = np.zeros((nb_slices, nb_echoes, nb_rows, nb_columns))
print(images_list.shape)
# OPERAÇÃO LENTA!!!!
#ideal: images_list = np.reshape(np.array(raw_images_list), (nb_slices, nb_echoes, nb_rows, nb_columns))
# NAO FUNCIONA PQ???????????
for sl in range(0,nb_slices):
    for ec in range(0,nb_echoes):
        images_list[sl,ec,:,:] = raw_images_list[:,:,sl,ec]

plt.imshow(raw_images_list[:,:,0,0].T)
plt.show()
plt.imshow(images_list[0,0,:,:].T)
plt.show()


patient_name = subject.header.general_info['patient_name']
repetition_time = subject.header.general_info['repetition_time']
flip_angle = subject.header.image_defs[0][29]
echo_times = np.zeros(nb_echoes)
for n in range(0, nb_echoes):
    echo_times[n] = subject.header.image_defs[n][24]
half_period = (echo_times[1] - echo_times[0]) * 0.001
ppm = 3.4e-6
hydroGyro = np.array(42.577e6)  # Hydrogen gyromagnetic ratio, Hz/T
imaging_frequency = 1/(2 * half_period * ppm)
magnetic_field = np.round(imaging_frequency/hydroGyro, 2)
slice_thickness = subject.header.image_defs[0][17]
slice_dimensions = subject.header.image_defs[0][23]
voxel_size = [slice_dimensions[0], slice_dimensions[1], slice_thickness]
water_chem_shift = 4.68
header_file = subject.header.__dict__
header = {
    "patient_name": subject.header.general_info['patient_name'],
    "magnetic_field": magnetic_field,
    "list_TE": echo_times,
    "repetition_time": repetition_time,
    "flip_angle": flip_angle,
    "image_dimensions_px": np.array([nb_rows, nb_columns]),
    "voxel_size_mm": voxel_size,
    "water_chem_shift": water_chem_shift,
    "imaging_frequency": imaging_frequency,
    "header_file": subject
}





#
#
# nb_frames = len(subject);
# nb_echoes = subject[0][0x018, 0x091].value;
# nb_slices = int(nb_frames / nb_echoes);
# nb_rows = subject[0][0x028, 0x010].value;
# nb_columns = subject[0][0x028, 0x011].value;
# # prepare 4D image matrix [slice, echo, rows, columns];
# images_list = np.reshape(np.array(raw_images_list), (nb_slices, nb_echoes, nb_rows, nb_columns));
# # get more header information to build header dictionary
# patient_name = subject[0][0x10, 0x10].value
# magnetic_field = subject[0][0x018, 0x087].value
# # list of time to echo values
# echo_times = np.zeros(nb_echoes)
# for n in range(0, nb_echoes):
#     echo_times[n] = subject[n][0x018, 0x081].value
# rep_time = subject[0][0x018, 0x080].value
# flip_angle = subject[0][0x018, 0x1314].value
# pixel_spacing = subject[0][0x028, 0x030].value
# slice_thickness = subject[0][0x18, 0x050].value
# voxel_size = np.array([pixel_spacing[0], pixel_spacing[1], slice_thickness])
# water_chem_shift = subject[0][0x2005, 0x140f][0][0x0018, 0x9053].value
# imaging_frequency = subject[0][0x018, 0x084].value
# # build header
# header = {
#     "patient_name": patient_name,
#     "magnetic_field": magnetic_field,
#     "list_TE": echo_times,
#     "repetition_time": rep_time,
#     "flip_angle": flip_angle,
#     "image_dimensions_px": np.array([nb_rows, nb_columns]),
#     "voxel_size_mm": voxel_size,
#     "water_chem_shift": water_chem_shift,
#     "imaging_frequency": imaging_frequency,
#     "path": dir_path,
#     "header_file": subject
# }
#
# #return header, images_list;