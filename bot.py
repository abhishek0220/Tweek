from dotenv import load_dotenv
load_dotenv()


def start_bot():
    from Tweek import tweek
    tweek.start_websocket()


start_bot()
