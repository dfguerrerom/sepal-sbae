import sepal_ui.sepalwidgets as sw
from traitlets import Int, link


class Tabs(sw.Card):

    current = Int(0).tag(sync=True)

    def __init__(self, titles, content, **kwargs):

        self.background_color = "primary"
        self.elevation = False

        self.tabs = [
            sw.Tabs(
                v_model=self.current,
                children=[
                    sw.Tab(children=[title], key=key)
                    for key, title in enumerate(titles)
                ],
            )
        ]

        self.content = [
            sw.TabsItems(
                v_model=self.current,
                children=[
                    sw.TabItem(children=[content], key=key)
                    for key, content in enumerate(content)
                ],
            )
        ]

        self.children = self.tabs + self.content

        link((self.tabs[0], "v_model"), (self.content[0], "v_model"))

        super().__init__(**kwargs)
