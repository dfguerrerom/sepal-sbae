import ee
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts.decorator import loading_button, switch
from traitlets import CInt, dlink, link

from component.message import cm
from component.scripts.gee_sbae import simulate_areas
from component.scripts.processing import get_sbae_error

ee.Initialize()


class SbaeView(sw.Card):
    """View of input components to perform an sample design. It will capture
    variables such as type of sample, shape and size of grid and will allow
    to perform"""

    def __init__(self, model, map_, sbae_result_view, *args, **kwargs):

        self.asset = None

        super().__init__(*args, **kwargs)

        self.class_ = "d-block pa-2"
        self.map_ = map_
        self.model = model
        self.sbae_result_view = sbae_result_view

        self.alert = sw.Alert(children=[cm.sbae.note])
        self.w_asset = sw.AssetSelect(
            default_asset="users/amitghosh/sdg_module/esa/cci_landcover",
            label=cm.sbae.asset,
            types=["IMAGE_COLLECTION", "IMAGE"],
        )

        self.w_properties = sw.Select(label=cm.sbae.properties, v_model=None).hide()
        self.w_value = sw.Select(label=cm.sbae.value, v_model=None).hide()

        self.btn = sw.Btn(cm.sbae.button)

        self.children = [
            self.w_asset,
            self.w_properties,
            self.w_value,
            self.alert,
            self.btn,
        ]

        self.w_asset.observe(self._process_asset, "v_model")
        self.w_properties.observe(self._fill_values, "v_model")
        self.w_value.observe(self.filter_fc, "v_model")
        self.btn.on_event("click", self._compute_sbae)
        self._process_asset({"new": "users/amitghosh/sdg_module/esa/cci_landcover"})

    def filter_fc(self, *args):
        """use user's input to filter feature collection and save asset member"""

        self.asset = ee.Image(
            self.fc.filter(
                ee.Filter.eq(self.w_properties.v_model, self.w_value.v_model)
            ).first()
        )

    @switch("loading", on_widgets=["w_value"])
    def _fill_values(self, change):
        """fill w_value items with all the aggregate array info from the selected property"""

        self.w_value.items = self.fc.aggregate_array(change["new"]).getInfo()

    def _process_asset(self, change):
        """process feature collection when is selected in asset widget"""

        if self.w_asset.asset_info["type"] == "IMAGE_COLLECTION":

            self.fc = ee.FeatureCollection(change["new"])
            properties = [
                prop
                for prop in self.fc.propertyNames().getInfo()
                if prop != "system:id"
            ] + ["system:index"]
            self.w_properties.items = properties
            self.w_properties.show()
            self.w_value.show()

        else:
            self.asset = ee.Image(change["new"])
            self.w_properties.hide()
            self.w_value.hide()

    @switch("loading", on_widgets=["sbae_result_view"])
    @loading_button(debug=True)
    def _compute_sbae(self, widget, event, data):
        """Event to trigger the computation of sbae based on user inputs"""

        self.sbae_result_view.loading_mode()

        simulated_areas, real_area = simulate_areas(self.model, self.asset)

        map_asset = self.asset.clip(self.model.aoi_model.feature_collection.geometry())
        self.map_.addLayer(map_asset.randomVisualizer(), {}, "Categorical image")

        diff_rate_df = get_sbae_error(simulated_areas, real_area)

        self.sbae_result_view.update_content(diff_rate_df)

        # Open this card when the process is complete
        self.map_.addLayer(self.model.aoi_model.feature_collection)
        self.map_.sbae_result_control.menu.v_model = True
