"""
-------------------------------------------------------------------------------
    VTK is free software: you can redistribute it and/or modify it
    under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 2.1 of the License, or
    (at your option) any later version.

    VTK is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
    for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with VTK.  If not, see <http://www.gnu.org/licenses/>.

Application
    stlAnalysis

Group
    grpGeometryAnalysis

Description
    Script to analyze STL geometry files using VTK. This script computes
    various geometric properties such as volume, surface area, curvature,
    and more. It also identifies points inside and outside the geometry.
    
Author    
    Amr Emad
Date
    June 21, 2024
Version
    v1.1

Dependencies
    - VTK (pip install vtk)
    - NumPy (pip install numpy)
    - JSON (Standard library)

Usage
    Run the script from the command line as follows:

    python stlAnalysis.py <path_to_stl_file> [options]

    Example:
    python stlAnalysis.py D:/AmrEmadDev/dev/flange.stl --volume --surface_area --center_of_mass --bounding_box --curvature --surface_normals --facet_areas --edge_lengths --aspect_ratios --inside_outside_points --generate_blockMeshDict

    Options:
    --volume: Compute volume
    --surface_area: Compute surface area
    --center_of_mass: Compute center of mass
    --bounding_box: Compute bounding box
    --curvature: Compute curvature
    --surface_normals: Compute surface normals
    --facet_areas: Compute facet areas
    --edge_lengths: Compute edge lengths
    --aspect_ratios: Compute aspect ratios
    --inside_outside_points: Compute inside and outside points
    --generate_blockMeshDict: Generate blockMeshDict for OpenFOAM
-------------------------------------------------------------------------------
"""

import vtk
import numpy as np
import json
import os
import argparse

def read_stl_file(filename):
    """
    Reads an STL file and returns the mesh data.

    @param filename: The path to the STL file.
    @return: The mesh data as a vtkPolyData object.
    """
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()

def compute_curvature(mesh, curvature_type='mean'):
    """
    Computes the curvature of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @param curvature_type: The type of curvature to compute ('mean', 'gaussian', 'maximum', 'minimum').
    @return: The mesh data with curvature values as a vtkPolyData object.
    """
    curvature_filter = vtk.vtkCurvatures()
    curvature_filter.SetInputData(mesh)
    
    if curvature_type == 'mean':
        curvature_filter.SetCurvatureTypeToMean()
    elif curvature_type == 'gaussian':
        curvature_filter.SetCurvatureTypeToGaussian()
    elif curvature_type == 'maximum':
        curvature_filter.SetCurvatureTypeToMaximum()
    elif curvature_type == 'minimum':
        curvature_filter.SetCurvatureTypeToMinimum()
    
    curvature_filter.Update()
    return curvature_filter.GetOutput()

def extract_curvature_data(curved_mesh):
    """
    Extracts curvature data from the mesh.

    @param curved_mesh: The mesh data with curvature values as a vtkPolyData object.
    @return: A list of curvature values.
    """
    curvature_data = curved_mesh.GetPointData().GetScalars()
    num_points = curved_mesh.GetNumberOfPoints()
    curvature_values = []
    for i in range(num_points):
        curvature_values.append(curvature_data.GetValue(i))
    return curvature_values

def compute_bounding_box(mesh):
    """
    Computes the bounding box of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: A tuple containing the minimum and maximum bounds of the mesh.
    """
    bounds = mesh.GetBounds()
    min_bounds = [bounds[0], bounds[2], bounds[4]]
    max_bounds = [bounds[1], bounds[3], bounds[5]]
    return min_bounds, max_bounds

def compute_surface_normals(mesh):
    """
    Computes the surface normals of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: A tuple containing the number of outward-facing and inward-facing normals.
    """
    normals_filter = vtk.vtkPolyDataNormals()
    normals_filter.SetInputData(mesh)
    normals_filter.ComputePointNormalsOff()
    normals_filter.ComputeCellNormalsOn()
    normals_filter.Update()
    
    normals = normals_filter.GetOutput().GetCellData().GetNormals()
    num_normals = normals.GetNumberOfTuples()
    
    outward_facing = 0
    inward_facing = 0
    
    for i in range(num_normals):
        normal = normals.GetTuple(i)
        if np.dot(normal, normal) > 0:  # Simple check assuming normals are unit vectors
            outward_facing += 1
        else:
            inward_facing += 1
    
    return outward_facing, inward_facing

def compute_facet_areas(mesh):
    """
    Computes the minimum and maximum facet areas of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: A tuple containing the minimum and maximum facet areas.
    """
    areas = []
    for i in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(i)
        points = cell.GetPoints()
        if points.GetNumberOfPoints() == 3:
            pt1 = np.array(points.GetPoint(0))
            pt2 = np.array(points.GetPoint(1))
            pt3 = np.array(points.GetPoint(2))
            edge1 = pt2 - pt1
            edge2 = pt3 - pt1
            area = np.linalg.norm(np.cross(edge1, edge2)) / 2
            areas.append(area)
    return min(areas), max(areas)

def compute_edge_lengths(mesh):
    """
    Computes the minimum and maximum edge lengths of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: A tuple containing the minimum and maximum edge lengths.
    """
    edge_lengths = []
    for i in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(i)
        points = cell.GetPoints()
        if points.GetNumberOfPoints() == 3:
            pt1 = np.array(points.GetPoint(0))
            pt2 = np.array(points.GetPoint(1))
            pt3 = np.array(points.GetPoint(2))
            edge_lengths.append(np.linalg.norm(pt2 - pt1))
            edge_lengths.append(np.linalg.norm(pt3 - pt1))
            edge_lengths.append(np.linalg.norm(pt3 - pt2))
    return min(edge_lengths), max(edge_lengths)

def compute_aspect_ratios(mesh):
    """
    Computes the minimum and maximum aspect ratios of the mesh.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: A tuple containing the minimum and maximum aspect ratios.
    """
    aspect_ratios = []
    for i in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(i)
        points = cell.GetPoints()
        if points.GetNumberOfPoints() == 3:
            pt1 = np.array(points.GetPoint(0))
            pt2 = np.array(points.GetPoint(1))
            pt3 = np.array(points.GetPoint(2))
            edge1 = np.linalg.norm(pt2 - pt1)
            edge2 = np.linalg.norm(pt3 - pt1)
            edge3 = np.linalg.norm(pt3 - pt2)
            edges = [edge1, edge2, edge3]
            aspect_ratio = max(edges) / min(edges)
            aspect_ratios.append(aspect_ratio)
    return min(aspect_ratios), max(aspect_ratios)

def is_point_inside(mesh, point):
    """
    Checks if a point is inside the geometry using vtkSelectEnclosedPoints.

    @param mesh: The mesh data as a vtkPolyData object.
    @param point: The point coordinates to check.
    @return: True if the point is inside the geometry, False otherwise.
    """
    enclosed_points = vtk.vtkSelectEnclosedPoints()
    enclosed_points.SetSurfaceData(mesh)
    
    points = vtk.vtkPoints()
    points.InsertNextPoint(point)
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    enclosed_points.SetInputData(polydata)
    enclosed_points.Update()
    
    return enclosed_points.IsInside(0)

def find_inside_point(mesh, center_of_mass, min_bounds, max_bounds, initial_distance=0.1, step_factor=0.5):
    """
    Finds a point inside the geometry by moving inward from the center of mass along a deterministic direction.

    @param mesh: The mesh data as a vtkPolyData object.
    @param center_of_mass: The center of mass of the geometry.
    @param min_bounds: The minimum bounds of the bounding box.
    @param max_bounds: The maximum bounds of the bounding box.
    @param initial_distance: The initial distance to move inward from the center of mass.
    @param step_factor: The factor by which to reduce the distance at each step.
    @return: A list representing the coordinates of the inside point.
    """
    direction = np.array([1.0, 1.0, 1.0], dtype=np.float64)  # Fixed direction for deterministic approach
    direction /= np.linalg.norm(direction)
    distance = initial_distance
    inside_point = np.array(center_of_mass, dtype=np.float64) - direction * distance
    
    while not is_point_inside(mesh, inside_point):
        distance *= step_factor
        inside_point = np.array(center_of_mass, dtype=np.float64) - direction * distance
        if distance < 1e-6:  # Break if the distance becomes too small to avoid infinite loop
            break

    return inside_point.tolist()

def compute_principal_axes(mesh):
    """
    Computes the principal axes of the mesh by calculating the inertia tensor manually.

    @param mesh: The mesh data as a vtkPolyData object.
    @return: The principal axes as an array of eigenvectors.
    """
    points = mesh.GetPoints()
    num_points = points.GetNumberOfPoints()
    center_of_mass = np.zeros(3)

    for i in range(num_points):
        point = np.array(points.GetPoint(i))
        center_of_mass += point
    center_of_mass /= num_points

    inertia_tensor = np.zeros((3, 3))

    for i in range(mesh.GetNumberOfCells()):
        cell = mesh.GetCell(i)
        p0 = np.array(points.GetPoint(cell.GetPointId(0)))
        p1 = np.array(points.GetPoint(cell.GetPointId(1)))
        p2 = np.array(points.GetPoint(cell.GetPointId(2)))

        # Move points to center of mass coordinate system
        p0 -= center_of_mass
        p1 -= center_of_mass
        p2 -= center_of_mass

        # Compute the inertia tensor for this triangle
        for p in [p0, p1, p2]:
            for j in range(3):
                for k in range(3):
                    inertia_tensor[j, k] += (p[j] * p[k])

    _, eigenvectors = np.linalg.eigh(inertia_tensor)
    return eigenvectors

def find_outside_point(mesh, center_of_mass, min_bounds, max_bounds, initial_distance=0.1, buffer=10, max_buffer=20):
    """
    Finds a point outside the geometry by moving outward from the center of mass along a principal axis direction.

    @param mesh: The mesh data as a vtkPolyData object.
    @param center_of_mass: The center of mass of the geometry.
    @param min_bounds: The minimum bounds of the bounding box.
    @param max_bounds: The maximum bounds of the bounding box.
    @param initial_distance: The initial distance to move outward from the center of mass.
    @param buffer: The minimum buffer size added to the bounding box for the blockMeshDict.
    @param max_buffer: The maximum buffer size allowed for the bounding box.
    @return: A list representing the coordinates of the outside point.
    """
    eigenvectors = compute_principal_axes(mesh)
    direction = eigenvectors[:, 0]  # Using the first principal axis direction
    direction /= np.linalg.norm(direction)

    bbox_center = (np.array(min_bounds) + np.array(max_bounds)) / 2.0
    bbox_size = np.array(max_bounds) - np.array(min_bounds)
    max_distance = np.linalg.norm(bbox_size) + max_buffer  # Max distance based on the bounding box and max buffer

    distance = initial_distance
    outside_point = np.array(center_of_mass, dtype=np.float64) + direction * distance

    # Loop to find a point outside the geometry but within max distance
    while distance <= max_distance:
        if not is_point_inside(mesh, outside_point):
            break
        distance += initial_distance
        outside_point = np.array(center_of_mass, dtype=np.float64) + direction * distance

    # Ensure the outside point is within 70% to 90% of the extended bounding box
    extended_min_bounds, extended_max_bounds = create_extended_bounding_box(min_bounds, max_bounds, buffer)
    for i in range(3):
        extended_range = extended_max_bounds[i] - extended_min_bounds[i]
        lower_bound = extended_min_bounds[i] + 0.7 * extended_range
        upper_bound = extended_max_bounds[i] - 0.1 * extended_range
        outside_point[i] = np.clip(outside_point[i], lower_bound, upper_bound)

    # Debug information
    print(f"Outside point distance: {distance}, max_distance: {max_distance}, outside_point: {outside_point}")

    return outside_point.tolist()

def create_extended_bounding_box(min_bounds, max_bounds, buffer):
    """
    Creates an extended bounding box based on the original bounding box and buffer.

    @param min_bounds: The minimum bounds of the original bounding box.
    @param max_bounds: The maximum bounds of the original bounding box.
    @param buffer: The buffer size to extend the bounding box.
    @return: The extended minimum and maximum bounds.
    """
    extended_min_bounds = [min_bounds[i] - buffer for i in range(3)]
    extended_max_bounds = [max_bounds[i] + buffer for i in range(3)]
    return extended_min_bounds, extended_max_bounds

def compute_geometry_center_and_lengths(min_bounds, max_bounds):
    """
    Computes the center of the geometry and the length in each direction.

    @param min_bounds: The minimum bounds of the bounding box.
    @param max_bounds: The maximum bounds of the bounding box.
    @return: The center of the geometry and the lengths in each direction.
    """
    center = [(min_bounds[i] + max_bounds[i]) / 2 for i in range(3)]
    lengths = [(max_bounds[i] - min_bounds[i]) for i in range(3)]
    return center, lengths

def write_json_report(filename, volume=None, surface_area=None, center_of_mass=None, 
                      min_bounds=None, max_bounds=None, curvature_values=None, 
                      surface_normals=None, min_area=None, max_area=None,
                      min_edge_length=None, max_edge_length=None,
                      min_aspect_ratio=None, max_aspect_ratio=None,
                      inside_point=None, outside_point=None):
    """
    Writes a JSON report with the computed metrics.

    @param filename: The path to the STL file.
    @param volume: The volume of the geometry.
    @param surface_area: The surface area of the geometry.
    @param center_of_mass: The center of mass of the geometry.
    @param min_bounds: The minimum bounds of the geometry.
    @param max_bounds: The maximum bounds of the geometry.
    @param curvature_values: The curvature values of the geometry.
    @param surface_normals: The number of outward-facing and inward-facing normals.
    @param min_area: The minimum facet area of the geometry.
    @param max_area: The maximum facet area of the geometry.
    @param min_edge_length: The minimum edge length of the geometry.
    @param max_edge_length: The maximum edge length of the geometry.
    @param min_aspect_ratio: The minimum aspect ratio of the geometry.
    @param max_aspect_ratio: The maximum aspect ratio of the geometry.
    @param inside_point: The coordinates of a point inside the geometry.
    @param outside_point: The coordinates of a point outside the geometry.
    """
    base_name = os.path.splitext(os.path.basename(filename))[0]
    json_output_file = f"{base_name}_report.json"
    
    report = {"filename": filename}
    
    if volume is not None:
        report["volume"] = volume
    if surface_area is not None:
        report["surface_area"] = surface_area
    if center_of_mass is not None:
        report["center_of_mass"] = center_of_mass
    if min_bounds is not None and max_bounds is not None:
        center, lengths = compute_geometry_center_and_lengths(min_bounds, max_bounds)
        report["bounding_box"] = {
            "min_bounds": min_bounds,
            "max_bounds": max_bounds,
            "center": center,
            "lengths": lengths
        }
    if curvature_values is not None:
        report["curvature_values"] = curvature_values
    if surface_normals is not None:
        report["surface_normals"] = {
            "outward_facing": surface_normals[0],
            "inward_facing": surface_normals[1]
        }
    if min_area is not None and max_area is not None:
        report["min_area"] = {"value": min_area, "units": "square meters"}
        report["max_area"] = {"value": max_area, "units": "square meters"}
    if min_edge_length is not None and max_edge_length is not None:
        report["min_edge_length"] = {"value": min_edge_length, "units": "meters"}
        report["max_edge_length"] = {"value": max_edge_length, "units": "meters"}
    if min_aspect_ratio is not None and max_aspect_ratio is not None:
        report["min_aspect_ratio"] = min_aspect_ratio
        report["max_aspect_ratio"] = max_aspect_ratio
    if inside_point is not None:
        report["inside_point"] = {"coordinates": inside_point, "units": "meters"}
    if outside_point is not None:
        report["outside_point"] = {"coordinates": outside_point, "units": "meters"}

    with open(json_output_file, 'w') as outfile:
        json.dump(report, outfile, indent=4)

def generate_blockMeshDict(min_bounds, max_bounds, buffer=10, xnCells=40, ynCells=100, znCells=50):
    """
    Generates the blockMeshDict for OpenFOAM based on bounding box values.

    @param min_bounds: The minimum bounds of the geometry.
    @param max_bounds: The maximum bounds of the geometry.
    @param buffer: Buffer size to add around the bounding box.
    @param xnCells: Number of cells in the x-direction.
    @param ynCells: Number of cells in the y-direction.
    @param znCells: Number of cells in the z-direction.
    """
    xmin, ymin, zmin = min_bounds
    xmax, ymax, zmax = max_bounds

    vertices = [
        (xmin - buffer, ymin - buffer, zmin - buffer),
        (xmax + buffer, ymin - buffer, zmin - buffer),
        (xmax + buffer, ymax + buffer, zmin - buffer),
        (xmin - buffer, ymax + buffer, zmin - buffer),
        (xmin - buffer, ymin - buffer, zmax + buffer),
        (xmax + buffer, ymin - buffer, zmax + buffer),
        (xmax + buffer, ymax + buffer, zmax + buffer),
        (xmin - buffer, ymax + buffer, zmax + buffer),
    ]

    blockMeshDict = """FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}
convertToMeters 1.0;

vertices
(
    {}
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({} {} {}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    enclosure
    {{
        type wall;
        faces
        (
            (0 3 2 1)
            (4 5 6 7)
            (0 1 5 4)
            (2 3 7 6)
            (1 2 6 5)
            (3 0 4 7)
        );
    }}
);

mergePatchPairs
(
);
""".format(
        "\n    ".join([f"({v[0]} {v[1]} {v[2]})" for v in vertices]),
        xnCells, ynCells, znCells
    )

    os.makedirs('system', exist_ok=True)
    with open('system/blockMeshDict', 'w') as f:
        f.write(blockMeshDict)

def parse_arguments():
    """
    Parse command-line arguments.

    @return: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="STL Geometry Analysis using VTK")
    parser.add_argument("filename", type=str, help="Path to the STL file")
    parser.add_argument("--volume", action="store_true", help="Compute volume")
    parser.add_argument("--surface_area", action="store_true", help="Compute surface area")
    parser.add_argument("--center_of_mass", action="store_true", help="Compute center of mass")
    parser.add_argument("--bounding_box", action="store_true", help="Compute bounding box")
    parser.add_argument("--curvature", action="store_true", help="Compute curvature")
    parser.add_argument("--surface_normals", action="store_true", help="Compute surface normals")
    parser.add_argument("--facet_areas", action="store_true", help="Compute facet areas")
    parser.add_argument("--edge_lengths", action="store_true", help="Compute edge lengths")
    parser.add_argument("--aspect_ratios", action="store_true", help="Compute aspect ratios")
    parser.add_argument("--inside_outside_points", action="store_true", help="Compute inside and outside points")
    parser.add_argument("--generate_blockMeshDict", action="store_true", help="Generate blockMeshDict for OpenFOAM")
    parser.add_argument("--buffer", type=float, default=10, help="Buffer size to add around the bounding box")
    parser.add_argument("--max_buffer", type=float, default=20, help="Maximum buffer size allowed for the bounding box")

    return parser.parse_args()

def main():
    """
    Main function to read the STL file, compute metrics, and write a JSON report.
    """
    args = parse_arguments()

    # Read the STL file
    mesh = read_stl_file(args.filename)
    
    # Compute and export data based on flags
    volume, surface_area, center_of_mass = None, None, None
    if args.volume or args.surface_area:
        mass_properties = vtk.vtkMassProperties()
        mass_properties.SetInputData(mesh)
        if args.volume:
            volume = mass_properties.GetVolume()
        if args.surface_area:
            surface_area = mass_properties.GetSurfaceArea()
    
    if args.center_of_mass:
        center_of_mass_filter = vtk.vtkCenterOfMass()
        center_of_mass_filter.SetInputData(mesh)
        center_of_mass_filter.Update()
        center_of_mass = center_of_mass_filter.GetCenter()
    
    min_bounds, max_bounds = None, None
    if args.bounding_box:
        min_bounds, max_bounds = compute_bounding_box(mesh)
    
    curvature_values = None
    if args.curvature:
        curved_mesh = compute_curvature(mesh, curvature_type='mean')
        curvature_values = extract_curvature_data(curved_mesh)
    
    surface_normals = None
    if args.surface_normals:
        surface_normals = compute_surface_normals(mesh)
    
    min_area, max_area = None, None
    if args.facet_areas:
        min_area, max_area = compute_facet_areas(mesh)
    
    min_edge_length, max_edge_length = None, None
    if args.edge_lengths:
        min_edge_length, max_edge_length = compute_edge_lengths(mesh)
    
    min_aspect_ratio, max_aspect_ratio = None, None
    if args.aspect_ratios:
        min_aspect_ratio, max_aspect_ratio = compute_aspect_ratios(mesh)
    
    inside_point, outside_point = None, None
    if args.inside_outside_points and center_of_mass is not None and min_bounds is not None and max_bounds is not None:
        inside_point = find_inside_point(mesh, center_of_mass, min_bounds, max_bounds)
        outside_point = find_outside_point(mesh, center_of_mass, min_bounds, max_bounds, buffer=args.buffer, max_buffer=args.max_buffer)  # Ensure within buffer range
    
    # Write JSON report
    write_json_report(args.filename, volume, surface_area, center_of_mass, min_bounds, max_bounds, curvature_values, surface_normals, min_area, max_area, min_edge_length, max_edge_length, min_aspect_ratio, max_aspect_ratio, inside_point, outside_point)
    print(f"JSON report written based on {args.filename}")

    # Generate blockMeshDict if requested
    if args.generate_blockMeshDict and min_bounds and max_bounds:
        generate_blockMeshDict(min_bounds, max_bounds, buffer=args.buffer)
        print("blockMeshDict generated successfully.")

if __name__ == "__main__":
    main()
