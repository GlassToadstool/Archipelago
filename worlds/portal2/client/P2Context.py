tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import TrackerGameContext as CommonContext, TrackerCommandProcessor as ClientCommandProcessor
    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext, ClientCommandProcessor
from kvui import GameManager, ScrollBox
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivy.metrics import dp

class P2ClientCommandProcessor(ClientCommandProcessor):

    def __init__(self, context: "P2CommonContext"):
        super().__init__(context)


class MenuLayout(MDGridLayout):

    def __init__(self):
        super().__init__(rows=1, cols=2)
        self.build()

    def set_map_data(self, map_data: dict):
        """
        - Set the map data
        - Update the menu
        """

    def build(self):
        """
        - List of chapter buttons on the left side
        - Add a dynamic list of map buttons on the right side of the grid that updates based on the selected chapter
        """

        self.clear_widgets()
        self.chapter_area = MDGridLayout(rows=8, cols=1)
        self.map_area = ScrollBox()
        self.map_area.layout.orientation = "vertical"
        self.map_area.layout.spacing = dp(3)
        self.map_area.scroll_type = ["bars"]
        self.map_area.do_scroll_x = False
        self.add_widget(self.chapter_area)
        self.add_widget(self.map_area)

        for chapter in range(1, 9):
            chapter_button = MDButton(
                MDButtonText(text=f"Chapter {chapter}"),
                on_release=lambda btn, chapter=chapter: self.select_chapter(f"Chapter {chapter}"),
            )
            self.chapter_area.add_widget(chapter_button)

    def select_chapter(self, chapter_name: str):
        """
        - Remove the old map buttons
        - Add the list of new map buttons
        """

        for child in self.map_area.layout.children[:]:
            self.map_area.layout.remove_widget(child)

        # Test code
        for map_name in range(1, 21):
            map_button = MDButton(
                MDButtonText(text=f"{chapter_name} - Map {map_name}"),
                on_release=lambda btn, map_name=map_name: self.select_map(f"{chapter_name} - Map {map_name}"),
            )
            self.map_area.layout.add_widget(map_button)

    def select_map(self, map_name: str):
        """
        - Handle the selection of a map button
        - Send map command to the game to load the selected map
        """


class P2GameManager(GameManager):
    def build(self):
        container = super().build()

        game_menu = self.add_client_tab("Maps", MenuLayout())
        self.log_panels["Maps"] = game_menu.content

        return container


class P2CommonContext(CommonContext):

    def make_gui(self) -> "type[kvui.GameManager]":
        """
        To return the Kivy `App` class needed for `run_gui` so it can be overridden before being built

        Common changes are changing `base_title` to update the window title of the client and
        updating `logging_pairs` to automatically make new tabs that can be filled with their respective logger.

        ex. `logging_pairs.append(("Foo", "Bar"))`
        will add a "Bar" tab which follows the logger returned from `logging.getLogger("Foo")`
        """

        class TextManager(P2GameManager):
            base_title = "Portal 2 Text Client"

        return TextManager