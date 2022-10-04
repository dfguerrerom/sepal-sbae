import concurrent.futures
from pathlib import Path

import ee
import geopandas as gpd
import pandas as pd
import sepal_ui.scripts.utils as su
from sepal_ui.model import Model
from sepal_ui.scripts.gee import get_assets
from traitlets import Bool, CInt, Int, Unicode

import component.parameter.directory as dir_
import component.scripts.gee_sampling as gee
from component.message import cm
from component.scripts import scripts

ee.Initialize()


class Model(Model):

    method = Unicode().tag(sync=True)
    "str: sampling method. either systematic or random"
    export_method = Unicode().tag(sync=True)
    "str: exportation method method. either local (.csv, .gpkg, .shp) or asset"
    shape = Unicode().tag(sync=True)
    "str: shape of the grid cell. the value will be used to create the grid."
    grid_size = CInt().tag(sync=True)
    "int: grid size of each cell. Value is displayed in meters"
    # out_crs = Unicode("EPSG:32737").tag(sync=True)
    out_crs = Unicode("EPSG:3857").tag(sync=True)
    "str(epsg, esri) crs: coordinate reference system from the output."
    n_points = CInt(1).tag(sync=True)
    "int: numbers of points to create within each cell. Only available when using random sampling method."
    seed = Int().tag(sync=True)
    "int: seed used to create random points"
    points = None
    "ee.FeatureCollection: sample points derived from the user inputs"
    nsamples = None
    "int: Total number of sampled points. It is the size of the points feature collection"
    samples_gdf = None
    "GeoDataFrame: geodataframe containing all the samples geometries with their own index"
    ready = Bool(False).tag(sync=True)
    "bool: trait to control either the samples are already created or not"
    gee_format = Unicode("").tag(sync=True)
    "str: file format when using export methods as asset"

    def __init__(self, aoi_model):

        self.aoi_model = aoi_model
        self.grid = None
        self.points = None
        self.nsamples = None

    def create_sample(self):
        """Create sampling desing within the grid based on the strategy"""

        self.ready = False

        # We are passing the model (self) and grid_size, because the functions will use
        # some default parameters from the model (self) and can vary the second parameter
        self.grid = gee.get_grid(self, self.grid_size)
        self.points = gee.create_sample(self, self.grid)

        self.ready = True

    def points_to_dataframe(self, alert):
        """Retrieve points from GEE concurrently and save the geodataframe in the model"""

        def get_features(offset):
            """converts fc into a batch_size list with a given offset"""
            return ee.FeatureCollection(
                self.points.toList(batch_size, offset)
            ).getInfo()

        workers = 4
        batch_size = min(int(self.nsamples / workers), 5000)

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Define an offset list to skip elements at each iteration
            offsets = [0] + [
                x * batch_size for x in range(1, (self.nsamples // batch_size) + 1)
            ]
            futures = [executor.submit(get_features, offset) for offset in offsets]
            results = []
            progress = 0
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                progress += 1 / len(offsets)
                alert.update_progress(progress)
            alert.update_progress(1)

        self.samples_gdf = gpd.GeoDataFrame(
            pd.concat([gpd.GeoDataFrame.from_features(result) for result in results])
        ).reset_index()

    def export_result(self, folder=None):
        """Export sample design points to the given format"""

        filename = scripts.get_filename(self, f".{self.export_method}")

        if self.export_method in ["asset", "gdrive"]:

            options = {
                "collection": self.points,
                "description": filename.stem,
            }

            if self.export_method == "gdrive":
                task_fn = ee.batch.Export.table.toDrive
                options.update(folder="sampling_test", fileFormat=self.gee_format)

            elif self.export_method == "asset":

                folder = folder or ee.data.getAssetRoots()[0]["id"]
                asset_id = str(Path(folder, filename.stem))
                print(asset_id)

                # check if the name already exist
                current_assets = [asset["name"] for asset in get_assets(folder)]

                # An user could export the same asset more than one time
                # Let's create an unique id
                while asset_id in current_assets:
                    asset_id = su.next_string(asset_id)

                task_fn = ee.batch.Export.table.toAsset
                options.update(assetId=asset_id)

            task = task_fn(**options)
            task.start()

            return cm.export.success_msg.local.format(filename.stem, task.id)

        else:

            drivers = {
                "gpkg": "GPKG",
                "shp": "ESRI Shapefile",
            }
            gdf = self.samples_gdf

            gdf["LON"] = gdf["geometry"].x
            gdf["LAT"] = gdf["geometry"].y

            # sort columns for CEO output
            gdf["PLOTID"] = gdf.index
            cols = gdf.columns.tolist()
            cols = [e for e in cols if e not in ("LON", "LAT", "PLOTID")]
            new_cols = ["PLOTID", "LAT", "LON"] + cols
            gdf = gdf[new_cols]

            if self.export_method == "csv":
                gdf[["PLOTID", "LAT", "LON"]].to_csv(filename, index=False)
            else:
                gdf.to_file(filename, driver=drivers[self.export_method])

            return cm.export.success_msg.local.format(filename.name)
