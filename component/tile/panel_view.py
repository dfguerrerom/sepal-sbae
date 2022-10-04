import ipyvuetify as v
import sepal_ui.aoi.aoi_view as aoi
import sepal_ui.sepalwidgets as sw

import component.tile.design_view as dv
import component.tile.sbae_view as sv
from component.message import cm
from component.widget import Tabs

__all__ = ["PanelView"]


class PanelView(v.Card, sw.SepalWidget):

    """Panel to incorporate each of the tabs that would be used for the end-
    user to validate their Planet API-key, select and area of interest and
    use whether a fixed short periods or the historical data.

    """

    def __init__(
        self, map_, model, aoi_model, resume_view, sbae_result_view, *args, **kwargs
    ):

        self.max_height = "500px"
        self.min_height = "370px"
        self.min_width = "462px"
        self.max_width = "462px"
        # self.class_ = "pa-2"

        super().__init__(*args, **kwargs)

        self.model = model
        self.map_ = map_

        # This button button action is called from the map_, to hide the control.
        self.close = v.Icon(children=["mdi-close"], attributes={"id": "panel"})
        self.pin = sw.Icon(children=["mdi-pin-off"], attributes={"id": "panel"})

        title = v.CardTitle(children=[cm.panel.name, v.Spacer(), self.pin, self.close])

        tabs_title = [cm.panel.tabs.aoi, cm.panel.tabs.design, cm.panel.tabs.sbae]

        self.aoi_view = aoi.AoiView(model=aoi_model, map_=self.map_)
        self.aoi_view.class_ = "pa-2 pt-5"
        self.aoi_view.elevation = False

        self.design_view = dv.DesignView(self.model, self.map_, resume_view)
        self.sbae_view = sv.SbaeView(self.model, self.map_, sbae_result_view)

        widgets = [self.aoi_view, self.design_view, self.sbae_view]

        tabs = Tabs(tabs_title, widgets)

        self.children = [title, tabs]
