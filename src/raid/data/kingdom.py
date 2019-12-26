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
        self._load_or_default_split_allotment()
        self._load_or_default_allotment_distribution()
        self._load_or_default_channel()
        self._load_or_default_command_channel()
        self._load_or_default_allotment_header()
        self._load_or_default_emoji()
        self._load_or_default_bank_target()
        self._load_or_default_bank_total()
        self._load_or_default_bank_hold()
        return self

    def save(self):
        self.data['bank_target'] = self.bank_target
        self.data['bank_total'] = self.bank_total
        self.data['bank_hold'] = self.bank_hold
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

    def set_bank_target(self, new_bank_target):
        if self._bank_target_is_valid(new_bank_target):
            self.bank_target = new_bank_target
            self.needs_persistance = True
            return True
        return False

    def set_bank_total(self, new_bank_total):
        if self._bank_total_is_valid(new_bank_total):
            self.bank_total = new_bank_total
            self.needs_persistance = True
            return True
        return False

    def set_bank_hold(self, new_bank_hold):
        if self._bank_hold_is_valid(new_bank_hold):
            self.bank_hold = new_bank_hold
            self.needs_persistance = True
            return True
        return False

    def set_split_allotment(self, new_split_allotment):
        if self._split_allotment_is_valid(new_split_allotment):
            self.split_allotment = new_split_allotment
            self.needs_persistance = True
            return True
        return False

    def _bank_target_is_valid(self, bank_target):
        return bank_target is not None and \
            isinstance(bank_target, int) and \
            bank_target >= 0

    def _bank_total_is_valid(self, bank_total):
        return bank_total is not None and \
            isinstance(bank_total, int) and \
            bank_total >= 0
    
    def _bank_hold_is_valid(self, bank_hold):
        return bank_hold is not None and \
            isinstance(bank_hold, int) and \
            bank_hold >= 0

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
    
    def _load_or_default_bank_target(self):
        if not ('bank_target' in self.data and self._bank_target_is_valid(self.data['bank_target'])):
            self.data['bank_target'] = 1000000
            self.needs_persistance = True
        self.bank_target = self.data['bank_target']
    
    def _load_or_default_bank_total(self):
        if not ('bank_total' in self.data and self._bank_total_is_valid(self.data['bank_total'])):
            self.data['bank_total'] = 500000
            self.needs_persistance = True
        self.bank_total = self.data['bank_total']

    def _load_or_default_bank_hold(self):
        if not ('bank_hold' in self.data and self._bank_hold_is_valid(self.data['bank_hold'])):
            self.data['bank_hold'] = 50000
            self.needs_persistance = True
        self.bank_hold = self.data['bank_hold']
    
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
        if len(allotment_pcts) != 8:
            return False
        for value in allotment_pcts:
            total += int(value)
        return total == 100