from pathlib import Path

import component.parameter.directory as dir_


def get_filename(model, ext):
    """creates an output folder and returns a file name"""

    seed = (
        f"_seed{model.seed}"
        if model.method in ["random", "rand_syst", "strat_random"]
        else None
    )

    folder_name = f"{model.aoi_model.name}"
    filename = (
        f"{model.aoi_model.name}_{model.method}_{model.shape}_grid{model.grid_size}m_"
        f"crs{model.out_crs}"
    ).replace(":", "")
    filename = filename + seed if seed else filename

    result_folder = dir_.SAMPLES_DIR / folder_name
    result_folder.mkdir(parents=True, exist_ok=True)

    return (result_folder / filename).with_suffix(ext)
