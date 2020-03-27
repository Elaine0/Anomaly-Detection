import os
import sys

import tensorflow as tf
from tensorflow import keras

from modules import utils as utils

# from keras.preprocessing.image import ImageDataGenerator
import numpy as np
import scipy.stats

# import requests
import matplotlib.pyplot as plt

# plt.style.use("seaborn-darkgrid")
import csv
import pandas as pd
import json

import argparse
from pathlib import Path


# import computer vision functions
import cv2
from skimage.util import img_as_ubyte
from modules.cv import scale_pixel_values as scale_pixel_values
from modules.cv import filter_gauss_images as filter_gauss_images
from modules.cv import filter_median_images as filter_median_images
from modules.cv import threshold_images as threshold_images
from modules.cv import label_images as label_images


# =========================================================================
# visualization functions


def plot_img_at_index(X, index):
    plt.style.use("default")
    _, _, _, channels = X.shape
    fig = plt.figure()
    if channels == 1:
        plt.imshow(X[index, :, :, 0], cmap=plt.cm.gray)
    elif channels == 3:
        plt.imshow(X[index, :, :, 0])
    plt.show()


def plot_img(img, title=None):
    plt.style.use("default")
    ndims = len(img.shape)
    fig = plt.figure()
    if ndims == 2:
        plt.imshow(img, cmap=plt.cm.gray)
    elif ndims == 3:
        _, _, channels = img.shape
        if channels == 3:
            plt.imshow(img)
        else:
            plt.imshow(img[:, :, 0], cmap=plt.cm.gray)
    plt.title(title)
    plt.show()
    # return fig


def hist_image(img, bins=400, range_x=None, title=None):
    # plot histogram
    plt.style.use("seaborn-darkgrid")
    img_1d = img.flatten()
    plt.figure()
    plt.hist(img_1d, bins=bins, range=range_x, density=True, stacked=True, label="image histogram")
    
    # print descriptive values
    mu = img_1d.mean()
    sigma = img_1d.std()
    minimum = np.amin(img_1d)
    maximum = np.amax(img_1d)
    print("{} \n mu = {} \n sigma = {} \n min = {}\n max = {}".format(title, mu, sigma, minimum, maximum))
    
    # compute and plot probability distribution function    
    X = np.linspace(start=minimum, stop=maximum, num=200, endpoint=True)
    pdf_x = [scipy.stats.norm(mu, sigma).pdf(x) for x in X]
    plt.plot(X, pdf_x, label="pixel distribution")
    plt.title(title)
    if range_x is not None:
        plt.xlim(range_x[0], range_x[1])
    plt.legend()
    plt.show()
    
def hist_image_uint8(img, range_x=None, title=None):
    # plot histogram    
    plt.style.use("seaborn-darkgrid")
    plt.figure()
    # compute bin edges
    img_1d = img.flatten()
    d = np.diff(np.unique(img_1d)).min()
    left_of_first_bin = img_1d.min() - float(d)/2
    right_of_last_bin = img_1d.max() + float(d)/2  
    bins = np.arange(left_of_first_bin, right_of_last_bin + d, d)
    plt.hist(img_1d, bins=bins, density=True, stacked=True, label="pixel value histogram")
    
    # print descriptive values
    mu = img_1d.mean()
    sigma = img_1d.std()
    minimum = np.amin(img_1d)
    maximum = np.amax(img_1d)
    print("{} \n mu = {} \n sigma = {} \n min = {}\n max = {}".format(title, mu, sigma, minimum, maximum))
    
    # compute and plot probability distribution function    
    X = np.linspace(start=minimum, stop=maximum, num=200, endpoint=True)
    pdf_x = [scipy.stats.norm(mu, sigma).pdf(x) for x in X]
    plt.plot(X, pdf_x, label="pixel distribution")
    plt.title(title)
    if range_x is not None:
        plt.xlim(range_x[0], range_x[1])
    plt.legend()
    plt.show()


    
# df_val = pd.read_pickle("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/validation/validation_results.pkl")


# areas = [40, 45, 50]
# thresholds = [135, 140, 145]
# elems = [(area, threshold) for threshold in thresholds for area in areas]

# =========================================================================

# VALIDATION
imgs_val_input = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/finetune/imgs_val_input.npy", allow_pickle=True)
imgs_val_pred = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/finetune/imgs_val_pred.npy", allow_pickle=True)
resmaps_val = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/finetune/resmaps_val.npy", allow_pickle=True)
# resmaps_val_l2 = (imgs_val_input - imgs_val_pred)**2

index_val = 0
# plot_img(imgs_val_input[index_val])
# plot_img(imgs_val_pred[index_val])
plot_img(resmaps_val[index_val], title="resmaps_val")
plot_img(resmaps_val[index_val], title="resmaps_val_l2")

hist_image(resmaps_val, title="resmaps_val")
# hist_image(resmaps_val_l2,  title="resmaps_val_l2")
hist_image(imgs_val_input, title="imgs_val_input")
hist_image(imgs_val_pred, title="imgs_val_pred")


# TEST
imgs_test_input = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_32_a_70/imgs_test_input.npy", allow_pickle=True)
imgs_test_pred = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_32_a_70/imgs_test_pred.npy", allow_pickle=True)
resmaps_test = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_32_a_70/resmaps_test.npy", allow_pickle=True)

index_test = 68
# plot_img(imgs_test_input[index_test])
# plot_img(imgs_test_pred[index_test])
plot_img(resmaps_test[index_test])



# testing ssim ===========================================================================

img_true = imgs_test_input[index_test]
plot_img(img_true[:,:,0], title="img_true")
img_pred = imgs_test_pred[index_test]
plot_img(img_pred[:,:,0], title="img_pred")

# for loss
tensor_true = tf.convert_to_tensor(img_true)
tensor_pred = tf.convert_to_tensor(img_pred)
tf.image.ssim(tensor_true, tensor_pred, 1.0)
tf.image.ssim(tf.convert_to_tensor(imgs_val_input), tf.convert_to_tensor(imgs_val_pred), 1.0) # shape=(21,)

# for validation

import importlib
import modules
importlib.reload(modules)

from modules.resmaps import resmaps_ssim as resmaps_ssim

# VALIDATION
resmaps_val_ssim = resmaps_ssim(imgs_val_input, imgs_val_pred)
plot_img(resmaps_val_ssim[index_val])
hist_image(resmaps_val_ssim, title="resmaps_val_ssim")

resmaps_val_ssim_uint8 = img_as_ubyte(resmaps_val_ssim)
plot_img(resmaps_val_ssim_uint8[index_val])
hist_image(resmaps_val_ssim_uint8, title="resmaps_val_ssim_uint8")

# TEST
resmaps_test_ssim = resmaps_ssim(imgs_test_input, imgs_test_pred)
plot_img(resmaps_test_ssim[index_test])
hist_image(resmaps_test_ssim, title="resmaps_test_ssim")

# find out which images have pixel intensity > 1 ---------------------------
def test_bool_array(array_bool):
    for boolean in array_bool:
        if boolean == True:
            print("YO")
            return True
    return False

my_list = []
for i, image in enumerate(resmaps_test_ssim):
    if test_bool_array(image.flatten()>1) == True:
        my_list.append(i)

# [1, 4, 6, 9, 17, 20, 91]
index = 1
plot_img(resmaps_test_ssim[index], title="resmaps_test_ssim[{}]".format(index))   
hist_image(resmaps_test_ssim[index], title="resmaps_test_ssim[{}]".format(index))     

# Testing clipping
from skimage.util import dtype_limits as dtype_limits
variable = dtype_limits(resmaps_test_ssim[index])

img_sample = resmaps_test_ssim[1]
img_sample_clip = np.clip(img_sample, -1, 1)
hist_image(img_sample_clip, title="img_sample_clip")



resmaps_test_ssim_clip = np.clip(resmaps_test_ssim.copy(), -1, 1)

hist_image(resmaps_test_ssim_clip, title="resmaps_test_ssim_clip")
hist_image(resmaps_test_ssim, title="resmaps_test_ssim")
# [1, 4, 6, 9, 17, 20, 91]
index = 1
plot_img(resmaps_test_ssim[index], title="resmaps_test_ssim[{}]".format(index))
plot_img(resmaps_test_ssim_clip[index], title="resmaps_test_ssim_clip[{}]".format(index))

# ----------------------------------------------------------------------------        

resmaps_test_ssim_uint8 = img_as_ubyte(resmaps_test_ssim_clip)
plot_img(resmaps_test_ssim_uint8[index_test])
hist_image(resmaps_test_ssim_uint8, title="resmaps_test_ssim")

# ============================= PLAYGROUND ====================================

# inspect pixel value distribution of val and test -----------------------
hist_image(resmaps_val, range_x=(-1,1), title="resmaps_val")
hist_image(resmaps_test, range_x=(-1,1), title="resmaps_test")

hist_image(resmaps_val, title="resmaps_val")
hist_image(resmaps_test, title="resmaps_test")


# scale pixel values in [0,1] and plot --------------------------------------
resmaps_val_scaled = (resmaps_val + 1)/2
index_val = 0
plot_img(resmaps_val[index_val])
plot_img(resmaps_val_scaled[index_val])
hist_image(resmaps_val_scaled, range_x=(0,1), title="resmaps_val_scaled")

resmaps_test_scaled = (resmaps_test + 1)/2
index_test = 68
plot_img(resmaps_test[index_test])
plot_img(resmaps_test_scaled[index_test])
hist_image(resmaps_test_scaled, range_x=(0,1), title="resmaps_test_scaled")


# Convert to 8-bit unsigned int for further processing -----------------------
resmaps_val_uint8 = img_as_ubyte(resmaps_val_scaled)
index_val = 0
plot_img(resmaps_val_uint8[index_val])
hist_image_uint8(resmaps_val_uint8, title="resmaps_val_uint8")
hist_image_uint8(resmaps_val_uint8, range_x=(0,255), title="resmaps_val_uint8")

resmaps_test_uint8 = img_as_ubyte(resmaps_test_scaled)
index_test = 68
plot_img(resmaps_test_uint8[index_test])
hist_image_uint8(resmaps_test_uint8, title="resmaps_test_uint8")
hist_image_uint8(resmaps_test_uint8, range_x=(0,255), title="resmaps_test_uint8")

# investigate Histogram Equalization ------------------------------ NOT SUITED
from skimage.exposure import equalize_hist as equalize_hist
img = resmaps_test_uint8[index_test]
plot_img(img, title="img")
# hist_image_uint8(img, title="img")

img_equal = equalize_hist(img)
plot_img(img_equal, title="img_equal")
equ = cv2.equalizeHist(img)
plot_img(equ, title="equ")

from modules.cv import equalize_images as equalize_images
resmaps_test_uint8_eq = equalize_images(resmaps_test_uint8)
plot_img(resmaps_test_uint8_eq[index_test], title="resmaps_test_uint8_eq[{}]".format(index_test))


threshold = 253
resmaps_test_uint8_eq_th = threshold_images(resmaps_test_uint8_eq, threshold)
index_test = 68
plot_img(resmaps_test_uint8_eq_th[index_test], title="resmaps_test_uint8_eq_th[{}]".format(index_test))

index_test = 0
plot_img(resmaps_test_uint8_eq_th[index_test], title="resmaps_test_uint8_eq_th[{}]".format(index_test))


# investigate blurring with gaussian filter ---------------------------------XXXXXX
resmaps_val_uint8_blur = filter_gauss_images(resmaps_val_uint8)

hist_image_uint8(resmaps_val_uint8, range_x=(0,255), title="resmaps_val_uint8")
hist_image_uint8(resmaps_val_uint8_blur, range_x=(0,255), title="resmaps_val_uint8_gauss")




img = resmaps_test_uint8[index_test]
plot_img(img, title="img")
hist_image_uint8(img, title="img")

resmaps_test_uint8_blur = filter_gauss_images(resmaps_test_uint8)
blur = resmaps_test_uint8_blur[index_test]
plot_img(blur, title="blur")
hist_image_uint8(blur, title="blur")

# threshold residual maps and plot results ----------------------------------

import importlib
import validate
importlib.reload(validate)


threshold = 140
resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold) # resmaps_val_th_uint8
index_val = 5
plot_img(resmaps_val_uint8_th[index_val], title="resmaps_val_uint8_th[{}]\n threshold = {}".format(index_val, threshold))


threshold = 131
resmaps_test_uint8_th = threshold_images(resmaps_test_uint8, threshold)
index_test = 68
plot_img(resmaps_test_uint8_th[index_test], title="resmaps_test_uint8_th[{}]\n threshold = {}".format(index_test, threshold))

# threshold = 141
resmaps_test_uint8_blur_th = threshold_images(resmaps_test_uint8, threshold)
# index_test = 68
plot_img(resmaps_test_uint8_blur_th[index_test], title="resmaps_test_uint8_blur_th[{}]\n threshold = {}".format(index_test, threshold))

# investigate shrinking down the threshold interval from [pixel_min, pixel_max] to a smaller interval that contains relevant thresholds ------------------

# compute descriptive values
mu = resmaps_val_uint8.flatten().mean()
sigma = resmaps_val_uint8.flatten().std()
minimum = np.amin(resmaps_val_uint8.flatten()) # pixel_min
maximum = np.amax(resmaps_val_uint8.flatten()) # pixel_max

# compute pdf and cdf
X = np.linspace(start=minimum, stop=maximum, num=200, endpoint=True)
pdf_x = [scipy.stats.norm(mu, sigma).pdf(x) for x in X]
cdf_x = [scipy.stats.norm(mu, sigma).cdf(x) for x in X]

# plot histogram, pdf and cdf
hist_image_uint8(resmaps_val_uint8, title="resmaps_val_uint8")
plt.plot(X, cdf_x, label="cdf")

# define relevant threshold ranges
cdf_relevant_range = np.arange(start=0.9, stop=1, step=0.0001) # start=0.9, stop=1, step=0.0001
# start=0.95, stop=1, step=0.00001 => th_min = 125, th_max = 149
th_relevant_range = [scipy.stats.norm(mu, sigma).ppf(cdf_value) for cdf_value in cdf_relevant_range]
th_min = int(round(np.amin(np.array(th_relevant_range)), 1)) - 1 # 124
th_max = int(round(np.amax(np.array(th_relevant_range)), 1)) + 1 # 135

# investigate resulting thresholded images with different values of selected relevant thresholds
threshold = 124
resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold)
index_val = 5
plot_img(resmaps_val_uint8_th[index_val], title="resmaps_val_uint8_th[{}]\n threshold = {}".format(index_val, threshold))

resmaps_test_uint8_th = threshold_images(resmaps_test_uint8, threshold)
index_test = 68
plot_img(resmaps_test_uint8_th[index_test], title="resmaps_test_uint8_th[{}]\n threshold = {}".format(index_test, threshold))

scipy.stats.norm(mu, sigma).ppf(0.99)

# threshold = 124
resmaps_test_uint8_th = threshold_images(resmaps_test_uint8, threshold)
index_test = 68
plot_img(resmaps_test_uint8_th[index_test], title="resmaps_test_uint8_th[{}]\n threshold = {}".format(index_test, threshold))



# smoothe image with median filter ------------------------------------------------------------

# VALIDATION
threshold = 127
index_val = 5
resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold)

# plot before median filter
plot_img(resmaps_val_uint8_th[index_val], title="resmaps_val_uint8_th[{}]\n threshold = {}".format(index_val, threshold))
# plot after median filter
resmaps_val_uint8_th_fil = filter_median_images(resmaps_val_uint8_th)
plot_img(resmaps_val_uint8_th_fil[index_val], title="resmaps_val_uint8_th_fil[{}]\n threshold = {}".format(index_val, threshold))


# TEST
threshold = 124
index_test = 68
resmaps_test_uint8_th = threshold_images(resmaps_test_uint8, threshold)

# plot before median filter
plot_img(resmaps_test_uint8_th[index_test], title="resmaps_test_uint8_th[{}]\n threshold = {}".format(index_test, threshold))
# plot after median filter
resmaps_test_uint8_th_fil = filter_median_images(resmaps_test_uint8_th)
plot_img(resmaps_test_uint8_th_fil[index_test], title="resmaps_test_uint8_th_fil[{}]\n threshold = {}".format(index_test, threshold)) 



# labeling --------------------------------------------------------------------------

# VALIDATION
threshold = 137
index_val = 5
resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold)
resmaps_val_uint8_th_fil = filter_median_images(resmaps_val_uint8_th)
resmaps_val_labeled, areas_all_val = label_images(resmaps_val_uint8_th_fil)
areas_all_1d_val = [item for sublist in areas_all_val for item in sublist]
plot_img(resmaps_val_labeled[index_val], title="resmaps_labeled[{}]\n threshold = {}".format(index_test, threshold))


# TEST
threshold = 137
index_val = 5
resmaps_test_uint8_th = threshold_images(resmaps_test_uint8, threshold)
resmaps_test_uint8_th_fil = filter_median_images(resmaps_test_uint8_th)
resmaps_test_labeled, areas_all_test = label_images(resmaps_test_uint8_th_fil)
areas_all_1d_test = [item for sublist in areas_all_test for item in sublist]
plot_img(resmaps_val_labeled[index_val], title="resmaps_labeled[{}]\n threshold = {}".format(index_test, threshold))


from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square

def label_images(images):
    """
    Segments images into images of connected components (anomalous regions).
    Returns segmented images and a list containing their areas. 
    """
    images_labeled = np.zeros(shape=images.shape)
    areas_all = []
    for i, image in enumerate(images):
        # segment current image in connected components
        image_labeled = label(image)
        images_labeled[i] = image_labeled
        # compute areas of anomalous regions in the current image
        regions = regionprops(image_labeled)
        areas = [region.area for region in regions]
        areas_all.append(areas)
    return images_labeled, areas_all



# investigating distribution of the size of anomalous regions with various thresholds -------------------------------

def get_max_area(resmaps, threshold):
    resmaps_th = threshold_images(resmaps, threshold)
    resmaps_fil = filter_median_images(resmaps_th)
    resmaps_labeled, areas_all = label_images(resmaps_fil)
    areas_all_1d = [item for sublist in areas_all for item in sublist]
    max_area = np.amax(np.array(areas_all_1d))    
    return max_area


#==================== ALGORITHM 1 (without area binning) ======================

# compute descriptive values
minimum = np.amin(resmaps_val_uint8)
maximum = np.amax(resmaps_val_uint8)
mu = resmaps_val_uint8.flatten().mean()
sigma = resmaps_val_uint8.flatten().std()
# scipy.stats.norm(mu, sigma).ppf(0.999)

# Compute threshold and area boundaries 
threshold_min = 126 # int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1
threshold_max = 156 # when nb_regions == 0, maximum
max_area = get_max_area(resmaps_val_uint8, threshold_min)

# initialize variables and parameters
thresholds = np.arange(threshold_min, threshold_max+1)
areas = np.arange(1, max_area+1)
counts = np.zeros(shape=(len(thresholds), max_area))

# loop over all thresholds and calculate area counts
for i, threshold in enumerate(thresholds):
    resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold)
    resmaps_val_uint8_th_fil = filter_median_images(resmaps_val_uint8_th)
    resmaps_val_labeled, areas_all_val = label_images(resmaps_val_uint8_th_fil)
    areas_all_val_1d = [item for sublist in areas_all_val for item in sublist]
    counts[i] = np.array([areas_all_val_1d.count(area) for area in areas])

# calculate sum of area counts (without binning) over all thresholds and plot
counts_sum = np.sum(counts, axis=0)
plt.figure()
plt.plot(areas, counts_sum)
# plt.bar(areas, counts_sum) # TRY !!!
plt.xlabel("areas_size")
plt.ylabel("counts_sum")
plt.title("sum of counts for thresholds in [{}, {}]".format(threshold_min, threshold_max))
plt.show()

# determine min area



# plot 
thresholds_to_plot = [132, 137, 141]
plt.figure()
for i, threshold in enumerate(thresholds_to_plot):
    j = list(thresholds).index(threshold)
    plt.plot(areas, counts[j], label="threshold = {}".format(threshold))
    # plt.bar(areas, counts) # TRY !!!

plt.title("sum of counts for thresholds in [{}, {}]".format(threshold_min, threshold_max))
plt.xlabel("areas_size")
plt.ylabel("counts")
plt.show()

# smooth curve (can be smoothed by binning the x-axis)
counts_sum_smooth = scipy.signal.savgol_filter(counts_sum, window_length=13, polyorder=3)
plt.figure()
plt.plot(areas, counts_sum, label="counts_sum")
plt.plot(areas, counts_sum_smooth, label="counts_sum_smooth")
plt.legend()
plt.xlabel("areas_size")
plt.ylabel("counts")
plt.grid(which="both")
plt.show()

#====================== ALGORITHM 2 (with area binning) =======================

def get_threshold_min(resmaps, ppf_value=0.97):
    # compute descriptive values
    minimum = np.amin(resmaps_val_uint8)
    maximum = np.amax(resmaps_val_uint8)
    mu = resmaps_val_uint8.flatten().mean()
    sigma = resmaps_val_uint8.flatten().std()
    th_min = int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1
    print("th_min = {} \n mu = {} \n sigma = {} \n min = {}\n max = {}".format(th_min, mu, sigma, minimum, maximum))
    return th_min

def get_xbars(edges):
    x_bars = edges[:-1] + ((edges[1] - edges[0]) / 2)
    return x_bars

    

def get_area_size_counts_multiple_thresholds(resmaps_val_uint8, th_min, th_max, nbins=200):
    # compute max_area
    max_area = get_max_area(resmaps_val_uint8, th_min)
    
    # initialize variables and parameters
    thresholds = np.arange(th_min, th_max+1)
    range_area = (0.5 , float(max_area)+0.5)
    counts = np.zeros(shape=(len(thresholds), nbins))
    
    # loop over all thresholds and calculate area counts (with binning)
    for i, threshold in enumerate(thresholds):
        resmaps_val_uint8_th = threshold_images(resmaps_val_uint8, threshold)
        resmaps_val_uint8_th_fil = filter_median_images(resmaps_val_uint8_th)
        resmaps_val_labeled, areas_all_val = label_images(resmaps_val_uint8_th_fil)
        areas_all_val_1d = [item for sublist in areas_all_val for item in sublist]
        count, edges = np.histogram(
                    areas_all_val_1d, 
                    bins=nbins, 
                    density=True, 
                    range=range_area
                )
        counts[i] = count
    return counts, edges

def get_sum_counts(counts, edges, th_min, th_max, plot=False):
    counts_sum = np.sum(counts, axis=0)
    x_bars = get_xbars(edges)    
    if plot:
        plt.figure()        
        plt.bar(x_bars, counts_sum, width=edges[1]-edges[0])
        plt.grid(which="both")
        plt.xlabel("areas_size")
        plt.ylabel("counts_sum (bins)")
        plt.title("sum of bin counts for thresholds in [{}, {}]".format(th_min, th_max))
        plt.show()
    return counts_sum, x_bars
    

# calculate sum of area counts (with binning) over all thresholds and plot
th_min = get_threshold_min(resmaps_val_uint8) # 126 # int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1
th_max = 156 # when nb_regions == 0, maximum 
counts, edges = get_area_size_counts_multiple_thresholds(resmaps_val_uint8, th_min, th_max)
counts_sum, x_bars = get_sum_counts(counts, edges, th_min, th_max, plot=True)

th_min = 129
counts, edges = get_area_size_counts_multiple_thresholds(resmaps_val_uint8, th_min, th_max)
counts_sum, x_bars = get_sum_counts(counts, edges, th_min, th_max, plot=True)


# determine min area ------------------------------------------------------------------------
counts_cumsum = np.cumsum(counts_sum)/np.sum(counts_sum)

th_min = get_threshold_min(resmaps_val_uint8_blur) # 126 # int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1
th_max = 156 # when nb_regions == 0, maximum 
counts, edges = get_area_size_counts_multiple_thresholds(resmaps_val_uint8, th_min, th_max)
counts_sum, x_bars = get_sum_counts(counts, edges, th_min, th_max, plot=True)



# fit histogram to an inverse exponential distribution ----------------------------------------------
tmp0 = scipy.stats.expon.pdf(counts_sum)
tmp1 = scipy.stats.expon.cdf(counts_sum)

plt.figure()
plt.plot(x_bars, scipy.stats.expon.cdf(counts_sum))
plt.grid(which="both")
plt.show()

# approximate area
# expon.ppf(0.01)

# ========================================================================

zlist = [get_max_area(resmaps_val_uint8, th) for th in list(range(132, 156))]



# VISUALIZING
def plot_area_distro_for_multiple_thresholds(resmaps, thresholds_to_plot, threshold_min, nbins=200, method="line", title="provide a title"):    
    # fix range so that counts have the save x value
    max_area = get_max_area(resmaps_val_uint8, threshold_min)
    range_area = (0.5 , float(max_area)+0.5)
    
    # compute residual maps for multiple thresholds
    fig = plt.figure(figsize=(12, 5))
    for threshold in thresholds_to_plot:
        resmaps_th = threshold_images(resmaps, threshold)
        resmaps_fil = filter_median_images(resmaps_th, kernel_size=3)
        resmaps_labeled, areas_all_val = label_images(resmaps_fil)
        areas_all_1d = [item for sublist in areas_all_val for item in sublist]       
        
        if method == "hist":            
            count, bins, ignored = plt.hist(
                areas_all_1d,
                bins=nbins,
                density=False,
                range=range_area, # previously commented
                histtype="barstacked",
                label="threshold = {}".format(threshold),
            )
        
        elif method == "line":
            count, bins = np.histogram(
                areas_all_1d, 
                bins=nbins, 
                density=False, 
                range=range_area # previously commented
            )
            bins_middle = bins[:-1] + ((bins[1] - bins[0]) / 2)
            plt.plot(
                bins_middle,
                count,
                linestyle="-",
                linewidth=0.5, # 0.5
                marker="x", # "o"
                markersize=0.5, # 0.5
                label="threshold = {}".format(threshold),
            )
            # plt.fill_between(bins_middle, count)
    
    plt.title(title)
    plt.legend()
    plt.xlabel("area size in pixel")
    plt.ylabel("count")
    plt.grid()
    plt.show()
    # return bins, count, areas_all_1d
    
threshold_min = 126 # int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1
    
thresholds_to_plot = [132, 137, 141] # [129, 135, 137, 139, 141]
title_val = "Distribution of anomaly areas' sizes for validation ResMaps with various Thresholds"
plot_area_distro_for_multiple_thresholds(resmaps_val_uint8, thresholds_to_plot, threshold_min, nbins=100, method="line", title=title_val)

resmaps_val_uint8_blur = filter_gauss_images(resmaps_val_uint8)
plot_area_distro_for_multiple_thresholds(resmaps_val_uint8_blur, thresholds_to_plot, 129, nbins=100, method="line", title="blur")

thresholds_to_plot = [132, 137, 141] # [129, 135, 137, 139, 141]
title_test = "Distribution of anomaly areas' sizes for test ResMaps with various Thresholds"
plot_area_distro_for_multiple_thresholds(resmaps_test_uint8, thresholds_to_plot, threshold_min, nbins=400, method="hist", title=title_test)


# investigating gaussian blur --------------------------------------------------------------------------------------------------------
threshold = 141
max_area = get_max_area(resmaps_val_uint8, threshold)
plot_area_distro_for_multiple_thresholds(resmaps_val_uint8, [threshold], threshold, nbins=max_area, method="line", title="no blur")

resmaps_val_uint8_blur = filter_gauss_images(resmaps_val_uint8)
max_area_blur = get_max_area(resmaps_val_uint8_blur, threshold)
plot_area_distro_for_multiple_thresholds(resmaps_val_uint8_blur, [threshold], threshold, nbins=max_area_blur, method="line", title="blur")



# compute descriptive values
mu = resmaps_val_uint8.flatten().mean()
sigma = resmaps_val_uint8.flatten().std()
int(round(scipy.stats.norm(mu, sigma).ppf(0.97), 1)) - 1


mu_blur = resmaps_val_uint8_blur.flatten().mean()
sigma_blur = resmaps_val_uint8_blur.flatten().std()
int(round(scipy.stats.norm(mu_blur, sigma_blur).ppf(0.97), 1)) - 1
# count_hand = np.array([areas_all.count(area) for area in range(1,max_area+1)])




# =============================================================================
# =============================================================================



# =============================================================================
# # investigate applying gaussian filter ----------------------------------
# threshold = 120
# resmaps_val_th_uint8 = threshold_images(resmaps_val_uint8, threshold)
# index_val = 5
# plot_img(resmaps_val_th_uint8[index_val], title="resmaps_test_th_uint8[{}]\n threshold = {}".format(index_val, threshold))
# =============================================================================



# =============================================================================
# # determine offset to previous method (no rescaling)

# resmaps_test_old_uint8 = img_as_ubyte(resmaps_test)
# hist_image_uint8(resmaps_test_old_uint8, range_x=(0,255), title="resmaps_test_old_uint8")
# threshold = 28
# # resmaps_test_th = threshold_images(resmaps_test, threshold)
# resmaps_test_old_th_uint8 = threshold_images(resmaps_test_old_uint8, threshold)
# index_test = 68
# plot_img(resmaps_test_old_th_uint8[index_test], title="resmaps_test_old_th_uint8[{}]\n threshold = {}".format(index_test, threshold))
# # OFFSET = 113
# =============================================================================


# =============================================================================
# =============================================================================

# ---------------------------------------------

# Convert to 8-bit unsigned int for further processing
resmaps_test = img_as_ubyte(resmaps_test)


# ---------------------------------------------

threshold = 0
# threshold residual maps
resmaps_th = threshold_images(resmaps_test, threshold)
index = 68
img = resmaps_th[index]  # resmaps_th
plot_img(img)

# ---------------------------------------------

# compute anomalous regions
resmaps_labeled, areas_all = label_images(resmaps_th)
index = 68
img = resmaps_labeled[index]  # resmaps_th
plot_img(img)

# ---------------------------------------------


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb


resmaps_labeled = label(resmaps_th)

index = 68

label_image = resmaps_labeled[index]
plt.imshow(label_image, cmap="nipy_spectral")

fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(label_image)


for region in regionprops(label_image):
    # take regions with large enough areas
    if region.area >= 10:
        # draw rectangle around segmented coins
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle(
            (minc, minr),
            maxc - minc,
            maxr - minr,
            fill=False,
            edgecolor="red",
            linewidth=2,
        )
        ax.add_patch(rect)


# https://scikit-image.org/docs/stable/api/skimage.measure.html#skimage.measure.label




# # OLD PATHS 
# imgs_test_input = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_28_a_50/imgs_test_input.npy", allow_pickle=True)
# imgs_test_pred = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_28_a_50/imgs_test_pred.npy", allow_pickle=True)
# resmaps_test = np.load("results/mvtec/capsule/mvtec2/MSE/25-02-2020_08-54-06/test/th_28_a_50/imgs_test_diff.npy", allow_pickle=True)