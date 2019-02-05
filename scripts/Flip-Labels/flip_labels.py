import argparse

from lut_config.lut_utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-LUT_in", help="File path for original lookup table for image labels")
    parser.add_argument("-LUT_out", help="File path for output lookup table for image labels")
    parser.add_argument("-image_in", help="File path for the original image file")
    parser.add_argument("-image_out", help="File path for the output of the updated image file")
    args = parser.parse_args()

    # VALID BAW INDEXES:  The are the only indexes found from BAW data processing
    VALID_BAW_INDEXES = [0,1024,1025,1026,1027,4,5,1028,7,8,1029,10,11,12,13,1030,15,16,17,18,1035,14,1021,24,26,28,31,1019,43,44,46,47,49,50,51,52,53,54,58,60,1020,63,1031,2116,1032,1033,2129,1034,85,1116,98,1129,120,123,128,129,130,143,251,252,253,254,255,600,2032,15000,15001,2035,1005,15071,15072,15073,1006,1007,3005,1008,3006,3007,15140,15141,15142,15143,15144,15145,15150,15151,15156,15157,2027,15160,15161,15162,15163,15164,15165,15172,15173,15174,15175,15178,15179,4035,2000,15184,15185,2028,15190,15191,15192,15193,15194,15195,3019,2002,15200,15201,3021,3022,3023,3024,3025,2011,3029,5001,5002,3030,3031,4001,4002,4003,4005,4006,4007,4008,4009,4010,4011,4012,4013,4014,4015,4016,4017,4018,4019,4020,4021,4022,4023,4024,4025,3002,3001,4026,4029,4027,4028,3008,3003,4030,4031,4032,3009,3014,3015,4034,3012,4033,3010,3011,3013,3020,3016,3017,3018,3026,3027,3028,2005,2006,2007,2008,2009,2010,3033,2012,2013,3032,3034,3035,2014,2015,2016,2017,2018,2019,2021,2020,2025,2022,999,1000,2024,1002,2026,2029,1009,1010,2034,1012,2030,2031,2033,1016,1017,1018,1015,1011,1013,1022,1014]

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
    df = rewriteDataframe(df, newLabelList, newIndexByOldIndex)

    # print("{0}, {1}".format(newLabelList.shape, df2.shape))
    # Filter only valid entries from the BAW workup
    df = df.loc[df['No.'].isin(VALID_BAW_INDEXES)]
    max_num_lbls = df.shape[0]

    ## Now make condensed numbering scheme
    map_nolr_condensed = dict()
    col_index = df.columns.get_loc("No.")
    for condensed_index in range(0,125):
      no_lr_idx = df.iloc[condensed_index]['No.']
      map_nolr_condensed[no_lr_idx] = condensed_index
      df.iloc[condensed_index,col_index] = condensed_index

    condensedNewIndexByOldIndex = dict()
    for k,no_lr_idx in newIndexByOldIndex.items():
        if no_lr_idx in VALID_BAW_INDEXES:
          condensedNewIndexByOldIndex[k] = map_nolr_condensed[no_lr_idx]
    del newIndexByOldIndex

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
