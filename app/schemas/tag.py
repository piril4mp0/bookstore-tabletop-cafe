from pydantic import BaseModel, Field


class TagBase(BaseModel):
	name: str = Field(
		...,
		min_length=1,
		max_length=50,
		description="The name of the tag",
		example="vegan",
	)


class TagCreate(TagBase):
	pass


class Tag(TagBase):
	id: int = Field(..., description="The unique identifier of the tag", example=1)

	class Config:
		from_attributes = True
