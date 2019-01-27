from decimal import *
import sys

def calculateEyeDistance(file):
    fiducialFile = open(file, 'r')
    fileLines = fiducialFile.readlines()

    for line in fileLines:
        label = line.split(',')
        if (label[0] == 'RE'):
            reLocation = label[1:4]
        if (label[0] == 'LE'):
            leLocation = label[1:4]

    sum = 0
    test = Decimal(reLocation[0]) + 1
    for index, coord in enumerate(reLocation):
        sum += (Decimal(reLocation[index]) - Decimal(leLocation[index]))**2
    distance = Decimal(sum).sqrt()
    return distance

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nERROR: Pass one .fcsv file as command line argument to calculate distance between eyes\n")
    else:
        fileName = sys.argv[1]
        print(calculateEyeDistance(fileName))
