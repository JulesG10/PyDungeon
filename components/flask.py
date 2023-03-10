from core import *


class Flask(CollectableItem):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('flask')
    
    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        self.size /= 2
