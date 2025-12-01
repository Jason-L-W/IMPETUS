import matplotlib.pyplot as plt
import numpy as np
import tracks

# All functions has to do with testing, plotting, and building the track

#########################################################################################

def plot(results):
    X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = results

    # Plots chosen track part
    fig = plt.figure()

    # --- 3D Plot ---
    ax3d = fig.add_subplot(1, 1, 1, projection='3d') 
    ax3d.plot3D(X, Y, Z, 'b-', label='Track') # Track Line
    ax3d.scatter(X + Nx, Y + Ny, Z + Nz, color='r', label='Normals') # Normal Force
    ax3d.set_xlabel('X')
    ax3d.set_ylabel('Y')
    ax3d.set_zlabel('Z')
    ax3d.set_title(f'{file_name}')
    ax3d.legend()

    # # --- 2D Plot ---
    # # X vs Y Plot
    # ax_xy = fig.add_subplot(2, 2, 2)
    # ax_xy.plot(X, Y, 'g-', label='Track XY')
    # ax_xy.scatter(X + Nx, Y + Ny, color='r', label='Normals')
    # ax_xy.set_xlabel('X')
    # ax_xy.set_ylabel('Y')
    # ax_xy.set_title('X vs Y Plot')
    # ax_xy.legend()

    # # X vs Z Plot
    # ax_xz = fig.add_subplot(2, 2, 3)
    # ax_xz.plot(X, Z, 'm-', label='Track XZ')
    # ax_xz.scatter(X + Nx, Z + Nz, color='r', label='Normals')
    # ax_xz.set_xlabel('X')
    # ax_xz.set_ylabel('Z')
    # ax_xz.set_title('X vs Z Plot')
    # ax_xz.legend()

    # # Y vs Z Plot
    # ax_yz = fig.add_subplot(2, 2, 4)
    # ax_yz.plot(Y, Z, 'c-', label='Track YZ')
    # ax_yz.scatter(Y + Ny, Z + Nz, color='r', label='Normals')
    # ax_yz.set_xlabel('Y')
    # ax_yz.set_ylabel('Z')
    # ax_yz.set_title('Y vs Z Plot')
    # ax_yz.legend()

    plt.tight_layout()
    plt.show()

    return None

#########################################################################################

