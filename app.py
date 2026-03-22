import discord
import json
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the blacklist configuration
with open('blacklist_config.json') as f:
    blacklist_config = json.load(f)

# Get the Discord token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

app = Flask(__name__)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_member_join(member):
    for server_id in blacklist_config['servers']:
        server = client.get_guild(server_id)
        if server:
            if member in server.members:
                print(f'{member.name} is on a blacklisted server: {server.name}')
                # You can add more actions here, like kicking or banning the user
                await member.kick(reason="Member is on a blacklisted server")
                break

@app.route('/check_user', methods=['POST'])
def check_user():
    data = request.json
    user_id = data['user_id']
    server_id = data['server_id']

    server = client.get_guild(server_id)
    if server:
        member = server.get_member(user_id)
        if member:
            return jsonify({'on_blacklist': server_id in blacklist_config['servers']})
        else:
            return jsonify({'on_blacklist': False})
    else:
        return jsonify({'on_blacklist': False})

if __name__ == '__main__':
    import threading
    threading.Thread(target=client.run, args=(TOKEN,)).start()
    app.run(port=5000)
