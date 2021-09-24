class PARRECfile:
    '''
    self.header contains:
        header = {
            "patient_name": patient_name,
            "patient_ID": patient_id
            "magnetic_field": magnetic_field,
            "list_TE": echo_times,
            "repetition_time": rep_time,
            "flip_angle": flip_angle,
            "image_dimensions_px": np.array([nb_rows, nb_columns]),
            "voxel_size_mm": voxel_size,
            "water_chem_shift": water_chem_shift,
            "imaging_frequency": imaging_frequency,
            "header_file": subject
        }
    '''

    def __init__(self, header, img_list):
        self.header = header
        self.img_list = img_list  #slice, echo, row, column
        id_localizer = self.header['path'].lower().find('pac') #make it all lowercase then look for "pac"
        if id_localizer != -1: #if finds "subj"
            patient_id = self.header['path'][id_localizer:id_localizer+6] #writes PAC+ next three digits
        else:
            patient_id = -1
        self.header_summary = {"Patient name": str(self.header['patient_name']),
                               "Patient ID": str(patient_id),
                       "Magnetic field (T)": str(self.header['magnetic_field']),
                       "Echo times (ms)": str(self.header['list_TE']),
                       "Repetition time (ms)": str(self.header['repetition_time']),
                       "Flip angle (deg)": str(self.header['flip_angle']),
                       "Image dimensions (px)": str(self.header['image_dimensions_px']),
                       "Voxel size (mm)": str(self.header['voxel_size_mm'])}
