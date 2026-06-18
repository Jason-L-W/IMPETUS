import tracks
import read_write_csv as CSV
import build
import numpy as np

def main():
    """
    Used to convert real track data from txt to csv format.
    Would later use this data to build track parts to certain scale.
    Uncomment the line below to convert txt files to csv format.
    """
    # Convert txt to csv
    # CSV.txt_to_csv("filename.txt")

    """
    Used to test track part functions and plot them in 3D.
    For now it is used to check if the track part functions are working correctly.
    Also to see if data matches output from MATLAB.
    """
    # Test code
    # Runs chosen track
    # combined_track = tracks.TrackPart.loopCG_func(11)  # Changable parameters for different tracks
    # X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = combined_track
    # print("CSV file generated:", file_name)
    

    # # Plots chosen track in a 3D plot
    # build.plot(combined_track)

    # Test combining multiple track parts
    # part1 = tracks.TrackPart.lifthill_func(11.0)
    # part2 = tracks.TrackPart.loopCG_func(11.0)
    # part3 = tracks.TrackPart.cobrarollCG_func(11.0)

    # combined, xy_composition = tracks.TrackPart.combine_tracks(part1, part2, part3)
    # build.plot(combined)

    print(np.tan(np.radians(60)))
    print(np.tan(np.deg2rad(60)))


    

if __name__ == "__main__":
    main()