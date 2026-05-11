from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

class GameBase(BaseModel):
    title: str = Field(...,min_length=1, max_length=255, description="The title of the game", example="Old Dragon 2")
    genre: List[str] = Field(...,description="The genre of the game", example=["RPG", "Fantasy"])
    description: str = Field(...,min_length=1, max_length=500, description="The description of the game", example="An epic fantasy role-playing game")
    release_date: date = Field(...,description="The release date of the game", example="2023-01-01")
    players: int = Field(...,gt=0, description="The number of players the game supports", example=4)

class GameCreate(GameBase):
    pass

class Game(GameBase):
    id: int = Field(..., description="The unique identifier of the game", example=1)

class GamePut(BaseModel):
    title: Optional[str] = Field(None,min_length=1, max_length=255, description="The title of the game", example="Old Dragon 2")
    genre: Optional[List[str]] = Field(None, description="The genre of the game", example=["RPG", "Fantasy"])
    description: Optional[str] = Field(None,min_length=1, max_length=500, description="The description of the game", example="An epic fantasy role-playing game")
    release_date: Optional[date] = Field(None, description="The release date of the game", example="2023-01-01")
    players: Optional[int] = Field(None,gt=0, description="The number of players the game supports", example=4)
