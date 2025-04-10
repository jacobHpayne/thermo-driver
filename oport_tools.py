### import directories needed to read through a folder and open FITS images
### runs in a virtual environment with Python 3.12.3, PATH = /Users/jacobpayne/Documents/UIOWA/OATLAB/OPORT/data_analysis/.venv/bin/python

import os
import sys
import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.io import ascii
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
from math import sqrt
from math import ceil


def get_fits_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.endswith('.fit'):
            files.append(file)
    return files

def get_asi294_resolution(data):
    ### return the scale factor of the image
    # details from https://www.zwoastro.com/product/asi294mm-mc/
    # 2.3 um pixel size
    # full resolution is 8288 x 5644
    x_full = 8288
    y_full = 5644
    y_img,x_img = data.shape
    return x_full/x_img

def center_of_mass(data):
    ms_data = data - np.mean(data)
    ms_data[ms_data<0] = 0
    x_com = int(np.sum(np.arange(data.shape[1]) * np.sum(ms_data, axis=0)) / np.sum(ms_data))
    y_com = int(np.sum(np.arange(data.shape[0]) * np.sum(ms_data, axis=1)) / np.sum(ms_data))
    return [x_com, y_com]

def get_ee(data, x=None, y=None, r = 100):
    ### returns a list of encircled energy values, for each radius up to r
    print("calculating encircled energy slowly (use get_ee_faster!)...")
    encircled_energy = list()
    for radius in range(1, r):
        mask = np.zeros(data.shape)
        # make a circular mask centered at the center of mass
        for i in range(x-r, x+r):
            for j in range(y-r, y+r):
                if mask[j,i] != 1:
                    if sqrt((i-x)**2 + (j-y)**2) < radius:
                        mask[j,i] = 1
        # calculate the encircled energy
        encircled_energy.append(np.sum(data[mask==1])/(np.sum(data))) #normalized by the mean of the background-subtracted data
    return encircled_energy

def get_ee_faster(data, x, y, r):
    #print("finding encircled energy...")
    encircled_energy=np.zeros(r+1)
    for i in range(x-r,x+r):
        for j in range(y-r,y+r):
            if sqrt((i-x)**2 + (j-y)**2) < r:
                encircled_energy[int(ceil(sqrt((i-x)**2 + (j-y)**2)))] = encircled_energy[int(ceil(sqrt((i-x)**2 + (j-y)**2)))]+data[j,i]
    #add inner rings
    for ring in range(1,r+1):
        encircled_energy[ring] = encircled_energy[ring]+encircled_energy[ring-1]
    #normalize
    return encircled_energy/encircled_energy[-1]

def plot_ee(energy, mm_res, title_string):
    ### add a subplot of encericled energy vs radius
    print("plotting encircled energy (use plot_fits!)...")
    plt.plot(energy)
    plt.xlabel('Radius (pixels)')
    plt.ylabel('Encircled Energy')
    plt.title(title_string)

    #get ee_val
    ee_50 = 0
    ee_95 = 0
    #get index at which the energy is greater than val
    for i in range(len(energy)):
        if energy[i] >= 0.5 and ee_50 != 0:
            ee_50 = i
        if energy[i] >= 0.95:
            ee_95 = i
            break
    #print the first 3 digits of ee_val in mm
    plt.text(ee_50, 0.50, '50% ee = {:.3f} mm'.format(ee_50/mm_res), ha='left', color='b')
    plt.text(ee_95, 0.95, '95% ee = {:.3f} mm'.format(ee_95/mm_res), ha='left', color='b')
    plt.show()
    return

def plot_fits(data, x, y, mm_res, energy, title_string, cmap='viridis'):
    #fig, (axs['C'], axs['A'], axs['B']) = plt.subplots(1, 3)
    fig, axs = plt.subplot_mosaic('AB;CD', layout='constrained')
    fig.suptitle(title_string, fontsize=18, fontweight='bold')
    axs['C'].set_title("Image")
    axs['A'].set_title("Encircled Energy")
    axs['B'].set_title("Pixel Values on the horizontal center line")

    axs['C'].imshow(data, cmap)
    #plt.colorbar()

    # plot a red reticule of around the center of "mass"
    center = plt.Circle((x, y), 5, color='r', fill=True)

    circle_1mm = plt.Circle((x, y), mm_res/2, color='r', fill=False) # 1 mm diameter
    axs['C'].text(x, y-(mm_res/2), 'Ø 1 mm', ha='left', color='w')

    #circle_2mm = plt.Circle((x, y), 2*(mm_res/2), color='r', fill=False) # 2 mm diameter
    #ax1.text(x, y-2*(mm_res/2), 'Ø 2 mm', ha='left', color='w')

    circle_3mm = plt.Circle((x, y), 3*(mm_res/2), color='r', fill=False) # 3 mm diameter
    axs['C'].text(x, y-3*(mm_res/2), 'Ø 3 mm', ha='left', color='w')

    axs['C'].add_artist(center)
    axs['C'].add_artist(circle_1mm)
    #ax1.add_artist(circle_2mm)
    axs['C'].add_artist(circle_3mm)

    # add a scale bar
    axs['C'].plot([data.shape[1]-(100+mm_res), data.shape[1]-100], [data.shape[0]-100, data.shape[0]-100], 'w', lw=2) #[x1, x2], [y1, y2]
    axs['C'].text(data.shape[1]-300, data.shape[0]-150, '1 mm', ha='center', color='w')

    ### add a subplot of encericled energy vs radius
    #print("plotting encircled energy...")
    axs['A'].plot(np.linspace(start=0,stop=len(energy)/mm_res,num=len(energy)),energy)
    axs['A'].set_xlabel('Radius (mm)')
    axs['A'].set_ylabel('Normalized Encircled Energy')

    #get ee_val
    ee_50 = 0
    ee_95 = 0
    #get index at which the energy is greater than val
    for i in range(len(energy)):
        if energy[i] >= 0.5 and ee_50 == 0:
            ee_50 = i
        if energy[i] >= 0.95:
            ee_95 = i
            break
    #print the first 3 digits of ee_val in mm
    #axs['A'].text(0, 0.50, '50% ee = {:.3f} mm'.format(ee_50/mm_res), ha='left', color='b', fontsize=12)
    #axs['A'].text(0, 0.95, '95% ee = {:.3f} mm'.format(ee_95/mm_res), ha='left', color='b', fontsize=12)
    axs['A'].text(0.5, 0.1, 'This plot is normalized by\nthe total Encircled Energy\nwithin Ø {:.3f} mm'.format(2*(len(energy)-1)/mm_res), ha='left', color='k',fontsize=12, bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.3'))
    #print('50% ee = {:.3f} mm'.format(ee_50/mm_res))
    #print('95% ee = {:.3f} mm'.format(ee_95/mm_res))

    ### add a subplot of the pixel values to look for a saturation plateu
    # get the linear slice of the center of the data
    r = len(energy)-1
    plateu = data[y, x-r:x+r]
    axs['B'].plot(plateu)
    axs['B'].set_xlabel('Pixel')
    axs['B'].set_ylabel('Pixel Value')

    ### print the terminal output
    axs['D'].text(0,1,("Analyzing: "+title_string), ha='left', family='monospace')
    axs['D'].text(0,0.9,("Data shape: "+str(data.shape)), ha='left', family='monospace')
    axs['D'].text(0,0.8,("Center of mass: ("+str(y)+", "+str(x)+")"), ha='left', family='monospace')
    axs['D'].text(0,0.7,("1mm = "+str(mm_res)+" pixels"), ha='left', family='monospace')
    axs['D'].text(0,0.6,("50% ee = {:.3f} mm".format(ee_50/mm_res)), ha='left', family='monospace')
    axs['D'].text(0,0.5,("95% ee = {:.3f} mm".format(ee_95/mm_res)), ha='left', family='monospace')
    # do not display the axis
    axs['D'].axis('off')
    
    plt.show()
    return

def get_background_subtracted_image(data, x, y, r):
    # edit the image data by subtracking background
    # The background is everything outside a study radius
    background_mask = np.ones(data.shape)
    background_mask[x-r:x+r, y-r:y+r] = 0
    background = np.mean(data[background_mask==1])
    bkgd_subtracted = np.subtract(data, background)
    bkgd_subtracted[bkgd_subtracted<0] = 0
    return bkgd_subtracted


def main():
    # path = '/Users/jacobpayne/Documents/UIOWA/OATLAB/OPORT/data_analysis/SPM008_manual_focus_sweep'
    path = '/Users/jacobpayne/Documents/UIOWA/OATLAB/OPORT/data_analysis/'
    sample_folder = 'SE25-1'
    files = get_fits_files(path+sample_folder)
    print("In Folder: ", path+sample_folder)
    for file in files:
        print("Analyzing File: ", file)
        file_path = path+sample_folder+"/"+file

        # get data from fits
        hdulist = fits.open(file_path)
        data = hdulist[0].data
        hdulist.close()

        #find the resolution
        binning = get_asi294_resolution(data)
        mm_res = int(ceil(1000/2.3/binning))

        ### set the radius for the encircled energy and background calculations
        # 3*1/2 = 1.5 mm radius
        r = int(ceil(3*(mm_res/2))) 
        #print("Data shape: ", data.shape)
        #print("1mm = ",mm_res," pixels")

        # find the center of mass
        x_com, y_com = center_of_mass(data)
        #print("Center of mass: (", y_com,", ",x_com,")")

        #ee = get_ee_faster(data, x_com, y_com, r)
        #plot_fits(data, x_com, y_com, mm_res, ee, "Raw Image")
        #plot_ee(ee, mm_res, "Encirlced Energy")
        
        bk_sub = get_background_subtracted_image(data, x_com, y_com, r)
        bk_sub_ee = get_ee_faster(bk_sub, x_com, y_com, r)
        plot_fits(bk_sub, x_com, y_com, mm_res, bk_sub_ee, sample_folder+" Background Subtracted Data", "Greys_r")
        #plot_ee(bk_sub_ee, mm_res, "Background Subtracted Encirlced Energy")
    return

main()
