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
    configure_emoji_pattern = re.compile(r'configure emoji\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)\s*(\S+)')

    # Bank Commands
    configure_bank_target_pattern = re.compile(r'configure bank target\s*(\d+)')
    configure_bank_total_pattern = re.compile(r'configure bank total\s*(\d+)')
    configure_bank_hold_pattern = re.compile(r'configure bank hold\s*(\d+)')

    configure_monthly_cost_pattern = re.compile(r'configure monthly raid cost\s*(\d+)')
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
            total += int(value)
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
            
            configure bank total :: configures the total held bank orns
                -- example: %raid configure bank total 1000000
            
            configure bank target :: configures the amount of orns the kingdom is targeting while in savings mode
                -- example: %raid configure bank target 1500000
            
            configure bank hold :: configures the amount of orns to hold in reserve per allocation towards the target
                -- example: %raid configure bank hold 50000
            
            configure header :: set the header message for raid allotments
                -- example: %raid configure header This appears at the top of an allotment
            
            configure channel :: configure the channel to post allotments to. Note, this bot truncates posts from this channel
                -- example: %raid configure channel raid-allotments
            
            configure command channel :: configure the channel that this bot listens to for commands.  Default is all channels
                -- example: %raid configure command channel officers

            configure monthly raid cost :: configure the cost of the monthly raid. Default is 4800.
                -- example: %raid configure monthly raid cost 4800
            
            post allotment :: remove posts from the allotment channel and post a new allotment
                -- example: %raid post allotment 189000
            ```
        """)

    def try_load_data(self, kingdom_id, kingdom_name):
        return Kingdom(self.datasource, kingdom_id, kingdom_name)

    def _get_allotment(self, kingdom, orns):
        allotments = []
        bank_total = kingdom.bank_total
        bank_target = kingdom.bank_target
        monthly_cost = kingdom.monthly_cost
        bank_hold = kingdom.bank_hold
        allotment_distribution = kingdom.allotment_distribution
        orns_gained = orns - bank_total
        usable_orns = orns_gained
        if bank_total < bank_target:
            usable_orns = usable_orns - bank_hold
        raid_costs = [910,910,1410,1910,2500,3000,5500,monthly_cost]
        if orns_gained < 0 or usable_orns < 0:
            kingdom.set_bank_total(orns)
            kingdom.save()
            return [0]*8

        for i in range(8):
            dist = allotment_distribution[i] / 100.0
            allotments.append(math.floor(dist * usable_orns / raid_costs[i]))
        
        if bank_total < bank_target:
            kingdom.set_bank_total(bank_total+bank_hold)
            kingdom.save()
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
        command_text = message.content.replace('%raid','').strip().replace(',','')
        match = self.configure_post_allotment_pattern.match(command_text)
        values = []
        if not match:
            return False
        values = match.groups()
        allotment = self._get_allotment(kingdom, int(values[0]))

        # delete old messages
        await msg_channel.purge()
        # populate new messages
        allotment_metadata = {}
        allotment_metadata['timestamp'] = datetime.utcnow()
        message_ids = []
        header_msg = await msg_channel.send(kingdom.allotment_header)
        message_ids.append(header_msg.id)     
        bosses = [
            "Dracon",
            "Fomor",
            "Starlord",
            "Titan",
            "Balor Elite",
            "King Arthus",
            "Apollyon",
            "Monthly Raid"
        ]
        emoji = kingdom.emoji
        for i in range(8):
            message_ids.append(await self._send_allotment_and_get_id(msg_channel, "{} {}".format(emoji[i], bosses[i]), allotment[i]))
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
            if len(command_text.split()) is 10 and match:
                values = match.groups()
                return operators.set_allotment(values)
            else:
                return 'Unable to parse the command. Expected 8 percentage ' + \
                'values totaling to 100:\n`%raid configure allotment' + \
                ' 0 0 0 10 15 25 25 0`'
        elif command_text.startswith('configure emoji'):
            match = self.configure_emoji_pattern.match(command_text)
            if len(command_text.split()) is 10 and match:
                values = match.groups()
                return operators.set_emoji(values)
            else:
                return 'Unable to parse the command. Expected 8 emoji tags.' + \
                    '%raid configure emoji <:dracon:648761031400882177> <:fomor:648761066666590229> ...'
        elif command_text.startswith('configure bank target'):
            match = self.configure_bank_target_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_bank_target(values[0])
            else:
                return 'Unable to parse the command. Expected an orn value ' + \
                'greater than 0:\n`%raid configure bank total 900000'
        elif command_text.startswith('configure monthly raid cost'):
            match = self.configure_monthly_cost_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_monthly_cost(values[0])
            else:
                return 'Unable to parse the command. Expected an orn value ' + \
                'greater than 0:\n`%raid configure monthly raid cost 4800'
        elif command_text.startswith('configure bank total'):
            match = self.configure_bank_total_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_bank_total(values[0])
            else:
                return 'Unable to parse the command. Expected an orn value ' + \
                'greater than 0:\n`%raid configure bank target 1500000'
        elif command_text.startswith('configure bank hold'):
            match = self.configure_bank_hold_pattern.match(command_text)
            if match:
                values = match.groups()
                return operators.set_bank_hold(values[0])
            else:
                return 'Unable to parse the command. Expected an orn value ' + \
                'greater than 0:\n`%raid configure bank hold 50000'
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

