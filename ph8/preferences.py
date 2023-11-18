from logging import getLogger
from types import SimpleNamespace
from typing import TypedDict
import discord
from discord.ext import commands
import openai
import json

logger = getLogger(__name__)


class ModelsResponseModel(TypedDict):
    id: str
    object: str
    created: int
    owned_by: str


class ModelsResponse(TypedDict):
    object: str
    data: list[ModelsResponseModel]


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id

    return commands.check(predicate)


def get_reference_id(message: discord.Message):
    return message.reference and message.reference.message_id


def parse_models_response(res: ModelsResponse):
    res["data"].sort(key=lambda x: x["created"], reverse=True)

    models = []

    for model in res["data"]:
        if not model["object"] == "model":
            continue
        if not model["id"].startswith("gpt-"):
            continue
        models.append(model["id"])

    return models


class PreferencesCog(commands.Cog, name="Preferences"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def __get_models(self):
        response: ModelsResponse = openai.Model.list()  # type: ignore
        return parse_models_response(response)

    async def cog_load(self):
        models = await self.__get_models()
        self.model.help = (
            "Sets the model to use for the bot.\n\nAvailable models:\n  " + "\n  ".join(models)
        )

    @commands.group()
    async def set(self, ctx: commands.Context):
        """Sets user preferences"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @set.command()
    async def model(self, ctx: commands.Context, value: str | None = None):
        if value is None:
            await ctx.send_help(ctx.command)


async def setup(bot: commands.Bot):
    await bot.add_cog(PreferencesCog(bot))
