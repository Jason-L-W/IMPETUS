from scipy.integrate import solve_ivp
import numpy as np
import read_write_csv as CSV
import build

# All Track Parts
# This class is used to store all track part functions
class TrackPart:
    # This is used to initialize the TrackPart class
    # Could be used to later connect different track parts together
    # For now, it just stores the output of each track part function
    def __init__(self, **kwargs):
        attr = ['X', 'Y', 'Z', 'Fx', 'Fy', 'Fz', 'Lx', 'Ly', 'Lz', 'Nx', 'Ny', 'Nz', 'file_name']
        for key in attr:
            setattr(self, key, kwargs.get(key, None))

    # ========================== Any track given data ==========================
    # Given data from a csv file, scale it and return the track part
    def from_data(data, scale, name):
        track_data = data.copy()

        # Scales the track based on your input scale
        track_data[:, 1:4] = track_data[:, 1:4] * scale / np.max(data[:, 2])

        X, Y, Z = track_data[:, 1], track_data[:, 2], track_data[:, 3]
        Fx, Fy, Fz = track_data[:, 4], track_data[:, 5], track_data[:, 6]
        Lx, Ly, Lz = track_data[:, 7], track_data[:, 8], track_data[:, 9]
        Nx, Ny, Nz = track_data[:, 10], track_data[:, 11], track_data[:, 12]

        pts = len(track_data)
        file_name = CSV.write_csv(track_data, pts, scale, name)
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name

    # ========================== Break track part (done) ==========================
    def break_func(L):
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
        
        file_name = CSV.write_csv(data, pts, L, "break")
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name
    
    # ========================== Camelback track part (done) ==========================
    def camelback_func(h):
        data = CSV.read_csv("cometcamelback.csv")
        camelback = data.copy()

        # Scales the track based on your input height
        camelback[:, 1:4] = camelback[:, 1:4] * h / np.max(data[:, 2])

        # Gets new values based on scaling
        X, Y, Z = camelback[:, 1] / 3, camelback[:, 2], camelback[:, 3]
        Fx, Fy, Fz = camelback[:, 4], camelback[:, 5], camelback[:, 6]
        Lx, Ly, Lz = camelback[:, 7], camelback[:, 8], camelback[:, 9]
        Nx, Ny, Nz = camelback[:, 10], camelback[:, 11], camelback[:, 12]

        pts = len(camelback)
        file_name = CSV.write_csv(camelback, pts, h, "camelback")
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name
    
    # ========================== Cobra Roll track part (should be done) ==========================
    def cobrarollCG_func(h):
        data = CSV.read_csv("flashbackcobraroll.csv")
        cobraroll = data.copy()
        # Scales the track based on your input height
        cobraroll[:, 1:4] = cobraroll[:, 1:4] * h / np.max(data[:, 2])
        
        X, Y, Z = cobraroll[:, 1] / 3, cobraroll[:, 2], cobraroll[:, 3]
        Fx, Fy, Fz = cobraroll[:, 4], cobraroll[:, 5], cobraroll[:, 6]
        Lx, Ly, Lz = cobraroll[:, 7], cobraroll[:, 8], cobraroll[:, 9]
        Nx, Ny, Nz = cobraroll[:, 10], cobraroll[:, 11], cobraroll[:, 12]

        pts = len(cobraroll)
        file_name = CSV.write_csv(cobraroll, pts, h, "cobarollCG")
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name

    # ========================== Corkscrew track part (done) ==========================
    def corkscrew_func(h):
        H = h * 4 # Total height of corkscrew
        r1 = H/2 # Radius of corkscrew
        B = 1/(2*r1)
        l2 = (3*np.pi*(H-h)**0.5)/2
        l1 = (-3*h*np.pi/(2*l2)+((3*h*np.pi/(2*l2))**2+6*B*h)**0.5)/(2*B)
        A = h/(2*l1**3)-B/l1

        # Section 1 (Track before the loop)
        X1 = np.linspace(0, l1, 50)
        Y1 = (A * X1**3) + (B * X1**2)
        Z1 = np.zeros_like(X1)
        Phi1 = np.linspace(0, -90, len(X1))

        # Section 2 (Track for the loop of corkscrew)
        l2 = (3 * np.pi / 2) * (H - h)**0.5
        t = np.arange(0, 3*np.pi, 0.01)
        X2 = l2 * t / (3*np.pi) + X1[-1]
        Y2 = (h/2) * (1+np.sin(t)) # Responsible for the loop angle
        Z2 = (h/2) * (1-np.cos(t)) + Z1[-1] # Offset to the side, so that the track doesn't turn into itself
        Phi2 = -90 - (540/(3*np.pi))*t

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

        
        dX = np.concatenate(([X[0]], X[1:] - X[:-1]))[:, np.newaxis]
        dY = np.concatenate(([Y[0]], Y[1:] - Y[:-1]))[:, np.newaxis]
        dZ = np.concatenate(([Z[0]], Z[1:] - Z[:-1]))[:, np.newaxis]
        dS = np.sqrt(dX**2 + dY**2 + dZ**2)
        dXZ = np.sqrt(dX**2 + dZ**2)

        N = np.zeros((3, len(X)))
        N[1, :] = np.cos(np.deg2rad(Phi))
        N[2, :] = -np.sin(np.deg2rad(Phi))

        Ry = np.zeros((3, 3, len(X)))
        Rz = np.zeros((3, 3, len(X)))

        # Build rotation matrices
        eps = 1e-8 # Used to prevent division by zero

        for i in range(len(X)):
            Ry[0, :, i] = [dX[i,0] / (dXZ[i,0]), 0, -dZ[i,0] / (dXZ[i,0])]
            Ry[1, :, i] = [0, 1, 0]
            Ry[2, :, i] = [dZ[i,0] / (dXZ[i,0]), 0, dX[i,0] / (dXZ[i,0])]

            Rz[0, :, i] = [dXZ[i,0] / (dS[i,0]), -dY[i,0] / (dS[i,0]), 0]
            Rz[1, :, i] = [dY[i,0] / (dS[i,0]),  dXZ[i,0] / (dS[i,0]), 0]
            Rz[2, :, i] = [0, 0, 1]

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
        file_name = CSV.write_csv(data, pts, r1, "corkscrew")

        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name

    # TODO
    def helix_func(h):
        R = 2 * h

        # All X components to the track
        X1 = np.arange(0, 3*R+1, 1) # Array of 1 from index 0 to 3*R
        X2 = np.arange(3*R + 1, 4*R + 1, 1)
        X3 = np.arange(4*R - 1, 2*R - 1, -1)
        X4 = np.arange(2*R + 1, 4*R + 1, 1)
        X5 = np.arange(4*R - 1, 3*R - 1, -1)
        X6 = np.arange(3*R - 1, -1, -1)

        # All Y components to the track
        Y1 = (h/2) * (1 - np.cos((np.pi*X1) / (3*R)))
        Y2345 = max(Y1) - (h/2) * (1 - np.cos(np.pi * (np.arange(1, 6*R+1, 1)) / (6*R)))
        Y6 = np.arange(1, len(X6), 0)

        # All Z components to the track
        Z1 = np.ones(len(X1))
        Z2 = -R + np.sqrt(R**2 - (X2 - 3*R)**2)
        Z3 = -R - np.sqrt(R**2 - (X3 - 3*R)**2)
        Z4 = -R + np.sqrt(R**2 - (X4 - 3*R)**2)
        Z5 = -R - np.sqrt(R**2 - (X5 - 3*R)**2)
        Z6 = np.arange(1, len(X6), -2*R)

        # All Phi components to the track (angle)
        Phi1 = (45/2) * (1 - np.cos((np.pi*X1) / (3*R)))
        Phi2345 = 54.2 + 9.2*(-np.cos(np.pi * np.arange(1, 6*R-1, 1) / (6*R)))
        Phi6 = 63.4 + (63.4/2) * (-1 + np.cos(np.pi*X1/(3*R)))

        # Combining compnents
        X = np.concatenate([X1, X2, X3, X4, X5, X6])
        Y = np.concatenate([Y1, Y2345, Y6])
        Z = np.concatenate([Z1, Z2, Z3, Z4, Z5, Z6])
        Phi = np.concatenate([Phi1, Phi2345, Phi6])


        return None

    # TODO
    def horseshoe_func(h):
        return None

    # ========================== Lifthill track part (done) ==========================
    def lifthill_func(h):
        # h is the max height
        data = CSV.read_csv("cometlifthill.csv")
        lifthill = data.copy()

        # Scales the track based on your input height
        lifthill[:, 1:4] = lifthill[:, 1:4] * h / np.max(data[:, 2])

        X, Y, Z = lifthill[:, 1], lifthill[:, 2], lifthill[:, 3]
        Fx, Fy, Fz = lifthill[:, 4], lifthill[:, 5], lifthill[:, 6]
        Lx, Ly, Lz = lifthill[:, 7], lifthill[:, 8], lifthill[:, 9]
        Nx, Ny, Nz = lifthill[:, 10], lifthill[:, 11], lifthill[:, 12]

        pts = len(lifthill)
        file_name = CSV.write_csv(lifthill, pts, h, "lifthill")
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name

    # ========================== Loop with constant G-force (possibly need to fix) ==========================
    # Need to make it so that when the loop ends, it ends at the same height it started --> Y=0
    def loopCG_func(r, ngs):
        g = 9.8
        H = ((ngs - 1) * r) / 2
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

        Lx = Y*Fz - Z*Fy
        Ly = Z*Fx - X*Fz
        Lz = X*Fy - Y*Fx

        pts = len(X)
        data = np.zeros((pts, 13))

        data = np.column_stack((np.arange(1, len(X) + 1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = CSV.write_csv(data, pts, r, "loopCG")
        
        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name
    
    # TODO
    # 2 Loops
    def loopwith2Rs(r1, r2):
        return None

    # TODO
    def rollback_func(h):
        R = (2/3) * h

        return None

    # TODO
    def rollup_func(h):
        return None

    # ========================== Combine multiple track parts into one (done) ==========================
    # Combines multiple track parts into one
    def combine_tracks(*parts):
        if not parts:
            return None

        # Flatten the first part
        X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, _ = parts[0]

        for part in parts[1:]:
            X2, Y2, Z2, Fx2, Fy2, Fz2, Lx2, Ly2, Lz2, Nx2, Ny2, Nz2, _ = part

            # Offset the new part to connect smoothly
            X2 += X[-1] - X2[0]
            Y2 += Y[-1] - Y2[0]
            Z2 += Z[-1] - Z2[0]

            # Concatenate safely
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


        pts = len(X)
        data = np.column_stack((np.arange(1, pts+1), X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz))
        file_name = CSV.write_csv(data, pts, "combined_track")

        return X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name



