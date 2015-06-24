from numpy import asfarray, dot, zeros, asarray, absolute
from numpy import average, copy
from numpy.linalg import eigh, norm
import sys

NUMFEATURES = 10
IMG_WIDTH = 450
IMG_HEIGHT = 450


def parseDirectory(directoryName,extension):
    '''This method returns a list of all filenames in the Directory directoryName. 
    For each file the complete absolute path is given in a normalized manner (with 
    double backslashes). Moreover only files with the specified extension are returned in 
    the list.
    '''
    if not isdir(directoryName): return
    imagefilenameslist=sorted([
        normpath(join(directoryName, fname))
        for fname in listdir(directoryName)
        if fname.lower().endswith('.'+extension)            
        ])
    return imagefilenameslist

#####################################################################################
# Implement required functions here
#
#
#

def generateListOfImgs(listOfTrainFiles):
    imgList = []
    for trainFile in listOfTrainFiles:
        imgList.append(Image.open(trainFile))
    return imgList

def convertImgListToNumpyData(imgList):
    imgArrays = []
    for img in imgList:
        imgArray = asfarray(img).reshape((1, -1))[0]
        normalizedImgArray = normalize(imgArray)
        imgArrays.append(normalizedImgArray)
    return asarray(imgArrays)

def normalize(array):
    max = array.max()
    return array / max

def calculateAverageImg(images):
    return average(images, axis=0)

def removeAverageImage(images, avgImage):
    for image in images:
        image -= avgImage
    return images

def calculateEigenfaces(faces, width, height):
    M = len(faces)
    w, v = eigh(faces.T.dot(faces))
    u = faces.dot(v)
    index = w.argsort()[::-1]
    w=w[index]
    u=u[:, index]
    return u

def transformToEigenfaceSpace(eigenfaces, face, numFeatures):
    pointToEigenspace = zeros(shape=(numFeatures))
    for i in range(numFeatures):
        pointToEigenspace[i] = dot((eigenfaces[:,i:i+1].T), face)
    return pointToEigenspace

def imageFromNormalizedArray(array, width=IMG_WIDTH, height=IMG_HEIGHT):
    return Image.fromarray(array.reshape((height, width))*250)

def mergeImage(rArray, gArray, bArray, width=IMG_WIDTH, height=IMG_HEIGHT):
    rChannel = imageFromNormalizedArray(rArray).convert('RGB').split()[0]
    gChannel = imageFromNormalizedArray(gArray).convert('RGB').split()[1]
    bChannel = imageFromNormalizedArray(bArray).convert('RGB').split()[2]
    return Image.merge('RGB', (rChannel, gChannel, bChannel))

def calculateDistance(transposedFaces, testface):
    distance = sys.float_info.max
    closestMatchIndex = 0
    for index, face in enumerate(transposedFaces):
        newdistance = norm(testface - face)
        if distance > newdistance:
            closestMatchIndex = index
            distance = newdistance
    return (closestMatchIndex, distance)

####################################################################################
#Start of main programm

if __name__ == '__main__':
    from os.path import isdir, join, normpath
    from os import listdir
    from PIL import Image

    import tkFileDialog

    #Choose Directory which contains all training images 
    TrainDir=tkFileDialog.askdirectory(title="Choose Directory of training images")
    #Choose the file extension of the image files
    Extension='png'
    
    ####################################################################################
    # Implement required functionality of the main programm here
    imageFileNames = parseDirectory(TrainDir, Extension)
    images = convertImgListToNumpyData(generateListOfImgs(imageFileNames))
    
    avgImage = calculateAverageImg(copy(images))
    imageFromNormalizedArray(avgImage).show()
    normedArrayOfFaces = removeAverageImage(copy(images), avgImage)


    eigenfaces = calculateEigenfaces(normedArrayOfFaces.T, len(images[0]), len(images))
    transposedFaces = []
    for face in normedArrayOfFaces:
        transposedFaces.append(transformToEigenfaceSpace(eigenfaces, face, NUMFEATURES))
    
    #Choose the image which shall be recognized
    testImageDirAndFilename=tkFileDialog.askopenfilename(title="Choose Image to detect")
    
    testImage = Image.open(testImageDirAndFilename)
    testface = convertImgListToNumpyData([testImage])[0]
    testface -= avgImage
    
    testface = transformToEigenfaceSpace(eigenfaces, testface, NUMFEATURES)
    
    closestMatchIndex, distance = calculateDistance(transposedFaces, testface, imageFileNames)
    print "closest distance: " + str(distance) + " image: " + imageFileNames[closestMatchIndex]
    
    testImageArray = normalize(convertImgListToNumpyData([testImage])[0])
    closestMatchArray = normalize(images[closestMatchIndex])
    diffToTestArray = absolute(normalize(closestMatchArray - testImageArray))
    
    # Ausgabe der Differenz als schwarz/weiss Bild.
    imageFromNormalizedArray(diffToTestArray).show()
    
    # Ausgabe des Bildes zur Anzeige der Differenz zwischen dem Test- und dem gefundenen Trainingsbild
    mergeImage(closestMatchArray + diffToTestArray, closestMatchArray, closestMatchArray).show()
    
    # Ausgabe des Durchschnittsbildes
    imageFromNormalizedArray(avgImage).show()