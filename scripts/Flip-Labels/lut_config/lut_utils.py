import pandas as pd
import re
import SimpleITK as sitk


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

GLB_CHANGELABELIMAGEFILTER =  sitk.ChangeLabelImageFilter()
def rewriteImageIndices(imageFileName, imageOutputPath, newIndexByOldIndex):
    """Rewrite the image so that its labels are identified by the new indices such that we have gotten rid of about half the indices

    :param imageFileName: the name of the file in which the original image is found
    :type imageFileName: str
    :param imageOutputPath: the name of the file to which the new image is to be written
    :type imageOutputPath: str
    :param newIndexByOldIndex: the mapping of old indices to new indices
    :type newIndexByOldIndex: str
    """
    # Get the image for which the labels will be rewritten
    image = sitk.ReadImage(imageFileName)

    # Alter the image so that its labels are referenced only by the new indices (get rid of half of the indices)
    newImage = sitk.Cast( GLB_CHANGELABELIMAGEFILTER.Execute(image, newIndexByOldIndex), sitk.sitkUInt8)
    sitk.WriteImage(newImage, imageOutputPath)
