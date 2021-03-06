# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 14:44:07 2018

@author: shirhe-lyh
"""

import cv2
import numpy as np
import os


def alpha_matte(image):
    """Returns the alpha channel of a given image."""
    if image.shape[2] > 3:
        alpha = image[:, :, 3]
        alpha = np.where(alpha > 0, 1, 0)
    else:
        reduced_image = np.sum(np.abs(255 - image), axis=2)
        alpha = np.where(reduced_image > 100, 1, 0)
    alpha = alpha.astype(np.uint8)
    return alpha


def trimap(mask, mode='mask', boundary_width=50, 
           kernel_size_low=25, kernel_size_high=75):
    """Returns the trimap of a given mask."""
    if mode == 'trivial':
        return np.ones_like(mask, dtype=np.uint8) * 128
    elif mode == 'boundary':
        trimap_b = np.ones_like(mask, dtype=np.uint8) * 128
        trimap_b[:boundary_width] = 0
        trimap_b[-boundary_width:] = 0
        trimap_b[:, :boundary_width] = 0
        trimap_b[:, -boundary_width:] = 0
        return trimap_b
    
    erode_kernel_size = np.random.randint(kernel_size_low, kernel_size_high)
    dilate_kernel_size = np.random.randint(kernel_size_low, kernel_size_high)
    erode_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (erode_kernel_size, erode_kernel_size))
    dilate_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (dilate_kernel_size, dilate_kernel_size))
    eroded_alpha = cv2.erode(mask, erode_kernel)
    dilated_alpha = cv2.dilate(mask, dilate_kernel)
    
    trimap_d = np.where(dilated_alpha > 0, 128, 0)
    trimap_e = np.where(eroded_alpha > 0, 127, 0)
    trimap_sum = trimap_d + trimap_e
    trimap_sum = trimap_sum.astype(np.uint8)
    return trimap_sum


def provide(txt_path, images_fg_dir=None, images_bg_dir=None, 
            trimaps_dir=None, masks_dir=None):
    """Returns the paths of images.
    
    Args:
        txt_path: A .txt file with format:
            [image_fg_0, image_bg_0,
             image_fg_1, image_bg_1,
             ...]
            representing the 1-1 correspondence of foreground and background
            images.
        images_fg_dir: Path to the foreground images directory.
        images_bg_dir: Path to the background images directory.
        trimaps_dir: Path to the trimaps directory.
        
    Returns:
        The paths of foreground and background images.
    """
    if not os.path.exists(txt_path):
        raise ValueError('`txt_path` does not exist.')
        
    with open(txt_path, 'r') as reader:
        txt_content = np.loadtxt(reader, str, delimiter=' ')
        np.random.shuffle(txt_content)
    if images_fg_dir is None and images_bg_dir is None:
        return txt_content
    image_paths = []
    for image_fg_path, image_bg_path, trimap_path, mask_path in txt_content:
        image_fg_abs_path = image_fg_path
        image_bg_abs_path = image_bg_path
        trimap_abs_path = trimap_path
        mask_abs_path = mask_path
        if images_fg_dir is not None:
            image_fg_abs_path = os.path.join(images_fg_dir, image_fg_path)
        if images_bg_dir is not None:
            image_bg_abs_path = os.path.join(images_bg_dir, image_bg_path)
        if trimaps_dir is not None:
            trimap_abs_path = os.path.join(trimaps_dir, trimap_path)
        if masks_dir is not None:
            mask_abs_path = os.path.join(masks_dir, mask_path)
        image_paths.append([image_fg_abs_path, image_bg_abs_path,
                            trimap_abs_path, mask_abs_path])
    return image_paths
