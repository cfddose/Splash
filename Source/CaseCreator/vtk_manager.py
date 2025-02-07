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

#------------------------------ Back up 25.12.2024 -------------------------------
##import vtk
##from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper
##from vtkmodules.vtkFiltersSources import vtkSphereSource, vtkCubeSource
##from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
##from vtkmodules.vtkCommonColor import vtkNamedColors
##import os

##class VTKManager:
##    """
##    VTKManager encapsulates VTK rendering operations and camera management
##    for applications requiring interactive 3D visualizations.
##    """

##    def __init__(self, renderer, vtk_widget):
##        """
##        Initializes the VTKManager with a renderer and VTK widget.
##        :param renderer: vtk.vtkRenderer instance for rendering operations.
##        :param vtk_widget: VTK widget instance (e.g., QVTKRenderWindowInteractor).
##        """
##        self.renderer = renderer
##        self.vtk_widget = vtk_widget
##        self.listOfColors = [
##            "Pink", "Red", "Green", "Blue", "Yellow",
##            "Orange", "Purple", "Cyan", "Magenta", "Brown"
##        ]
##        self.colorCounter = 0  # Tracks color assignments for actors.

##        # Set default Cyan-Gray gradient background
##        colors = vtkNamedColors()
##        self.set_background(
##            background=colors.GetColor3d("Grey"),
##            gradient_background=True,
##            background2=colors.GetColor3d("Cyan")
##        )

##        # Add default axes actor to the renderer
##        self.axes_actor = vtkAxesActor()
##        self.axes_actor.SetTotalLength(1.0, 1.0, 1.0)  # Default axes length
##        self.renderer.AddActor(self.axes_actor)
##        
##        # Set interactor style for easy manipulation
##        interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
##        style = vtk.vtkInteractorStyleTrackballCamera()
##        interactor.SetInteractorStyle(style)

##    def render_all(self):
##        """
##        Renders all elements in the VTK widget's render window.
##        """
##        self.vtk_widget.GetRenderWindow().Render()

##    def reset_camera(self):
##        """
##        Resets the camera to fit all visible actors in the view and zooms out slightly.
##        """
##        self.renderer.ResetCamera()
##        camera = self.renderer.GetActiveCamera()
##        camera.Zoom(0.8)  # Zoom out slightly
##        self.render_all()

##    def set_camera_orientation(self, position, focal_point=(0, 0, 0), view_up=(0, 0, 1)):
##        """
##        Adjusts the camera orientation for the renderer.
##        :param position: Tuple (x, y, z) specifying the camera's position.
##        :param focal_point: Tuple (x, y, z) for the camera's focal point. Default is origin.
##        :param view_up: Tuple (x, y, z) specifying the camera's up direction.
##        """
##        camera = self.renderer.GetActiveCamera()
##        camera.SetPosition(*position)
##        camera.SetFocalPoint(*focal_point)
##        camera.SetViewUp(*view_up)
##        self.reset_camera()
##    
##    # FLAG! Ask Thaw about the logic behind the function below     
##    # this function will read STL file and show it in the VTK renderer | FLAG! local path!
###    def showSTL(self,stlFile=r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src\pipe.stl"):
###        # Read stl
###        try:
###            self.reader = vtk.vtkSTLReader()
###            self.reader.SetFileName(stlFile)
###            stl_name = os.path.basename(stlFile)
###            print("STL Name: ",stl_name)
###            self.render3D(actorName=stl_name)
###        except:
###            print("Reading STL not successful. Try again")    
##    def showSTL(self, stlFile):
##        try:
##            print(f"Rendering STL: {stlFile}")
##            self.render_stl(stlFile)
##        except Exception as e:
##            print(f"Error rendering STL {stlFile}: {e}")

##    def update_vtk_background(self, index):
##        """
##        Updates the VTK background based on the selected index in the ComboBox.
##        :param index: The index of the selected background type in the ComboBox.
##        """
##        colors = vtk.vtkNamedColors()

##        if index == 0:     # Cyan-Gray Gradient
##            self.renderer.GradientBackgroundOn()
##            self.renderer.SetBackground(colors.GetColor3d("Grey"))  # Top color
##            self.renderer.SetBackground2(colors.GetColor3d("Cyan"))  # Bottom color
##        elif index == 1:   # White-Black Gradient 
##            self.renderer.GradientBackgroundOn()
##            self.renderer.SetBackground(colors.GetColor3d("White"))  # Top color
##            self.renderer.SetBackground2(colors.GetColor3d("Black"))  # Bottom color
##        elif index == 2:   # Blue Gradient
##            self.renderer.GradientBackgroundOn()
##            self.renderer.SetBackground(colors.GetColor3d("SkyBlue"))  # Top color
##            self.renderer.SetBackground2(colors.GetColor3d("MidnightBlue"))  # Bottom color
##        elif index == 3:   # Solid White
##            self.renderer.GradientBackgroundOff()
##            self.renderer.SetBackground(colors.GetColor3d("White"))
##        elif index == 4:   # Solid Black
##            self.renderer.GradientBackgroundOff()
##            self.renderer.SetBackground(colors.GetColor3d("Black"))

##        # Trigger a re-render to reflect changes
##        self.vtk_widget.GetRenderWindow().Render()
##            
##    def render3D(self,actorName=None):  
##        # self.ren and self.iren must be used. other variables are local variables
##        # Create a mapper
##        mapper = vtk.vtkPolyDataMapper()
##        mapper.SetInputConnection(self.reader.GetOutputPort())
##        # Create an actor
##        actor = vtk.vtkActor()
##        actor.SetMapper(mapper)
##        if actorName:
##            actor.SetObjectName(actorName)
##        # set random colors to the actor
##        colors = vtk.vtkNamedColors()
##        
##        if(self.colorCounter>9):
##            self.colorCounter = 0
##        actor.GetProperty().SetColor(colors.GetColor3d(self.listOfColors[self.colorCounter]))
##        self.ren.AddActor(actor)
##        axes = vtk.vtkAxesActor()
##        axes.SetTotalLength(0.1, 0.1, 0.1)
##        self.ren.AddActor(axes)        
##        self.colorCounter += 1        
##        #self.iren.Start()

##    def toggle_actor_representation(self, representation_mode, edge_visibility=False):
##        """
##        Changes the representation mode of all actors in the renderer.
##        :param representation_mode: VTK representation mode ("Wireframe" or "Surface").
##        :param edge_visibility: Whether to display edges on the actors.
##        """
##        actors = self.renderer.GetActors()
##        actors.InitTraversal()
##        for _ in range(actors.GetNumberOfItems()):
##            actor = actors.GetNextActor()
##            if representation_mode == "Wireframe":
##                actor.GetProperty().SetRepresentationToWireframe()
##            else:
##                actor.GetProperty().SetRepresentationToSurface()
##            actor.GetProperty().EdgeVisibilityOn() if edge_visibility else actor.GetProperty().EdgeVisibilityOff()
##        self.render_all()

##    def highlight_actor(self, stl_file, stl_names, colors, highlight_color=(1.0, 0.0, 1.0)):
##        """
##        Highlights a specific actor based on its STL file name.
##        """
##        actors = self.renderer.GetActors()
##        actors.InitTraversal()
##        for _ in range(actors.GetNumberOfItems()):
##            actor = actors.GetNextActor()
##            if actor.GetObjectName() in stl_names:
##                if actor.GetObjectName() == stl_file:
##                    actor.GetProperty().SetColor(*highlight_color)
##                else:
##                    idx = stl_names.index(actor.GetObjectName())
##                    actor.GetProperty().SetColor(colors.GetColor3d(self.listOfColors[idx % len(self.listOfColors)]))
##        self.render_all()

##    def draw_axes(self, char_len):
##        """
##        Updates the axes length in the renderer.
##        :param char_len: Length of the axes lines.
##        """
##        self.axes_actor.SetTotalLength(char_len, char_len, char_len)
##        self.render_all()

##    def draw_mesh_point(self, location, domain_bounds=None, size_factor=None, remove_previous=True):
##        """
##        Adds a spherical marker at the specified location.
##        :param location: Tuple (x, y, z) indicating the marker's position.
##        :param domain_bounds: Optional tuple (minX, minY, minZ, maxX, maxY, maxZ) for scaling the sphere radius.
##        :param size_factor: Radius of the sphere. If None, calculate dynamically based on domain bounds.
##        :param remove_previous: If True, removes any existing sphere with the same name.
##        """
##        if not isinstance(location, (tuple, list)) or len(location) != 3:
##            print(f"Invalid location for mesh point: {location}")
##            return

##        if remove_previous:
##            self.remove_actor_by_name("MeshPoint")  # Remove existing mesh point actor

##        if size_factor is None:
##            # Calculate a dynamic radius based on domain bounds or fallback to a default
##            if domain_bounds and len(domain_bounds) == 6:
##                minX, minY, minZ, maxX, maxY, maxZ = domain_bounds
##                max_extent = max(maxX - minX, maxY - minY, maxZ - minZ)
##                size_factor = max_extent * 0.01  # Sphere is 1% of the largest extent
##            else:
##                size_factor = 0.01  # Default size if bounds are unavailable

##        # Ensure the radius is not below a minimum threshold
##        size_factor = max(size_factor, 1e-3)  # Minimum radius of 1e-3

##        sphere = vtkSphereSource()
##        sphere.SetCenter(location)
##        sphere.SetRadius(size_factor)

##        # Increase resolution for a smoother sphere
##        sphere.SetThetaResolution(32)  # Number of subdivisions around the sphere
##        sphere.SetPhiResolution(32)    # Number of subdivisions from top to bottom

##        mapper = vtkPolyDataMapper()
##        mapper.SetInputConnection(sphere.GetOutputPort())
##        actor = vtkActor()
##        actor.SetMapper(mapper)
##        actor.GetProperty().SetColor(0, 0, 1)  # Blue for mesh point
##        actor.GetProperty().SetOpacity(0.25)
##        actor.SetObjectName("MeshPoint")  # Name the actor

##        print(f"Adding sphere actor at location: {location} with radius: {size_factor}")
##        self.add_actor(actor)

##    def set_background(self, background, gradient_background=False, background2=None):
##        """
##        Sets the background color of the renderer.
##        :param background: RGB tuple for the primary color.
##        :param gradient_background: If True, sets a gradient background.
##        :param background2: RGB tuple for the secondary gradient color.
##        """
##        if gradient_background and background2:
##            self.renderer.GradientBackgroundOn()
##            self.renderer.SetBackground(background)
##            self.renderer.SetBackground2(background2)
##        else:
##            self.renderer.GradientBackgroundOff()
##            self.renderer.SetBackground(background)
##        self.render_all()

##    def add_actor(self, actor):
##        """
##        Adds an actor to the renderer.
##        :param actor: vtk.vtkActor instance to add.
##        """
##        self.renderer.AddActor(actor)
##        self.render_all()

##    def remove_actor_by_name(self, name):
##        """
##        Removes an actor from the renderer by its assigned name.
##        :param name: Name of the actor to remove.
##        """
##        actors = self.renderer.GetActors()
##        actors.InitTraversal()
##        for _ in range(actors.GetNumberOfItems()):
##            actor = actors.GetNextActor()
##            if actor.GetObjectName() == name:
##                self.renderer.RemoveActor(actor)
##                break
##        self.render_all()

##    def render_stl(self, stl_file, color=(0.5, 0.5, 0.5)):
##        """
##        Renders an STL file in the VTK renderer.
##        :param stl_file: Path to the STL file.
##        :param color: RGB tuple for the actor's color.
##        """
##        actor_name = os.path.basename(stl_file)  # Use file name as actor name
##        self.remove_actor_by_name(actor_name)  # Remove any existing actor with the same name

##        # Read STL file
##        reader = vtk.vtkSTLReader()
##        reader.SetFileName(stl_file)

##        # Map STL data
##        mapper = vtk.vtkPolyDataMapper()
##        mapper.SetInputConnection(reader.GetOutputPort())

##        # Create actor
##        actor = vtk.vtkActor()
##        actor.SetMapper(mapper)
##        actor.GetProperty().SetColor(color)
##        actor.SetObjectName(actor_name)

##        # Add STL actor
##        self.add_actor(actor)

##        # Re-add axes actor to ensure it stays on top
##        self.renderer.RemoveActor(self.axes_actor)  # Remove and re-add to maintain rendering order
##        self.renderer.AddActor(self.axes_actor)
##        self.render_all()

##    def add_sphere_to_VTK(self, center=(0.0, 0.0, 0.0), radius=1.0, objectName="Sphere", removePrevious=True):
##        """
##        Adds a sphere to the renderer.
##        :param center: Tuple (x, y, z) specifying the sphere's center.
##        :param radius: Radius of the sphere.
##        :param objectName: Name of the sphere object.
##        :param removePrevious: If True, removes any existing sphere with the same name.
##        """
##        sphere = vtkSphereSource()
##        sphere.SetCenter(center)
##        sphere.SetRadius(radius)
##        self.add_object_to_VTK(sphere, objectName=objectName, removePrevious=removePrevious)

##    def add_box_to_VTK(self, minX=0.0, minY=0.0, minZ=0.0, maxX=1.0, maxY=1.0, maxZ=1.0, boxName="Box"):
##        """
##        Adds a bounding box to the renderer.
##        :param minX: Minimum x-coordinate of the box.
##        :param minY: Minimum y-coordinate of the box.
##        :param minZ: Minimum z-coordinate of the box.
##        :param maxX: Maximum x-coordinate of the box.
##        :param maxY: Maximum y-coordinate of the box.
##        :param maxZ: Maximum z-coordinate of the box.
##        :param boxName: Name of the box object.
##        """
##        cube = vtkCubeSource()
##        cube.SetXLength(maxX - minX)
##        cube.SetYLength(maxY - minY)
##        cube.SetZLength(maxZ - minZ)
##        cube.SetCenter((maxX + minX) / 2, (maxY + minY) / 2, (maxZ + minZ) / 2)
##        self.add_object_to_VTK(cube, objectName=boxName, removePrevious=True)

##    def add_object_to_VTK(self, obj, objectName, removePrevious=False, color=(0.5, 0.5, 0.5), opacity=0.5):
##        """
##        Adds a VTK object to the renderer.
##        :param obj: VTK source object (e.g., vtkSphereSource).
##        :param objectName: Name of the object.
##        :param removePrevious: If True, removes existing object with the same name.
##        :param color: RGB tuple for the object's color.
##        :param opacity: Opacity of the object.
##        """
##        mapper = vtkPolyDataMapper()
##        mapper.SetInputConnection(obj.GetOutputPort())
##        actor = vtkActor()
##        actor.SetMapper(mapper)
##        actor.GetProperty().SetColor(color)
##        actor.GetProperty().SetOpacity(opacity)
##        actor.SetObjectName(objectName)

##        if removePrevious:
##            self.remove_actor_by_name(objectName)

##        self.add_actor(actor)
#------------------------------ Back up 25.12.2024 -------------------------------




import vtk
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper
from vtkmodules.vtkFiltersSources import vtkSphereSource, vtkCubeSource
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkCommonColor import vtkNamedColors
import os
from enum import Enum

# to store the vtk rendering mode
class vtkMode(Enum):
    VTK_WIREFRAME = 0
    VTK_SURFACE = 1
    VTK_EDGES = 2

class VTKManager:
    """
    VTKManager encapsulates VTK rendering operations and camera management
    for applications requiring interactive 3D visualizations.
    """

    def __init__(self, renderer, vtk_widget):
        """
        Initializes the VTKManager with a renderer and VTK widget.
        :param renderer: vtk.vtkRenderer instance for rendering operations.
        :param vtk_widget: VTK widget instance (e.g., QVTKRenderWindowInteractor).
        """
        # Initialize the renderer and widget
        self.renderer = renderer
        self.vtk_widget = vtk_widget
        self.colorCounter = 0
        self.listOfColors = [
            "Pink", "Red", "Green", "Blue", "Yellow",
            "Orange", "Purple", "Cyan", "Magenta", "Brown"
        ]

        # Set background
        colors = vtkNamedColors()
        self.set_background(
            background=colors.GetColor3d("Grey"),
            gradient_background=True,
            background2=colors.GetColor3d("Cyan")
        )

        # Configure axes
        self.axes_actor = vtkAxesActor()
        self._configure_axes(self.axes_actor)
        self.renderer.AddActor(self.axes_actor)

        # Set interactor style
        interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        style = vtk.vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(style)

        # Add an initial grid
        self.add_initial_grid(grid_spacing=1.0, grid_size=10.0)

        # Set the default camera view
        self.set_default_camera()

    def _configure_axes(self, axes_actor):
        """
        Configures the appearance of the axes for better aesthetics.
        :param axes_actor: Instance of vtkAxesActor.
        """
        axes_actor.SetShaftTypeToCylinder()  # Cylindrical shafts
        axes_actor.SetTipTypeToCone()  # Smooth arrow tips
        axes_actor.SetAxisLabels(1)  # Enable labels
        axes_actor.SetTotalLength(5.0, 5.0, 5.0)  # Default length

        # Thickness and smoothness
        axes_actor.SetCylinderRadius(0.02)  # Shaft thickness
        axes_actor.SetConeRadius(0.08)  # Arrowhead thickness
        axes_actor.SetConeResolution(32)  # Smooth arrowhead
        axes_actor.SetCylinderResolution(32)  # Smooth shaft

    def render_all(self):
        self.vtk_widget.GetRenderWindow().Render()

    def draw_axes(self, char_len):
        """
        Updates the axes actor length dynamically.
        :param char_len: Length for axes.
        """
        char_len = max(char_len, 1e-3)  # Minimum length of 1e-3
        print("Char Length: ", char_len)
        assert char_len < 0, "Invalid length for axes."
        self.axes_actor.SetTotalLength(char_len, char_len, char_len)
        self.renderer.RemoveActor(self.axes_actor)  # Re-add to ensure proper rendering order
        self.renderer.AddActor(self.axes_actor)
        self.render_all()      

    def reset_camera(self):
        """
        Resets the camera to fit all visible actors in the view and zooms out slightly.
        """
        self.renderer.ResetCamera()
        camera = self.renderer.GetActiveCamera()
        camera.Zoom(0.8)  # Zoom out slightly
        self.render_all()

    def set_camera_orientation(self, position, focal_point=(0, 0, 0), view_up=(0, 0, 1)):
        """
        Adjusts the camera orientation for the renderer.
        :param position: Tuple (x, y, z) specifying the camera's position.
        :param focal_point: Tuple (x, y, z) for the camera's focal point. Default is origin.
        :param view_up: Tuple (x, y, z) specifying the camera's up direction.
        """
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(*position)
        camera.SetFocalPoint(*focal_point)
        camera.SetViewUp(*view_up)
        self.reset_camera()

    def set_default_camera(self):
        """
        Sets the default camera position to mimic the desired isometric view,
        with axes centered and a grid-like background.
        """
        camera = self.renderer.GetActiveCamera()

        # Set the camera position directly above the XY plane
        # Adjust these values to fine-tune the perspective
        camera.SetPosition(0, 0, 10)  # Camera is 10 units above the XY plane
        camera.SetFocalPoint(0, 0, 0)  # Camera looks at the origin
        camera.SetViewUp(0, 1, 0)  # The Y-axis is up in the view

        # Optional: Zoom out slightly for a better overview
        self.renderer.ResetCamera()
        camera.Zoom(1.2)

        # Update the renderer to apply the new camera settings
        self.render_all()
        print("Default camera set to mimic the provided view.")
           
        
    def save_camera_state(self):
        """
        Saves the current camera state for reuse.
        """
        camera = self.renderer.GetActiveCamera()
        self.saved_camera_position = camera.GetPosition()
        self.saved_camera_focal_point = camera.GetFocalPoint()
        self.saved_camera_view_up = camera.GetViewUp()
        print("Camera state saved.")
    
    def restore_camera_state(self):
        """
        Restores the previously saved camera state.
        """
        if hasattr(self, "saved_camera_position") and hasattr(self, "saved_camera_focal_point"):
            camera = self.renderer.GetActiveCamera()
            camera.SetPosition(*self.saved_camera_position)
            camera.SetFocalPoint(*self.saved_camera_focal_point)
            camera.SetViewUp(*self.saved_camera_view_up)
            self.render_all()
            print("Camera state restored.")
        else:
            print("No saved camera state to restore.")
    
    # FLAG! Ask Thaw about the logic behind the function below     
    # this function will read STL file and show it in the VTK renderer | FLAG! local path!
#    def showSTL(self,stlFile=r"C:\Users\mrtha\Desktop\GitHub\foamAutoGUI\src\pipe.stl"):
#        # Read stl
#        try:
#            self.reader = vtk.vtkSTLReader()
#            self.reader.SetFileName(stlFile)
#            stl_name = os.path.basename(stlFile)
#            print("STL Name: ",stl_name)
#            self.render3D(actorName=stl_name)
#        except:
#            print("Reading STL not successful. Try again")    
    def showSTL(self, stlFile):
        try:
            print(f"Rendering STL: {stlFile}")
            self.render_stl(stlFile)
        except Exception as e:
            print(f"Error rendering STL {stlFile}: {e}")

    def update_vtk_background(self, index):
        """
        Updates the VTK background based on the selected index in the ComboBox.
        :param index: The index of the selected background type in the ComboBox.
        """
        colors = vtk.vtkNamedColors()

        if index == 0:     # Cyan-Gray Gradient
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground(colors.GetColor3d("Grey"))  # Top color
            self.renderer.SetBackground2(colors.GetColor3d("Cyan"))  # Bottom color
        elif index == 1:   # White-Black Gradient 
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground(colors.GetColor3d("White"))  # Top color
            self.renderer.SetBackground2(colors.GetColor3d("Black"))  # Bottom color
        elif index == 2:   # Black-White Gradient 
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground(colors.GetColor3d("Black"))  # Top color
            self.renderer.SetBackground2(colors.GetColor3d("White"))  # Bottom color
        elif index == 3:   # Blue Gradient
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground(colors.GetColor3d("SkyBlue"))  # Top color
            self.renderer.SetBackground2(colors.GetColor3d("MidnightBlue"))  # Bottom color
        elif index == 4:   # Solid White
            self.renderer.GradientBackgroundOff()
            self.renderer.SetBackground(colors.GetColor3d("White"))
        elif index == 5:   # Solid Black
            self.renderer.GradientBackgroundOff()
            self.renderer.SetBackground(colors.GetColor3d("Black"))

        # Trigger a re-render to reflect changes
        self.vtk_widget.GetRenderWindow().Render()
            
    def render3D(self,actorName=None):  
        # self.ren and self.iren must be used. other variables are local variables
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self.reader.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        if actorName:
            actor.SetObjectName(actorName)
        # set random colors to the actor
        colors = vtk.vtkNamedColors()
        
        if(self.colorCounter>9):
            self.colorCounter = 0
        actor.GetProperty().SetColor(colors.GetColor3d(self.listOfColors[self.colorCounter]))
        self.ren.AddActor(actor)
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(0.1, 0.1, 0.1)
        self.ren.AddActor(axes)        
        self.colorCounter += 1        
        #self.iren.Start()

    def toggle_actor_representation(self, representation_mode, edge_visibility=False):
        """
        Changes the representation mode of all actors in the renderer.
        :param representation_mode: VTK representation mode ("Wireframe" or "Surface").
        :param edge_visibility: Whether to display edges on the actors.
        """
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if representation_mode == "Wireframe":
                actor.GetProperty().SetRepresentationToWireframe()
            else:
                actor.GetProperty().SetRepresentationToSurface()
            actor.GetProperty().EdgeVisibilityOn() if edge_visibility else actor.GetProperty().EdgeVisibilityOff()
        self.render_all()

    def highlight_actor(self, stl_file, stl_names, colors, highlight_color=(1.0, 0.0, 1.0)):
        """
        Highlights a specific actor based on its STL file name.
        """
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if actor.GetObjectName() in stl_names:
                if actor.GetObjectName() == stl_file:
                    actor.GetProperty().SetColor(*highlight_color)
                else:
                    idx = stl_names.index(actor.GetObjectName())
                    actor.GetProperty().SetColor(colors.GetColor3d(self.listOfColors[idx % len(self.listOfColors)]))
        self.render_all()

    def highlight_boundary(self, boundary_name, boundary_names, colors, highlight_color=(1.0, 0.0, 1.0)):
        """
        Highlights a specific boundary based on its name.
        """
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if actor.GetObjectName() in boundary_names:
                if actor.GetObjectName() == boundary_name:
                    actor.GetProperty().SetColor(*highlight_color)
                else:
                    
                    idx = boundary_names.index(actor.GetObjectName())
                    #print(f"Boundary names: {boundary_names}")
                    #print(f"Boundary name: {boundary_name}")
                    #print(f"Index: {idx}")
                    # the color of the boundary is set to white
                    actor.GetProperty().SetColor(colors.GetColor3d("White"))
        self.render_all()

    def draw_axes(self, char_len):
        """
        Updates the axes length in the renderer.
        :param char_len: Length of the axes lines.
        """
        self.axes_actor.SetTotalLength(char_len, char_len, char_len)
        self.render_all()

    def draw_mesh_point(self, location, domain_bounds=None, size_factor=None, remove_previous=True):
        """
        Adds a spherical marker at the specified location.
        :param location: Tuple (x, y, z) indicating the marker's position.
        :param domain_bounds: Optional tuple (minX, minY, minZ, maxX, maxY, maxZ) for scaling the sphere radius.
        :param size_factor: Radius of the sphere. If None, calculate dynamically based on domain bounds.
        :param remove_previous: If True, removes any existing sphere with the same name.
        """
        if not isinstance(location, (tuple, list)) or len(location) != 3:
            print(f"Invalid location for mesh point: {location}")
            return

        if remove_previous:
            self.remove_actor_by_name("MeshPoint")  # Remove existing mesh point actor

        if size_factor is None:
            # Calculate a dynamic radius based on domain bounds or fallback to a default
            if domain_bounds and len(domain_bounds) == 6:
                minX, minY, minZ, maxX, maxY, maxZ = domain_bounds
                max_extent = max(maxX - minX, maxY - minY, maxZ - minZ)
                size_factor = max_extent * 0.01  # Sphere is 1% of the largest extent
            else:
                size_factor = 0.01  # Default size if bounds are unavailable

        # Ensure the radius is not below a minimum threshold
        size_factor = max(size_factor, 1e-3)  # Minimum radius of 1e-3

        sphere = vtkSphereSource()
        sphere.SetCenter(location)
        sphere.SetRadius(size_factor)

        # Increase resolution for a smoother sphere
        sphere.SetThetaResolution(32)  # Number of subdivisions around the sphere
        sphere.SetPhiResolution(32)    # Number of subdivisions from top to bottom

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 0, 1)  # Blue for mesh point
        actor.GetProperty().SetOpacity(0.25)
        actor.SetObjectName("MeshPoint")  # Name the actor

        print(f"Adding sphere actor at location: {location} with radius: {size_factor}")
        self.add_actor(actor)

    def set_background(self, background, gradient_background=False, background2=None):
        """
        Sets the background color of the renderer.
        :param background: RGB tuple for the primary color.
        :param gradient_background: If True, sets a gradient background.
        :param background2: RGB tuple for the secondary gradient color.
        """
        if gradient_background and background2:
            self.renderer.GradientBackgroundOn()
            self.renderer.SetBackground(background)
            self.renderer.SetBackground2(background2)
        else:
            self.renderer.GradientBackgroundOff()
            self.renderer.SetBackground(background)
        self.render_all()

    def add_actor(self, actor):
        """
        Adds an actor to the renderer.
        :param actor: vtk.vtkActor instance to add.
        """
        self.renderer.AddActor(actor)
        self.render_all()

    def remove_actor_by_name(self, name):
        """
        Removes an actor from the renderer by its assigned name.
        :param name: Name of the actor to remove.
        """
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if actor.GetObjectName() == name:
                self.renderer.RemoveActor(actor)
                break
        self.render_all()

    def remove_stl(self,stl_file):
        """
        Removes an actor from the renderer by its assigned name.
        :param name: Name of the actor to remove.
        """
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if actor.GetObjectName() == stl_file:
                self.renderer.RemoveActor(actor)
                break
        self.render_all()

    def render_stl(self, stl_file, color=(0.5, 0.5, 0.5)):
        """
        Renders an STL file in the VTK renderer and rescales the axes.
        :param stl_file: Path to the STL file.
        :param color: RGB tuple for the actor's color.
        """
        # Remove initial grid if present
        self.remove_initial_grid()
        
        # Rescale axes labels so it can look more pleasing 
        self.rescale_axes_to_geometry()
     
        actor_name = os.path.basename(stl_file)  # Use file name as actor name
        self.remove_actor_by_name(actor_name)  # Remove any existing actor with the same name

        # Read STL file
        reader = vtk.vtkSTLReader()
        if not os.path.isfile(stl_file):
            print(f"Error: File not found - {stl_file}")
            return
        reader.SetFileName(stl_file)

        # Map STL data
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(1.0)  # Slightly translucent for better visuals
        actor.SetObjectName(actor_name)

        # Add STL actor
        self.add_actor(actor)

        # Re-add axes actor to ensure it stays on top
        self.renderer.RemoveActor(self.axes_actor)  # Remove and re-add to maintain rendering order
        self.renderer.AddActor(self.axes_actor)

        # Adjust the camera after adding the actor
        self.set_default_camera()

        # Rescale the axes based on the geometry
        self.rescale_axes_to_geometry()

        # Print debug info
        print(f"STL file rendered: {stl_file}")
        print(f"Actor name: {actor_name}")
        print(f"Color: {color}")

        # Render all actors
        self.render_all()

    def add_sphere_to_VTK(self, center=(0.0, 0.0, 0.0), radius=1.0, objectName="Sphere", removePrevious=True):
        """
        Adds a sphere to the renderer.
        :param center: Tuple (x, y, z) specifying the sphere's center.
        :param radius: Radius of the sphere.
        :param objectName: Name of the sphere object.
        :param removePrevious: If True, removes any existing sphere with the same name.
        """
        sphere = vtkSphereSource()
        sphere.SetCenter(center)
        sphere.SetRadius(radius)
        self.add_object_to_VTK(sphere, objectName=objectName, removePrevious=removePrevious)

    def add_box_to_VTK(self, minX=0.0, minY=0.0, minZ=0.0, maxX=1.0, maxY=1.0, maxZ=1.0, objectName="Box"):
        """
        Adds a bounding box to the renderer.
        :param minX: Minimum x-coordinate of the box.
        :param minY: Minimum y-coordinate of the box.
        :param minZ: Minimum z-coordinate of the box.
        :param maxX: Maximum x-coordinate of the box.
        :param maxY: Maximum y-coordinate of the box.
        :param maxZ: Maximum z-coordinate of the box.
        :param boxName: Name of the box object.
        """
        cube = vtkCubeSource()
        cube.SetXLength(maxX - minX)
        cube.SetYLength(maxY - minY)
        cube.SetZLength(maxZ - minZ)
        cube.SetCenter((maxX + minX) / 2, (maxY + minY) / 2, (maxZ + minZ) / 2)
        self.add_object_to_VTK(cube, objectName=objectName, removePrevious=True)

    def add_cylinder_to_VTK(self, center=(0.0, 0.0, 0.0), radius=1.0, height=1.0, objectName="Cylinder", removePrevious=True):
        """
        Adds a cylinder to the renderer.
        :param center: Tuple (x, y, z) specifying the cylinder's center.
        :param radius: Radius of the cylinder.
        :param height: Height of the cylinder.
        :param objectName: Name of the cylinder object.
        :param removePrevious: If True, removes any existing cylinder with the same name.
        """
        cylinder = vtk.vtkCylinderSource()
        cylinder.SetCenter(center)
        cylinder.SetRadius(radius)
        cylinder.SetHeight(height)
        cylinder.SetResolution(64)  # Increase resolution for a smoother cylinder
        self.add_object_to_VTK(cylinder, objectName=objectName, removePrevious=removePrevious)

    def add_object_to_VTK(self, obj, objectName, removePrevious=False, color=(0.5, 0.5, 0.5), opacity=0.5):
        """
        Adds a VTK object to the renderer.
        :param obj: VTK source object (e.g., vtkSphereSource).
        :param objectName: Name of the object.
        :param removePrevious: If True, removes existing object with the same name.
        :param color: RGB tuple for the object's color.
        :param opacity: Opacity of the object.
        """
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(obj.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetOpacity(opacity)
        actor.SetObjectName(objectName)

        if removePrevious:
            self.remove_actor_by_name(objectName)

        self.add_actor(actor)
        

    def add_initial_grid(self, grid_spacing=1.0, grid_size=10.0, grid_name="InitialGrid", line_color=(0, 0, 0)):
        """
        Adds a grid to the VTK renderer to serve as an initial placeholder.
        :param grid_spacing: Distance between grid lines.
        :param grid_size: Half the length of the grid (total grid size will be 2 * grid_size).
        :param grid_name: Name of the grid object for reference.
        :param line_color: RGB tuple for the grid line color.
        """
        if grid_spacing <= 0:
            print("Invalid grid spacing. Must be greater than 0.")
            return

        # Remove any existing grid with the same name
        self.remove_actor_by_name(grid_name)

        # Create grid lines in X and Y directions
        grid_lines = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Generate grid points and lines
        start = -grid_size
        end = grid_size
        num_lines = int((2 * grid_size) / grid_spacing) + 1

        # Add horizontal and vertical lines
        for i in range(num_lines):
            # X-direction lines
            y = start + i * grid_spacing
            points.InsertNextPoint(start, y, 0)
            points.InsertNextPoint(end, y, 0)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * i)
            lines.InsertCellPoint(2 * i + 1)

            # Y-direction lines
            x = start + i * grid_spacing
            points.InsertNextPoint(x, start, 0)
            points.InsertNextPoint(x, end, 0)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * i + num_lines * 2)
            lines.InsertCellPoint(2 * i + num_lines * 2 + 1)

        # Set points and lines to the grid
        grid_lines.SetPoints(points)
        grid_lines.SetLines(lines)

        # Create a mapper and actor for the grid
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid_lines)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(line_color)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetLineWidth(1.0)
        actor.SetObjectName(grid_name)

        # Add the grid actor to the renderer
        self.add_actor(actor)
        print(f"Initial grid added with spacing {grid_spacing} and size {grid_size}.")

    def add_x_grid(self, ny=10, nz=10, x=0, y1=-10, y2=10, z1=-10, z2=10, grid_name="XGrid", line_color=(0, 0, 0)):
        """
        Adds a grid in the X-direction to the VTK renderer.
        :param ny: Number of grid lines in the Y-direction.
        :param nz: Number of grid lines in the Z-direction.
        :param x: X-coordinate of the grid.
        :param y1: Start Y-coordinate of the grid.
        :param y2: End Y-coordinate of the grid.
        :param z1: Start Z-coordinate of the grid.
        :param z2: End Z-coordinate of the grid.
        :param grid_name: Name of the grid object for reference.
        :param line_color: RGB tuple for the grid line color.
        """
        # Remove any existing grid with the same name
        self.remove_actor_by_name(grid_name)

        # Create grid lines in Y and Z directions
        grid_lines = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Generate grid points and lines
        for i in range(ny + 1):
            y = y1 + i * (y2 - y1) / ny
            z = z1
            points.InsertNextPoint(x, y, z)
            z = z2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * i)
            lines.InsertCellPoint(2 * i + 1)

        for i in range(nz + 1):
            y = y1
            z = z1 + i * (z2 - z1) / nz
            points.InsertNextPoint(x, y, z)
            y = y2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * (i + ny + 1))
            lines.InsertCellPoint(2 * (i + ny + 1) + 1)

        # Set points and lines to the grid
        grid_lines.SetPoints(points)
        grid_lines.SetLines(lines)

        # Create a mapper and actor for the grid
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid_lines)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(line_color)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetLineWidth(1.0)
        actor.SetObjectName(grid_name)

        # Add the grid actor to the renderer
        self.add_actor(actor)
        #print(f"X-grid added at X={x} with {ny} lines in Y and {nz} lines in Z.")
    
    def add_y_grid(self, nx=10, nz=10, y=0, x1=-10, x2=10, z1=-10, z2=10, grid_name="YGrid", line_color=(0, 0, 0)):
        """
        Adds a grid in the Y-direction to the VTK renderer.
        :param nx: Number of grid lines in the X-direction.
        :param nz: Number of grid lines in the Z-direction.
        :param y: Y-coordinate of the grid.
        :param x1: Start X-coordinate of the grid.
        :param x2: End X-coordinate of the grid.
        :param z1: Start Z-coordinate of the grid.
        :param z2: End Z-coordinate of the grid.
        :param grid_name: Name of the grid object for reference.
        :param line_color: RGB tuple for the grid line color.
        """
        # Remove any existing grid with the same name
        self.remove_actor_by_name(grid_name)

        # Create grid lines in X and Z directions
        grid_lines = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Generate grid points and lines
        for i in range(nx + 1):
            x = x1 + i * (x2 - x1) / nx
            z = z1
            points.InsertNextPoint(x, y, z)
            z = z2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * i)
            lines.InsertCellPoint(2 * i + 1)

        for i in range(nz + 1):
            x = x1
            z = z1 + i * (z2 - z1) / nz
            points.InsertNextPoint(x, y, z)
            x = x2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * (i + nx + 1))
            lines.InsertCellPoint(2 * (i + nx + 1) + 1)

        # Set points and lines to the grid
        grid_lines.SetPoints(points)
        grid_lines.SetLines(lines)

        # Create a mapper and actor for the grid
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid_lines)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(line_color)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetLineWidth(1.0)
        actor.SetObjectName(grid_name)

        # Add the grid actor to the renderer
        self.add_actor(actor)
        #print(f"Y-grid added at Y={y} with {nx} lines in X and {nz} lines in Z.")

    def add_z_grid(self, nx=10, ny=10, z=0, x1=-10, x2=10, y1=-10, y2=10, grid_name="ZGrid", line_color=(0, 0, 0)):
        """
        Adds a grid in the Z-direction to the VTK renderer.
        :param nx: Number of grid lines in the X-direction.
        :param ny: Number of grid lines in the Y-direction.
        :param z: Z-coordinate of the grid.
        :param x1: Start X-coordinate of the grid.
        :param x2: End X-coordinate of the grid.
        :param y1: Start Y-coordinate of the grid.
        :param y2: End Y-coordinate of the grid.
        :param grid_name: Name of the grid object for reference.
        :param line_color: RGB tuple for the grid line color.
        """
        # Remove any existing grid with the same name
        self.remove_actor_by_name(grid_name)

        # Create grid lines in X and Y directions
        grid_lines = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()

        # Generate grid points and lines
        for i in range(nx + 1):
            x = x1 + i * (x2 - x1) / nx
            y = y1
            points.InsertNextPoint(x, y, z)
            y = y2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * i)
            lines.InsertCellPoint(2 * i + 1)

        for i in range(ny + 1):
            x = x1
            y = y1 + i * (y2 - y1) / ny
            points.InsertNextPoint(x, y, z)
            x = x2
            points.InsertNextPoint(x, y, z)
            lines.InsertNextCell(2)
            lines.InsertCellPoint(2 * (i + nx + 1))
            lines.InsertCellPoint(2 * (i + nx + 1) + 1)

        # Set points and lines to the grid
        grid_lines.SetPoints(points)
        grid_lines.SetLines(lines)

        # Create a mapper and actor for the grid
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(grid_lines)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(line_color)
        actor.GetProperty().SetOpacity(1.0)
        actor.GetProperty().SetLineWidth(1.0)
        actor.SetObjectName(grid_name)

        # Add the grid actor to the renderer
        self.add_actor(actor)
        #print(f"Z-grid added at Z={z} with {nx} lines in X and {ny} lines in Y.")
 
    def add_boundary_grid(self,grid_name="inlet",point1=(0,0,0),point2=(0,1,1),plane=0,nx=1,ny=10,nz=10,line_color=(1,1,1)):   
        """
        Adds a boundary grid to the VTK renderer.
        :param grid_name: Name of the grid object for reference.
        :param point1: First point of the boundary.
        :param point2: Second point of the boundary.
        :param plane: Plane of the boundary (0: X plane, 1: Y plane, 2: Z plane).
        """
        # Remove any existing grid with the same name
        self.remove_actor_by_name(grid_name)

        # Create grid lines in the specified plane
        if plane == 0: # X-plane
            self.add_x_grid(ny=ny, nz=nz, x=point1[0], y1=point1[1], y2=point2[1], z1=point1[2], z2=point2[2], grid_name=grid_name, line_color=line_color)
        elif plane == 1: # Y-plane
            self.add_y_grid(nx=nx, nz=nz, y=point1[1], x1=point1[0], x2=point2[0], z1=point1[2], z2=point2[2], grid_name=grid_name, line_color=line_color)
        elif plane == 2: # Z-plane
            self.add_z_grid(nx=nx, ny=ny, z=point1[2], x1=point1[0], x2=point2[0], y1=point1[1], y2=point2[1], grid_name=grid_name, line_color=line_color)
        else:
            print("Invalid plane for boundary grid. Must be 0, 1, or 2.")

    # these are to add grids in the boundaries of the domain
    def add_left_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (minx,miny,minz)
        point2 = (minx,maxy,maxz)
        plane = 0 # X-plane
        nx = 1
        self.add_boundary_grid(grid_name="inlet",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def add_right_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (maxx,miny,minz)
        point2 = (maxx,maxy,maxz)
        plane = 0
        nx = 1
        self.add_boundary_grid(grid_name="outlet",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def add_front_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (minx,miny,minz)
        point2 = (maxx,miny,maxz)
        plane = 1
        ny = 1
        self.add_boundary_grid(grid_name="front",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def add_back_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (minx,maxy,minz)
        point2 = (maxx,maxy,maxz)
        plane = 1
        ny = 1
        self.add_boundary_grid(grid_name="back",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def add_bottom_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (minx,miny,minz)
        point2 = (maxx,maxy,minz)
        plane = 2
        nz = 1
        self.add_boundary_grid(grid_name="bottom",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def add_top_grid(self,domain_size):
        minx,maxx,miny,maxy,minz,maxz,nx,ny,nz = domain_size
        point1 = (minx,miny,maxz)
        point2 = (maxx,maxy,maxz)
        plane = 2
        nz = 1
        self.add_boundary_grid(grid_name="top",point1=point1,point2=point2,plane=plane,nx=nx,ny=ny,nz=nz)

    def toggle_grids_visibility(self, visible):
        """
        Toggles the visibility of all grid actors in the renderer.
        :param visible: Boolean indicating whether to show or hide the grids.
        """
        grid_names = ["inlet", "outlet", "front", "back", "bottom", "top"]
        actors = self.renderer.GetActors()
        actors.InitTraversal()
        for _ in range(actors.GetNumberOfItems()):
            actor = actors.GetNextActor()
            if actor.GetObjectName() in grid_names:
                actor.SetVisibility(visible)
        self.render_all()

    def hide_boundary_grids(self):
        """
        Hides all boundary grid actors in the renderer.
        """
        self.toggle_grids_visibility(False)
    
    def show_boundary_grids(self):
        """
        Shows all boundary grid actors in the renderer.
        """
        self.toggle_grids_visibility(True)

    def remove_initial_grid(self, grid_name="InitialGrid"):
        """
        Removes the initial grid from the renderer.
        :param grid_name: Name of the grid object to remove.
        """
        self.remove_actor_by_name(grid_name)
        print(f"Initial grid '{grid_name}' removed.")
           
# Thaw: I removed this one due to duplication
#    def rescale_axes_to_geometry(self):
#        """
#        Rescales the axes actor based on the bounds of the geometry loaded in the renderer.
#        """
#         Compute the bounds of all visible props
#        bounds = self.renderer.ComputeVisiblePropBounds()

#        if bounds == (0, -1, 0, -1, 0, -1):
#            print("No geometry found to compute bounds. Axes will not be rescaled.")
#            return

        # Compute the largest extent of the geometry
        # added 1e-3 to prevent zero lengths
#        max_extent = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4], 1e-3)
        
        # Scale the axes length proportionally (e.g., 10% of the max extent)
#        axes_length = max_extent * 0.1
#        self.draw_axes(axes_length)
#        print(f"Axes rescaled to length {axes_length:.2f} based on geometry bounds.")
        
        
    # Attempt to rescale axes labels for better visuals     
    def scale_axes_labels(self, scale_factor):
        """
        Scales the axes labels (X, Y, Z) dynamically based on a scale factor.
        :param scale_factor: The scaling factor for the axes labels' font size.
        """
        axes_labels = [
            self.axes_actor.GetXAxisCaptionActor2D(),
            self.axes_actor.GetYAxisCaptionActor2D(),
            self.axes_actor.GetZAxisCaptionActor2D()
        ]

        for label_actor in axes_labels:
            text_property = label_actor.GetCaptionTextProperty()
            current_size = text_property.GetFontSize()
            # Update font size proportionally
            text_property.SetFontSize(int(current_size * scale_factor))
            # Optionally, adjust other properties (e.g., color, boldness)
            # text_property.SetBold(True)
            # text_property.SetColor(1, 1, 1)  # White labels

        
    def rescale_axes_to_geometry(self):
        """
        Rescales the axes actor and their labels based on the bounds of the geometry loaded in the renderer.
        """
        # Compute the bounds of all visible props
        bounds = self.renderer.ComputeVisiblePropBounds()

        if bounds == (0, -1, 0, -1, 0, -1):
            print("No geometry found to compute bounds. Axes will not be rescaled.")
            return

        # Compute the largest extent of the geometry
        max_extent = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

        # Scale the axes length proportionally (e.g., 10% of the max extent)
        axes_length = max_extent * 0.1
        self.draw_axes(axes_length)

        # Scale the labels proportionally (e.g., scale factor = axes_length / default_length)
        default_axes_length = 5.0  # The default axes length in `vtkAxesActor`
        scale_factor = axes_length / default_axes_length
        self.scale_axes_labels(scale_factor)

        print(f"Axes rescaled to length {axes_length:.2f} and labels scaled with factor {scale_factor:.2f}.")
    
            
