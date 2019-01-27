import glob
import os
import SimpleITK as sitk
import pandas
import itk


class GetImagesFromRef():
    def __init__(self, fcsv_filename):
        self.base_mount_dir='/localscratch/Users/johnsonhj'
        self.base_output_dir=os.path.join(self.base_mount_dir,'20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images_cropped')
        self.base_data_dir=os.path.join(self.base_mount_dir,'20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images')

        self._fcsv = fcsv_filename
        self._data_dir = os.path.dirname(self._fcsv)
        self._test_file_pat = os.path.basename(self._fcsv).replace(".fcsv","")
        self._t1w = os.path.join(self._data_dir,self._test_file_pat+"_t1w_cropped.nii.gz")
        self._t2w = os.path.join(self._data_dir,self._test_file_pat+"_t2w_cropped.nii.gz")
        if( not os.path.exists( self._t2w )):
            self._t2w=None
        self._dense_seg = os.path.join(self._data_dir,self._test_file_pat+"_compact125_seg.nii.gz")
        if( not os.path.exists( self._dense_seg )):
            self._dense_seg=None
    def getOutputFile(self,fn):
        base_fn = os.path.basename(fn)
        return os.path.join( self.base_output_dir, base_fn )



def make_brain_ref_image():
    ref_img = sitk.Image(256,256,190, sitk.sitkUInt8)
    ref_img.SetSpacing([1.0,1.0,1.0])
    ref_img.SetOrigin( [-127.5, -127.5, -94.5 + 20.0 ] )
    return ref_img

def getMinCutOff(fcsv_filename):
    with open(fcsv_filename, 'r') as fcsvfid:
        fcsv_content = fcsvfid.read()
    if "fiducial file version = 4.6" in fcsv_content:
        #print("new reader: {0}".format(fcsv_filename))
        col_names=["id","LR","PA","SI","ow","ox","oy","oz","vis","sel","lock","lmk","dumma","dummyb"]
    else:
        #print("old reader: {0}".format(fcsv_filename))
        col_names=["lmk","LR","PA","SI","dummya","dummyb"]
    df=pandas.read_csv(fcsv_filename,sep=',',comment="#",header=None,names=col_names)
    #print(df)
    ## Take 20 off RL and SI directions  Chop above dens
    row = df.loc[df['lmk'] == "dens_axis"].iloc[0]

    min_loc_lr = row["LR"]
    min_loc_pa = row["PA"]
    safety_margin = 5.0
    min_loc_si = row["SI"] - safety_margin
    return [min_loc_lr,min_loc_pa,min_loc_si]

def ChopImageIndexesBelowZPoint(inputImage, physpoint):
    # Assumes an identity direction matrix
    mask= sitk.Image(inputImage)
    index=mask.TransformPhysicalPointToIndex(physpoint)
    npmask=sitk.GetArrayFromImage(mask)
    npmask[0:index[2],:,:] = 0 # Set values to zero

    outputImage= sitk.GetImageFromArray(npmask)
    outputImage.CopyInformation(mask)

    return outputImage

def update_bb(new_bb, current_bb):
    for i in range(0,3):
        if new_bb[i] < current_bb[i]:
            current_bb[i] = new_bb[i]
    for i in range(3,6):
        if new_bb[i] > current_bb[i]:
            current_bb[i] = new_bb[i]
    return current_bb

def resample_to_ref(image, reference_image, transform):
    # Output image Origin, Spacing, Size, Direction are taken from the reference
    # image in this call to Resample
    interpolator = sitk.sitkNearestNeighbor
    default_value = 0.0
    return sitk.Resample(image, reference_image, transform,
                         interpolator, default_value)

def rescale8bit(image):
  return sitk.Cast(sitk.RescaleIntensity(image), sitk.sitkUInt8)

def resample_and_rescale8bit(image, reference_image, transform):
  uint8_img = rescale8bit(image)
  return resample_to_ref(uint8_img, reference_image, transform)

def readToUChar8(fn):
  in_img = sitk.ReadImage(fn, sitk.sitkUInt16)
  image = sitk.Cast(sitk.RescaleIntensity(in_img), sitk.sitkUInt8)
  return image


import SimpleITK as sitk

RESAMPLE_IMG_SIZE = [192, 216, 192]
# NOTE:  We need to move about 20 mm anterior to avoid cutting off back of brain.
#       bacause the AC point is NOT in the center of the brain.
RESAMPLE_IMG_ORIG = [-96.0, -88.0, -96.0]
RESAMPLE_IMG_SPAC = [1.0, 1.0, 1.0]


def resample_256_iso(inimg, interp):
  """

  :param inimg:
  :param interp:
  :return:
  """
  # interp = sitk.sitkNearestNeighbor
  # interp = sitk.sitkLinear

  ref_img = sitk.Image(RESAMPLE_IMG_SIZE, sitk.sitkUInt16)
  ref_img.SetOrigin(RESAMPLE_IMG_ORIG)
  ref_img.SetSpacing(RESAMPLE_IMG_SPAC)
  resampler = sitk.ResampleImageFilter()
  resampler.SetReferenceImage(ref_img)
  resampler.SetInterpolator(interp)
  resampled = resampler.Execute(inimg)
  if interp == sitk.sitkNearestNeighbor:
    resampled = sitk.Cast(resampled, sitk.sitkUInt16)
  return resampled


def WriteImageUInt8(resampled, outfile, rescaleIntensity=True):
  if rescaleIntensity:
    resampled = rescale8bit(resampled)
  sitk.WriteImage(resampled, outfile)


def lblmap_renumber(orig_lm, remapper, use_UInt8=True):
    """
    Renumber a labelmap with new label numbers
    :param orig_lm:  baw labeled image
    :param output_fn: compact labeled image filename
    :param remapper a mapping from old to new values
    :return:
    """
    baw2compact_clif = sitk.ChangeLabelImageFilter()
    baw2compact_clif.SetChangeMap(remapper)
    if use_UInt8:
      out = sitk.Cast(baw2compact_clif.Execute(orig_lm), sitk.sitkUInt8)
    else:
      out = sitk.Cast(baw2compact_clif.Execute(orig_lm), sitk.sitkUInt16)
    return out


def nifit_net_write_csv(out_file, out_dict):
  with open(out_file, 'w') as ofid:
    for k, v in out_dict.items():
      ofid.write("{key},{value}\n".format(key=k, value=v))
