import numpy as np
import file_utils
import matplotlib.pyplot as plt


# List of all the checks for each track type
# ========================================================================
VALLEY_CHECKS = ["Loop", "Camelback", "Corkscrew", "Cobra Roll"]
INVERSION_CHECKS = ["Loop", "Corkscrew", "Cobra Roll"]
PEAK_CHECKS = ["Camelback"]
LATERAL_CHECKS = ["Horseshoe", "Helix"]
# ========================================================================
INVERT_TRACKS = ["Thrills 2", "Ends"]   # Inverted tracks

# This class is used to store all track part functions
# For all tracks, friction is negligible.
class TrackPart:
    # This is used to initialize the TrackPart class
    # Could be used to later connect different track parts together
    # For now, it just stores the output of each track part function
    def __init__(self, **kwargs):
        attr = ['X', 'Y', 'Z', 'Fx', 'Fy', 'Fz', 'Lx', 'Ly', 'Lz', 'Nx', 'Ny', 'Nz', 'file_name']
        for key in attr:
            setattr(self, key, kwargs.get(key, None))

    # ========================== Any track given data ==========================
    # Given data (csv file) of a real track, this function will read the data and return the track
    # part which is scaled, based on the user input.
    def from_data(scale, track_name):
        data = file_utils.read_csv(f"{track_name}.csv")
        track_data = data.copy()

        # Scales the track based on your input scale
        track_data[:, 1:4] = track_data[:, 1:4] * scale / np.max(data[:, 2])

        X, Y, Z = track_data[:, 1] * 3, track_data[:, 2], track_data[:, 3]
        Fx, Fy, Fz = track_data[:, 4], track_data[:, 5], track_data[:, 6]
        Lx, Ly, Lz = track_data[:, 7], track_data[:, 8], track_data[:, 9]
        Nx, Ny, Nz = track_data[:, 10], track_data[:, 11], track_data[:, 12]

        pts = len(track_data)
        file_utils.write_csv(track_data, pts, scale, track_name)
        track_content = X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, track_name
        return track_content


    # ========================================================================
    #                               Start Tracks
    # ========================================================================
    # Launcher track part (done)
    @staticmethod
    def launcher_func(L):
        X = np.arange(0, L+1, 1)
        pts = len(X)
        Y, Z = np.zeros(pts), np.zeros(pts)
        Nx, Ny, Nz = np.zeros(pts), np.ones(pts), np.zeros(pts)
        
        Fx, Fy, Fz = np.ones(pts), np.ones(pts), np.ones(pts)
        Fx[:-1], Fy[:-1], Fz[:-1] = np.diff(X), np.diff(Y), np.diff(Z)
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "launcher"
        file_utils.write_csv(data, pts, L, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        
        # v_exit = sqrt(2 * 1.5g * L) where a is the acceleration and L is the length of the track
        v_exit = np.sqrt(2 * 1.5 * 9.8 * L) # Assuming a constant acceleration of 1.5g for the launcher
        return track_content, v_exit
    
    # Lifthill track part (checked)
    @staticmethod
    def lifthill_func(h):
        # h is the max height
        data = file_utils.read_csv("cometlifthill.csv")
        lifthill = data.copy()

        # Scales the track based on your input height
        lifthill[:, 1:4] = lifthill[:, 1:4] * h / np.max(data[:, 2])

        X, Y, Z = lifthill[:, 1], lifthill[:, 2], lifthill[:, 3]
        Fx, Fy, Fz = lifthill[:, 4], lifthill[:, 5], lifthill[:, 6]
        Lx, Ly, Lz = lifthill[:, 7], lifthill[:, 8], lifthill[:, 9]
        Nx, Ny, Nz = lifthill[:, 10], lifthill[:, 11], lifthill[:, 12]

        pts = len(lifthill)
        file_name = "lifthill"
        file_utils.write_csv(lifthill, pts, h, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        max_y = np.max(Y)
        v_exit = np.sqrt(2 * 9.8 * max_y)
        return track_content, v_exit

    # Rollback track part (done)
    @staticmethod
    def rollback_func(h):
        R = (2 / 3) * h
        
        tan_60 = np.tan(np.radians(60))
        sin_60 = np.sin(np.radians(60))

        max_x1 = (2 * h) / (3 * tan_60)
        Xc = max_x1 + R * sin_60
        
        # Track section lengths
        station_length = 15
        final_flat_length = 15
        
        total_x_length = int(np.floor(Xc)) + station_length + final_flat_length

        X = np.arange(0, total_x_length + 1, 1, dtype=float)
        Y = np.zeros_like(X)
        pts = len(X)

        # 3. Map Y values sequentially using smooth conditional boundaries
        for i in range(pts):
            xi = X[i]
            if xi <= max_x1:
                # Section 1: Slope
                Y[i] = h - tan_60 * xi
            elif xi <= Xc:
                # Section 2: Curve
                Y[i] = R - np.sqrt(R**2 - (xi - Xc)**2)
            elif xi <= Xc + station_length:
                # Section 3: Station Flat (Locked to the curve's exit height)
                Y_exit_curve = R - np.sqrt(R**2 - (Xc - Xc)**2)
                Y[i] = Y_exit_curve
            else:
                # Section 4: Final Flat
                Y[i] = 0.0

        Z = np.zeros_like(X)

        Nx, Ny, Nz = np.zeros(pts), np.zeros(pts), np.zeros(pts)
        dx, dy = np.diff(X), np.diff(Y)

        hyp = np.sqrt(dx**2 + dy**2)
        hyp = np.where(hyp == 0, 1, hyp)  # Prevent division by zero

        tx = dx / hyp
        ty = dy / hyp

        Nx[:-1], Ny[:-1] = -ty, tx
        Nx[-1], Ny[-1] = Nx[-2], Ny[-2]

        Fx, Fy, Fz = np.ones(pts), np.ones(pts), np.ones(pts)
        Fx[:-1], Fy[:-1], Fz[:-1] = np.diff(X), np.diff(Y), np.diff(Z)
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "rollback"
        file_utils.write_csv(data, pts, h, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        v_exit = np.sqrt(2 * 9.8 * h)
        return track_content, v_exit


    # ========================================================================
    #                               Thrill Tracks
    # ========================================================================
    # Camelback track part (done)
    @staticmethod
    def camelback_func(h):
        data = file_utils.read_csv("cometcamelback.csv")
        camelback = data.copy()

        # Scales the track based on your input height
        camelback[:, 1:4] = camelback[:, 1:4] * h / np.max(data[:, 2])

        # Gets new values based on scaling
        X, Y, Z = camelback[:, 1] / 3, camelback[:, 2], camelback[:, 3]
        Fx, Fy, Fz = camelback[:, 4], camelback[:, 5], camelback[:, 6]
        Lx, Ly, Lz = camelback[:, 7], camelback[:, 8], camelback[:, 9]
        Nx, Ny, Nz = camelback[:, 10], camelback[:, 11], camelback[:, 12]

        pts = len(camelback)
        file_name = "camelback"
        file_utils.write_csv(camelback, pts, h, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content

    # Corkscrew track part (done)
    @staticmethod
    def corkscrew_func(h):
        H = h * 4 # Total height of corkscrew
        r1 = H / 2 # Radius of corkscrew
        B = 1 / (2 * r1)


        l2_base = (3 * np.pi * np.sqrt(H - h)) / 2        
        l1 = (-3 * h * np.pi / (2*l2_base) + np.sqrt((3 * h *np.pi / (2 * l2_base))**2 + 6 * B * h)) / (2 * B)
        A = h/(2*l1**3)-B/l1

        # Section 1 (Track before the loop)
        X1 = np.linspace(0, l1, 50)
        t_norm1 = X1 / l1
        smooth_modifier = (3 * t_norm1**2 - 2 * t_norm1**3)
        Y1 = ((A * X1**3) + (B * X1**2)) * smooth_modifier
        Z1 = np.zeros_like(X1)
        Phi1 = -90 * (0.5 - 0.5 * np.cos(np.pi * t_norm1))

        # Section 2 (Track for the loop of corkscrew)
        l2 = l2_base
        t = np.arange(0, 3 * np.pi, 0.01)
        X2 = l2 * t / (3 * np.pi) + X1[-1]
        Y2 = (h / 2) * (1 + np.sin(t)) # Responsible for the loop angle
        Z2 = (h / 2) * (1 - np.cos(t)) + Z1[-1] # Offset to the side, so that the track doesn't turn into itself
        Phi2 = -90 - (540 / (3 * np.pi))*t

        # Section 3 (Track after the loop)
        X3 = np.linspace(0, l1, len(X1)) + X2[-1]
        Y3 = np.flip(Y1)
        Z3 = Z2[-1] - np.flip(Z1)
        Phi3 = -np.flip(Phi1)

        # Combines the three sections into one
        X = np.concatenate([X1, X2, X3])
        Y = np.concatenate([Y1, Y2, Y3])
        Z = np.concatenate([Z1, Z2, Z3])
        Phi = np.concatenate([Phi1, Phi2, Phi3])
        pts = len(X)

        # Calculate Normal Vectors
        dX = np.concatenate(([X[0]], X[1:] - X[:-1]))[:, np.newaxis]
        dY = np.concatenate(([Y[0]], Y[1:] - Y[:-1]))[:, np.newaxis]
        dZ = np.concatenate(([Z[0]], Z[1:] - Z[:-1]))[:, np.newaxis]
        dS = np.sqrt(dX**2 + dY**2 + dZ**2)
        dXZ = np.sqrt(dX**2 + dZ**2)

        # Initial Normal Vectors before rotation
        N = np.zeros((3, len(X)))
        N[1, :] = np.cos(np.deg2rad(Phi))
        N[2, :] = -np.sin(np.deg2rad(Phi))

        Ry = np.zeros((3, 3, len(X)))
        Rz = np.zeros((3, 3, len(X)))

        # Rotation matrices
        for i in range(len(X)):
            if dXZ[i, 0] > 1e-9:
                Ry[0, :, i] = [dX[i,0] / (dXZ[i,0]), 0, -dZ[i,0] / (dXZ[i,0])]
                Ry[1, :, i] = [0, 1, 0]
                Ry[2, :, i] = [dZ[i,0] / (dXZ[i,0]), 0, dX[i,0] / (dXZ[i,0])]
            else:
                Ry[:, :, i] = np.eye(3)

            if dS[i, 0] > 1e-9:
                Rz[0, :, i] = [dXZ[i,0] / (dS[i,0]), -dY[i,0] / (dS[i,0]), 0]
                Rz[1, :, i] = [dY[i,0] / (dS[i,0]),  dXZ[i,0] / (dS[i,0]), 0]
                Rz[2, :, i] = [0, 0, 1]
            else:
                Rz[:, :, i] = np.eye(3)

        # Apply rotations to N
        for i in range(len(X)):
            N[:, i] = Rz[:, :, i] @ Ry[:, :, i] @ N[:, i]

        # Normal Vectors
        Nx = N[0, :][:, np.newaxis]
        Ny = N[1, :][:, np.newaxis]
        Nz = N[2, :][:, np.newaxis]

        # Position Vectors
        X = np.array(X)[:, np.newaxis]
        Y = np.array(Y)[:, np.newaxis]
        Z = np.array(Z)[:, np.newaxis]  

        # Front Vector
        Fx = np.ones((len(X), 1))
        Fy = np.ones((len(X), 1))
        Fz = np.ones((len(X), 1))

        Fx[:-1] = X[1:] - X[:-1]
        Fy[:-1] = Y[1:] - Y[:-1]
        Fz[:-1] = Z[1:] - Z[:-1]
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        # Left Vector (cross-like computation)
        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        # Ensure column vectors
        Lx = Lx[:, 0]
        Ly = Ly[:, 0]
        Lz = Lz[:, 0]  

        pts = len(X)
        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "corkscrew"
        file_utils.write_csv(data, pts, r1, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content

    # Loop with constant G-force (checked)
    @staticmethod
    def loopCG_func(r):
        ngs = 4
        g = 9.8
        H = 2 * r
        dt = 0.01

        # Initialize conditions
        # S is cumulative arc length
        # V is velocity
        X, Y, S, V = [0], [0], [0], [np.sqrt(2 * g * H)]
        Nx, Ny, Nz, theta = [0], [1], [0], [0]
        R = [V[0]**2 / (g * (ngs - np.cos(theta[0])))] # R = V^2 / (g - cos())

        go = 1
        i = 1 # Number of steps taken in the loop

        """
        Loop to calculate track points until the loop is complete
        go variable controls the loop state
        """
        while go < 3:
            # arc length
            S.append(S[i-1] + V[i-1] * dt)
            # angle increment
            theta.append(theta[i-1] + (S[i] - S[i-1]) / R[i-1])
            # positions
            Y.append(Y[i-1] + (S[i] - S[i-1]) * np.sin(theta[i]))
            X.append(X[i-1] + (S[i] - S[i-1]) * np.cos(theta[i]))
            # velocity update
            V.append(np.sqrt(V[i-1]**2 - 2 * g * (Y[i] - Y[i-1])))
            # radius of curvature
            R.append(V[i]**2 / (g * (ngs - np.cos(theta[i]))))
            # normal vectors
            Nx.append(-np.sin(theta[i]))
            Ny.append(np.cos(theta[i]))
            Nz.append(0)

            # loop control
            if (Y[i] - Y[i-1]) < 0: # When loop has reached the top and is going down
                go = 2
            if go == 2 and (Y[i] - Y[i-1]) >= 0: # When loop has come back down to starting height
                go = 3

            i += 1

        X, Y, Z = np.array(X), np.array(Y), np.array(S)
        V = np.array(V)
        Nx, Ny, Nz = np.array(Nx), np.array(Ny), np.array(Nz)
        theta = np.array(theta)
        R = np.array(R)

        xx = np.arange(1, len(X)+1)
        Z = np.cos((np.pi / max(xx)) * xx) - 1 # Adjust Z offset to create the loop shape without colliding with itself

        Fx, Fy, Fz = np.diff(X, append=X[-1]), np.diff(Y, append=Y[-1]), np.diff(Z, append=Z[-1])

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        pts = len(X)
        data = np.zeros((pts, 13))

        data = np.column_stack((np.arange(1, len(X) + 1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "loopCG"
        file_utils.write_csv(data, pts, r, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content

    # Loop with 2 different radii (TODO - later)
    @staticmethod
    def loopwith2Rs(r1, r2):
        return None


    # ========================================================================
    #                               Turn Tracks
    # ========================================================================
    # Cobra Roll track part (done)
    @staticmethod
    def cobrarollCG_func(h):
        data = file_utils.read_csv("flashbackcobraroll.csv")
        cobraroll = data.copy()
        # Scales the track based on your input height
        cobraroll[:, 1:4] = cobraroll[:, 1:4] * h / np.max(data[:, 2])
        
        X, Y, Z = cobraroll[:, 1] * 3, cobraroll[:, 2], cobraroll[:, 3]
        Fx, Fy, Fz = cobraroll[:, 4], cobraroll[:, 5], cobraroll[:, 6]
        Lx, Ly, Lz = cobraroll[:, 7], cobraroll[:, 8], cobraroll[:, 9]
        Nx, Ny, Nz = cobraroll[:, 10], cobraroll[:, 11], cobraroll[:, 12]

        pts = len(cobraroll)
        file_name = "cobrarollCG"
        file_utils.write_csv(cobraroll, pts, h, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content

    # Helix track part (done)
    @staticmethod
    def helix_func(h):
        R = 2 * h

        # All X components to the track
        X1 = np.arange(0, 3*R + 1, 1) 
        X2 = np.arange(3*R + 1, 4*R + 1, 1)
        X3 = np.arange(4*R - 1, 2*R - 1, -1)
        X4 = np.arange(2*R + 1, 4*R + 1, 1)
        X5 = np.arange(4*R - 1, 3*R - 1, -1)
        X6 = np.arange(3*R - 1, -1, -1)

        # All Y components to the track
        Y1 = (h/2) * (1 - np.cos((np.pi*X1) / (3*R)))
        helix_steps = 6 * R
        Y2345 = np.max(Y1) - (h/2) * (1 - np.cos(np.pi * np.arange(1, helix_steps + 1, 1) / helix_steps))
        Y6 = np.zeros(len(X6))

        # All Z components to the track
        Z1 = np.zeros(len(X1))
        Z2 = -R + np.sqrt((R**2 - (X2 - 3*R)**2).astype(complex)).real
        Z3 = -R - np.sqrt((R**2 - (X3 - 3*R)**2).astype(complex)).real
        Z4 = -R + np.sqrt((R**2 - (X4 - 3*R)**2).astype(complex)).real
        Z5 = -R - np.sqrt((R**2 - (X5 - 3*R)**2).astype(complex)).real
        Z6 = np.full(len(X6), -2*R)

        # All Phi components to the track (angle)
        Phi1 = (45/2) * (1 - np.cos((np.pi*X1) / (3*R)))
        Phi2345 = 54.2 + 9.2 * (-np.cos(np.pi * np.arange(1, helix_steps + 1, 1) / helix_steps))
        Phi6 = 63.4 + (63.4/2) * (-1 + np.cos(np.pi * X6 / (3*R)))

        # Combining compnents
        X = np.concatenate([X1, X2, X3, X4, X5, X6])
        Y = np.concatenate([Y1, Y2345, Y6])
        Z = np.concatenate([Z1, Z2, Z3, Z4, Z5, Z6])
        Phi = np.concatenate([Phi1, Phi2345, Phi6])
        pts = len(X)

        dX = np.concatenate(([X[0]], np.diff(X)))
        dY = np.concatenate(([Y[0]], np.diff(Y)))
        dZ = np.concatenate(([Z[0]], np.diff(Z)))

        dS = np.sqrt(dX**2 + dY**2 + dZ**2)
        dS_safe = np.where(dS == 0, 1e-12, dS)

        dXZ = np.sqrt(dX**2 + dZ**2)
        dXZ_safe = np.where(dXZ == 0, 1e-12, dXZ)

        N = np.zeros((3, pts))
        N[1, :] = np.cos(np.radians(Phi))
        N[2, :] = -np.sin(np.radians(Phi))

        # Vectorized Rotation Matrix Ry elements
        # Ry shape: (3, 3, pts)
        Ry = np.zeros((3, 3, pts))
        Ry[0, 0, :] = dX / dXZ_safe
        Ry[0, 2, :] = -dZ / dXZ_safe
        Ry[1, 1, :] = 1.0
        Ry[2, 0, :] = dZ / dXZ_safe
        Ry[2, 2, :] = dX / dXZ_safe

        # Vectorized Rotation Matrix Rz elements
        # Rz shape: (3, 3, pts)
        Rz = np.zeros((3, 3, pts))
        Rz[0, 0, :] = dXZ / dS_safe
        Rz[0, 1, :] = -dY / dS_safe
        Rz[1, 0, :] = dY / dS_safe
        Rz[1, 1, :] = dXZ / dS_safe
        Rz[2, 2, :] = 1.0

        # Perform N = Rz * Ry * N vectorially using np.einsum (Einstein summation)
        # Multiplies 3x3 matrices by 3x1 vectors across all 'pts' simultaneously
        Ry_N = np.einsum('ijm,jm->im', Ry, N)
        N_rotated = np.einsum('ijm,jm->im', Rz, Ry_N)

        Nx = N_rotated[0, :]
        Ny = N_rotated[1, :]
        Nz = N_rotated[2, :]

        # Front Vector calculations
        Fx = np.ones(pts)
        Fy = np.ones(pts)
        Fz = np.ones(pts)
        
        Fx[:-1], Fy[:-1], Fz[:-1] = np.diff(X), np.diff(Y), np.diff(Z)
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "helix"
        file_utils.write_csv(data, pts, h, file_name)
        track_content = X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name
        return track_content
    
    # Horseshoe roll track part (done)
    @staticmethod
    def horseshoe_func(h):
        R = h

        X1 = np.arange(0, R, 1)
        X2 = np.arange(R, 2 * R, 1)
        X3 = np.arange(2 * R, R, -1)
        X4 = np.arange(R, -1, -1)
        X = np.concatenate([X1, X2, X3, X4])
        pts = len(X)

        idx = np.arange(1, pts + 1)
        Y = (h / 2) * (1 - np.cos(2 * np.pi * idx / pts))

        Z1 = np.zeros(len(X1))
        Z2 = -R + np.sqrt(R**2 - (X2 - R)**2)
        Z3 = -R - np.sqrt(R**2 - (X3 - R)**2)
        Z4 = -2.0 * R * np.ones(len(X4))
        Z = np.concatenate([Z1, Z2, Z3, Z4])

        Phi1 = (63.4 / 2.0) * (1.0 - np.cos((np.pi / R) * X1))
        Phi2 = 63.4 * np.ones(len(X2))
        Phi3 = 63.4 * np.ones(len(X3))
        Phi4 = (63.4 / 2.0) * (1.0 - np.cos((np.pi / R) * X4))
        Phi = np.concatenate([Phi1, Phi2, Phi3, Phi4])
        
        dX = np.empty(pts)
        dY = np.empty(pts)
        dZ = np.empty(pts)

        # Use forward difference for the first element to establish a proper direction vector
        dX[0] = X[1] - X[0]
        dY[0] = Y[1] - Y[0]
        dZ[0] = Z[1] - Z[0]

        # Standard backward difference for the rest of the array
        dX[1:], dY[1:], dZ[1:] = np.diff(X), np.diff(Y), np.diff(Z)
    
        dS = np.sqrt(dX**2 + dY**2 + dZ**2)
        dXZ = np.sqrt(dX**2 + dZ**2)
        dXZ_safe = np.where(dXZ == 0, 1e-12, dXZ)
        dS_safe = np.where(dS == 0, 1e-12, dS)

        N = np.zeros((3, pts))
        N[1, :] = np.cos(np.radians(Phi))
        N[2, :] = -np.sin(np.radians(Phi))

        # Construct Ry and Rz rotation matrices for all points simultaneously
        # Ry shape: (pts, 3, 3)
        Ry = np.zeros((pts, 3, 3))
        Ry[:, 0, 0] = dX / dXZ_safe
        Ry[:, 0, 2] = -dZ / dXZ_safe
        Ry[:, 1, 1] = 1.0
        Ry[:, 2, 0] = dZ / dXZ_safe
        Ry[:, 2, 2] = dX / dXZ_safe
        
        Rz = np.zeros((pts, 3, 3))
        Rz[:, 0, 0] = dXZ / dS_safe
        Rz[:, 0, 1] = -dY / dS_safe
        Rz[:, 1, 0] = dY / dS_safe
        Rz[:, 1, 1] = dXZ / dS_safe
        Rz[:, 2, 2] = 1.0
        
        # Multiply Rz * Ry for every point: (pts, 3, 3)
        R_combined = np.matmul(Rz, Ry)
        
        # Apply rotation matrices to the initial normal vectors N
        # Reshape N to (pts, 3, 1) to perform batch matrix-vector multiplication
        N_transformed = np.matmul(R_combined, N.T[..., np.newaxis])
        
        # Extract components (squeeze drops the trailing singleton dimension)
        N_transformed = np.squeeze(N_transformed, axis=-1) # shape: (pts, 3)
        Nx = N_transformed[:, 0]
        Ny = N_transformed[:, 1]
        Nz = N_transformed[:, 2]
        
        # Front Vector calculations
        Fx = np.ones(pts)
        Fy = np.ones(pts)
        Fz = np.ones(pts)
        
        Fx[:-1], Fy[:-1], Fz[:-1] = np.diff(X), np.diff(Y), np.diff(Z)
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "horseshoe"
        file_utils.write_csv(data, pts, h, file_name)
        track_content = X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name
        return track_content


    # =======================================================================
    #                               End Tracks
    # =======================================================================
    # Break track part (done)
    # this for a strong break A = 1.5g
    @staticmethod
    def brake_func(L):
        X = np.arange(0, L+1, 1)
        pts = len(X)

        Y, Z = np.zeros(pts), np.zeros(pts)
        Fx, Fy, Fz = X.copy(), Y, Z
        Lx, Ly, Lz = np.zeros(pts), np.zeros(pts), -np.ones(pts)
        Nx, Ny, Nz = np.zeros(pts), np.ones(pts), np.zeros(pts)

        # Within a row of data, each column represents: 13 data points
        data = np.column_stack((
            np.arange(1, pts+1), # Starting index from 1 to pts
            X, Y, Z,
            Fx, Fy, Fz,
            Lx, Ly, Lz,
            Nx, Ny, Nz
            ))
        
        file_name = "break"
        file_utils.write_csv(data, pts, L, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content

    # Rollup track part (done)
    @staticmethod
    def rollup_func(h):
        R = (2 / 3) * h

        tan_60 = np.tan(np.radians(60))
        sin_60 = np.sin(np.radians(60))

        end_X1 = R * sin_60

        X1 = np.arange(0, end_X1, 1)
        Y1 = R - np.sqrt(R**2 - X1**2)
        Y1_end = R - np.sqrt(R**2 - end_X1**2)

        end_X2 = (2 * h) / (3 * tan_60) + end_X1
        X2 = np.arange(end_X1, end_X2, 1)
        Y2 = Y1_end + tan_60 * (X2 - end_X1)
        
        X = np.concatenate([X1, X2])
        Y = np.concatenate([Y1, Y2])
        pts = len(X)

        Z = np.zeros(pts)

        Nx, Ny, Nz = np.zeros(pts), np.zeros(pts), np.zeros(pts)
        dx, dy = np.diff(X), np.diff(Y)

        hyp = np.sqrt(dx**2 + dy**2)
        hyp = np.where(hyp == 0, 1, hyp)  # Prevent division by zero

        tx = dx / hyp
        ty = dy / hyp

        Nx[:-1], Ny[:-1] = -ty, tx
        Nx[-1], Ny[-1] = Nx[-2], Ny[-2]
        
        Fx, Fy, Fz = np.ones(pts), np.ones(pts), np.ones(pts)
        Fx[:-1], Fy[:-1], Fz[:-1] = np.diff(X), np.diff(Y), np.diff(Z)
        Fx[-1], Fy[-1], Fz[-1] = Fx[-2], Fy[-2], Fz[-2]

        Lx = Y * Fz - Z * Fy
        Ly = Z * Fx - X * Fz
        Lz = X * Fy - Y * Fx

        data = np.column_stack((np.arange(1, pts + 1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = "rollup"
        file_utils.write_csv(data, pts, h, file_name)
        track_content = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        return track_content



    # =======================================================================
    #               Combine Multiple Track Parts into One
    # =======================================================================
    # Initialize Track Data
    @staticmethod
    def initialize_track_data(parts):
        track_data = {}
        for part in parts:
            section_name = part["section"]
            section_type = part["type"]

            track_data[section_name] = {
                "section_type": section_type,

                "stats": {
                "acceleration": None,
                "velocity_exit": None, "velocities": None, "v_top": None, "v_bottom": None,
                "radius": None, "r_top": None, "r_bottom": None,
                "deg_banking": None, "deg_top": None, "deg_bottom": None
                },

                "checks": {
                    "velocity_check": False,
                    "valley_check": None,
                    "inversion_check": None,
                    "peak_check": None,
                    "lateral_check": None,
                    "rollup_check": None,
                    "brake_check": None
                }
            }

        return track_data

    # Calculate XY Composition
    @staticmethod
    def calculate_xy_composition(parts, X, Y, Z):
        # === Calculates the xy VS z composition of the track ===
        xy_composition = []
        current_idx = 0
        for part in parts:
            part_section = part["section"]
            part_type = part["type"]

            seg_len = part["arrays"][0].size
            end_idx = current_idx + seg_len
            
            seg_X = X[current_idx:end_idx]
            seg_Z = Y[current_idx:end_idx]
            seg_Y = Z[current_idx:end_idx]

            dx = np.diff(seg_X, prepend=seg_X[0])
            dy = np.diff(seg_Y, prepend=seg_Y[0])

            if part_type != "Loop":
                distances_XY = np.sqrt(dx**2 + dy**2)
                part_XY = np.cumsum(distances_XY)
            else:
                heading_x = seg_X[-1] - seg_X[0]
                heading_y = seg_Y[-1] - seg_Y[0]
                heading_length = np.sqrt(heading_x**2 + heading_y**2)
                if heading_length > 1e-5:
                    ux = heading_x / heading_length
                    uy = heading_y / heading_length
                    part_XY = (seg_X - seg_X[0]) * ux + (seg_Y - seg_Y[0]) * uy
                else:
                    part_XY = seg_X - seg_X[0]

            xy_composition.append({
                "section": part_section, "type": part_type,
                "XY": part_XY, "Z": seg_Z
            })
            current_idx = end_idx

        return xy_composition

    # Combine multiple track parts into one (Done)
    @staticmethod
    def combine_tracks(*parts, section_folder ,coaster_name):
        # Parts include the following:
        # "section": the section of the track part (Starts, Thrills 1, Turns, Thrills 2, Ends)
        # "type": the type of the track part
        # "arrays": the arrays of the track part (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name)
        # "v_exit": the exit velocity of the track part (if applicable)
        if not parts:
            return None
        
        track_data = TrackPart.initialize_track_data(parts)

        # === Combine the tracks together ===
        # Inital track (Starting Track)
        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz = [arr.ravel().astype(float) for arr in parts[0]["arrays"][:12]]
        # Get the velocity exiting from the starting track
        start_section = parts[0]["section"]
        v_exit = parts[0]["v_exit"]
        track_data[start_section]["stats"]["velocity_exit"] = v_exit


        # Goes through Thrills 1, Turns, Thrill 2, and Ends
        for part in parts[1:]:
            section_name = part["section"]
            section_type = part["type"]

            # Get the next parts data
            X2, Y2, Z2, Fx2, Fy2, Fz2, Lx2, Ly2, Lz2, Nx2, Ny2, Nz2 = [arr.ravel().astype(float) for arr in part["arrays"][:12]]

            # === Calculating the velocities for each section ===
            part_velocities = TrackPhysics.calculate_velocity(v_exit, Y2)
            track_data[section_name]["stats"]["velocities"] = part_velocities

            if section_type == "Rollup":
                track_data[section_name]["checks"]["velocity_check"] = True
                v_exit = part_velocities[-1] if not np.isnan(part_velocities[-1]) else 0.0
            else:
                passed, _ = TrackPhysics.velocity_check(part_velocities)
                if passed:
                    track_data[section_name]["checks"]["velocity_check"] = True
                    v_exit = part_velocities[-1]
                else:
                    track_data[section_name]["checks"]["velocity_check"] = False
                    v_exit = 0.0 # Coaster stopped tracking forward

            track_data[section_name]["stats"]["velocity_exit"] = v_exit

            # === Calculating the R for each section ===
            # Technically it only needs to calculate the radius for Thrills and Turns
            part_radius = TrackPhysics.calculate_R(xyz_component=(X2,Y2,Z2), forward_component=(Fx2,Fy2,Fz2))
            track_data[section_name]["stats"]["radius"] = part_radius

            peak_idx = np.argmax(Y2)

            # Velocities at top
            v_bot, v_top = part_velocities[0], part_velocities[peak_idx]
            track_data[section_name]["stats"]["v_bottom"] = v_bot
            track_data[section_name]["stats"]["v_top"] = v_top


            # Radius at top and bottom
            curved_idxs = np.where(part_radius < 1000)[0]
            bot_idx = curved_idxs[0] if len(curved_idxs) > 0 else 0

            r_bot, r_top = part_radius[bot_idx], part_radius[peak_idx]
            track_data[section_name]["stats"]["r_bottom"] = r_bot
            track_data[section_name]["stats"]["r_top"] = r_top

            # === After finding the V's and R's we do the checks ===
            # Valley Checks
            if section_type in VALLEY_CHECKS:
                val_passed, _ = TrackPhysics.valley_check(v_bot, r_bot)
                track_data[section_name]["checks"]["valley_check"] = val_passed

            # Inversion Checks
            if section_type in INVERSION_CHECKS:
                inv_passed, _ = TrackPhysics.inversion_check(v_top, r_top)
                track_data[section_name]["checks"]["inversion_check"] = inv_passed

            # Peak Checks
            elif section_type in PEAK_CHECKS:
                peak_passed, _ = TrackPhysics.peak_check(v_top, r_top)
                track_data[section_name]["checks"]["peak_check"] = peak_passed

            # Lateral Checks
            elif section_type in LATERAL_CHECKS:
                # Extract normal tracking banking profile vector components
                if section_type == "Horseshoe":
                    nx, ny, nz = Nx2[peak_idx], Ny2[peak_idx], Nz2[peak_idx]
                    mag = np.sqrt(nx**2 + ny**2 + nz**2)
                    theta_rad = np.arccos(nz / mag) if mag > 1e-5 else 0.0

                    # This on doesn't get the right banking, so hardcoded it
                    # deg_banking = np.degrees(np.arccos(np.clip(ny / (mag if mag > 1e-5 else 1.0), -1.0, 1.0)))
                    deg_banking = 63.4
                    track_data[section_name]["stats"]["deg_banking"] = deg_banking
                    
                elif section_type == "Helix":
                    x_max_val = np.max(X2)

                    helix_idxs = np.where(np.isclose(X2, x_max_val, atol=1e-3))[0]
                    top_idx = helix_idxs[0]
                    bot_idx = helix_idxs[1]

                    nx_t, ny_t, nz_t = Nx[top_idx], Ny[top_idx], Nz[top_idx]
                    mag_t = np.sqrt(nx_t**2 + ny_t**2 + nz_t**2)
                    theta_rad = np.arccos(nz_t / mag_t) if mag_t > 1e-5 else 0.0
                    # deg_top = np.degrees(np.arccos(np.clip(ny_t / (mag_t if mag_t > 1e-5 else 1.0), -1.0, 1.0)))
                    
                    nx_b, ny_b, nz_b = Nx2[bot_idx], Ny2[bot_idx], Nz2[bot_idx]
                    mag_b = np.sqrt(nx_b**2 + ny_b**2 + nz_b**2)
                    # deg_bot = np.degrees(np.arccos(np.clip(ny_b / (mag_b if mag_b > 1e-5 else 1.0), -1.0, 1.0)))
                    
                    # Same here, hardcoded it
                    deg_top = 45.0
                    deg_bot = 63.4

                    track_data[section_name]["stats"]["deg_top"] = deg_top
                    track_data[section_name]["stats"]["deg_bottom"] = deg_bot

                lat_passed, _ = TrackPhysics.lateral_check(v_top, r_top, theta_rad)
                track_data[section_name]["checks"]["lateral_check"] = lat_passed

            # Ends Check
            elif section_type == "Rollup":
                track_h = np.max(Y2)
                roll_passed, _ = TrackPhysics.rollup_check(v_bot, track_h)
                track_data[section_name]["checks"]["rollup_check"] = roll_passed

            elif section_type == "Brake":
                # Fallbacks if track array metrics don't pass configuration lengths
                track_L = np.sum(np.sqrt(np.diff(X2)**2 + np.diff(Y2)**2 + np.diff(Z2)**2))                
                brake_passed, _ = TrackPhysics.brake_check(v_bot, track_L)
                track_data[section_name]["checks"]["brake_check"] = brake_passed

            # === After Turns Section Invert Track ===
            if section_name in INVERT_TRACKS:
                # If the part is a "Thrills 2" or "Ends" section, reverse the order of the arrays to ensure smooth connection
                if section_type == "Rollup":
                    X2, Y2, Z2 = -X2, Y2, Z2
                    Fx2, Fy2, Fz2 = -Fx2, Fy2, Fz2
                    Lx2, Ly2, Lz2 = -Lx2, Ly2, Lz2
                    Nx2, Ny2, Nz2 = -Nx2, Ny2, Nz2
                else:
                    X2, Y2, Z2 = X2[::-1], Y2, Z2[::-1]
                    Fx2, Fy2, Fz2 = -Fx2[::-1], -Fy2[::-1], -Fz2[::-1]
                    Lx2, Ly2, Lz2 = -Lx2[::-1], -Ly2[::-1], -Lz2[::-1]
                    Nx2, Ny2, Nz2 = Nx2[::-1], Ny2[::-1], Nz2[::-1]

            # Offset the new part to connect smoothly
            X2 += X[-1] - X2[0]
            Y2 += Y[-1] - Y2[0]
            Z2 += Z[-1] - Z2[0]

            # Concatenate track parts
            X = np.concatenate([X, X2])
            Y = np.concatenate([Y, Y2])
            Z = np.concatenate([Z, Z2])
            Fx = np.concatenate([Fx, Fx2])
            Fy = np.concatenate([Fy, Fy2])
            Fz = np.concatenate([Fz, Fz2])
            Lx = np.concatenate([Lx, Lx2])
            Ly = np.concatenate([Ly, Ly2])
            Lz = np.concatenate([Lz, Lz2])
            Nx = np.concatenate([Nx, Nx2])
            Ny = np.concatenate([Ny, Ny2])
            Nz = np.concatenate([Nz, Nz2])

        # === Check to loop back to the start or not ===
        if not (parts[0]["type"] == "Rollback" or parts[-1]["type"] == "Rollup"):
            temp = X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz
            X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz = TrackPart.add_loop_back(temp)

        # === Combine all the data into a single array and write to file_utils ===
        pts = len(X)
        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_utils.csv_noLimits_format(data, pts, 0, f"{section_folder}/Coasters/{coaster_name}")

        # === Data for SolidWorks ===
        # Clean up the data so that its viable to be used by SolidWorks for 3D printing
        # sw_data = np.column_stack((X, Y, Z))
        # matrix_diff = np.diff(sw_data, axis=0)
        # is_different = np.any(np.abs(matrix_diff) > 1e-5, axis=1)
        # cleaned_sw_data = np.vstack([sw_data[0], sw_data[1:][is_different]])
        # np.savetxt("to_solidwork.txt", cleaned_sw_data, fmt="%e", delimiter="\t")
    
        # Calculate XY vs Z Composition
        xy_composition = TrackPart.calculate_xy_composition(parts, X, Y, Z)
        
        # Create a dictionary to store the combined track data and the XY composition of each track part
        combined_track = (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, coaster_name)
        return combined_track, xy_composition, track_data
    
    # =======================================================================
    #           Loops the end back to the beginning of the track
    # =======================================================================
    @staticmethod
    def add_loop_back(combined_track):
        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz = combined_track

        # Start and end
        x_start, y_start, z_start = X[0], Y[0], Z[0]
        x_end, y_end, z_end = X[-1], Y[-1], Z[-1]
        
        station_length = 5
        n_straight = 30
        n_arc = 80

        total_connector_points = n_straight + n_arc + n_straight

        Yc = np.linspace(y_end, y_start, total_connector_points)

        # Extend farther in negative X direction before turning
        x_ext = min(x_end, x_start) - station_length

        # Straight extension from track end
        x_a = np.linspace(x_end, x_ext, n_straight)
        z_a = np.full_like(x_a, z_end)

        # Semicircle in X-Z floor plane
        z_mid = (z_start + z_end) / 2
        radius = abs(z_start - z_end) / 2

        theta = np.linspace(0, np.pi, n_arc)

        # Flip this sign if the curve bends the wrong way
        bulge_sign = -1

        x_b = x_ext + bulge_sign * radius * np.sin(theta)
        z_b = z_mid + (z_end -  z_mid) * np.cos(theta)

        # Straight segment back to station/start
        x_c = np.linspace(x_ext, x_start, n_straight)
        z_c = np.full_like(x_c, z_start)

        Xc = np.concatenate([x_a, x_b, x_c])
        Zc = np.concatenate([z_a, z_b, z_c])

        # Simple connector vectors
        Fxc = np.diff(Xc, append=Xc[-1])
        Fyc = np.diff(Yc, append=Yc[-1])
        Fzc = np.diff(Zc, append=Zc[-1])

        Lxc = np.zeros_like(Xc)
        Lyc = np.zeros_like(Xc)
        Lzc = -np.ones_like(Xc)

        Nxc = np.zeros_like(Xc)
        Nyc = np.ones_like(Xc)
        Nzc = np.zeros_like(Xc)

        combined_track = (
            np.concatenate([X, Xc]),
            np.concatenate([Y, Yc]),
            np.concatenate([Z, Zc]),
            np.concatenate([Fx, Fxc]),
            np.concatenate([Fy, Fyc]),
            np.concatenate([Fz, Fzc]),
            np.concatenate([Lx, Lxc]),
            np.concatenate([Ly, Lyc]),
            np.concatenate([Lz, Lzc]),
            np.concatenate([Nx, Nxc]),
            np.concatenate([Ny, Nyc]),
            np.concatenate([Nz, Nzc]),
        )

        return combined_track



# ========================== Physics Calculations for Track Design (TODO) ==========================
class TrackPhysics:
    g = 9.8

    @staticmethod
    def calculate_velocity(v_exit, Y_array):
        # Check if the exit velocity from the previous track part is sufficient to navigate the next track part
        # This can be done by calculating the required velocity to navigate the next track part and comparing it to the exit velocity
        delta_y = Y_array - Y_array[0]
        v_squared = (v_exit ** 2) - (2 * TrackPhysics.g * delta_y)

        with np.errstate(invalid='ignore'):
            velocity_array = np.sqrt(v_squared)
        
        return velocity_array

    @staticmethod
    def calculate_R(xyz_component, forward_component):
        X, Y, Z = xyz_component
        Fx, Fy, Fz = forward_component

        # delta_S = np.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        position = np.column_stack((X,Y,Z))
        delta_position = np.diff(position, axis=0)
        delta_S = np.linalg.norm(delta_position, axis=1)

        # delta_theta = arccos((F1xF2x + F1yF2y + F1zF2z) / (|F1| * |F2|))
        forces = np.column_stack((Fx,Fy,Fz))
        
        F_current = forces[:-1]
        F_next = forces[1:]
        dot_product = np.sum(F_current * F_next, axis = 1)

        mag_current = np.linalg.norm(F_current, axis = 1)
        mag_next = np.linalg.norm(F_next, axis = 1)
        mag_product = mag_current * mag_next
        mag_product = np.where(mag_product == 0, 1e-12, mag_product)

        cos_theta = dot_product / mag_product
        cos_theta = np.clip(cos_theta, -1.0, 1.0)
        delta_theta = np.arccos(cos_theta)

        # radius = delta_S / delta_theta
        with np.errstate(divide='ignore', invalid='ignore'):
            radius = np.where(delta_theta == 0, np.inf, delta_S / delta_theta)
        # Add another last element of the radius array to the end so it matches length of velocities
        radius = np.append(radius, radius[-1])

        # print(f"{section} section's radius: {radius}")
        return radius
    
    @staticmethod
    def velocity_check(velocity_array):
        if np.isnan(velocity_array).any():
            first_fail_idx = np.where(np.isnan(velocity_array))[0][0]
            return False, first_fail_idx
        return True, None

    @staticmethod
    def valley_check(v_bot, r_1):
        # Check if the valley between two track parts is too deep for the given exit velocity
        # This can be done by calculating the potential energy at the lowest point of the valley and comparing it to the kinetic energy of the coaster at that point
        g_valley = TrackPhysics.g + (v_bot**2 / r_1)
        if g_valley >= (5 * TrackPhysics.g):
            return False, g_valley
        return True, g_valley

    @staticmethod
    def inversion_check(v_at_ymax, r_at_ymax):
        if r_at_ymax <= 1e-3:
            return False, 0.0

        v_min = np.sqrt(r_at_ymax * TrackPhysics.g)
        if v_at_ymax < v_min:
            return False, v_min
        return True, v_min

    @staticmethod
    def peak_check(v_at_max, r_at_ymax):
        if r_at_ymax <= 1e-3:
            return False, 0.0
        
        v_max = np.sqrt(r_at_ymax * TrackPhysics.g)
        if v_at_max > v_max:
            return False, v_max
        return True, v_max

    @staticmethod
    def lateral_check(v_top, r, theta_rad):
        # (v_top^2 / R) * cos(theta) - g * sin(theta) < 1.5g
        if r <= 1e-3:
            return False, 0.0
        
        lat_accel = ((v_top**2 / r) * np.cos(theta_rad)) - (TrackPhysics.g * np.sin(theta_rad))
        max_allowed = 1.5 * TrackPhysics.g
        
        if np.abs(lat_accel) > max_allowed:
            return False, lat_accel / TrackPhysics.g
        return True, lat_accel / TrackPhysics.g

    @staticmethod
    def rollup_check(v_bot, h):
        # h_climb = (v_bot^2 / 2g)
        h_climb = (v_bot**2) / (2 * TrackPhysics.g)
        # Need the h_climb to be larger 
        if h < h_climb:
            return False, h_climb
        return True, h_climb
    
    @staticmethod
    def brake_check(v_bot, L):
        # v_max = sqrt(2 * a * L), check if v_bot < v_max
        a_decel = 1.5
        v_max = np.sqrt(2 * a_decel * TrackPhysics.g * L)
        if v_bot > v_max:
            return False, v_max
        return True, v_max
    

if __name__ == "__main__":
    (X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name) = TrackPart.horseshoe_func(11.0)

    
    # print(f"X: {max(X)}")
    # print(f"Y: {max(Y)}")

    # X, Y, Z = X[::-1], Y, Z[::-1]
    # Fx, Fy, Fz = -Fx[::-1], -Fy[::-1], -Fz[::-1]
    # Lx, Ly, Lz = -Lx[::-1], -Ly[::-1], -Lz[::-1]
    # Nx, Ny, Nz = Nx[::-1], Ny, Nz[::-1]

    
    plt.figure()
    plt.plot(X, Y, 'b-', label='Track Path')
    plt.plot(X + Nx, Y + Ny, 'r-', alpha=0.4, label='Normals')
    plt.show()