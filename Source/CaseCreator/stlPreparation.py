"""
/*--------------------------------*- C++ -*----------------------------------*\
-------------------------------------------------------------------------------
 *****   ******   *          ***     *****   *     *  
*     *  *     *  *         *   *   *     *  *     *  
*        *     *  *        *     *  *        *     *  
 *****   ******   *        *******   *****   *******  
      *  *        *        *     *        *  *     *  
*     *  *        *        *     *  *     *  *     *  
 *****   *        *******  *     *   *****   *     *  
-------------------------------------------------------------------------------
 * SplashCaseCreator is part of Splash CFD automation tool.
 * Copyright (c) 2024 THAW TAR
 * Copyright (c) 2025 Mohamed Aly Sayed and Thaw Tar
 * All rights reserved.
 *
 * This software is licensed under the GNU Lesser General Public License version 3 (LGPL-3.0).
 * You may obtain a copy of the license at https://www.gnu.org/licenses/lgpl-3.0.en.html
 */
"""

import vtk
import os
# from OCC.Core.STEPControl import STEPControl_Reader
# from OCC.Core.STEPControl import STEPControl_Writer
# from OCC.Core.StlAPI import StlAPI_Writer
# from OCC.Core.IFSelect import IFSelect_RetDone


def count_word_in_file(file_path, word):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
            # Use the str.count() method to count occurrences of the word
            count = text.count(word)
            return count
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
    
def has_duplicates(strings):
    seen = set()
    for string in strings:
        if string in seen:
            return True
        seen.add(string)
    return False

def has_spaces(strings):
    for string in strings:
        if string=="" or string=="\n":
            return True
    return False

def extract_text_between_words(input_file_path, start_word, end_word):
    names = []
    texts = []
    text_block = [] # to store a text block between start word and end word
    #copyText = False # flag to copy the text
    try:
        # Read the entire content of the file
        with open(input_file_path, 'r') as file:
            for line in file:
                #if copyText:
                text_block.append(line)
                if start_word in line and end_word not in line:
                    # split the line
                    solid_name = line.split(" ")[1]
                    #print(solid_name)
                    names.append(solid_name)
                    #copyText = True
                if end_word in line:
                    # add the text_block into texts
                    texts.append(text_block)
                    # clear text_block to hold new data
                    text_block = []
                    #copyText = False
        return names,texts

    except FileNotFoundError:
        print(f"The file {input_file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_lines_to_file(file_path,lines):
    try:
        with open(file_path, 'w') as file:
            for line in lines:
                file.write(line)  # Add a newline character after each line
        #print(f"Lines have been written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_multiple_textfiles(names,texts):
    idx = 0
    for name in names:
        file_name = name+".stl"
        text = texts[idx]
        #print(f"Writing file: {file_name}")
        write_lines_to_file(file_name,text)
        idx += 1

def separate_stl(stl_name):
    names,texts = extract_text_between_words(stl_name,start_word="solid",end_word="endsolid")
    hasDupli = has_duplicates(names)
    hasSpace = has_spaces(names)
    stl_dir = os.path.dirname(stl_name)
    #print(f"STL directory: {stl_dir}")
    #hasDiffLen = len(names) == len(texts)
    if hasDupli or hasSpace:
        print(f"No name patches or duplicate names detected! Creating names based on STL name")
        names = []
        for i in range(len(texts)):
            a_name = stl_name[:-4]+f"_{i+1}"
            names.append(a_name)
        write_multiple_textfiles(names,texts)
    else:
        # if the names are right, write the files
        # check if the names have strange characters
        # if they have, create names based on the stl name
        n = []
        for name in names:
            name = name[:-1]
            n.append(name)
        #print(names)
        # join the stl_dir with the names
        names = [os.path.join(stl_dir,name) for name in n]
        print(f"Writing files to: {names}")
        write_multiple_textfiles(names,texts)

# function to test whether stl file is binary or ascii
def is_stl_binary(file_path):
    try:
        with open(file_path, 'rb') as file:
            header = file.read(80)
            if b'solid' in header:
                return False  # ASCII STL files start with 'solid'
            else:
                return True  # Binary STL files do not start with 'solid'
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

     
def convert_binary_to_ascii(input_file_path, output_file_path):
    try:
        # Create a reader for the binary STL file
        reader = vtk.vtkSTLReader()
        reader.SetFileName(input_file_path)
        reader.Update()  # Ensure that the file is read

        # Create a writer for the ASCII STL file
        writer = vtk.vtkSTLWriter()
        writer.SetFileName(output_file_path)
        writer.SetInputData(reader.GetOutput())
        writer.SetFileTypeToASCII()  # Specify ASCII format

        # Write the file
        writer.Write()
        print(f"Successfully converted {input_file_path} to ASCII format and saved as {output_file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def is_stl_closed(stl_file_path):
    # Read the STL file
    reader = vtk.vtkSTLReader()
    reader.SetFileName(stl_file_path)
    reader.Update()

    # Get the output polydata
    polydata = reader.GetOutput()

    # Use vtkFeatureEdges to find boundary edges
    feature_edges = vtk.vtkFeatureEdges()
    feature_edges.SetInputData(polydata)
    feature_edges.BoundaryEdgesOn()
    feature_edges.FeatureEdgesOff()
    feature_edges.NonManifoldEdgesOff()
    feature_edges.ManifoldEdgesOff()
    feature_edges.Update()

    # Get the number of boundary edges
    number_of_boundary_edges = feature_edges.GetOutput().GetNumberOfCells()

    # If there are no boundary edges, the mesh is closed
    is_closed = number_of_boundary_edges == 0

    return is_closed

def remesh_stl(input_file_path, output_file_path, reduction_factor=0.5):
    # Read the STL file
    reader = vtk.vtkSTLReader()
    reader.SetFileName(input_file_path)
    reader.Update()

    # Apply the decimation filter
    decimate = vtk.vtkDecimatePro()
    decimate.SetInputConnection(reader.GetOutputPort())
    decimate.SetTargetReduction(reduction_factor)  # Reduce the number of triangles
    decimate.PreserveTopologyOn()  # Try to preserve the topology
    decimate.Update()

    # Write the remeshed STL file
    writer = vtk.vtkSTLWriter()
    writer.SetFileName(output_file_path)
    writer.SetInputConnection(decimate.GetOutputPort())
    writer.Write()

    print(f"Remeshed STL file saved as {output_file_path}")

def is_multipatch_stl(stl_file_path):
    number_of_patches = count_word_in_file(stl_file_path, "endsolid")
    return number_of_patches > 1

if __name__ == "__main__":
    # Define the input and output file paths
    input_file_path = "/Users/thawtar/Desktop/Work/03_Splash/04_CAD/pipe/combined_test/pipe_combined_named.stl"
    output_file_path = "/Users/thawtar/Desktop/Work/03_Splash/04_CAD/pipe/"
    separate_stl(input_file_path)
