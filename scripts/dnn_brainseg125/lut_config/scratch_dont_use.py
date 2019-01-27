
if 0 == 1:
  def generate_compact_numbering(found_label_map_values):
      # num_lbls=len(found_label_map_values)
      lbl_mapping=dict()
      for new_lbl in range(0,len(found_label_map_values)):
          old_lbl = found_label_map_values[new_lbl]
          lbl_mapping[new_lbl] = old_lbl
      return lbl_mapping

  GLBL_COMPACT_TO_BAW_MAPPING=generate_compact_numbering(GLBL_FOUND_LBL_VALUES)

  GLBL_BAW_TO_COMPACT_MAPPING=dict()
  for k,v in GLBL_COMPACT_TO_BAW_MAPPING.items():
      GLBL_BAW_TO_COMPACT_MAPPING[v]=k


  def fx(oldvalue):
      return GLBL_BAW_TO_COMPACT_MAPPING[int(oldvalue)]

  def compact_labelmapnaming_mapping():
      input_file = BAW_ATLAS_MAPPING
      label_map_information = pd.read_csv(input_file, comment='#', delimiter=',',
                                          skiprows=0, dtype=str, na_values=[""],
                                          encoding="ISO-8859-1", names=['Num', 'LabelName', 'R', 'G', 'B', 'A'])
      label_map_information['Num'] = label_map_information['Num'].astype('int')
      # print(label_map_information)
      # /Shared/paulsen/Experiments/20160520_PREDICTHD_long_Results/fcMRI_024/1163/31855/JointFusion/allVol/labelVolume.csv
      label_map_information = label_map_information[label_map_information['Num'].isin(GLBL_BAW_TO_COMPACT_MAPPING.keys())]
      label_map_information['NewLbl'] = label_map_information['Num'].apply(fx)
      label_map_information['Num'] = label_map_information['NewLbl']
      label_map_information.drop(columns='NewLbl', inplace=True)
      label_map_information.loc[len(label_map_information)] = [215, 'Lesion', '255', '0', '0', '255']
      label_map_information.sort_values(by='Num', inplace=True)
      label_map_information.to_csv(os.path.join(OUT_DIR,OUTPUT_PREFIX,'niftinetseg.txt'), sep='\t', header=False, index=False)
      print(label_map_information)

  compact_labelmapnaming_mapping()


# print(generate_compact_numbering(GLBL_FOUND_LBL_VALUES))
# def lblmap_get_lables(lbl_map):
#     """
#     A function
#     :return:
#     """
#     lbl = sitk.ReadImage(lbl_map,sitk.sitkUInt16)
#     GLBL_LSIF.Execute(lbl)
#     ls = GLBL_LSIF.GetLabels()
#     GLBL_FOUND_LBL_VALUES.update(ls)
