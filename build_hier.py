# coding =utf-8

import os
from plyfile import PlyData,PlyElement
import shapely
import open3d as o3d
from matplotlib import pyplot
def take_z(elem):
    return elem[2]
"""
return point(xyz rgb label) ordered by height
"""
def get_point_data(path):
    ply_data=PlyData.read(path).elements[0].data[0:]
    ply_data=ply_data.tolist()
    ply_data.sort(key=take_z)
    return ply_data

def map_2_xy_panel(point_list):
    return point_list[:,0:2],point_list[:,3:6]

def point_cloud_to_volume(points, vsize, radius=1.0):
    """ input is Nx3 points.
        output is vsize*vsize*vsize
        assumes points are in range [-radius, radius]
    """
    vol = np.zeros((vsize, vsize, vsize))
    voxel = 2 * radius / float(vsize)
    print('voxel: ', voxel)
    locations = (points + radius) / voxel
    print('locations: ', locations)
    locations = locations.astype(int)
    print('locations: ', locations)
    vol[locations[:, 0], locations[:, 1], locations[:, 2]] = 1.0
    return vol

def pyplot_draw_volume(vol, output_filename=None):
    """ vol is of size vsize*vsize*vsize
        output an image to output_filename
    """
    points = volume_to_point_cloud(vol)
    pyplot_draw_point_cloud(points, output_filename)

def volume_to_point_cloud(vol):
    """ vol is occupancy grid (value = 0 or 1) of size vsize*vsize*vsize
        return Nx3 numpy array.
    """
    vsize = vol.shape[0]
    assert (vol.shape[1] == vsize and vol.shape[1] == vsize)
    points = []
    for a in range(vsize):
        for b in range(vsize):
            for c in range(vsize):
                if vol[a, b, c] == 1:
                    points.append(np.array([a, b, c]))
    if len(points) == 0:
        return np.zeros((0, 3))
    points = np.vstack(points)
    return points

def preview(coords,colors):
    _coords=np.array(coords)
    _colors=np.array(colors)
    max_x,max_y,min_x,min_y=np.max(_coords[:,0]),np.max(_coords[:,1],np.min(_coords[:,0]),np.min(_coords[:,1]))

def main():
    points=get_point_data('./scene0000_00_vh_clean_2.labels.ply')
    points=points[:]
    print(points)
    vols=oint_cloud_to_volume(points,4096,radius=1.0)
    pyplot(vol)

main()

