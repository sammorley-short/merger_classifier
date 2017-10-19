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
    new_coords = [tuple(map(sum, zip(shift, pixel))) for shift in shifts]
    # TODO: Make below more elegant
    new_coords = filter(lambda x: x[0] > 0 and x[0] < frame_size
                        and x[1] > 0 and x[1] < frame_size, new_coords)
    if threshold is None:
        new_coords = filter(lambda p: np.isnan(binary_map[p]), new_coords)
    else:
        new_coords = filter(lambda p: binary_map[p] > threshold, new_coords)
    return new_coords


def build_contour_map(pixdata, levels):
    """
    Builds contour map with given number of levels from input pixel data
    """
    std = find_std(pixdata)
    start_pixel = get_centre_pixel(pixdata)
    frame_size = len(pixdata)
    contour_runs = [[np.full_like(pixdata, None), i * std]
                    for i in range(1, levels + 1)]

    binary_maps = []
    for binary_map, threshold in contour_runs:

        if pixdata[start_pixel] < threshold:
            print "Initial pixel not hot"
            return np.full_like(pixdata, None)

        binary_map[start_pixel] = 1
        active_pix = get_pixel_neighbourhood(
            start_pixel, frame_size, binary_map)

        while active_pix:
            gen_pix = []
            for pixel in active_pix:
                if pixdata[pixel] > threshold:
                    binary_map[pixel] = 1
                    gen_pix += [pixel]
                else:
                    binary_map[pixel] = 0
            active_pix = \
                set(flatten([get_pixel_neighbourhood(gen_pixel, frame_size, binary_map)
                             for gen_pixel in gen_pix]))
        binary_maps += [np.nan_to_num(binary_map)]

    final_map = reduce(np.add, binary_maps)

    return final_map

if __name__ == '__main__':
    data_subdir = 'data'
    fits_data_subdir = 'fits'
    img_data_subdir = 'imgs'

    levels = 5

    userhome = os.path.expanduser('~')
    cwd = os.getcwd()
    fits_data_dir = os.path.join(cwd, data_subdir, fits_data_subdir)
    img_data_dir = os.path.join(cwd, data_subdir, img_data_subdir)
    for root, dirs, files in os.walk(fits_data_dir):
        for file in files:
            if file.endswith(".fits"):
                print file
                file_no = file[:-5]
                f = pyfits.open(os.path.join(root, file))
                pixdata = f[0].data
                final_map = build_contour_map(pixdata, levels)
                plt.imshow(final_map)
                plt.colorbar()
                img_file = file_no + '.png'
                plt.savefig(os.path.join(img_data_dir, img_file))
                plt.close()
                f.close()
