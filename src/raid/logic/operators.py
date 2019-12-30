import re
import inspect

class Operators:

    def __init__(self, data):
        self.kingdom = data
        super().__init__()
    
    def _validate_allotment_percentages(self, values):
        total = 0
        for value in values:
            total += int(value)
        return total == 100

    def _dump_pct_table(self, status, allotment_pcts):
      allotments = list(map(str,allotment_pcts))
      return inspect.cleandoc("""
      {}
      ```
      +--------------------+----------------------+
      | Raid               | Percentage Allocated |
      +--------------------+----------------------+
      | Dracon             |          {}          |
      +--------------------+----------------------+
      | Fomor              |          {}          |
      +--------------------+----------------------+
      | Starlord           |          {}          |
      +--------------------+----------------------+
      | Titan              |          {}          |
      +--------------------+----------------------+
      | Balor Elite        |          {}          |
      +--------------------+----------------------+
      | Fallen King Arthus |          {}          |
      +--------------------+----------------------+
      | Apollyon           |          {}          |
      +--------------------+----------------------+
      | Monthly Raid       |          {}          |
      +--------------------+----------------------+
      ```
      """.format(
          status,
          allotments[0].zfill(2),
          allotments[1].zfill(2),
          allotments[2].zfill(2),  
          allotments[3].zfill(2),
          allotments[4].zfill(2),
          allotments[5].zfill(2),
          allotments[6].zfill(2),
          allotments[7].zfill(2)))

    def show_configuration(self):
      return inspect.cleandoc("""
      {} Raid Configuration:
      Bank Total: {}
      Bank Target: {}
      Bank Hold: {}
      Split allotment: {}
      Reporting Channel: {}
      Command Channel: {}
      Current Monthly Raid Cost: {}
      {}
      """.format(
        self.kingdom.kingdom_name,
        self.kingdom.bank_total,
        self.kingdom.bank_target,
        self.kingdom.bank_hold,
        self.kingdom.split_allotment,
        self.kingdom.channel,
        self.kingdom.command_channel,
        self.kingdom.monthly_cost,
        self._dump_pct_table("Raid allotment Distribution:", self.kingdom.allotment_distribution)
      ))

    def set_bank_target(self, bank_target):
      bank = int(bank_target)
      self.kingdom.set_bank_target(bank)
      self.kingdom.save()
      return "Kingdom savings will target {} orns.".format(bank)

    def set_monthly_cost(self, monthly_cost):
      bank = int(monthly_cost)
      self.kingdom.set_monthly_cost(bank)
      self.kingdom.save()
      return "The monthly raid cost for the kingdom is set to {} orns.".format(bank)
    
    def set_bank_total(self, bank_total):
      bank = int(bank_total)
      self.kingdom.set_bank_total(bank)
      self.kingdom.save()
      return "The bank currently holds {} orns.".format(bank)
    
    def set_bank_hold(self, bank_hold):
      bank = int(bank_hold)
      self.kingdom.set_bank_hold(bank)
      self.kingdom.save()
      return "{} orns will be witheld from every allocation when the bank total ({}) is less than the bank target ({}).".format(bank, self.kingdom.bank_total, self.kingdom.bank_target)
    
    def set_channel(self, channel):
      self.kingdom.set_channel(channel)
      self.kingdom.save()
      return "Setting #{} as the reporting channel".format(channel)
    
    def set_command_channel(self, channel):
      self.kingdom.set_command_channel(channel)
      self.kingdom.save()
      return "Setting #{} as the command channel".format(channel)

    def set_allotment_header(self, header):
      self.kingdom.set_allotment_header(header)
      self.kingdom.save()
      return "Setting the following as the allotment header:\n{}".format(header)
    
    def set_allotment(self, allotment_pcts):
      if not self._validate_allotment_percentages(allotment_pcts):
        return self._dump_pct_table(":exclamation: The values provided do not sum to 100:", allotment_pcts)
      # Save the percents to kingdom data
      if self.kingdom.set_allotment_distribution(allotment_pcts):
        self.kingdom.save()
        return self._dump_pct_table(":white_check_mark: Saving the following configuration:", allotment_pcts)
      return self._dump_pct_table(":exclamation: There was an error validating or saving the following values:", allotment_pcts)

    def set_emoji(self, emojis):
      # Save the percents to kingdom data
      if self.kingdom.set_emoji(emojis):
        self.kingdom.save()
        return "Raid emoji persisted: {}".format(emojis)
      return self._dump_pct_table(":exclamation: There was an error validating or saving the following values:", emojis)
