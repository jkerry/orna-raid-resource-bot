import configargparse
from raid.data.kingdom import Kingdom
from raid import logic

p = configargparse.ArgParser(default_config_files=['./*.conf'])
p.add('-t', '--token', required=True, env_var='DISCORD_BOT_TOKEN', help='Discord bot token')
p.add('-d', '--datasource', required=True, env_var='ORNA_BOT_DATASOURCE', help='A MongoDB Connection string for orna kingdom data')
p.add('-k', '--kingdom_id', required=False, env_var='ORNA_KINGDOM_ID', help='A unique key for the active kingdom')

options = p.parse_args()

logic.init(options)