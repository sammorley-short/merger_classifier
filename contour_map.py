import csv
import os.path
import sys
import pyfits
import itertools as it
import numpy as np
from matplotlib import pyplot as plt


def flatten(array, level=1):
    """ Flattens array to given level """
    for i in range(level):
        array = [item for sublist in array for item in sublist]
    return array


def find_std(pixdata):
    """
    Finds the standard deviation to use on contour map by finding std of
    darkest corner
    """
    frame_size = len(pixdata)
    tl = pixdata[:frame_size/10, :frame_size/10]
    tr = pixdata[-frame_size/10::, :frame_size/10]
    bl = pixdata[:frame_size/10, -frame_size/10::]
    br = pixdata[-frame_size/10::, -frame_size/10::]
    return np.std(min([tl, tr, bl, br], key=np.mean))


def get_centre_pixel(pixdata):
    """ Gets the central pixel to start CA from """
    return int(len(pixdata)/2), int(len(pixdata)/2)


def get_pixel_neighbourhood(pixel, frame_size, binary_map, threshold=None):
    shifts = it.product([0, 1, -1], [0, 1, -1])
    shifts.next()
    shifts = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    new_coords = [tuple(map(sum, zip(shift, pixel))) for shift in shifts]
    # TODO: Make below more elegant
    new_coords = filter(lambda x: x[0] > 0 and x[0] < frame_size
                        and x[1] > 0 and x[1] < frame_size, new_coords)
    if threshold is None:
        new_coords = filter(lambda p: np.isnan(binary_map[p]), new_coords)
    else:
        new_coords = filter(lambda p: binary_map[p] > threshold, new_coords)
    return new_coords


def build_contour_map(pixdata, levels=1):
    """
    Builds contour map with given number of levels from input pixel data
    """
    # If integer number of levels given, makes them equally spaced, else
    # follows the contours defined in the levels list
    contours = range(1, levels+1) if type(levels) is int else levels
    # Gets std of image,s tarting pixel and frame size
    std = find_std(pixdata)
    start_pixel = get_centre_pixel(pixdata)
    frame_size = len(pixdata)
    # Provides a blank bitmap for each run
    contour_runs = [[np.full_like(pixdata, None), i * std]
                    for i in contours]
    # For each contour level builds bitmap
    binary_maps = []
    for binary_map, threshold in contour_runs:
        # If first pixel not bright enough, sets bitmap to blank canvas
        if pixdata[start_pixel] < threshold:
            print "Initial pixel not hot enough (< %f)" % (threshold)
            binary_maps += [np.full_like(pixdata, 0)]
            break
        binary_map[start_pixel] = 1
        # Gets initial set of starter pixels
        active_pix = \
            get_pixel_neighbourhood(start_pixel, frame_size, binary_map)
        # While active pixels exist, keep searching
        while active_pix:
            # Tracks pixels that are found above threshold this round
            gen_pix = []
            # If pixel below threshold, set to 0, else 1 and add to gen pixels
            for pixel in active_pix:
                if pixdata[pixel] > threshold:
                    binary_map[pixel] = 1
                    gen_pix += [pixel]
                else:
                    binary_map[pixel] = 0
            # Gets next set of active pixels from gen pixels
            active_pix = \
                set(flatten([get_pixel_neighbourhood(gen_pixel, frame_size,
                                                     binary_map)
                             for gen_pixel in gen_pix]))
        # Saves bitmap
        binary_maps += [np.nan_to_num(binary_map)]
    # Adds all the binary maps together to produce final map
    final_map = reduce(np.add, binary_maps)
    return final_map


def batch_apply_bitmap(main_dir, fits_subdir, img_subdir, levels):
    """
    Applies bitmap to multiple fits files in directory and outputs images to
    another subdirectory. Writes pngs with same name as fits file
    """
    # Builds os-specific directory addresses
    userhome = os.path.expanduser('~')
    cwd = os.getcwd()
    fits_data_dir = os.path.join(cwd, main_dir, fits_subdir)
    img_data_dir = os.path.join(cwd, main_dir, img_subdir)
    # Walks over files in fits directory
    for root, dirs, files in os.walk(fits_data_dir):
        for file in files:
            if file.endswith(".fits"):
                print "Processing %s" % (file)
                file_no = file[:-5]
                # Opens file and gets pixel data
                f = pyfits.open(os.path.join(root, file))
                pixdata = f[0].data
                # Builds contour map
                final_map = build_contour_map(pixdata, levels)
                # Plots image and saves
                plt.imshow(final_map)
                plt.colorbar()
                img_file = file_no + '.png'
                plt.savefig(os.path.join(img_data_dir, img_file))
                plt.close()
                f.close()


if __name__ == '__main__':
    main_dir = 'data'
    fits_subdir = 'fits'
    img_subdir = 'imgs'

    levels = [1, 10, 100]

    batch_apply_bitmap(main_dir, fits_subdir, img_subdir, levels)
