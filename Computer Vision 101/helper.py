import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def load_my_image(fname = 'dog-breed-identification/train/0246f44bb123ce3f91c939861eb97fb7.jpg'):
    '''returns array containing greyscale values for supplied file (at thumbnail size)'''
    image_color = Image.open(fname).resize((90, 125), Image.ANTIALIAS)
    image_grayscale = image_color.convert('L')
    image_array = np.asarray(image_grayscale)
    return(image_array)

def apply_conv_locally(conv, image_section):
    '''Returns output of applying conv to image_section. Both inputs are numpy arrays.
    image_section is assumed to be same size/shape as conv.
    '''
    out = (conv * image_section).sum()
    return out

def scale_for_display(image):
    '''Scales numpy array containing image data to be integers in range [0, 256]'''
    out = image - image.min()
    out = (out / out.max() * 256)
    return out.astype(int)


def apply_conv_to_image(conv, image):
    '''Applies conv (supplied as list of lists) to image (supplied as numpy array). Returns output array'''
    assert(type(image) == np.ndarray)
    print("----------------------------")
    print("Filter: ")
    print(np.array(conv))
    image_height, image_width = image.shape
    conv_array = np.array(conv)
    conv_height, conv_width = conv_array.shape
    filtered_image_height = image.shape[0] - conv_height + 1
    filtered_image_width = image.shape[1] - conv_width + 1
    filtered_image = np.zeros((filtered_image_height, filtered_image_width))
    for i in range(filtered_image_height):
        for j in range(filtered_image_width):
            filtered_image[i, j] = apply_conv_locally(conv_array, image[i:i+conv_height, j:j+conv_width])
    return(filtered_image)

def show(image, scale_before_display=True):
    '''Displays numpy array as image.  Scale_before_display ensures values are integers in [0, 256]'''
    if scale_before_display:
        to_display = scale_for_display(image)
    else:
        to_display = image
    plt.imshow(to_display, cmap='gray')
    plt.axis('off')
    plt.show()