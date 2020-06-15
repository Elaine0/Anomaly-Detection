import numpy as np
import cv2
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb



def equalize_images(images):
    """
    Performs Histograms Equalization on images.
    https://opencv2-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_histograms/py_histogram_equalization/py_histogram_equalization.html

    Parameters
    ----------
    images : array of uint8
        Residual maps.

    Returns
    -------
    images_equalized : array of uint8
        Equalized images.

    """
    images_equalized = np.zeros(shape=images.shape, dtype="uint8")
    for i, image in enumerate(images):
        image_equalized = cv2.equalizeHist(image)
        image_equalized = np.expand_dims(image_equalized, axis=-1)
        images_equalized[i] = image_equalized
    return images_equalized


def filter_gauss_images(images, kernel_size=5):
    images_filtered = np.zeros(shape=images.shape, dtype="uint8")
    kernel = (kernel_size, kernel_size)
    for i, image in enumerate(images):
        image_filtered = cv2.GaussianBlur(image, kernel, 0)
        image_filtered = np.expand_dims(image_filtered, axis=-1)
        images_filtered[i] = image_filtered
    return images_filtered


def filter_median_images(images, kernel_size=3):
    """
    Filter images according to Median Filtering.
    https://opencv2-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html

    Parameters
    ----------
    images : array of uint8
        Thresholded residual maps.
    kernel_size : int, optional
        Size of the kernel window. The default is 3.

    Returns
    -------
    images_filtered : array of uint8
        Filtered images.

    """
    images_filtered = np.zeros(shape=images.shape, dtype="uint8")
    for i, image in enumerate(images):
        image_filtered = cv2.medianBlur(image, kernel_size)
        image_filtered = np.expand_dims(image_filtered, axis=-1)
        images_filtered[i] = image_filtered
    return images_filtered


def threshold_images(images, threshold):
    """
    All pixel values < threshold  ==> 0, else ==> 255
    """
    images_th = np.zeros(shape=images.shape, dtype="uint8")
    for i, image in enumerate(images):
        image_th = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)[1]
        image_th = np.expand_dims(image_th, axis=-1)
        images_th[i] = image_th.astype("uint8")
    return images_th


def label_images(images):
    """
    Segments images into images of connected components (regions).
    Returns segmented images and a list of lists, whereby each list 
    contains the areas of the regions of the corresponding image. 
    
    Parameters
    ----------
    images : array of uint8
        Thresholded residual maps.
    kernel_size : int, optional
        Size of the kernel window. The default is 3.

    Returns
    -------
    images_labeled : array of uint8
        Labeled images.
    areas_all : list of lists
        List of lists, whereby each list contains the areas of the regions of the corresponding image.

    """
    images_labeled = np.zeros(shape=images.shape)
    areas_all = []
    for i, image_th in enumerate(images):
        # # close small holes with binary closing
        # bw = closing(image_th, square(3))

        # # remove artifacts connected to image border
        # cleared = clear_border(bw)

        # # label image regions
        # image_labeled = label(cleared)

        image_labeled = label(image_th)

        # append image
        images_labeled[i] = image_labeled

        # compute areas of anomalous regions in the current image
        regions = regionprops(image_labeled)
        areas = [region.area for region in regions]
        areas_all.append(areas)

    return images_labeled, areas_all