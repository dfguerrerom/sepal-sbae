import concurrent.futures

import ee

from component.message import cm
from component.scripts import gee_sampling

ee.Initialize()


def unnest(group):
    # receives a list of dictionaries and unnest them
    d_group = ee.Dictionary(group)
    return ee.List([[ee.String(d_group.get("group"))], [d_group.get("sum")]]).flatten()


def get_total_area(ee_geometry):
    """Returns real area by reducing the AOI geometry"""

    # Total area (by reducing geometry)
    total_area = (
        ee.Image.pixelArea()
        .divide(1e4)
        .reduceRegion(
            **{
                "reducer": ee.Reducer.sum(),
                "geometry": geometry.geometry(),
                "scale": 300,
                "maxPixels": 1e14,
            }
        )
        .get("area")
    )


def get_area_by_category(model, cat_image):
    """returns real area by category"""

    # Get area by category
    real_cat_area = ee.List(
        ee.Image.pixelArea()
        .divide(1e4)
        .addBands(cat_image)
        .reduceRegion(
            **{
                "reducer": ee.Reducer.sum().group(1),
                "geometry": model.aoi_model.feature_collection.geometry(),
                "scale": 300,
                "maxPixels": 1e14,
            }
        )
        .get("groups")
    )
    real_cat_area = real_cat_area.map(unnest).unzip()
    return ee.Dictionary.fromLists(
        ee.List(real_cat_area.get(0)).map(lambda x: ee.String.encodeJSON(x)),
        real_cat_area.get(1),
    ).getInfo()


def get_simulated_area(model, cat_image, grid_size):
    """

    Returns simulated area by category using the given grid size

    Args:
        model (sbae.model): sbae model to get the default values (user inputs) and pass
            to the sampling creation
        cat_image (ee.Image): categorical image to perform simulated based area
            estimation.
        grid_size (int): grid size to create the sampling design

    """
    print(f"Processing with {grid_size}")

    proj = ee.Projection("EPSG:3857").atScale(grid_size)
    grid = gee_sampling.get_grid(model, grid_size)
    pixel_size = cat_image.projection().nominalScale()

    sample_img = gee_sampling.create_sample(model, grid)
    sample_img = (
        sample_img.reduceToImage(["system:index"], ee.Reducer.count())
        .selfMask()
        .reproject(proj.atScale(pixel_size))
    )

    res = (
        ee.Image.pixelArea()
        .divide(1e4)
        .addBands(cat_image)
        .addBands(sample_img)
        .updateMask(sample_img.mask())
        .reduceRegion(
            **{
                "reducer": ee.Reducer.sum().group(1).group(2),
                "geometry": model.aoi_model.feature_collection.geometry(),
                "scale": pixel_size,
                "maxPixels": 1e14,
            }
        )
        .get("groups")
    )
    res = ee.Dictionary(ee.List(res).get(0)).get("groups")
    res = ee.List(ee.List(res).map(unnest)).unzip()
    # Get the simulated area by category using the input grid size.
    sample_cat_area = ee.Dictionary.fromLists(
        ee.List(res.get(0)).map(lambda x: ee.String.encodeJSON(x)), res.get(1)
    ).getInfo()

    return sample_cat_area


def simulate_areas(model, cat_image):

    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:

        grid_sizes = [model.grid_size * mult for mult in [1, 2, 3, 4, 5, 10, 20, 50]]

        futures = {
            executor.submit(get_simulated_area, model, cat_image, grid_size): grid_size
            for grid_size in grid_sizes
        }

        real_area = {
            executor.submit(get_area_by_category, model, cat_image): "real_area"
        }

        futures.update(real_area)

        simulated_areas = {}
        # As we don't know which task was completed first, we have to save them in a
        # key(grid_size) : value (future.result()) format
        for future in concurrent.futures.as_completed(futures):

            future_name = futures[future]

            if future_name != "real_area":
                simulated_areas[future_name] = future.result()
            else:
                real_area = future.result()

        return (simulated_areas, real_area)
