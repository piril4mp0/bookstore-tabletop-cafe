from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.game import Game as GameModel
from app.schemas.game import GameCreate, GamePut


class GameService:
    """GameService Class deals with business logic involving the Games endpoint"""

    @staticmethod
    def save_game(db: Session, game: GameCreate) -> GameModel:
        """Saves a game to the database
        _summary_

        Args:
            db (Session): _description_
            game (GameCreate): _description_

        Returns:
            GameModel: _description_
        """
        new_game = GameModel(**game.model_dump())
        db.add(new_game)
        db.commit()
        db.refresh(new_game)
        return new_game

    # TODO
    # IMPLEMENT offset and limit query string
    @staticmethod
    def get_games(db: Session, genre: str | None = None) -> list[GameModel]:
        """Gets all games from the database
        _summary_

        Args:
            db (Session): _description_
            genre (str | None, optional): _description_. Defaults to None.

        Returns:
            list[GameModel]: _description_
        """
        stmt = select(GameModel)
        if genre:
            stmt = stmt.where(GameModel.genre.any(genre))
        return list(db.scalars(stmt).all())

    @staticmethod
    def get_game_by_id(db: Session, id: int) -> GameModel | None:
        """Gets a game from the database by id
        _summary_

        Args:
            db (Session): _description_
            id (int): _description_

        Returns:
            GameModel | None: _description_
        """
        return db.get(GameModel, id)

    @staticmethod
    def update_game(db: Session, id: int, game_update: GamePut) -> GameModel | None:
        """Updates a game from the database
        _summary_

        Args:
            db (Session): _description_
            id (int): _description_
            game_update (GamePut): _description_

        Returns:
            GameModel | None: _description_
        """
        current_game = db.get(GameModel, id)
        if not current_game:
            return None

        update_data = game_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(current_game, key, value)
        db.commit()
        db.refresh(current_game)
        return current_game

    @staticmethod
    def delete_game(db: Session, id: int) -> bool:
        """
        Deletes a game from the database
        _summary_
        Args:
            db (Session): _description_
            id (int): _description_

        Returns:
            bool: _description_
        """
        current_game = db.get(GameModel, id)
        if not current_game:
            return False
        db.delete(current_game)
        db.commit()
        return True
