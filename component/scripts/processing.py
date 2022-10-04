import pandas as pd


def get_sbae_error(sim_class_areas, real_class_areas):
    """Calculates the area error from each class"""

    grid_sizes = sim_class_areas.keys()

    # convert gee real area result into pd.df and sort it by its grid_sizes
    real_df = pd.DataFrame.from_dict(real_class_areas, orient="index").sort_index()
    # repeat the column (just to subtract it later easier)
    real_df = pd.concat([real_df] * len(grid_sizes), axis=1)
    real_df.columns = grid_sizes

    # convert gee sbae result into pd.df and sort it by its grid_size
    sim_df = pd.DataFrame.from_dict(sim_class_areas)[sorted(grid_sizes)]

    # get the proportion of each class over the total simulated area.
    sim_df_rate = sim_df / sim_df.sum()

    total_real_area = real_df.sum().iloc[0]

    # get the "simulated" area, multiplying the proportion by total_real_area
    sim_df_mult_real_area = sim_df_rate * (real_df.sum().iloc[0])

    # get the absolute difference between the simulated and the real area
    abs_diff_df = abs(real_df.subtract(sim_df_mult_real_area, axis=1, fill_value=0))

    diff_rate_df = (abs_diff_df / real_df) * 100

    return diff_rate_df
