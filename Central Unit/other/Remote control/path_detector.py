"""This is a simplistic Path Detector.

    A Path Detector module is a python file that contains a `detect` function
    that is capable of analyzing a binarized image in which non-zero pixels
    indicate road boundaries. The analysis should identify the path (or,
    multiple paths) to follow.

    See the description of the `detect` function below for more details.

    This Simplistic Path Detector implements a first crude idea to path
    detection, and needs ample modification in order to obtain a working
    prototype.

    In this Simplistic Path Detector, a path is detected by sampling a single
    row towards the bottom of the image. Non-zero pixels are identified to
    infer the road between the car center and the road center is calculated and
    used as the path to follow. """

import logging
import numpy as np
import cv2
from scipy import ndimage
import time
import random

# Log which path detector is being used. This appears in the output. Useful
# for ensuring that the correct path detector is being used.
logging.info('Simplistic PathDetector has been initialized')

heading = 0
count = 0
temp_cont_r = None
temp_cont_l = None
temp_mid = None
choice = None
run = None

def detect(mask):
    global count
    global heading
    global temp_cont_l
    global temp_cont_r
    global temp_mid
    global choice
    #logging.data('1')
    
    """This function receives a binarized image in its `mask` argument
    (`mask` is a h x w  numpy array where h is the height and w the width).
    The non-zero pixels in the array encode road boundaries.
    The task of this function is to analyze the mask, and identify the path
    that the car should follow.

    Returns: a tuple (dict, img) where:
      `dict` is a dictionary that is transmitted to the state machine
           it should contain all the information that the state machine
           requires to actuate the identified path(s).
           Implementors are free to encode this information in the dictionary
           in any way that they like. Of course, the state machine needs to
           be written correspondingly to correctly decode the information.g

      `img` is optionally a numpy array (of the same width and height
            as the mask) that visualizes the found path. Used for
            visualization in the viewer only.
    """

    img_height, img_width = mask.shape
    x0 = int(img_width*.5)  # center of the image
    # row to sample (first row at the top is row zero)
    y0 = int(img_height*.75)
    # assume the car center is at coordinate (img_width/2, img_height)
    car_center = (x0, img_height)
    
    if count == 1:
        mask = cut_mask(mask, temp_cont_l, temp_cont_r, choice)
        test_stop_m = mask[y0-15, temp_mid]
        test_stop_l = mask[y0-15, temp_cont_l-15]
        test_stop_r = mask[y0-15, temp_cont_r+15]
        if test_stop_m == 0 and test_stop_l == 255 and test_stop_r == 255:
            count = 0

    # try to find the road center by sampling the horizontal line passing
    # through (x0,y0) -- find_center is a function defined further below
    road_center, contact_l, contact_r = find_center(mask, x0, y0, heading)
    if count == 0:
        run_l = cv2.countNonZero(mask[y0-12, contact_l-5:contact_l-2])
        run_r = cv2.countNonZero(mask[y0-12, contact_r+2:contact_r+5])
        if run_l == 0 or run_r == 0:
            count = 1
            choices = []
            test_front = mask[y0-95, contact_l+15: contact_r-15]
            test_left = mask[y0-45 : y0-25, contact_l-8]
            test_right = mask[y0-45 : y0-25, contact_r+8]
            if cv2.countNonZero(test_front) == 0:
                choices += [1]
            if cv2.countNonZero(test_left) == 0:
                choices += [2]
            if cv2.countNonZero(test_right) == 0:
                choices += [3]
            if choices != [] and 1 != len(choices):
                choice = random.choice(choices)
                temp_cont_l = contact_l
                temp_cont_r = contact_r
                temp_mid = int((temp_cont_l+temp_cont_r)/2)
            else:
                count = 0
  
    # calculate the angle between the vertical line that passes through
    # the car center and the line that connects the car center with the road
    # center -- model_to_heading is a function further defined below
    
    heading = model_to_heading(road_center, car_center)
    distance =  ((road_center[0] - \
    car_center[0])**2 + (road_center[1] - car_center[1])**2)**(1/2)
    
    # send the calculated information to the state machine
    # NOTE: one may want to extend the analysis and measure, e.g., how
    # reliable the path is (in other words: how long one thinks one could
    # follow it.) If this is measured one may also want to include it in
    # this dictionary so that the state
    # machine can use this.
    
    path_dict = {'heading': heading+12.15, 'distance': distance}

    # uncomment the following line if you want to print the dictionary
    # for debugging purposes
    # logging.debug('returning %s' % str(path_dict))

    # for debugging purposes, we visualize the above process

    # create a new image, of the same dimensions as mask, but colore
    path_img = np.zeros((img_height, img_width, 3), np.uint8)

    # Draw a small filled dot at the car center, 4 pixels wide, in blue
    cv2.circle(path_img, car_center, 4, (255, 0, 0), -1)

    # Draw a green line to display the row that was sampled
    cv2.line(path_img, (0, y0), (img_width, y0), (0, 255, 0))
    #if type(contact_r) == float and type(contact_l) == float:
    cv2.line(path_img, (contact_r, 0), (contact_r, img_height), (255, 0, 0))
    cv2.line(path_img, (contact_l, 0), (contact_l, img_height), (255, 0, 0))
    cv2.line(path_img, (contact_r+5, y0-45), (contact_r+5, y0-25), (0, 0, 255))
    cv2.line(path_img, (contact_l-5, y0-45), (contact_l-5, y0-25), (0, 0, 255))
    cv2.line(path_img, (contact_l+15, y0-95), (contact_r-15, y0-95), (0, 0, 255))
    cv2.line(path_img, (contact_l-8, y0-14), (contact_l-4, y0-14), (219, 0, 115))
    cv2.line(path_img, (contact_r+4, y0-14), (contact_r+8, y0-14), (219, 0, 115))
    # Draw a small filled dot at the calculated road center, 4 pixels wide,
    # in red
    cv2.circle(path_img, road_center, 4, (0, 0, 255), -1)
    cv2.circle(path_img, (x0, y0), 4, (255, 0, 0), -1)
    # Return the path dictionary and image. The path_dict will be sent
    # to the state machine. The path_img is displayed in the viewer
    return (path_dict, path_img)


def find_center(mask, x, y, heading):
    """Sample the horizontal line passing through coordinate (x,y) for non-zero
       pixels in mask to determine road center"""
    img_height, img_width = mask.shape
    sample_width = int(img_width/2)
    p0 = np.array([x, y])
    pl = np.array([x-sample_width, y])
    pr = np.array([x+sample_width, y])

    # Take 40 samples on the left and 40 samples on the right
    # profile is a function further defined below
    xl, yl, l_val = profile(mask, p0, pl, 40)
    xr, yr, r_val = profile(mask, p0, pr, 40)

    # now analyze the sampling: find the first non-zero pixel in the samples
    idx_l = np.nonzero(l_val)[0]
    idx_r = np.nonzero(r_val)[0]

    if idx_l.size == 0:
        # No non-zero pixel was found on the left. This means that we don't
        # see the left hand side of the road on row y0
        # arbitrarily set the road boundary at x = x0 - 30
        # this param ceter value (30) likely needs to be tuned
        # inutile, impossible avec angle de caméra
        contact_l = p0 + np.array([-30, 0])
    else:
        if idx_l[0] != 0 or heading <= 0:
        # Interpret the first non-zero pixel as the road boundary
            contact_l = np.array([xl[idx_l[0]], yl[idx_l[0]]])
        else:
            idx_l = [idx_l[i] for i in range(len(idx_l)) if idx_l[i] > 10] 
            contact_l = np.array([xl[idx_l[0]], yl[idx_l[0]]])
    if idx_r.size == 0:
        contact_r = p0 + np.array([30, 0])
    else:
        if idx_r[0] != 0 or heading >= 0:
            contact_r = np.array([xr[idx_r[0]], yr[idx_r[0]]])
        else:
            idx_r = [idx_r[i] for i in range(len(idx_r)) if idx_r[i] > 10]
            contact_r = np.array([xr[idx_r[0]], yr[idx_r[0]]])
    # we define the road center to be mid-way contact_l and contact_r
    center = (contact_l + contact_r) / 2
    return (int(center[0]), int(center[1])), int(contact_l[0]), int(contact_r[0])


def model_to_heading(model_xy, car_center_xy):
    """Calculate the angle (in degrees) between the vertical line that
       passes through the point `car_center_xy` and the line that connects
       `car_center_xy` with `model_xy`.
       A negative angle means that the car should turn clockwise; a positive
       angle that the car should move counter-clockwise."""
    dx = 1. * model_xy[0]-car_center_xy[0]
    dy = 1. * model_xy[1]-car_center_xy[1]

    heading = -np.arctan2(dx, -dy)*180/np.pi

    return heading


def profile(mask, p0, p1, num):
    """Takes `num` equi-distance samples on the straight line between point `p0`
       and point `p2` on binary image `mask`.

       Here, points p0 and p1 are 2D points (x-coord,y-coord)

       Returns: a triple (n, m, vals) where:
       - n is a numpy array of size `num` containing the x-coordinates of
         sampled points
       - m is a numpy array of size `num` containing the y-coordinates of
         sampled points
       - vals is a numpy array of size `num` containing the sampled point
         values, i.e.  vals[i] = mask[m[i], n[i]]
         (recall that images are indexed first on y-coordinate, then on
          x-coordinate)
     """
    n = np.linspace(p0[0], p1[0], num)
    m = np.linspace(p0[1], p1[1], num)
    return [n, m, ndimage.map_coordinates(mask, [m, n], order=0)]
    
def cut_mask(mask, temp_tact_l, temp_tact_r, choice):
    if choice == 3:
        mask[:, temp_tact_l] = 255
    elif choice == 2:
        mask[:, temp_tact_r] = 255
    else:
        mask[:, temp_tact_l], mask[:, temp_tact_r] = 255, 255
    return mask