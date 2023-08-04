import igakit.cad as cad
import igakit.nurbs as nurbs
import igakit.plot as plot

# Create the control points of the cube
control_points = [
    [0, 0, 0],  # Vertex 0
    [1, 0, 0],  # Vertex 1
    [1, 1, 0],  # Vertex 2
    [0, 1, 0],  # Vertex 3
    [0, 0, 1],  # Vertex 4
    [1, 0, 1],  # Vertex 5
    [1, 1, 1],  # Vertex 6
    [0, 1, 1],  # Vertex 7
]

# Create the knot vector for a single knot span along each direction
knot_vector = [0, 0, 1, 1]

# Create a T-spline surface (assuming a uniform knot vector in both directions)
surface = cad.Surface(control_points, (knot_vector, knot_vector))

# Create a 3D tensor-product T-spline volume
cube = cad.Volume(surface, (knot_vector, knot_vector, knot_vector))

# Define the material properties and loads (you may adjust these as needed)
youngs_modulus = 210e9  # Young's modulus (Pa)
poissons_ratio = 0.3   # Poisson's ratio
thickness = 0.1        # Thickness of the cube (m)
load = [0, 0, -1000]   # Load applied at the center (N/m^2)

# Convert the T-spline volume to a NURBS volume
nurbs_cube = nurbs.NURBS(cube)

# Perform isogeometric analysis (FEA) on the cube
results = nurbs_cube.isogeometric_analysis(youngs_modulus, poissons_ratio, thickness, load)

# Plot the results (displacements in this example)
plot.volume(nurbs_cube, results.displacements)
