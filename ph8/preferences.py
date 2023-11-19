from datetime import datetime
from logging import getLogger
from typing import TypedDict, Any
import discord
from discord.ext import commands
import openai
import ph8.config


logger = getLogger(__name__)


class UserPrefDict(TypedDict):
    model_name: str | None


class OpenAIModel(TypedDict):
    id: str
    object: str
    created: int
    owned_by: str


class OpenAIModelsResponse(TypedDict):
    object: str
    data: list[OpenAIModel]



class Preferences(commands.Cog):
    __user_prefs: dict[str, UserPrefDict] = {}
    __cached_models: list[OpenAIModel] = []

    @property
    def models(self):
        if len(self.__cached_models) == 0:
            response: OpenAIModelsResponse = openai.Model.list()  # type: ignore
            response["data"].sort(key=lambda x: x["created"], reverse=True)

            for model in response["data"]:
                if not model["object"] == "model":
                    continue

                if not model["id"].startswith("gpt-"):
                    continue

                self.__cached_models.append(model)

        return self.__cached_models

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def __ensure_user_prefs(self, user_key: str):
        if user_key not in self.__user_prefs:
            self.__user_prefs[user_key] = {
                "model_name": ph8.config.models.default,
            }

    def get_user_pref(self, user_id: int, param: str):
        user_key = str(user_id)
        self.__ensure_user_prefs(user_key)
        return self.__user_prefs[user_key][param]

    def set_user_pref(self, user_id: int, param: str, value: Any):
        user_key = str(user_id)
        self.__ensure_user_prefs(user_key)
        self.__user_prefs[user_key][param] = value

    async def __get_model_info(self, ctx: commands.Context):
        current_model = self.get_user_pref(ctx.author.id, "model_name")
        longest_model_name = max([len(model["id"]) for model in self.models])
        models_str = "\n".join(
            [
                "|{}| {} | {}".format(
                    "*" if model["id"] == current_model else " ",
                    datetime.fromtimestamp(model["created"]).strftime("%Y-%m-%d"),
                    model["id"],
                )
                for model in self.models
            ]
        )

        separator_len = longest_model_name + 18

        await ctx.reply(
            "```"
            + "The following is a list of models you have access to;\n"
            + "`*` indicates the model currently in use.\n\n"
            + "|?| CREATED    | ID\n"
            + f"{separator_len*'-'}\n"
            + f"{models_str}\n\n"
            + f"HINT: Use `$ph8.model set <model_name>` to set your model.\n"
            + "```"
        )

    async def __set_model(
        self,
        ctx: commands.Context,
        model_name: str,
    ):
        """Sets the model used for your responses."""
        valid_model_names = [model["id"] for model in self.models]
        if model_name not in valid_model_names:
            await ctx.message.add_reaction("❌")
            await ctx.reply(f"```❌ Invalid model name.```")
            return

        if model_name == self.get_user_pref(ctx.author.id, "model_name"):
            await ctx.message.add_reaction("⚠️")
            await ctx.reply(f"```⚠️ This is already the selected model.```")
            return

        self.set_user_pref(ctx.author.id, "model_name", model_name)
        await ctx.message.add_reaction("✅")

    @commands.command()
    async def model(
        self,
        ctx: commands.Context,
        model_name=commands.parameter(
            description="The ID of the model you'd like used for responses.",
            default=None,
        ),
    ):
        await (
            self.__get_model_info(ctx)
            if model_name is None
            else self.__set_model(ctx, model_name)
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Preferences(bot))
