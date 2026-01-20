import tracks
import read_write_csv as CSV
import build

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
    # results = tracks.TrackPart.corkscrew_func(19)  # Changable parameters for different tracks
    # X, Y, Z, Fx, Fy, Fz, Lx, Ly, Lz, Nx, Ny, Nz, file_name = results
    # print("CSV file generated:", file_name)
    

    # # Plots chosen track in a 3D plot
    # build.plot(results)

    # Test combining multiple track parts
    part1 = tracks.TrackPart.camelback_func(10)
    part2 = tracks.TrackPart.break_func(15)
    part3 = tracks.TrackPart.cobrarollCG_func(12)

    combined = tracks.TrackPart.combine_tracks(part1, part2, part3)
    build.plot(combined)


    

if __name__ == "__main__":
    main()