import re

class MessageParser:
    load_pattern = re.compile(r'load\s*(\d+)\s*(.*)')

    def parse_command(self, message):
        command_text = message.content.replace('%raid','').strip()
        print("Command recieved: {}".format(command_text))
        if command_text.startswith('load'):
            match = self.load_pattern.match(command_text)
            if match:
                orns = match.group(1)
                reason = match.group(2)
                op = "Congrats! loading {} orns because: {}".format(orns, reason)
                print(op) 
                return op
            else:
                return 'unable to parse the command. Expected: "load 99872 Victory against Late Luminosity"'

