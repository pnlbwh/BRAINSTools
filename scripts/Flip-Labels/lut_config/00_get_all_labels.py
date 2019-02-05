# \author Hans J. Johnson
# This small script reads all the matching label map files and creates a list of all found labels in that list.

import SimpleITK as sitk
import glob
import os


def get_uniqe_set_of_found_labels(all_filenames, verbose):
  """
  Reads label map files and creates a unique set of all labels found from that list
  :param all_filenames:  A list of filenames
  :param verbose:    Print filename and set additions to the screen
  :return: A set of all labels found in the list of filenames
  """
  lsif = sitk.LabelShapeStatisticsImageFilter()
  found_label_numbers = set([0])  # always ensure that zero is part of the set!
  label_set = dict()
  for ff in all_filenames:
    im = sitk.ReadImage(ff, sitk.sitkUInt16)
    lsif.Execute(im)
    labels_found = set( sorted( lsif.GetLabels() ) )
    new_found_label_numbers = found_label_numbers.union(labels_found)
    if verbose:
      label_diff = new_found_label_numbers - found_label_numbers
      print("{0}: {1}".format(os.path.basename(ff), label_diff))
    label_set[os.path.basename(ff)] = list(labels_found)
    found_label_numbers = new_found_label_numbers
  return found_label_numbers, label_set


if __name__ == '__main__':
  import json
  all_files = glob.glob(
    "/localscratch/Users/johnsonhj/20181002_LesionMappingBAW/20181017_niftinet_data_inputs/images/*_dense_seg.nii.gz")
  all_files = [x for x in all_files if not "combined_dense_seg.nii.gz" in x]

  found_label_numbers, label_set = get_uniqe_set_of_found_labels(all_files, True)
  with open('found_labels.txt', 'w') as fid:
    fid.write("[ {0} ]".format(','.join([str(x) for x in found_label_numbers])))

  with open('label_set.json', 'w') as fp:
    json.dump(label_set, fp)
