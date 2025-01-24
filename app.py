import os
import discord
import requests
import asyncio
from datetime import datetime
from flask import Flask
from threading import Thread
from waitress import serve

app = Flask('')

@app.route('/')
def home():
    return "Bot está activo"

def run():
    serve(app, host='0.0.0.0', port=8080)

Thread(target=run).start()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

error_texts = [
    "Error", "Runtime Error", "Build Error", 
    "Restart Space", "This Space is sleeping due to inactivity"
]

def get_current_time():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

async def check_space_status():
    channel_id = int(os.getenv("CHANNEL_ID"))
    role_id = int(os.getenv("ROLE_ID"))
    space_url = os.getenv("SPACE_URL")
    channel = await client.fetch_channel(channel_id)

    if channel is None:
        print("Error: No se pudo obtener el canal. Verifica el ID del canal en las variables de entorno.")
        return 

    while True:
        try:
            response = requests.get(space_url)
            current_time = get_current_time()

            hyperlink = f"[Acceder al Space]({space_url})"

            if response.status_code == 200:
                page_content = response.text
              
                if any(error_text in page_content for error_text in error_texts):
                    print(f"El Space está inactivo ({current_time}).")
                    await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar. {hyperlink}")
                else:
                    print(f"El Space está activo ({current_time}).")
                    await channel.send(f"✅ El Space está activo ({current_time}). {hyperlink}")
            else:
                print(f"El Space está inactivo (código de estado distinto de 200) ({current_time}).")
                await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar. {hyperlink}")
        except requests.exceptions.RequestException as e:
            current_time = get_current_time()  # Obtener la hora y fecha actual en caso de error
            print(f"Error al acceder al Space: {e} ({current_time})")
            # Enviar mensaje de error con el hyperlink
            await channel.send(f"⚠️ <@&{role_id}> El Space está inactivo ({current_time}). Favor de verificar. {hyperlink}")

        await asyncio.sleep(300)

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    client.loop.create_task(check_space_status())

# Inicia el bot de Discord
client.run(os.getenv("DISCORD_BOT_TOKEN"))
