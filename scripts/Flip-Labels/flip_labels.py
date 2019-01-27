import pandas as pd
import os
from os.path import dirname
import SimpleITK as sitk
import numpy as np
import itk
import matplotlib.pyplot as plt
import re
import sys
import argparse

def getDataframeFromFile(filePath):
    """Get the dataframe from the original lookup table's file

    :param filePath: the name of the file containing the original lookup table
    :type filePath: str

    :returns df: the dataframe representing the lookup table
    :type dataframe: pandas.DataFrame
    """
    # Create a data frame from the file containing the lookup table
    df = pd.read_table(filePath, error_bad_lines=False, comment="#")
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

        if label not in indexByLabel:
            # If this label has not been encountered before, its old index and its new index are the same
            newIndexByOldIndex[row['No.']] = row['No.']
            # If a right or left indicator was removed from a label, rewrite the index of the label
            indexByLabel[label] = row['No.']
        else:
            # If a label is changed and matches another label, make its index match the index of the other label
            newIndexByOldIndex[row['No.']] = indexByLabel[label]
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
    imageFilter = sitk.ChangeLabelImageFilter()
    newImage = imageFilter.Execute(image, newIndexByOldIndex)
    sitk.WriteImage(newImage, imageOutputPath)
    print("Finished creating the recoded image")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-LUT_in", help="File path for original lookup table for image labels")
    parser.add_argument("-LUT_out", help="File path for output lookup table for image labels")
    parser.add_argument("-image_in", help="File path for the original image file")
    parser.add_argument("-image_out", help="File path for the output of the updated image file")
    args = parser.parse_args()

    # Extract the command line arguments
    LUT_in = args.LUT_in    # File path for original lookup table for image labels
    LUT_out = args.LUT_out  # File path for output lookup table for image labels
    image_in = args.image_in   # File path for the original image file
    image_out = args.image_out # File path for the output of the updated image file

    # There are 3 scenarios for which this program will be used
    # 1. image_in, image_out, LUT_in, and LUT_out all used -- modify an image and its lookup table
    # 2. image_in, image_out, LUT_in used -- just recode an image
    # 3. LUT_in, LUT_out used -- just recode a lookup table
    if(image_in and (not image_out or not LUT_in)):
        parser.error('The -image_in argument requires the -image_out and -LUT_in arguments')
    if(not image_in and
      (not LUT_in or not LUT_out)):
        parser.error('If -image_in is not given, arguments -LUT_in and -LUT_out are required (for recoding a lookup table)')


    # Get the dataframe from the lookuptable file
    df = getDataframeFromFile(LUT_in)

    # Create new labels and indices for brain parts after removing left/right terms
    newLabelList, newIndexByOldIndex = removeLeftRightExpressions(df)

    # Rewrite the dataframe for the new labels and indices
    rewriteDataframe(df, newLabelList, newIndexByOldIndex)

    # Write the new lookup table to a file
    if LUT_out:
        writeLookupTableToFile(df, LUT_out)
    else:
        print("Not writing new lookup table because no -LUT_out was specified")

    # Write the new image to a file
    if image_in:
        rewriteImageIndices(image_in, image_out, newIndexByOldIndex)
    else:
        print("Not creating a recoded image because no -image_in was specified")

    print

################################################################
# Three Example uses of this script
#
# 1. Modify an image and its lookup table
# python flip_labels.py -LUT_in ../modified_data/BAWHDAdultAtlas_FreeSurferConventionColorLUT_20160524.txt -LUT_out ../modified_data/BAWHDAdultAtlas_FreeSurferConventionColorLUT_LRIndependent.txt -image_in ../modified_data/TRIO_TRIO_MR2_dense_seg.nii.gz -image_out ../modified_data/TRIO_TRIO_MR2_dense_seg_LRIndependent.nii.gz
#
# 2. Recode an image
# python flip_labels.py -LUT_in ../modified_data/BAWHDAdultAtlas_FreeSurferConventionColorLUT_20160524.txt -image_in ../modified_data/TRIO_TRIO_MR2_dense_seg.nii.gz -image_out ../modified_data/TRIO_TRIO_MR2_dense_seg_LRIndependent.nii.gz
#
# 3. Recode a lookup table
# python flip_labels.py -LUT_in ../modified_data/BAWHDAdultAtlas_FreeSurferConventionColorLUT_20160524.txt -LUT_out ../modified_data/BAWHDAdultAtlas_FreeSurferConventionColorLUT_LRIndependent.txt
################################################################
