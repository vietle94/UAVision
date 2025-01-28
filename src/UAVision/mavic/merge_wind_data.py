import pandas as pd
import glob
import os
import argparse


def merge_wind_data(dir_in, dir_out):
    dir_in = dir_in.replace("\\", "/") + "/"
    dir_out = dir_out.replace("\\", "/") + "/"
    file_path_wind = [x for x in glob.glob(dir_in + "/*.csv")]
    df = pd.DataFrame({})    
    for file in file_path_wind:
        file_name = os.path.basename(file)
        start_time = pd.to_datetime(file_name[-23:-4], format='%Y-%m-%d_%H-%M-%S')
        df_ = pd.read_csv(file)
        df_['datetime'] = start_time + pd.to_timedelta(df_['Flight time'])
        df = pd.concat([df, df_], ignore_index=True)
    df.to_csv(dir_out + "wind_merged.csv", index=False)
    print(f"{len(file_path_wind)} files merged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description for arguments")
    parser.add_argument("dir_in", help="Input directory", type=str)
    parser.add_argument("dir_out", help="Output directory", type=str)
    argument = parser.parse_args()

    merge_wind_data(argument.dir_in, argument.dir_out)

    print("Finished merging files")
