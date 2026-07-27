tracker_loaded = False
try:
    from worlds.tracker.TrackerClient import (
        TrackerGameContext as CommonContext,
        TrackerCommandProcessor as ClientCommandProcessor,
    )

    tracker_loaded = True
except ModuleNotFoundError:
    from CommonClient import CommonContext, ClientCommandProcessor
import asyncio
import logging

from Utils import async_start
from kvui import GameManager, ScrollBox
from kivy.metrics import dp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel

from .. import Portal2World

HOST = "localhost"
PORT = int(Portal2World.settings.default_portal2_port)

logger = logging.getLogger("Portal2Client")

async def send_instant_command(command: str):
        try:
            _, writer = await asyncio.open_connection(HOST, PORT)
            writer.write((command + "\n").encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except:
            logger.error(f"Connection to portal 2 failed for instant command")


class P2ClientCommandProcessor(ClientCommandProcessor):

    def __init__(self, context: "P2CommonContext"):
        super().__init__(context)

class MapInfo(MDGridLayout):

    def __init__(self, map_data: dict):
        super().__init__(rows=2, cols=1, padding=[0, 50])
        self.map_data = map_data
        self.build()

    def build(self):
        chapter_info_string = f"{self.map_data["title"]}\n\nRequired Items:\n"
        
        if self.map_data["required_items"]:
            chapter_info_string += ', '.join(self.map_data["required_items"])
        else:
            chapter_info_string += "All required items acquired"
            
        chapter_info_string +=  "\n\n"
        
        if self.map_data["sub_locations"]:
            chapter_info_string += "Sublocations:\n"
            sub_locations_incomplete = [name for name, complete in self.map_data["sub_locations"].items() if not complete]
            if sub_locations_incomplete:
                chapter_info_string += ', '.join(sub_locations_incomplete)
            else:
                chapter_info_string += "All sublocations completed"
        
        self.chapter_info = MDLabel(text=chapter_info_string)

        if self.map_data["disabled"]:
            self.play_map_button = MDButton(
                    MDButtonText(text="Map not yet available"),
                    disabled=True
                )
        else:
            self.play_map_button = MDButton(
                    MDButtonText(text="Play Map"),
                    on_release=lambda btn: self.select_map()
                )
                    
        
        # Add all these to the layout
        self.add_widget(self.chapter_info)
        self.add_widget(self.play_map_button)
        
        
    def select_map(self):
        """
        Send map command to the game to load the selected map
        """
        
        async_start(send_instant_command(f"{self.map_data['command']}"), "send_map_command")


class MenuLayout(MDGridLayout):

    def __init__(self):
        super().__init__(rows=1, cols=3)
        self.menu_info = []
        self.current_chapter = None
        self.map_area = None
        self.map_info = None

    def update_menu(self, menu_data: dict[str, dict]):
        """
        - Set the map data
        - Update the menu
        """
        self.menu_info = menu_data
        
        selected_chapter = self.current_chapter or list(self.menu_info.keys())[0]
        if self.map_area is not None:
            self.select_chapter(selected_chapter)

    def build(self):
        """
        - List of chapter buttons on the left side
        - Add a dynamic list of map buttons on the right side of the grid that updates based on the selected chapter
        """
        
        if self.menu_info is None:
            raise Exception("Menu data not set. Call update_menu() once before build().")

        self.clear_widgets()
        self.chapter_area = MDGridLayout(rows=9, cols=1)
        self.map_area = ScrollBox()
        self.map_area.layout.orientation = "vertical"
        self.map_area.layout.spacing = dp(3)
        self.map_area.scroll_type = ["bars"]
        self.map_area.do_scroll_x = False
        self.add_widget(self.chapter_area)
        self.add_widget(self.map_area)

        for chapter_name in self.menu_info.keys():
            chapter_button = MDButton(
                MDButtonText(text=chapter_name),
                on_release=lambda btn, chapter=chapter_name: self.select_chapter(
                    chapter
                ),
            )
            self.chapter_area.add_widget(chapter_button)

    def select_chapter(self, chapter_name: str):
        """
        - Remove the old map buttons
        - Add the list of new map buttons
        """
        
        if self.map_area is None:
            raise Exception("Map area not initialized. Call build() before select_chapter().")
        
        self.current_chapter = chapter_name

        for child in self.map_area.layout.children[:]:
            self.map_area.layout.remove_widget(child)
            
        if not self.menu_info:
            no_maps_label = MDButton(
                MDButtonText(text="No maps available for this chapter"),
                disabled=True,
            )
            self.map_area.layout.add_widget(no_maps_label)
            return

        map_data = self.menu_info[chapter_name]
        disable_map = False
        for map in map_data:
            map_button = MDButton(
                MDButtonText(text=map['title']),
                on_release=lambda btn, _map_name=map['title']: self.select_map(
                    _map_name,
                )
            )
            self.map_area.layout.add_widget(map_button)
            map["disabled"] = disable_map
            disable_map = not map["completed"]

    def select_map(self, map_name: str):
        """
        - Handle the selection of a map button
        - Send map command to the game to load the selected map
        """
        maps = self.menu_info[self.current_chapter]
        map_data = next((map for map in maps if map["title"] == map_name), None)
        
        if not map_data:
            print(f"Map '{map_name}' not found in chapter '{self.current_chapter}'")
            return
        
        # Replace the map info area
        if self.map_info:
            self.remove_widget(self.map_info)
        
        self.map_info = MapInfo(map_data)
        self.add_widget(self.map_info)


class P2GameManager(GameManager):
    def build(self):
        container = super().build()

        game_menu = self.add_client_tab("Maps", MenuLayout())
        self.log_panels["Maps"] = game_menu.content

        return container


class P2CommonContext(CommonContext):

    def make_gui(self) -> "type[kvui.GameManager]":
        class TextManager(P2GameManager):
            base_title = "Portal 2 Text Client"

        return TextManager

    def get_menu(self) -> "MenuLayout":
        return self.ui.log_panels["Maps"]
