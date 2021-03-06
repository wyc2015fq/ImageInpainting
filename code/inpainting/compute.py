## CSC320 Winter 2016 
## Assignment 2
## (c) Kyros Kutulakos
##
## DISTRIBUTION OF THIS CODE ANY FORM (ELECTRONIC OR OTHERWISE,
## AS-IS, MODIFIED OR IN PART), WITHOUT PRIOR WRITTEN AUTHORIZATION 
## BY THE INSTRUCTOR IS STRICTLY PROHIBITED. VIOLATION OF THIS 
## POLICY WILL BE CONSIDERED AN ACT OF ACADEMIC DISHONESTY

##
## DO NOT MODIFY THIS FILE ANYWHERE EXCEPT WHERE INDICATED
##

import numpy as np
import cv2 as cv

# File psi.py define the psi class. You will need to 
# take a close look at the methods provided in this class
# as they will be needed for your implementation
import psi        

# File copyutils.py contains a set of utility functions
# for copying into an array the image pixels contained in
# a patch. These utilities may make your code a lot simpler
# to write, without having to loop over individual image pixels, etc.
import copyutils

#########################################
## PLACE YOUR CODE BETWEEN THESE LINES ##
#########################################

# If you need to import any additional packages
# place them here. Note that the reference 
# implementation does not use any such packages

#########################################
#
#########################################
#
# Computing the Patch Confidence C(p)
#
# Input arguments: 
#    psiHatP: 
#         A member of the PSI class that defines the
#         patch. See file inpainting/psi.py for details
#         on the various methods this class contains.
#         In particular, the class provides a method for
#         accessing the coordinates of the patch center, etc
#    filledImage:
#         An OpenCV image of type uint8 that contains a value of 255
#         for every pixel in image I whose color is known (ie. either
#         a pixel that was not masked initially or a pixel that has
#         already been inpainted), and 0 for all other pixels
#    confidenceImage:
#         An OpenCV image of type uint8 that contains a confidence 
#         value for every pixel in image I whose color is already known.
#         Instead of storing confidences as floats in the range [0,1], 
#         you should assume confidences are represented as variables of type 
#         uint8, taking values between 0 and 255.
#
# Return value:
#         A scalar containing the confidence computed for the patch center
#

def computeC(psiHatP=None, filledImage=None, confidenceImage=None):
    assert confidenceImage is not None
    assert filledImage is not None
    assert psiHatP is not None
    
    #########################################
    ## PLACE YOUR CODE BETWEEN THESE LINES ##
    #########################################
    cwindow, _ = copyutils.getWindow(confidenceImage, psiHatP._coords, psiHatP._w)
    filled, valid = copyutils.getWindow(filledImage, psiHatP._coords, psiHatP._w)
    psiPArea = valid.sum()
    C = cwindow[filled>0].sum() / psiPArea
    #########################################
    
    return C

#########################################
#
# Computing the max Gradient of a patch on the fill front
#
# Input arguments: 
#    psiHatP: 
#         A member of the PSI class that defines the
#         patch. See file inpainting/psi.py for details
#         on the various methods this class contains.
#         In particular, the class provides a method for
#         accessing the coordinates of the patch center, etc
#    filledImage:
#         An OpenCV image of type uint8 that contains a value of 255
#         for every pixel in image I whose color is known (ie. either
#         a pixel that was not masked initially or a pixel that has
#         already been inpainted), and 0 for all other pixels
#    inpaintedImage:
#         A color OpenCV image of type uint8 that contains the 
#         image I, ie. the image being inpainted
#
# Return values:
#         Dy: The component of the gradient that lies along the 
#             y axis (ie. the vertical axis).
#         Dx: The component of the gradient that lies along the 
#             x axis (ie. the horizontal axis).
#
    
def computeGradient(psiHatP=None, inpaintedImage=None, filledImage=None):
    assert inpaintedImage is not None
    assert filledImage is not None
    assert psiHatP is not None
    
    #########################################
    ## PLACE YOUR CODE BETWEEN THESE LINES ##
    #########################################
    # Sobel filter kernel size
    kw = 1
    sobel_size = 2 * kw + 1
    # Get target patch pixels
    inpainted, _ = copyutils.getWindow(inpaintedImage, psiHatP._coords, psiHatP._w)
    inpainted = cv.cvtColor(inpainted, cv.COLOR_BGR2GRAY)
    filled, _ = copyutils.getWindow(filledImage, psiHatP._coords, psiHatP._w)
    # Using Sobel/Scharr filter to calculate gradients at each pixel
    Gx = cv.Scharr(src=inpainted, ddepth=cv.CV_32F, dx=1, dy=0, borderType=cv.BORDER_REPLICATE)
    Gy = cv.Scharr(src=inpainted, ddepth=cv.CV_32F, dx=0, dy=1, borderType=cv.BORDER_REPLICATE)
    # Valid gradient should be calculated from all filled pixels
    erode_kernel = np.ones((sobel_size,sobel_size),np.uint8)
    filled_eroded = cv.erode(filled, erode_kernel, borderType=cv.BORDER_REPLICATE,iterations=1)
    Gx *= filled_eroded>0
    Gy *= filled_eroded>0
    # Find the maximum gradient in the target patch as the patch's gradient
    d = np.sqrt(Gx**2 + Gy**2)
    dmax = d == d.max()
    # Change coordinations to kivy's display coordination
    Dx = -Gy[dmax][0]
    Dy = Gx[dmax][0]
    #########################################
    
    return Dy, Dx

#########################################
#
# Computing the normal to the fill front at the patch center
#
# Input arguments: 
#    psiHatP: 
#         A member of the PSI class that defines the
#         patch. See file inpainting/psi.py for details
#         on the various methods this class contains.
#         In particular, the class provides a method for
#         accessing the coordinates of the patch center, etc
#    filledImage:
#         An OpenCV image of type uint8 that contains a value of 255
#         for every pixel in image I whose color is known (ie. either
#         a pixel that was not masked initially or a pixel that has
#         already been inpainted), and 0 for all other pixels
#    fillFront:
#         An OpenCV image of type uint8 that whose intensity is 255
#         for all pixels that are currently on the fill front and 0 
#         at all other pixels
#
# Return values:
#         Ny: The component of the normal that lies along the 
#             y axis (ie. the vertical axis).
#         Nx: The component of the normal that lies along the 
#             x axis (ie. the horizontal axis).
#
# Note: if the fill front consists of exactly one pixel (ie. the
#       pixel at the patch center), the fill front is degenerate
#       and has no well-defined normal. In that case, you should
#       set Nx=None and Ny=None
#

def computeNormal(psiHatP=None, filledImage=None, fillFront=None):
    assert filledImage is not None
    assert fillFront is not None
    assert psiHatP is not None

    #########################################
    ## PLACE YOUR CODE BETWEEN THESE LINES ##
    #########################################
    kw = 1
    size = 2 * kw + 1
    # Get target patch's pixels in fill front image
    front, _ = copyutils.getWindow(fillFront, psiHatP._coords, kw)
    # Center pixel's gradient
    Gx = cv.Scharr(src=front, ddepth=cv.CV_32F, dx=1, dy=0, borderType=cv.BORDER_REPLICATE)[kw][kw]
    Gy = cv.Scharr(src=front, ddepth=cv.CV_32F, dx=0, dy=1, borderType=cv.BORDER_REPLICATE)[kw][kw]
    # Change to unit vector
    d = np.sqrt(Gy**2 + Gx**2)
    if d != 0:
        Gx /= d
        Gy /= d
    #  Change coordinations to kivy's display coordination
    Ny = Gy
    Nx = Gx
    #########################################

    return Ny, Nx