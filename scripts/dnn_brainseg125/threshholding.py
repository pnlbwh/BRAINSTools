import SimpleITK as sitk


def create_spherical_mask(subject):
  # Get the voxel from the physical space point
  LE_voxel = sitk.TransformPhysicalPointToIndex(subject.LE)
  RE_voxel = sitk.TransformPhysicalPointToIndex(subject.RE)

  # Eye diameter across vertically approx 18-19 mm
  # Eye diameter across horizontally approx 20 mm
  mask = subject.T1 * 0  # Create mask of image size
  mask[LE_voxel] = 1  # Set center of eye to 1
  dilated_image_LE = sitk.BinaryDilate(mask, radius=10, kernel=sitk.sitkBall)  # Create 'sphere' for eye, r=10
  mask = subject.T1 * 0  # Repeat
  mask[RE_voxel] = 1
  dilated_image_RE = sitk.BinaryDilate(mask, radius=10, kernel=sitk.sitkBall)  # binary image
  mask_LE_RE = (dilated_image_LE, dilated_image_RE)

  return mask_LE_RE


def get_thresholds(subject, mask_LE_RE):
  # Get the threshold by multiplying the image by left and right eye masks
  T1_threshold = sitk.StatisticsImageFilter.execute(subject.T1 * mask_LE_RE[0] + subject.T1 * mask_LE_RE[1]).getMean()
  T2_threshold = sitk.StatisticsImageFilter.execute(subject.T2 * mask_LE_RE[0] + subject.T2 * mask_LE_RE[1]).getMean()
  return (T1_threshold, T2_threshold)


# Uses a spherical shape to create left eye and right eye masks w/ scaling
# 1 times LE and 2 times RE
def getTotalMask(subject):
  mask_LE_RE = create_spherical_mask(subject)
  return mask_LE_RE[0] * 1 + mask_LE_RE[1] * 2


## Something to do with Eye segmentations
def gen_mask(subject, eye_segmentation_mask, t1_threshold, t2_threshold):
    brain_mask = (subject.seg > 0) * 3
    t2_mask = (subject.t2 > t2_threshold)
    t1_mask = (subject.t1 < t1_threshold)
    eye_segmentation_mask = eye_segmentation_mask * t1_mask * t2_mask
    return eye_segmentation_mask + brain_mask

def closure_function(mask):
  dilated = sitk.BinaryDilate(mask, 3)
  return sitk.BinaryErode(dilated, 3)
