import re
import inspect
from raid.logic.operators import Operators
from raid.data.kingdom import Kingdom
from datetime import datetime
import math

class MessageParser:
    configure_channel_pattern = re.compile(r'configure channel\s*(\S+)')
    configure_command_channel_pattern = re.compile(r'configure command channel\s*(\S+)')
    configure_header_pattern = re.compile(r'configure header\s*(.*)')
    configure_allotment_pattern = re.compile(r'configure allotment\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)')
    configure_raid_emoji = re.compile(r'configure emoji\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)')
    configure_bank_pattern = re.compile(r'configure bank\s*(\d+)')
    configure_post_allotment_pattern = re.compile(r'post allotment\s*(\d+)')
    configure_split_pattern = re.compile(r'configure split\s*([TtrueFfals]+)')
    allocate_pattern = re.compile(r'allocate\s*(\d+)')

    datasource = None
    
    def __init__(self, discord_client):
        self.discord_client = discord_client
        super().__init__()

    def set_datasource(self, datasource):
        self.datasource = datasource

    def validate_allotment_percentages(self, values):
        total = 0
        for value in values:
            print(total)
            total += int(value)
        print(total)
        return total == 100

    def help(self):
        return inspect.cleandoc("""
            *Raid Resource Bot: Available Commands*
            ```
            show configuration :: Displays all kingdom raid configuration
                -- example: %raid show configuration
            
            configure allotment :: configures the raid distribution percentages. Monthly raid is last.
                -- example: %raid configure allotment 0 0 0 0 0 40 50 10
            
            configure emoji :: configures the raid emoji. IDs are unique per server. Monthly raid is last.
                -- example: %raid configure emoji <:dracon:648761031400882177> <:fomor:648761066666590229> ...
            
            configure bank :: configures the percent per allocation to reserve
                -- example: %raid configure bank 10
            
            configure header :: set the header message for raid allotments
                -- example: %raid configure header This appears at the top of an allotment
            
            configure channel :: configure the channel to post allotments to. Note, this bot truncates posts from this channel
                -- example: %raid configure channel raid-allotments
            
            configure command channel :: configure the channel that this bot listens to for commands.  Default is all channels
                -- example: %raid configure command channel officers
            
            post allotment :: remove posts from the allotment channel and post a new allotment
                -- example: %raid post allotment
            ```
        """)

    def try_load_data(self, kingdom_id, kingdom_name):
        return Kingdom(self.datasource, kingdom_id, kingdom_name)

    def _get_allotment(self, bank_pct, allotment_distribution, orns):
        allotments = []
        usable_orns = math.floor(orns * (1.0 - bank_pct))
        raid_costs = [910,910,1410,1910,2500,3000,5500,3000]
        for i in range(8):
            dist = allotment_distribution[i] / 100.0
            allotments.append(math.floor(dist * usable_orns / raid_costs[i]))
        return allotments

    def _allowed_command_channel(self, allowed_channel, channel):
        return allowed_channel is None or allowed_channel == channel

    async def send_allotment(self, message):
        # find the kingdom channel
        kingdom = Kingdom(self.datasource, message.guild.id, message.guild.name)
        kingdom.load()
        if not self._allowed_command_channel(kingdom.command_channel, message.channel.name):
            return None
        channel_name = kingdom.channel
        guild = self.discord_client.get_guild(kingdom.kingdom_id)
        msg_channel = None
        for channel in guild.channels:
            if channel.name == channel_name:
                msg_channel = channel
        if msg_channel is None:
            return "failed to identify kingdom announcement channel!"
        # calculate the current orn distributions
        command_text = message.content.replace('%raid','').strip()
        match = self.configure_post_allotment_pattern.match(command_text)
        values = []
        if not match:
            return False
        values = match.groups()
        allotment = self._get_allotment(int(kingdom.bank_pct)/100.0, kingdom.allotment_distribution, int(values[0]))

        # delete old messages
        await msg_channel.purge()
        # populate new messages
        allotment_metadata = {}
        allotment_metadata['timestamp'] = datetime.utcnow()
        message_ids = []
        header_msg = await msg_channel.send(kingdom.allotment_header)
        message_ids.append(header_msg.id)
        bosses = [
            "<:dracon:648761031400882177> Dracon",
            "<:fomor:648761066666590229> Fomor",
            "<:starlord:648761098777919498> Starlord",
            "<:titan:648761098790502410> Titan",
            "<:balor_knight:648761098648027156> Balor Elite",
            "<:king_arthus:648761098941628427> King Arthus",
            "<:apollyon:648761098794696713> Apollyon",
            ":calendar: Monthly Raid"
        ]
        for i in range(8):
            message_ids.append(await self._send_allotment_and_get_id(msg_channel, bosses[i], allotment[i]))
        return "Allotment Sent!"

    async def _send_allotment_and_get_id(self, channel, boss, allotment):
        if allotment == 0:
            return None
        msg = await channel.send("================================\n{boss}: Allotment: {allotment}".format(boss=boss, allotment=allotment))
        return msg.id

    def parse_command(self, message):
        kingdom_id = message.guild.id
        kingdom_name = message.guild.name
        data = self.try_load_data(kingdom_id, kingdom_name)
        if not self._allowed_command_channel(data.command_channel, message.channel.name):
            return None
        operators = Operators(data)
        command_text = message.content.replace('%raid','').strip()
        print("Command recieved: {}".format(command_text))
        if command_text.startswith('help'):
            return self.help()
        elif command_text.startswith('show configuration'):
            return operators.show_configuration()
        elif command_text.startswith('configure allotment'):
            match = self.configure_allotment_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_allotment(values)
            else:
                return 'Unable to parse the command. Expected 8 percentage ' + \
                'values totaling to 100:\n`%raid configure allotment' + \
                ' 0 0 0 10 15 25 25 0`'
        elif command_text.startswith('configure bank'):
            match = self.configure_bank_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_bank(values[0])
            else:
                return 'Unable to parse the command. Expected a percentage ' + \
                'value between 0 and 100:\n`%raid configure bank 15'
        elif command_text.startswith('configure channel'):
            match = self.configure_channel_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_channel(values[0])
            else:
                return 'Unable to parse the command. Expected a channel name' + \
                '\n`%raid configure channel raid-allotments'
        elif command_text.startswith('configure header'):
            match = self.configure_header_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_allotment_header(values[0])
            else:
                return 'failed to parse a header configuration, which should never happen'
        elif command_text.startswith('configure command channel'):
            match = self.configure_command_channel_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_command_channel(values[0])
            else:
                return 'failed to parse a header configuration, which should never happen'
        elif command_text.startswith('configure split'):
            return 'not implemented'
        else:
            return self.help()

