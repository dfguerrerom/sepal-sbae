from timeit import default_timer as timer

import sepal_ui.sepalwidgets as sw

from component.message import cm
from component.widget.save_dialog import SaveDialog


class ResumeView(sw.Card):
    def __init__(self, model, save_dialog, *args, **kwargs):

        self.min_width = "550px"
        self.max_width = "550px"

        super().__init__(*args, **kwargs)

        self.model = model
        self.save_dialog = save_dialog

        self.w_title = sw.CardTitle(children=[cm.results.title])
        self.w_description = sw.CardText(children=[cm.results.description])
        self.btn = sw.Btn(cm.export.btn, disabled=True)

        self.size_placeh = sw.Html(tag="div")
        self.shape_placeh = sw.Html(tag="div")
        self.seed_placeh = sw.Html(tag="div")
        self.npoints_placeh = sw.Html(tag="div")

        info_dict = {
            "n_points": [cm.results.n_points, self.npoints_placeh],
            "grid_size": [cm.results.size, self.size_placeh],
            "shape": [cm.results.shape, self.shape_placeh],
            "seed": [cm.results.seed, self.seed_placeh],
        }

        content = [
            (
                sw.Flex(
                    class_="d-block",
                    children=[
                        sw.Html(tag="strong", children=[values[0]]),
                        values[1],
                    ],
                ),
                sw.Divider(vertical=True, class_="mx-4"),
            )
            for values in info_dict.values()
        ]
        # Flat the nested elements and remove the last divider
        info_content = [e for row in content for e in row][:-1]

        self.w_info = sw.Layout(class_="d-flex", children=info_content).hide()

        self.children = [
            self.w_title,
            self.w_description,
            sw.CardActions(children=[self.btn]),
        ]

        # bindings
        self.model.observe(self._activate_btn, "ready")

        # Events
        self.btn.on_event(
            "click", lambda *x: setattr(self.save_dialog, "v_model", True)
        )

    def _activate_btn(self, change):
        """Observe model ready member and activate button"""

        setattr(self.btn, "disabled", not change["new"])

    def update_content(self):
        """Request and set the sample info in the card content."""

        self.npoints_placeh.children = ["Calculating..."]
        self.w_description.children = [self.w_info.show()]
        self.w_title.children = [cm.design.method[self.model.method]]
        self.size_placeh.children = [f"{self.model.grid_size} m"]
        self.shape_placeh.children = [cm.design.shape[self.model.shape]]
        self.seed_placeh.children = [f"{self.model.seed}"]

        # Save this number into the module since this is something
        # time consuming.
        self.model.nsamples = self.model.points.size().getInfo()
        self.npoints_placeh.children = [str(self.model.nsamples)]
