from datetime import datetime
from logging import getLogger
from typing import TypedDict, Any
import discord
from discord.ext import commands
import openai
import ph8.config


logger = getLogger(__name__)


class UserPrefDict(TypedDict):
    model_id: str | None


class OpenAIModel(TypedDict):
    id: str
    object: str
    created: int
    owned_by: str


class OpenAIModelsResponse(TypedDict):
    object: str
    data: list[OpenAIModel]


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == ctx.bot.owner_id

    return commands.check(predicate)


def get_reference_id(message: discord.Message):
    return message.reference and message.reference.message_id


__models: list[OpenAIModel] = []


def get_models():
    if len(__models) == 0:
        response: OpenAIModelsResponse = openai.Model.list()  # type: ignore
        response["data"].sort(key=lambda x: x["created"], reverse=True)

        for model in response["data"]:
            if not model["object"] == "model":
                continue

            if not model["id"].startswith("gpt-"):
                continue

            __models.append(model)

    return __models


class Preferences(commands.Cog):
    __user_prefs: dict[str, UserPrefDict] = {}

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def __ensure_user_prefs(self, user_key: str):
        if user_key not in self.__user_prefs:
            self.__user_prefs[user_key] = {
                "model_id": ph8.config.models.default,
            }

    def get_user_pref(self, user_id: int, param: str):
        logger.info("get_user_pref %s %s", user_id, param)
        user_key = str(user_id)
        self.__ensure_user_prefs(user_key)

        return self.__user_prefs[user_key][param]

    def set_user_pref(self, user_id: int, param: str, value: Any):
        logger.info("set_user_pref %s %s %s", user_id, param, value)
        user_key = str(user_id)
        self.__ensure_user_prefs(user_key)
        self.__user_prefs[user_key][param] = value

    @commands.group()
    async def model(
        self,
        ctx: commands.Context,
    ):
        if ctx.invoked_subcommand is None:
            current_model = self.get_user_pref(ctx.author.id, "model_id")
            models = get_models()
            longest_model_id = max([len(model["id"]) for model in models])
            models_str = "\n".join(
                [
                    "|{}| {} | {}".format(
                        "*" if model["id"] == current_model else " ",
                        datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                        model["id"],
                    )
                    for model in models
                ]
            )

            separator_len = longest_model_id + 18

            await ctx.reply(
                "```"
                + "The following is a list of models you have access to;\n"
                + "`*` indicates the model currently in use.\n\n"
                + "|?| CREATED    | ID\n"
                + f"{separator_len*'-'}\n"
                + f"{models_str}\n\n"
                + f"HINT: Use `$ph8.model set <model_id>` to set your model.\n"
                + "```"
            )

    @model.command(name="set")
    @commands.is_owner()
    async def set_model(
        self,
        ctx: commands.Context,
        model_id=commands.parameter(
            description="The ID of the model you'd like used for responses.",
            default=None,
        ),
    ):
        """Sets the model used for your responses."""

        if not model_id:
            await ctx.send_help(ctx.command)
            return

        valid_model_ids = [model["id"] for model in get_models()]
        if model_id not in valid_model_ids:
            await ctx.message.add_reaction("❌")
            await ctx.reply(f"```⚠️ Invalid model ID.```")
            return

        self.set_user_pref(ctx.author.id, "model_id", model_id)
        await ctx.message.add_reaction("✅")


async def setup(bot: commands.Bot):
    await bot.add_cog(Preferences(bot))
