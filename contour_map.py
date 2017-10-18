import pyfits
import numpy as np


def find_std(pixdata):
    frame_size = len(pixdata)
    tl = pixdata[:frame_size/10, :frame_size/10]
    tr = pixdata[-frame_size/10::, :frame_size/10]
    bl = pixdata[:frame_size/10, -frame_size/10::]
    br = pixdata[-frame_size/10::, -frame_size/10::]
    return np.std(min([tl, tr, bl, br], key=np.mean))


def get_centre_pixel(pixdata):
    return int(len(pixdata)/2), int(len(pixdata)/2)


def get_pixel_neighbourhood(pixel, size):
    shifts = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    new_coords = [map(sum, zip(shift, pixel)) for shift in shifts]
    return new_coords

if __name__ == '__main__':
    f = pyfits.open('data/1.fits')
    pixdata = f[0].data
    print pixdata.shape
    # pixdata = pixdata[:10, :10]

    print find_std(pixdata)

    # print[map(tl, tr, bl, br
    # print pixdata
    # start_pixel = get_centre_pixel(pixdata)
    # frame_size = len(pixdata)
    # binary_map = np.full_like(pixdata, None)

    # print binary_map
    # print get_pixel_neighbourhood(start_pixel, frame_size)
