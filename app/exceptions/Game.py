class GameNotFoundException(Exception):
    def __init__(self, id: int):
        self.game_id = id
