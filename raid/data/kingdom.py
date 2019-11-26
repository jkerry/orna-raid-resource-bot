from pymongo import MongoClient
from pprint import pprint

class Kingdom:
    def __init__(self, datasource, kingdom_id, kingdom_name):
        self.kingdom_id = kingdom_id
        self.kingdom_name = kingdom_name
        self.client = MongoClient(datasource)
        self.db = self.client.orna
        self.needs_persistance = False
        self.data = {
            'id': self.kingdom_id,
            'name': self.kingdom_name
        }
        if self.load() is None or self.needs_persistance:
            self.save()


    def load(self):
        print("Loading kingdom data for {}...".format(self.kingdom_id))
        result = self.db.kingdoms.find_one({'id': self.kingdom_id})
        if result is not None:
            self.data = result
            self._load_or_default_bank_pct()
            self._load_or_default_split_allotment()
            self._load_or_default_allotment_distribution()
            self._load_or_default_channel()
            self._load_or_default_command_channel()
            self._load_or_default_allotment_header()
            self._load_or_default_emoji()
            return self
        else:
            return None

    def save(self):
        self.data['bank_pct'] = self.bank_pct
        self.data['split_allotment'] = self.split_allotment
        self.data['kingdom_id'] = self.kingdom_id
        self.data['kingdom_name'] = self.kingdom_name
        self.data['allotment_distribution'] = self.allotment_distribution
        self.data['channel'] = self.channel
        self.data['command_channel'] = self.command_channel
        self.data['allotment_header'] = self.allotment_header
        self.data['emoji'] = self.emoji
        result = self.db.kingdoms.replace_one({'id': self.kingdom_id}, self.data, upsert=True)
        self.needs_persistance = False
        print("Updated {} records.".format(result.modified_count))

    def set_allotment_distribution(self, allotment_pcts):
        if self._allotment_distribution_is_valid(allotment_pcts):
            self.allotment_distribution = list(map(int, allotment_pcts))
            self.needs_persistance = True
            return True
        return False

    def set_emoji(self, emojis):
        self.emoji = emojis
        self.needs_persistance = True
        return True

    def set_allotment_header(self, allotment_header):
        self.allotment_header = allotment_header
        return True

    def set_command_channel(self, command_channel):
        self.command_channel = command_channel
        self.needs_persistance = True
        return True

    def set_channel(self, channel):
        self.channel = channel
        self.needs_persistance = True
        return True

    def set_bank_pct(self, new_bank_pct):
        if self._bank_pct_is_valid(new_bank_pct):
            self.bank_pct = new_bank_pct
            self.needs_persistance = True
            return True
        return False

    def set_split_allotment(self, new_split_allotment):
        if self._split_allotment_is_valid(new_split_allotment):
            self.split_allotment = new_split_allotment
            self.needs_persistance = True
            return True
        return False

    def _bank_pct_is_valid(self, bank_pct):
        return bank_pct is not None and \
            isinstance(bank_pct, int) and \
            bank_pct >= 0 and bank_pct <= 100

    def _load_or_default_allotment_header(self):
        if 'allotment_header' not in self.data:
            self.data['allotment_header'] = "Raid Allotments (24 hours):"
            self.needs_persistance = True
        self.allotment_header = self.data['allotment_header']

    def _load_or_default_allotment_distribution(self):
        if not ('allotment_distribution' in self.data and self._allotment_distribution_is_valid(self.data['allotment_distribution'])):
            self.data['allotment_distribution'] = [0,0,0,0,0,40,50,10]
            self.needs_persistance = True
        self.allotment_distribution = self.data['allotment_distribution']
    
    def _load_or_default_emoji(self):
        if not ('emoji' in self.data):
            self.data['emoji'] = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":calendar:"]
            self.needs_persistance = True
        self.emoji = self.data['emoji']

    def _load_or_default_command_channel(self):
        if 'command_channel' not in self.data:
            self.data['command_channel'] = None
            self.needs_persistance = True
        self.command_channel = self.data['command_channel']

    def _load_or_default_channel(self):
        if 'channel' not in self.data:
            self.data['channel'] = 'raid_allotments'
            self.needs_persistance = True
        self.channel = self.data['channel']

    def _load_or_default_bank_pct(self):
        if not ('bank_pct' in self.data and self._bank_pct_is_valid(self.data['bank_pct'])):
            self.data['bank_pct'] = 10
            self.needs_persistance = True
        self.bank_pct = self.data['bank_pct']
    
    def _split_allotment_is_valid(self, split_allotment):
        return split_allotment is not None and \
            isinstance(split_allotment, bool)

    def _load_or_default_split_allotment(self):
        if not ('split_allotment' in self.data and self._split_allotment_is_valid(self.data['split_allotment'])):
            self.data['split_allotment'] = True
            self.needs_persistance = True
        self.split_allotment= self.data['split_allotment']

    def _allotment_distribution_is_valid(self, allotment_pcts):
        total = 0
        if len(allotment_pcts) is not 8:
            return False
        for value in allotment_pcts:
            total += int(value)
        return total == 100