import pandas as pd
import re
import SimpleITK as sitk
import json

def generate_compact_numbering(found_label_map_values):
  """
  Given a set of unique labels, create a mapping from those labels to a compact numbering order
  :param found_label_map_values:
  :return: dictionary with new values as keys, and old values as values
  """
  # num_lbls=len(found_label_map_values)
  lbl_mapping = dict()
  for new_lbl in range(0, len(found_label_map_values)):
    old_lbl = found_label_map_values[new_lbl]
    lbl_mapping[new_lbl] = old_lbl
  return lbl_mapping

def getDataframeFromFile(filePath):
    """Get the dataframe from the original lookup table's file

    :param filePath: the name of the file containing the original lookup table
    :type filePath: str

    :returns df: the dataframe representing the lookup table
    :type dataframe: pandas.DataFrame
    """
    # Create a data frame from the file containing the lookup table
    df = pd.read_table(filePath, error_bad_lines=False, comment="#", names=['No.',	'Label',	'R',	'G',	'B',	'A', 'dummy1', 'dummy2'])
    df.drop(['dummy1', 'dummy2'], axis=1)
    return df

def removeLeftRightExpressions(df):
    """Remove all right or left indicators in the dataframe

    :param df: the original dataframe of representing the image's lookup table
    :type df: pandas.DataFrame

    :returns newLabelList: the new list of labels for parts of the brain after having removed any strings that indicate the part being on the left or right
    :type newLabelList: list
    :returns newIndexByOldIndex: a dictionary whose key is the old index for a part of the brain and the value is the new index for that part
    :type newIndexByOldIndex: dict
    """
    newLabelList = []
    indexByLabel = {}
    newIndexByOldIndex = {}
    for index, row in df.iterrows():
        label = row['Label']
        label = re.sub(r'Left|Right|left|right|lh|rh|', '', label)
        label = re.sub(r'^L[A-Z].*|^R[A-Z].*', label[1:], label)
        label = re.sub(r'^-', '', label)

        old_index = row['No.']
        if label not in indexByLabel:
            # If this label has not been encountered before, its old index and its new index are the same
            newIndexByOldIndex[old_index] = old_index
            # If a right or left indicator was removed from a label, rewrite the index of the label
            indexByLabel[label] = old_index
        else:
            # If a label is changed and matches another label, make its index match the index of the other label
            new_index = indexByLabel[label]
            newIndexByOldIndex[ old_index ] = new_index
        newLabelList.append(label)
    return newLabelList, newIndexByOldIndex

def rewriteDataframe(df, newLabelList, newIndexByOldIndex):
    """Rewrites the dataframe defining the image's lookup table after

    :param df: the df to rewrite
    :type df: pandas.DataFrame
    :param newLabelList: the new labels for the image now that the left/right indications have been removed
    :type newLabelList: list
    :param newIndexByOldIndex: the mapping of old indices to new indices so that the left and right versions of a part are the same index
    :type newIndexByOldIndex: dict
    """

    # Rewrite the label column with the right and left indicators removed
    df['Label'] = newLabelList
    # Rewrite the number for labels so that the right and left of a label are identified by the same number
    df['No.'] = newIndexByOldIndex.values()
    df.drop_duplicates(subset='Label',keep='first',inplace=True)
    return df

def writeLookupTableToFile(df, LUT_outputName):
    """Write the dataframe containing the lookup table to a tab separated file

    :param df: the dataframe containing the lookup table
    :type df: pandas.DataFrame
    :param LUT_outputName: the name of the file to write the new lookup table
    :type LUT_outputName: dict
    """
    # Write the dataframe to a file
    df.to_csv(LUT_outputName, sep='\t', index=False)
    print("Finished writting new lookup table")


def rewriteImageIndices(imageFileName, imageOutputPath, newIndexByOldIndex):
    """"Rewrite the image so that its labels are identified by the new indices such that we have gotten rid of about half the indices

    :param imageFileName: the name of the file in which the original image is found
    :type imageFileName: str
    :param imageOutputPath: the name of the file to which the new image is to be written
    :type imageOutputPath: str
    :param newIndexByOldIndex: the mapping of old indices to new indices
    :type newIndexByOldIndex: str
    """
    chnglblfilter = sitk.ChangeLabelImageFilter()
    # Get the image for which the labels will be rewritten
    image = sitk.ReadImage(imageFileName)

    # Alter the image so that its labels are referenced only by the new indices (get rid of half of the indices)
    newImage = sitk.Cast(chnglblfilter.Execute(image, newIndexByOldIndex), sitk.sitkUInt8)
    sitk.WriteImage(newImage, imageOutputPath)


def condense_one_dataset(LUT_in, LUT_out, image_in, image_out, mapping_out):
  """
  :param LUT_in: File path for original lookup table for image labels
  :param LUT_out: File path for output lookup table for image labels
  :param image_in: File path for the original image file
  :param image_out: File path for the output of the updated image file
  :return:
  """
  # VALID BAW INDEXES:  The are the only indexes found from BAW data processing
  VALID_BAW_INDEXES = [0, 1024, 1025, 1026, 1027, 4, 5, 1028, 7, 8, 1029, 10, 11, 12, 13, 1030, 15, 16, 17, 18, 1035,
                       14, 1021, 24, 26, 28, 31, 1019, 43, 44, 46, 47, 49, 50, 51, 52, 53, 54, 58, 60, 1020, 63, 1031,
                       2116, 1032, 1033, 2129, 1034, 85, 1116, 98, 1129, 120, 123, 128, 129, 130, 143, 251, 252, 253,
                       254, 255, 600, 2032, 15000, 15001, 2035, 1005, 15071, 15072, 15073, 1006, 1007, 3005, 1008, 3006,
                       3007, 15140, 15141, 15142, 15143, 15144, 15145, 15150, 15151, 15156, 15157, 2027, 15160, 15161,
                       15162, 15163, 15164, 15165, 15172, 15173, 15174, 15175, 15178, 15179, 4035, 2000, 15184, 15185,
                       2028, 15190, 15191, 15192, 15193, 15194, 15195, 3019, 2002, 15200, 15201, 3021, 3022, 3023, 3024,
                       3025, 2011, 3029, 5001, 5002, 3030, 3031, 4001, 4002, 4003, 4005, 4006, 4007, 4008, 4009, 4010,
                       4011, 4012, 4013, 4014, 4015, 4016, 4017, 4018, 4019, 4020, 4021, 4022, 4023, 4024, 4025, 3002,
                       3001, 4026, 4029, 4027, 4028, 3008, 3003, 4030, 4031, 4032, 3009, 3014, 3015, 4034, 3012, 4033,
                       3010, 3011, 3013, 3020, 3016, 3017, 3018, 3026, 3027, 3028, 2005, 2006, 2007, 2008, 2009, 2010,
                       3033, 2012, 2013, 3032, 3034, 3035, 2014, 2015, 2016, 2017, 2018, 2019, 2021, 2020, 2025, 2022,
                       999, 1000, 2024, 1002, 2026, 2029, 1009, 1010, 2034, 1012, 2030, 2031, 2033, 1016, 1017, 1018,
                       1015, 1011, 1013, 1022, 1014]

  # There are 3 scenarios for which this program will be used
  # 1. image_in, image_out, LUT_in, and LUT_out all used -- modify an image and its lookup table
  # 2. image_in, image_out, LUT_in used -- just recode an image
  # 3. LUT_in, LUT_out used -- just recode a lookup table
  if (image_in and (not image_out or not LUT_in)):
    parser.error('The -image_in argument requires the -image_out and -LUT_in arguments')
  if (not image_in and
    (not LUT_in or not LUT_out)):
    parser.error('If -image_in is not given, arguments -LUT_in and -LUT_out are required (for recoding a lookup table)')

  # Get the dataframe from the lookuptable file
  df = getDataframeFromFile(LUT_in)

  # Create new labels and indices for brain parts after removing left/right terms
  newLabelList, newIndexByOldIndex = removeLeftRightExpressions(df)

  # Rewrite the dataframe for the new labels and indices
  df = rewriteDataframe(df, newLabelList, newIndexByOldIndex)

  # print("{0}, {1}".format(newLabelList.shape, df2.shape))
  # Filter only valid entries from the BAW workup
  df = df.loc[df['No.'].isin(VALID_BAW_INDEXES)]
  max_num_lbls = df.shape[0]

  ## Now make condensed numbering scheme
  map_nolr_condensed = dict()
  col_index = df.columns.get_loc("No.")
  for condensed_index in range(0, 125):
    no_lr_idx = df.iloc[condensed_index]['No.']
    map_nolr_condensed[no_lr_idx] = condensed_index
    df.iloc[condensed_index, col_index] = condensed_index

  condensedNewIndexByOldIndex = dict()
  for k, no_lr_idx in newIndexByOldIndex.items():
    if no_lr_idx in VALID_BAW_INDEXES:
      condensedNewIndexByOldIndex[k] = map_nolr_condensed[no_lr_idx]
  del newIndexByOldIndex
  if mapping_out:
    with open(mapping_out, 'w') as jfid:
      json.dump(condensedNewIndexByOldIndex,jfid, indent=2)

  # Write the new lookup table to a file
  if LUT_out:
    writeLookupTableToFile(df, LUT_out)
  else:
    print("Not writing new lookup table because no -LUT_out was specified")

  # Write the new image to a file
  if image_in:
    rewriteImageIndices(image_in, image_out, condensedNewIndexByOldIndex)

  else:
    print("Not creating a recoded image because no -image_in was specified")
