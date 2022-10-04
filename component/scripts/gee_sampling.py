import ee

from component.message import cm

ee.Initialize()


def get_grid(model, grid_size):
    """Creates an squared grid in GEE. It can be as feature or as image (True).

    Args:
        model (sbae.Model): the model will be used to get the default arguments that are
        used to create the sample points such as: grid shape and out_crs.

    """

    aoi = model.aoi_model.feature_collection
    if not aoi:
        raise Exception(cm.error.no_aoi)

    if model.shape == "square":
        geometry = ee.FeatureCollection(aoi).geometry().transform(model.out_crs, 100)
        return ee.FeatureCollection(geometry.coveringGrid(model.out_crs, grid_size))


def create_sample(model, grid):
    """Create sampling desing within the grid based on the strategy.
    This function can be called from the model (and then using the input grid_size parameter
    from the user) or called from the sbae calculation in which the grid_size will vary
    to get the sampling error.

    Args:
        model (sbae.Model): the model will be used to get the default arguments that are
        used to create the sample points such as: out_crs, seed, n_points and model.
    """

    if model.method == "random":

        def random_point(element):
            """returns a random point within each grid cell with own seed"""
            feature = ee.Feature(ee.List(element).get(0))
            ft_seed = ee.Number(ee.List(element).get(1))

            return ee.FeatureCollection.randomPoints(
                feature.geometry().transform(model.out_crs, 1),
                model.n_points,
                ft_seed.multiply(model.seed),
            )

        sequence = ee.List.sequence(1, grid.size())
        grid_list = grid.toList(grid.size())
        numbered_grid = grid_list.zip(sequence)

        return ee.FeatureCollection(numbered_grid.map(random_point)).flatten()

    elif model.method == "systematic":
        return grid.map(lambda ft: ft.centroid(1).transform(model.out_crs))
