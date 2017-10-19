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
    frame_size = len(pixdata)
    tl = pixdata[:frame_size/10, :frame_size/10]
    tr = pixdata[-frame_size/10::, :frame_size/10]
    bl = pixdata[:frame_size/10, -frame_size/10::]
    br = pixdata[-frame_size/10::, -frame_size/10::]
    return np.std(min([tl, tr, bl, br], key=np.mean))


def get_centre_pixel(pixdata):
    return int(len(pixdata)/2), int(len(pixdata)/2)


def get_pixel_neighbourhood(pixel, frame_size, binary_map, threshold=None):
    shifts = it.product([0, 1, -1], [0, 1, -1])
    shifts.next()
    new_coords = [tuple(map(sum, zip(shift, pixel))) for shift in shifts]
    # Make more elegant
    new_coords = filter(lambda x: x[0] > 0 and x[0] < frame_size
                        and x[1] > 0 and x[1] < frame_size, new_coords)
    if threshold is None:
        new_coords = filter(lambda p: np.isnan(binary_map[p]), new_coords)
    else:
        new_coords = filter(lambda p: binary_map[p] > threshold, new_coords)
    return new_coords

if __name__ == '__main__':
    f = pyfits.open('data/1.fits')
    pixdata = f[0].data
    std = find_std(pixdata)
    start_pixel = get_centre_pixel(pixdata)
    frame_size = len(pixdata)
    binary_map = np.full_like(pixdata, None)

    if pixdata[start_pixel] < std:
        print "Initial pixel not hot"
        sys.exit()

    binary_map[start_pixel] = 1
    active_pix = get_pixel_neighbourhood(start_pixel, frame_size, binary_map)

    while active_pix:
        gen_pix = []
        for pixel in active_pix:
            if pixdata[pixel] > std:
                binary_map[pixel] = 1
                gen_pix += [pixel]
            else:
                binary_map[pixel] = 0
        active_pix = \
            set(flatten([get_pixel_neighbourhood(gen_pixel, frame_size, binary_map)
                         for gen_pixel in gen_pix]))

    # for i in [1]:
    #     new_std = (i + 1) * std

    #     binary_map[start_pixel] = i + 1
    #     active_pix = \
    #         get_pixel_neighbourhood(start_pixel, frame_size, binary_map)

    #     while active_pix:
    #         gen_pix = []
    #         for pixel in active_pix:
    #             if pixdata[pixel] > new_std:
    #                 binary_map[pixel] = i + 1
    #                 gen_pix += [pixel]
    #             else:
    #                 binary_map[pixel] = i
    #         active_pix = \
    #             set(flatten([get_pixel_neighbourhood(gen_pixel, frame_size,
    #                                                  binary_map, i)
    #                          for gen_pixel in gen_pix]))

    print np.unique(binary_map)

    plt.imshow(binary_map)
    plt.colorbar()
    plt.savefig('fig.png')
