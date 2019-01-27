import SimpleITK as sitk
import os
import pandas as pd


class Subject(object):
  def __init__(self, identifier, t1, t2, seg, fcsv):
    fcsv[1] = -fcsv[1]
    fcsv[1] = -fcsv[1]
    self.identifier = identifier
    self.t1 = t1  # sitk.Image()
    self.t2 = t2  # sitk.Image()
    self.seg = seg  # sitk.Image()
    self.RE = fcsv.loc[fcsv[0] == 'RE'].values[0][1:4]  # physical point 3-tuple of right eye
    self.LE = fcsv.loc[fcsv[0] == 'LE'].values[0][1:4]  # physical point 3-tuple of left eye

def get_subject_list(directory: str):
  subjects = set()
  for file in os.listdir(directory):
    path = os.path.join(directory, file)
    if os.path.isfile(path):
      subjects.add(file[:10])
  return list(subjects)


def get_subject(identifier: str, directory: str):
  reader = sitk.ImageFileReader()
  reader.SetFileName(os.path.join(directory, f'{identifier}_t1w.nii.gz'))
  t1 = reader.Execute()
  reader.SetFileName(os.path.join(directory, f'{identifier}_t2w.nii.gz'))
  t2 = reader.Execute()
  reader.SetFileName(os.path.join(directory, f'{identifier}_seg.nii.gz'))
  seg = reader.Execute()
  fcsv = pd.read_csv(os.path.join(directory, f'{identifier}.fcsv'), comment='#', header=None)
  return Subject(identifier=identifier, t1=t1, t2=t2, seg=seg, fcsv=fcsv)
