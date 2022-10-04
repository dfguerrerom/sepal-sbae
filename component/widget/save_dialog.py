import ipyvuetify as v
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts.decorator import loading_button
from traitlets import Int, observe

from component.message import cm
from component.scripts import scripts


class SaveDialog(v.Dialog):
    """Dialog cart save samples result in a file with"""

    reload = Int().tag(sync=True)

    methods = {"csv": True, "gpkg": True, "shp": True, "asset": True, "gdrive": True}
    ee_formats = ["SHP", "GeoJSON", "KML", "KMZ", "CSV", "TFRecord"]

    def __init__(self, model, *args, **kwargs):

        self.persistent = True
        self.v_model = False
        self.max_width = "90vh"

        super().__init__(*args, **kwargs)

        self.model = model

        self.close = v.Icon(children=["mdi-close"])

        self.w_export_method = sw.Select(
            label=cm.export.method.label,
            items=[
                {"value": k, "text": cm.export.method[k], "disabled": not state}
                for k, state in self.methods.items()
            ],
            v_model=next(iter(self.methods)),
        )

        self.w_file_format = sw.Select(
            class_="ml-2",
            label=cm.export.fileformat.label,
            items=[{"value": format_, "text": format_} for format_ in self.ee_formats],
            v_model=next(iter(self.ee_formats)),
            style_="max-width:128px; min-width:128px;",
        ).hide()

        self.w_file_name = v.TextField(
            label=cm.export.output.label, type="string", v_model=""
        )

        w_filename = sw.Flex(
            class_="d-flex", children=[self.w_file_name, self.w_file_format]
        )

        # Action buttons
        self.btn = sw.Btn(cm.export.save)
        self.cancel = v.Btn(children=[cm.export.cancel])

        self.alert = sw.Alert().hide()

        self.children = [
            v.Card(
                class_="pa-4",
                children=[
                    v.CardTitle(children=[cm.export.title, v.Spacer(), self.close]),
                    v.CardText(children=[self.w_export_method, w_filename, self.alert]),
                    v.CardActions(children=[self.btn, self.cancel]),
                ],
            )
        ]

        self.model.bind(self.w_export_method, "export_method")
        self.model.bind(self.w_file_format, "gee_format")

        # Create events

        self.close.on_event("click", lambda *x: setattr(self, "v_model", False))
        self.cancel.on_event("click", lambda *x: setattr(self, "v_model", False))
        self.btn.on_event("click", self._save)

        self.w_export_method.observe(self._reset, "v_model")
        self.observe(self._set_filename, "v_model")

    def _reset(self, change):
        """restore resume view widgets to its default value"""

        self.alert.reset()

        if change["new"] == "gdrive":
            self.w_file_format.show()
        else:
            self.w_file_format.hide()

    def _set_filename(self, *args):
        """sets filename within the widget filename. It will called once"""

        self.w_file_name.v_model = str(scripts.get_filename(self.model, ".csv").stem)

    @loading_button(debug=True)
    def _save(self, *args):
        """trigger exportation method from model"""

        # We only need to transform to dataframe if not in gee options
        if self.model.export_method not in ["asset", "gdrive"]:
            self.model.points_to_dataframe(self.alert)

        result = self.model.export_result()

        self.alert.append_msg(result, type_="success")
