from czifile import CziFile
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import blob_log
from scipy.ndimage.filters import gaussian_filter

def load_frame(fname, z, channel, smooth=True, sigma=3):
    """
    Load a frame, specifying z and channel.

    Parameters
    ---
    fname: str, file path to a .czi file.
    z: scalar, index of frame on the stack.
    channel: scalar, channel number.
    smooth (optional): boolean, smooths if True.
    sigma (optional): scalar, area over which to smooth.

    Return
    ---
    frame: (x,y) array, smoothed (or unsmoothed) frame.
    """

    # Opens the czi file and converts its contents into an array.
    with CziFile(fname) as czi:
        im = czi.asarray()

    im = np.squeeze(im)         # Eliminates the singleton dimensions.
    frame = im[channel,z]       # Indexes the channel and plane.

    # Smooths the image.
    if smooth:
        frame = gaussian_filter(frame, sigma)

    return frame


def detect_blobs(frame, threshold=0.04, min_sigma=10, max_sigma=30):
    """
    Detect blobs in an array.

    Parameters
    ---
    frame: (x,y) array, image to analyze.
    threshold (optional): scalar, threshold for blob detection, see doc for blog_log().
    min_sigma (optional): scalar, roughly the minimum size of blob allowed, see doc for blob_log().
    max_sigma (optional): scalar, roughly the maximum size of blob allowed, see doc for blob_log().

    Return
    ---
    blobs: (n,3) array, n detected blobs. Each row is (y,x,r) where x and y are coordinates and r is radius.
    """

    # Do blob detection.
    blobs = blob_log(frame, threshold=threshold, min_sigma=min_sigma, max_sigma=max_sigma)

    return blobs

def plot_blobs(frame, blobs, channel, ax=None):
    """
    Plots image and overlays detected cell bodies.

    Parameters
    ---
    frame: (x,y) array, image to plot.
    blobs: (n,3) array, detected blobs.
    channel: scalar, channel used, needed for color palette in plot.
    ax (optional): Axes object, axis on which to plot. If not specified, produces new figures.
    """

    # If axis handle is not given, make a figure.
    if ax is None:
        fig, ax = plt.subplots()

    # Plot 2nd channel in blue with red cells and 3rd channel in green with black cells.
    if channel == 1:
        color = 'Blues'
        circle_color = 'red'
    elif channel == 2:
        color = 'Greens'
        circle_color = 'black'
    else:
        raise ValueError('Channel must be 1 or 2') # Catch instances where an unsupported channel is entered.

    # Plot the image with the specified palette. Make it slightly transparent (alpha).
    i = ax.imshow(frame, cmap=color, alpha=0.7)

    # Improve the contrast. Feel free to omit this line for a more genuine image.
    i.set_clim(20, frame.max() / 5)

    # For each detected cell, store its coordinates then plot a circle centered around it.
    for blob in blobs:
        y,x,r= blob
        c = plt.Circle((x,y), r, fill=False, color=circle_color, linewidth=1, alpha=0.5) # Makes circle object.
        ax.add_patch(c)     # This line actually plots the circle.

    return ax


def analyze_frame(fname, z):
    """
    Wrapper function for cell counting.

    Parameters
    ---
    fname: str, file path to .czi file.
    z: scalar, index of frame on the stack.

    Returns
    ---
    ch1_blobs and ch2_blobs: (n,3) arrays, coordinates and size of detected neurons from each channel.
    """

    # Load the frames from both channels.
    ch1 = load_frame(fname, z, channel=1)
    ch2 = load_frame(fname, z, channel=2)

    # Detect blobs from both channels.
    ch1_blobs = detect_blobs(ch1)
    ch2_blobs = detect_blobs(ch2)

    # Plot both channels.
    fig, ax = plt.subplots()    # Make a common axis for both plots.
    plot_blobs(ch2, ch2_blobs, 2, ax)
    plot_blobs(ch1, ch1_blobs, 1, ax)

    return ch1_blobs, ch2_blobs

if __name__ == '__main__':
    # Replace this with your own file path.
    fname = r'C:\Users\William Mau\PycharmProjects\PythonForNeuro\Data\C1F2_S1_L.czi'

    # Analyze 1 plane.
    analyze_frame(fname,z=9)
    plt.show()

    # Analyze multiple planes.
    for i in np.arange(3,10):
        analyze_frame(fname, z=i)
    plt.show()