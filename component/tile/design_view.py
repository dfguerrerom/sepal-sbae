import time
from importlib import reload
from random import randint
from timeit import default_timer as timer

import ipyvuetify as v
import nest_asyncio
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts.decorator import loading_button
from traitlets import CInt, dlink, link

from component.message import cm


class DesignView(sw.Layout):
    """View of input components to perform an sample design. It will capture
    variables such as type of sample, shape and size of grid and will allow
    to perform"""

    methods = {
        "systematic": True,
        "random": True,
        "rand_syst": False,
        "strat_random": False,
    }

    shapes = {"square": True, "triangle": False, "hexagon": False}

    def __init__(self, model, map_, resume_view, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.class_ = "d-block pa-2"
        self.model = model
        self.map_ = map_
        self.resume_view = resume_view

        self.alert = sw.Alert()
        self.w_method = sw.Select(
            label=cm.design.method.label,
            items=[
                {"value": k, "text": cm.design.method[k], "disabled": not state}
                for k, state in self.methods.items()
            ],
            v_model=next(iter(self.methods)),
        )

        self.w_shape = sw.Select(
            label=cm.design.shape.label,
            items=[
                {"value": k, "text": cm.design.shape[k], "disabled": not state}
                for k, state in self.shapes.items()
            ],
            v_model=next(iter(self.shapes)),
        )

        self.w_size = sw.TextField(
            type="number",
            label=cm.design.size.label,
            class_="mr-2",
            v_model=5000,
            attributes={"id": "size"},
        )

        self.w_random = RandomInt().hide()
        self.w_npoints = sw.TextField(
            type="number",
            label=cm.design.npoints.label,
            class_="mr-2",
            v_model=1,
            attributes={"id": "npoints"},
        ).hide()

        self.btn = sw.Btn("Calculate grid")

        self.children = [
            self.w_method,
            self.w_shape,
            sw.Layout(
                class_="pa-0 ma-0",
                row=True,
                align="center",
                children=[
                    v.Flex(children=[self.w_size], xs6=True),
                    v.Layout(
                        class_="d-flex",
                        children=[
                            v.Flex(class_="mr-2", xs6=True, children=[self.w_random]),
                            v.Flex(xs6=True, children=[self.w_npoints]),
                        ],
                        xs6=True,
                    ),
                ],
            ),
            self.btn,
            self.alert,
        ]

        # Bindings
        dlink((self.w_random, "seed"), (self.model, "seed"))

        self.model.bind(self.w_npoints, "n_points")
        self.model.bind(self.w_method, "method")
        self.model.bind(self.w_shape, "shape")
        self.model.bind(self.w_size, "grid_size")

        # Events
        self.w_method.observe(self.display_seed, "v_model")
        self.btn.on_event("click", self.display_result)

        # Events
        self.w_size.on_event("blur", self.set_default)
        self.w_npoints.on_event("blur", self.set_default)

    def set_default(self, widget, event, data):
        """Set default value when there is nothing and blur event comes"""

        if widget.v_model == "":
            if widget.attributes["id"] == "size":
                widget.v_model = 5000
            elif widget.attributes["id"] == "npoints":
                widget.v_model = 1

    @loading_button(debug=True)
    def display_result(self, *args):
        """Event to display grid and sample points on the map"""

        self.map_.remove_layer("Sample", none_ok=True)
        self.map_.remove_layer("Grid", none_ok=True)

        # Set the calls to gee
        aoi = self.model.aoi_model.feature_collection
        self.model.create_sample()

        if not self.map_.find_layer("AOI", none_ok=True):
            self.map_.centerObject(aoi)
            self.map_.addLayer(aoi, {}, "AOI")

        self.map_.addLayer(self.model.grid, {"color": "gray", "width": 1}, "Grid")
        self.map_.addLayer(
            self.model.points,
            {"pointSize": 1, "color": "red", "fillColor": None},
            "Sample",
        )

        self.resume_view.update_content()

    def display_seed(self, change):
        """Display seed when method is purely random or random"""

        if change["new"] in ["random", "rand_syst", "strat_random"]:
            self.w_random.show()
            self.w_npoints.show()
        else:
            self.w_npoints.hide()
            self.w_random.hide()


class RandomInt(sw.Layout):

    seed = CInt(1).tag(sync=True)

    def __init__(self, *args, **kwargs):

        self.class_ = "flex-nowrap d-flex pa-0 ma-0 flex-nowrap"
        self.align_center = True
        self.row = True

        super().__init__(*args, **kwargs)

        btn = v.Btn(
            small=True, children=[sw.Icon(small=True, children=["fas fa-sync-alt"])]
        )
        self.w_number = sw.TextField(label="Seed", v_model=self.seed, type="number")

        self.children = [self.w_number, btn]

        self.w_number.observe(self.get_change, "v_model")
        self.w_number.on_event("blur", self.set_default)
        btn.on_event("click", self.get_random)

    def set_default(self, widget, event, data):
        """Set default value when there is nothing and blur event comes"""
        if widget.v_model == "":
            self.w_number.v_model = 1

    def get_change(self, change):
        """receives the change and set it to the v_model"""

        if change["new"] == "":
            return

        self.seed = int(change["new"])

    def get_random(self, *args):
        """Creates a random number and set it into the text field"""

        rand_int = randint(1, 9999)
        self.w_number.v_model = rand_int
