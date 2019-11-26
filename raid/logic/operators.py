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
      Bank Percent: {}
      Split allotment: {}
      Reporting Channel: {}
      {}
      """.format(
        self.kingdom.kingdom_name,
        self.kingdom.bank_pct,
        self.kingdom.split_allotment,
        self.kingdom.channel,
        self._dump_pct_table("Raid allotment Distribution:", self.kingdom.allotment_distribution)
      ))

    def set_bank(self, bank):
      bank_pct = int(bank)
      self.kingdom.set_bank_pct(bank_pct)
      self.kingdom.save()
      return "Banking {} percent orns per allotment".format(bank_pct)
    
    def set_channel(self, channel):
      self.kingdom.set_channel(channel)
      self.kingdom.save()
      return "Setting #{} as the reporting channel".format(channel)
    
    def set_allotment(self, allotment_pcts):
      
      if not self._validate_allotment_percentages(allotment_pcts):
        return self._dump_pct_table(":exclamation: The values provided do not sum to 100:", allotment_pcts)
      # Save the percents to kingdom data
      if self.kingdom.set_allotment_distribution(allotment_pcts):
        self.kingdom.save()
        return self._dump_pct_table(":white_check_mark: Saving the following configuration:", allotment_pcts)
      return self._dump_pct_table(":exclamation: There was an error validating or saving the following values:", allotment_pcts)
