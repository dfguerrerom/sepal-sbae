from ipyleaflet import WidgetControl
from sepal_ui import mapping as m
from sepal_ui import sepalwidgets as sw

import component.tile.panel_view as pv
import component.tile.resume_view as rv
import component.tile.sbae_results_view as sr
from component.message import cm
from component.widget.menu_control import MenuControl
from component.widget.save_dialog import SaveDialog

__all__ = ["Map"]


class Map(m.SepalMap):
    def __init__(self, model, aoi_model, *args, **kwargs):

        self.model = model
        self.aoi_model = aoi_model

        kwargs["gee"] = True
        kwargs["statebar"] = False

        super().__init__()

        self.add_control(
            m.FullScreenControl(
                self, position="topleft", fullscreen=False, fullapp=False
            )
        )

        self.save_dialog = SaveDialog(self.model)
        self.resume_view = rv.ResumeView(self.model, self.save_dialog)
        self.sbae_result_view = sr.SbaeResultsView()
        self.panel_view = pv.PanelView(
            self, self.model, self.aoi_model, self.resume_view, self.sbae_result_view
        )

        self.panel_control = MenuControl(
            "fas fa-wrench", self.panel_view, m=self, attributes={"id": "panel"}
        )
        self.sbae_result_control = MenuControl(
            "fas fa-chart-bar",
            self.sbae_result_view,
            m=self,
            attributes={"id": "sbae_results"},
        )

        self.add_widget_as_control(self.resume_view, "bottomright")
        self.add_widget_as_control(self.save_dialog, "bottomright")

        self.add_control(self.panel_control)
        self.add_control(self.sbae_result_control)
        self.panel_control.position = "topleft"
        self.sbae_result_control.position = "topright"

        self.panel_view.close.on_event("click", self.close_card)
        self.sbae_result_view.close.on_event("click", self.close_card)

        self.panel_view.pin.on_event("click", self.pin_card)
        self.sbae_result_view.pin.on_event("click", self.pin_card)

    def pin_card(self, widget, event, data):
        """un/pin card, It has to change the menu v_model from the control"""

        if widget.attributes["id"] == "sbae_results":
            menu = self.sbae_result_control.menu
        elif widget.attributes["id"] == "panel":
            menu = self.panel_control.menu

        pin_states = ["mdi-pin", "mdi-pin-off"]
        menu.close_on_click = not menu.close_on_click
        widget.children = pin_states[menu.close_on_click]

    def close_card(self, widget, event, data):
        """Close menu card. It has to change the menu v_model from the control"""

        if widget.attributes["id"] == "sbae_results":
            self.sbae_result_control.menu.v_model = False

        elif widget.attributes["id"] == "panel":
            self.panel_control.menu.v_model = False

    def add_widget_as_control(self, widget, position, first=False):
        """
        Add widget as control in the given position

        Args:
            widget (dom.widget): Widget to convert as map control
            position (str): 'topleft', 'topright', 'bottomright', 'bottomleft'
            first (Bool): Whether set the control as first or last element
        """

        new_control = WidgetControl(
            widget=widget, position=position, transparent_bg=True
        )

        if first == True:

            self.controls = tuple(
                [new_control] + [control for control in self.controls]
            )
        else:

            self.controls = self.controls + tuple([new_control])

    def set_code(self, link):
        "add the code link btn to the map"

        btn = m.MapBtn("fas fa-code", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.add_control(control)

    def set_wiki(self, link):
        "add the wiki link btn to the map"

        btn = m.MapBtn("fas fa-book-open", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.add_control(control)

    def set_issue(self, link):
        "add the code link btn to the map"

        btn = m.MapBtn("fas fa-bug", href=link, target="_blank")
        control = WidgetControl(widget=btn, position="bottomleft")
        self.add_control(control)
