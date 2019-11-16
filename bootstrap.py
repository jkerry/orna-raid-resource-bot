import configargparse
from raid.data.kingdom import Kingdom

p = configargparse.ArgParser(default_config_files=['./*.conf'])
p.add('-t', '--token', required=True, env_var='DISCORD_BOT_TOKEN', help='Discord bot token')
p.add('-d', '--datasource', required=True, env_var='ORNA_BOT_DATASOURCE', help='A MongoDB Connection string for orna kingdom data')
p.add('-k', '--kingdom_id', required=True, env_var='ORNA_KINGDOM_ID', help='A unique key for the active kingdom')

options = p.parse_args()
data = Kingdom(options.datasource.strip(), options.kingdom_id.strip())
data.data = {
    'name': 'EE',
    'accumulated_orns': 128000,
    'bank_pct': 0.2,
    'base_rotation_time_hours': 10,
    'daily_rotation_hours': 12
}
data.save()