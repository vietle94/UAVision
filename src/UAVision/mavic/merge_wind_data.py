import pandas as pd
import glob
import os
import argparse


def merge_wind_data(dir_in, dir_out):
    dir_in = dir_in.replace("\\", "/") + "/"
    dir_out = dir_out.replace("\\", "/") + "/"
    file_path_wind = [x for x in glob.glob(dir_in + "/*.csv")]
    file_names_wind = [os.path.basename(x) for x in file_path_wind]
    appended_df_wind = []
    for x, x_name in zip(file_path_wind, file_names_wind):
        df_temp = pd.read_csv(x)
        date_ = x_name.split("_")[1]
        time_ = x_name.split("_")[2].split(".")[0].replace("-", ":")
        date_time_ = pd.to_datetime(date_ + " " + time_)
        df_temp["datetime"] = date_time_ + pd.to_timedelta(df_temp["Flight time"])
        appended_df_wind.append(df_temp)

    data_merged = pd.concat(appended_df_wind, ignore_index=True)
    data_merged.to_csv(dir_out + "wind_merged.csv", index=False)
    print(f"{len(file_path_wind)} folders merged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Description for arguments")
    parser.add_argument("dir_in", help="Input directory", type=str)
    parser.add_argument("dir_out", help="Output directory", type=str)
    argument = parser.parse_args()

    merge_wind_data(argument.dir_in, argument.dir_out)

    print("Finished merging files")
