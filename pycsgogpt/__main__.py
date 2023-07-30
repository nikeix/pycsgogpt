import typer
from pycsgogpt.csgo_chatbot import CSGOChatBot

app = typer.Typer()

def entry(
    player_name: str,
    openapi_key: str,
    telnet_port: int = typer.Option(21234,
    help="The telnet port for the CSGO server."),
    chat_history_size: int = 20,
) -> None:
    chat_bot = CSGOChatBot(telnet_port, player_name, chat_history_size)
    chat_bot.set_openai_key(openapi_key)

    try:
        chat_bot.loop()
    except KeyboardInterrupt:
        print("Exiting...")
    except ConnectionRefusedError:
        print(f"Connection refused. Make sure you add `-netconport {telnet_port}` to the CSGO server launch options.")
        print("Is csgo running?")
    except ConnectionAbortedError:
        print("Bye!")

def main():
    app.command()(entry)
    app()
    
    
if __name__ == "__main__":
    main()
