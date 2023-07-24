import openai
import telnetlib
import random
from typing import Optional

TELNET_IP = "127.0.0.1"
MSG_STRING = " : "
DEAD_MSG = "*DEAD*"

MAX_CHAT_SIZE = 128
MIN_CHAT_SIZE = 2

T_CHAT_PREFIX = "(Terrorist)"
CT_CHAT_PREFIX = "(Counter-Terrorist)"

class CSGOChatBot:
    def __init__(self, telnet_port: int, player_name: str):
        self.telnet_port = telnet_port
        self.player_name = player_name

    def set_openai_key(self, api_key: str) -> None:
        openai.api_key = api_key

    def get_response_for_message(self, sender: str, msg: str) -> Optional[str]:
        system_message = f"""
            You are a human playing CSGO.
            Keep your message short and funny.
            Never mention that you are an AI.
            Insert smiley faces and emojis.
            No hashtags.
            Keep the response as short as possible.
            Use lowercase only.
            The maximum length of the response is {random.randint(MIN_CHAT_SIZE, MAX_CHAT_SIZE)}.
            """

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{sender}: {msg}"},
            ]
        )

        response = completion.choices[0].message.content
        return response

    def connect_to_server(self) -> telnetlib.Telnet:
        t = telnetlib.Telnet(TELNET_IP, self.telnet_port)
        t.write(b"say ::::: pycsgogpt started! :::::\n")
        return t

    def process_message(self, t: telnetlib.Telnet, output: str) -> None:
        player_info, player_msg = output.split(MSG_STRING, maxsplit=1)
        is_team = T_CHAT_PREFIX in player_info or CT_CHAT_PREFIX in player_info
        player_name = player_info.strip().replace(DEAD_MSG, "").replace(T_CHAT_PREFIX, "").replace(CT_CHAT_PREFIX, "")

        if self.player_name in player_name:
            return
        
        print(f"- {player_name}: {player_msg.strip()}")

        response = self.get_response_for_message(player_name, player_msg.strip())
        if response:
            say_cmd = "say_team" if is_team else "say"
            t.write(f"{say_cmd} {response}\n".encode("utf-8"))

    def loop(self) -> None:
        t = self.connect_to_server()

        while True:
            output = t.read_until(b"\n", timeout=0.1).decode("utf-8")
            if not output:
                continue

            if MSG_STRING not in output:
                continue

            self.process_message(t, output)
