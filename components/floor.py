from core import *
from utility import DungeonActionTypes, DungeonActionData, DungeonRoleTypes

from components.character import Character

class Floor(Tileset):

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('floor')

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        if self.name == "floor_spikes":
            self.animation_speed = 1

    def trap_damage(self, action: ActionEvent):
        if action.name != DungeonActionTypes.COLLISION and action.name != DungeonActionTypes.COLLISION_IN:
            return

        if not isinstance(action.object, Character) or not isinstance(action.data, DungeonActionData):
            return

        if action.data.role != DungeonRoleTypes.PLAYER:
            return

        frame = int(self.animation_index) % len(self.texture.textures)
        if frame == 0 or frame == 3:
            char: Character = action.object
            char.damage(10)
            char.repulce_oposite(self.position, self.size, 800, 10)

        return True

    def on_action(self, action: ActionEvent):
        if self.name == "floor_spikes":
            return self.trap_damage(action)
