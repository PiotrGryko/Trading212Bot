import json


class Logger:

    def __init__(self) -> None:
        super().__init__()
        self.last_segment = ""
        self.segment_size = 100

    def critical(self, message):
        print(f"\033[31m{message}")

    def debug(self, message):
        print(f"\033[37m{message}")

    def info(self, message):
        print(f"\033[34m{message}")

    def success_or_warrning(self, message, success):
        if success:
            print(f"\033[32m{message}")
        else:
            print(f"\033[35m{message}")

    def open_segment(self, message):
        wing_size = int((self.segment_size - len(message)) / 2 - 2)
        wing = ""
        for index in range(wing_size):
            wing += "#"
        self.last_segment = f"{wing} {message} {wing}"
        print(f"\033[33m\n{self.last_segment}")

    def close_segment(self):
        value = ""
        for index in range(len(self.last_segment)):
            value += "#"
        print(f"\033[33m{value}\n")

    def json(self, data):
        print(json.dumps(data, indent=4))

    def analysis_result(self, message):
        wing_size = int((self.segment_size - len(message)) / 2 - 2)
        wing = ""
        for index in range(wing_size):
            wing += "#"
        segment = f"{wing} {message} {wing}"
        print(f"\033[36m{segment}")

    def analysis_critical(self, message):
        wing_size = int((self.segment_size - len(message)) / 2 - 2)
        wing = ""
        for index in range(wing_size):
            wing += "#"
        segment = f"{wing} {message} {wing}"
        print(f"\033[31m{segment}")
