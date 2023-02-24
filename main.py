from BTP.BTP import *
import BTP.BTP

import os
import sys
import random

from core import *
from components import *
from utility import *
from map import *


class GameState:
    NONE = -1
    MENU = 0
    GAME = 1
    MAP_CREATOR = 2


class Loading:

    def __init__(self, btp: Win) -> None:
        self.btp = btp
        self.loading = 0

    def center_text(self, text: str, size: int):
        tsize = self.btp.text_size(text, size)
        return (self.btp.get_render_size() - tsize)/2, tsize

    def on_draw_error(self, error: str):
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        pos_err, size_err = self.center_text(error, 40)
        pos_err.y -= 50
        self.btp.draw_text(error, pos_err, 40, BLACK)

        info = "Please restart your game, or update it!"
        pos_inf, size_inf = self.center_text(info, 20)
        pos_inf.y += 30
        self.btp.draw_text(info,pos_inf, 20, BLACK)

        self.btp.draw_line(pos_err + Vec(0, 60), pos_err + Vec(size_err.x, 60), BLACK)
        

    def on_draw(self, dt):
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        text = "Loading textures..."
        tsize = self.btp.text_size(text, 40)
        pos = (self.btp.get_render_size() - tsize)/2
        pos.y -= 20

        self.btp.draw_text(text, pos, 40, BLACK)
        self.btp.draw_rect(Vec(pos.x, pos.y + 60),Vec(tsize.x * (self.loading/100), 20), BLACK)

        self.loading += dt * 30
        if self.loading >= 100:
            self.loading = 0


class Menu:
    def __init__(self, btp: Win) -> None:
        self.btp = btp

        self.btn_mapcr = Button(self.btp)
        self.btn_select = Button(self.btp)
        self.input_map = Input(self.btp)
        self.selected_map = ""
        self.last_selected = ""

    def on_load(self):
        margin = Vec(40, 10)
        fontsize = 30

        position = Vec(0, -100)
        wt = (self.btp.get_render_size() -
              (self.btp.text_size("Map creator", fontsize) + margin*2))/2

        self.btn_mapcr.build("Map creator", wt + position, margin, fontsize)

        position.y += 100
        self.input_map.build(self.get_first_map(), wt +
                             position, margin, fontsize)

        position.y += 100
        self.btn_select.build("Load & Play", wt + position, margin, fontsize)

    def get_first_map(self):
        file = [f.replace('.dat', '')
                for f in os.listdir(".") if f.endswith('.dat')]
        return file[0] if len(file) > 0 else ""

    def reset_input(self, text=""):
        self.input_map.build(text, self.input_map.position,
                             self.input_map.margin, self.input_map.button.text.fontsize)

    def on_draw_ui(self, dt: float) -> GameState:
        state = GameState.MENU
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        bgalpha = 0 if self.btn_mapcr.is_hover() else 20
        if self.btn_mapcr.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                self.reset_input()
            state = GameState.MAP_CREATOR

        bgalpha = 0 if self.btn_select.is_hover() else 20
        if self.btn_select.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                state = GameState.GAME

            self.reset_input()

        self.selected_map = self.input_map.draw(BLACK)
        self.btp.draw_text(".dat", self.input_map.position + Vec(self.input_map.button.size.x +
                           20, self.input_map.button.size.y/2), self.input_map.button.text.fontsize, BLACK)

        self.btp.draw_rect(self.btn_mapcr.position -
                           self.btn_mapcr.margin, Vec(5, 280), BLACK)

        return state

    def get_selected_map(self):
        return self.last_selected


class Game:

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        self.btp = btp
        self.last_key = 0
        self.index = 0

        self.atlas = atlas
        self.stats = Stats(self.btp)
        self.map = Map(self.btp, self.atlas)

        self.character: Character
        
        self.heart_value = 20
        self.max_life = 100
        self.hearts_display: list[Optional[UI]] = [ None for i in range(int(self.max_life/self.heart_value))]
        self.last_life = 0

    def close_game(self):
        self.map.stop_update_thread()

    def new_game(self, name):
        self.map.clear_map()
        self.map.load_map(name)
        self.map.start_update_thread()
        self.map.force_update_view()

    def on_ready(self):
        self.map.on_ready()

        characters: list[Character] = self.atlas.from_instance(Character)
        self.character = random.choice(characters).copy()
        self.character.atlas = self.atlas
        self.character.action_data = DungeonActionData(role=DungeonRoleTypes.PLAYER)
        

    def update_hearts(self, position : Vec):
        parts = split_num(self.character.life, self.heart_value)
        
        for index in range(int(self.max_life/self.heart_value)):
            if index >= len(parts):
                self.hearts_display[index] = self.atlas.copy(UI, "ui_heart_empty")
            elif parts[index] == self.heart_value:
                self.hearts_display[index] = self.atlas.copy(UI, "ui_heart_full")            
            else:
                self.hearts_display[index] = self.atlas.copy(UI, "ui_heart_half")

            self.hearts_display[index].size /=3
            self.hearts_display[index].position = position + Vec(self.hearts_display[index].size.x * index, 0)

    def on_draw(self, dt: float):
        self.btp.camera_follow_rect(
            self.character.position,
            self.character.size,
            0.0, # min distance 
            0.0, # speed
            0.0 # min speed
        )

        self.map.on_draw(dt)
        self.character.on_update_control(dt, self.map.get_collision_tiles())
        self.character.on_draw(dt)


        #self.angle += dt * 100
        # pos = self.character.position + Vec(self.character.size.x/4, self.character.size.y/4)
        # size = Vec(50)
        # newp = rotate_around(pos, pos+size/2, self.angle)
        # self.btp.draw_rectrot(newp, size, self.angle, Color(255, 0, 0, 255))
  
    def on_draw_ui(self, dt: float) -> bool:
        key = self.btp.get_key_code()
        if key != 0:
            self.last_key = key

        self.stats["FPS"] = round(1/dt) if dt != 0 else 0
        self.stats["Key"] = self.last_key
        self.stats["View chunk"] = len(self.map.view_chunks)
        self.stats["View tile"] = self.map.view_tile_count
        self.stats["Player life"] = self.character.life

        self.stats.on_draw(Vec(), 20, BLACK)
        
        self.character.on_draw_ui(dt)
        
        if self.last_life != self.character.life:
            self.last_life = self.character.life
            self.update_hearts(self.btp.get_render_size() * Vec(0.1, 0.9))
        
        for heart in self.hearts_display:
            if heart is not None:
                heart.on_draw(dt)

        return self.btp.is_key_pressed(Keyboard.ENTER) or not self.character.is_alive()


class Dungeon(Win):
    ASSETS_DIR = "./assets/"

    def __init__(self) -> None:
        super().__init__()
        print(BTP.BTP.__doc__)

        self.texture_atlas = TextureAtlas()
        self.objects_atlas = ObjectBaseAtlas()
        self.object_base: list[ComponentObject] = [
            Character,
            Doors,
            Floor,
            Wall,
            Coin,
            Chest,
            SingleItem,
            Flask,
            Weapon,
            UI
        ]

        self.loading = Loading(self)
        self.menu = Menu(self)
        self.game = Game(self, self.objects_atlas)
        self.map_creator = MapCreator(self, self.objects_atlas)

        self.state = GameState.MENU
        self.no_assets = False

    def on_ready(self) -> None:
        if self.no_assets:
            return
        
        for obj in self.objects_atlas.objects:
            if isinstance(obj, ComponentObject):
                obj.on_ready(self)
                obj.accepted_actions = DungeonActionTypes.all()

        self.camera_follow_rect(
            Vec(),
            Vec(TILE_SIZE),
            0.0, 0.0, 0.0
        )

        self.map_creator.on_ready()
        self.game.on_ready()

    def on_close(self) -> None:
        pass

    def on_draw_background(self, dt: float) -> None:
        pass

    def on_draw(self, dt: float) -> None:
        match self.state:
            case GameState.MAP_CREATOR:
                self.map_creator.on_draw(dt)
            case GameState.GAME:
                self.game.on_draw(dt)

    def on_draw_ui(self, dt: float) -> None:
        if self.is_loading():
            return

        if self.no_assets:
            self.loading.on_draw_error("Assets not found")
            return

        match self.state:
            case GameState.MENU:
                self.state = self.menu.on_draw_ui(dt)
                if self.state == GameState.MAP_CREATOR:
                    self.game.close_game()

                    self.map_creator.clear_map()
                    self.map_creator.load_map(self.menu.get_selected_map())
                    self.map_creator.start_update_thread()
                    self.map_creator.force_update_view()

                elif self.state == GameState.GAME:
                    self.map_creator.stop_update_thread()
                    self.game.new_game(self.menu.get_selected_map())

            case GameState.MAP_CREATOR:
                if self.map_creator.on_draw_ui(dt):
                    self.state = GameState.MENU
                    self.menu.reset_input(self.menu.get_first_map())
            case GameState.GAME:
                if self.game.on_draw_ui(dt):
                    self.state = GameState.MENU
                    self.menu.reset_input(self.menu.get_first_map())

    def on_draw_loading(self, dt: float) -> None:
        self.loading.on_draw(dt)

    def on_load(self) -> None:
        if not os.path.exists(Demo.ASSETS_DIR):
            self.no_assets = True
            return
        
        files = os.listdir(Demo.ASSETS_DIR)
        for filename in files:
            texture_path = os.path.abspath(Demo.ASSETS_DIR + filename)
            texture_id = self.load_image(texture_path)

            self.texture_atlas.add(filename, texture_id)

        for type in self.object_base:
            self.objects_atlas.register(type)

        for texture in self.texture_atlas.textures:
            self.objects_atlas.add(texture)

        self.menu.on_load()
        
        # time.sleep(3)


def main(args):
    Dungeon().start(1680, 1050, "Demo - BTP v{}".format(BTP.BTP.__version__), False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:1]))