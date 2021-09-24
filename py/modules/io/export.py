import csv
import os.path

#todo incluir patient e roi id, mudar nome do arquivo (teste.csv)
def export_csv(patient_id, voxel_size, rois, include_csv_hdr):
    path_to_py = os.path.abspath(os.path.join(__file__, '../..')) #go to ../py
    path = os.path.join(path_to_py, '../csv_files/')  # go to py/csv_files
    filename = str(patient_id)
    csv_header = ["Patient ID", "ROI ID", "Area (mm2)"]
    print(csv_header)
    csv_header.extend(list(rois[0].results.keys()))
    csv_header.append("Average signal in each echo")
    csv_results = []
    for idx, roi in enumerate(rois):
        csv_res = []
        csv_res.append(patient_id)
        csv_res.append(rois[idx].name)
        csv_res.append(rois[idx].area_px*voxel_size[0]*voxel_size[1])
        print(csv_res)
        for item in list(rois[idx].results.values()):
            csv_res.append(str(item))
        for item in rois[idx].list_SI:
            csv_res.append(str(item))
        csv_results.append(csv_res)

    print(csv_header)
    print(csv_results)
    with open(path + filename + '.csv', 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        if include_csv_hdr:  # if checked TRUE
            wr.writerow(csv_header)
        wr.writerows(csv_results)

    print('file saved.')
    return
