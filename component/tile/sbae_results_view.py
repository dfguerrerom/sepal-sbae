import plotly.graph_objects as go
import sepal_ui.sepalwidgets as sw

from component.message import cm


class SbaeResultsView(sw.Card):
    def __init__(self, *args, **kwargs):

        self.min_width = "550px"
        self.max_width = "650px"

        super().__init__(*args, **kwargs)

        self.close = sw.Icon(children=["mdi-close"], attributes={"id": "sbae_results"})
        self.pin = sw.Icon(children=["mdi-pin-off"], attributes={"id": "sbae_results"})

        title = sw.CardTitle(
            children=[cm.sbae.title, sw.Spacer(), self.pin, self.close]
        )
        self.w_description = sw.CardText(children=[cm.sbae.description])
        self.w_classes = sw.Select(label=cm.sbae.classes.label, v_model=None)

        self.fig = go.FigureWidget()
        self.fig.update_layout(
            template="plotly_dark",
            template_layout_paper_bgcolor="#1a1a1a",
            title_text="SBAE",
        )
        self.fig.add_trace(go.Scatter())

        self.w_desc_fig = sw.CardText(children=[self.w_classes, self.fig]).hide()

        self.children = [
            title,
            self.w_description,
            self.w_desc_fig,
        ]

    def loading_mode(self):
        """show loading cards and hide any previous graph displayed"""

        self.w_description.show()
        self.w_desc_fig.hide()

    def update_content(self, diff_rate_df):
        """Use the received dataframe to create and update the graphs"""

        self.w_classes.items = diff_rate_df.index.to_list()

        def update(change):

            class_ = change["new"]
            data = diff_rate_df.loc[class_]
            lines = go.Scatter(
                x=data.index,
                y=data.values,
            )
            self.fig.update_traces(lines)
            self.fig.update_layout(title_text=f"SBAE / class {class_}")

        self.w_classes.observe(update, "v_model")

        self.w_description.hide()
        self.w_desc_fig.show()
