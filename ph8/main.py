import ph8.discord
import ph8.config
import ph8.ai.chains


async def handle_message(details: ph8.discord.MessageDetails):
    if not details.should_respond:
        return

    print(f"Received message: {details.message.content}")

    response = ph8.ai.chains.conversational.invoke(details.message.content)
    print(f"Response: {response}")

    await details.message.reply(response)


def init():
    ph8.discord.add_message_handler(handle_message)
    ph8.discord.client.run(ph8.config.discord.token)


if __name__ == "__main__":
    init()
