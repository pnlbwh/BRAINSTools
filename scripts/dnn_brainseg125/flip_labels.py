import argparse

from lut_config.lut_utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-LUT_in", help="File path for original lookup table for image labels")
    parser.add_argument("-LUT_out", help="File path for output lookup table for image labels")
    parser.add_argument("-image_in", help="File path for the original image file")
    parser.add_argument("-image_out", help="File path for the output of the updated image file")
    parser.add_argument("-mapping_out", help="json file for storing the mapping from old to new index numbers")
    args = parser.parse_args()

    # Extract the command line arguments
    LUT_in = args.LUT_in
    LUT_out = args.LUT_out
    image_in = args.image_in
    image_out = args.image_out
    mapping_out = args.mapping_out
    condense_one_dataset(LUT_in, LUT_out, image_in, image_out, mapping_out)



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
