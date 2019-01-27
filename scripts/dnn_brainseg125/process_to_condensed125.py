import glob
import os
import SimpleITK as sitk
import pandas
import itk

from condensed_data_prep_utils import *

if __name__ == '__main__':
  base_mount_dir='/localscratch/Users/johnsonhj'


  all_fcsv=glob.glob(os.path.join(base_mount_dir,"20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images/*.fcsv"))
  #all_fcsv = [ "/Shared/johnsonhj/2018Projects/20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images/LesionIdentification_trainingSet_s3623.fcsv"]
  #all_fcsv=glob.glob("/Shared/johnsonhj/2018Projects/20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images/TRIO_TRIO_MR2*.fcsv")
  print(len(all_fcsv))

  ## [0, 0, 38, 254, 254, 198]
  current_bb = [256, 256, 256, 0, 0, 0]


  ref_img = make_brain_ref_image()

  lssf = sitk.LabelShapeStatisticsImageFilter()
  for one_fcsv in all_fcsv:
    ds = GetImagesFromRef(one_fcsv)
    if not ds._dense_seg:
      continue
    # print(ds._dense_seg)
    min_value = getMinCutOff(ds._fcsv)
    dense_seg_im = sitk.ReadImage(ds._dense_seg, sitk.sitkUInt16)
    dense_seg_im = ChopImageIndexesBelowZPoint(dense_seg_im, min_value)

    t1_im = readToUChar8(ds._t1w)
    t1_im = ChopImageIndexesBelowZPoint(t1_im, min_value)

    if (ds._t2w):
      t2_im = readToUChar8(ds._t2w)
      t2_im = ChopImageIndexesBelowZPoint(t2_im, min_value)
      valid_region = sitk.Cast(((t1_im != 0) + (t2_im != 0) + (dense_seg_im != 0)) > 0, sitk.sitkUInt8)
    else:
      valid_region = sitk.Cast(((t1_im != 0) + (dense_seg_im != 0)) > 0, sitk.sitkUInt8)

    dense_seg_im = dense_seg_im * sitk.Cast(valid_region, dense_seg_im.GetPixelID())
    t1_im = t1_im * valid_region
    if (ds._t2w):
      t2_im = t2_im * valid_region
    lssf.Execute(valid_region)
    bb = lssf.GetBoundingBox(1)
    current_bb = update_bb(bb, current_bb)

    ## --- Now resample with NN
    idtfxm = sitk.Transform()
    dense_seg_ref_im = resample_and_rescale8bit(dense_seg_im, ref_img, idtfxm)
    t1_ref_im = resample_and_rescale8bit(t1_im, ref_img, idtfxm)
    t2_ref_im = resample_and_rescale8bit(t2_im, ref_img, idtfxm)
    ## --- compress signals
    # \TODO
    ## --- Write to disk
    sitk.WriteImage(dense_seg_ref_im, ds.getOutputFile(ds._dense_seg))
    sitk.WriteImage(t1_ref_im, ds.getOutputFile(ds._t1w))
    print(ds.getOutputFile(ds._t1w))
    if (ds._t2w):
      sitk.WriteImage(t2_ref_im, ds.getOutputFile(ds._t2w))

    print(one_fcsv)
  print(current_bb)
