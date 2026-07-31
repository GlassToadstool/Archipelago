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
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
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
            chapter_info_string += "Sub locations:\n"
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
                    on_release=lambda btn: self.play_map()
                )
                    
        
        # Add all these to the layout
        self.add_widget(self.chapter_info)
        self.add_widget(self.play_map_button)
        
        
    def play_map(self):
        """
        Send map command to the game to load the selected map
        """
        
        async_start(send_instant_command(f"{self.map_data['command']}"), "send_map_command")
        
class ChapterButton(MDButton):
    
    def __init__(self, chapter_name: str, chapter_maps: list, on_release):
        self.chapter_name = chapter_name
        self.chapter_maps = chapter_maps
        finished_checks, total_checks = self.calculate_completeness()
        
        self.button_text = MDButtonText(text=f"{self.chapter_name} {finished_checks}/{total_checks}")
                
        super().__init__(
                self.button_text,
                on_release = on_release
        )
        
    def calculate_completeness(self) -> tuple:
        total_checks = 0
        finished_checks = 0
        for map in self.chapter_maps:
            total_checks += map["total_locations"]
            finished_checks += map["finished_locations"]
            
        return finished_checks, total_checks
        
    def update_title(self, chapter_maps: dict):
        self.chapter_maps = chapter_maps
        finished_checks, total_checks = self.calculate_completeness()
        self.button_text.text = f"{self.chapter_name} {finished_checks}/{total_checks}"


class MenuLayout(MDGridLayout):

    def __init__(self):
        super().__init__(rows=1, cols=3, padding=[40, 10])
        self.menu_info = []
        self.selected_chapter = None
        self.selected_map = None
        self.map_area = None
        self.map_info = None
        self.is_open_world = False
        self.return_to_menu = False
        self.chapter_buttons: list[ChapterButton] = []

    def update_menu(self, menu_data: dict[str, dict]):
        """
        - Set the map data
        - Update the menu
        """
        self.menu_info = menu_data
        
        self.refresh_chapter_titles()
        
        selected_chapter = self.selected_chapter or list(self.menu_info.keys())[0]
        if self.map_area is not None:
            self.select_chapter(selected_chapter)
            
            if self.selected_map:
                self.select_map(self.selected_map)
            
    def refresh_chapter_titles(self):
        for cb in self.chapter_buttons:
            cb.update_title(self.menu_info[cb.chapter_name])
            
    def set_open_world(self):
        self.is_open_world = True

    def build(self):
        """
        - List of chapter buttons on the left side
        - Add a dynamic list of map buttons on the right side of the grid that updates based on the selected chapter
        """
        
        if self.menu_info is None:
            raise Exception("Menu data not set. Call update_menu() once before build().")

        self.clear_widgets()
        self.chapter_area = MDGridLayout(rows=10, cols=1)
        self.map_area = ScrollBox()
        self.map_area.layout.orientation = "vertical"
        self.map_area.layout.spacing = dp(3)
        self.map_area.scroll_type = ["bars"]
        self.map_area.do_scroll_x = False
        self.add_widget(self.chapter_area)
        self.add_widget(self.map_area)

        for chapter_name, maps in self.menu_info.items():            
            chapter_button = ChapterButton(chapter_name, maps, lambda btn, chapter=chapter_name: self.select_chapter(chapter))
            self.chapter_buttons.append(chapter_button)
            self.chapter_area.add_widget(chapter_button)
        
        menu_toggle_box = MDGridLayout(cols=2, row_default_height=40, row_force_default=True, padding=10)
        self.auto_next_map_button = MDIconButton(icon = "checkbox-blank-outline", on_release=self.toggle_switch)
        button_label = MDLabel(text="Return to menu on map finish: ")
        menu_toggle_box.add_widget(button_label)
        menu_toggle_box.add_widget(self.auto_next_map_button)
        self.chapter_area.add_widget(menu_toggle_box)
        

    def select_chapter(self, chapter_name: str):
        """
        - Remove the old map buttons
        - Add the list of new map buttons
        """
        
        if self.map_area is None:
            raise Exception("Map area not initialized. Call build() before select_chapter().")
        
        self.selected_chapter = chapter_name

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
                MDButtonText(text=f"{map['title']} {map["finished_locations"]}/{map["total_locations"]}"),
                on_release=lambda btn, _map_name=map['title']: self.select_map(
                    _map_name,
                )
            )
            self.map_area.layout.add_widget(map_button)
            map["disabled"] = disable_map
            if not self.is_open_world:
                disable_map = not map["completed"]

    def select_map(self, map_name: str):
        """
        - Handle the selection of a map button
        - Send map command to the game to load the selected map
        """
        maps = self.menu_info[self.selected_chapter]
        map_data = next((map for map in maps if map["title"] == map_name), None)
        
        if not map_data:
            print(f"Map '{map_name}' not found in chapter '{self.selected_chapter}'")
            return
        
        self.selected_map = map_data["title"]
        
        # Replace the map info area
        if self.map_info:
            self.remove_widget(self.map_info)
        
        self.map_info = MapInfo(map_data)
        self.add_widget(self.map_info)
        
    def toggle_switch(self, instance):
        self.return_to_menu = not self.return_to_menu
        if self.return_to_menu:
            self.auto_next_map_button.icon = "checkbox-outline"
        else:
            self.auto_next_map_button.icon = "checkbox-blank-outline"
        
        logger.info(self.return_to_menu)


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
