import os
import asyncio
import logging
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp

logging.basicConfig(level=logging.INFO)

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_STRING = os.environ.get("SESSION_STRING")

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
calls = PyTgCalls(userbot)

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio.mp3"

@app.on_message(filters.command("play"))
async def play(client, message: Message):
    if len(message.command) < 2:
        await message.reply("သီချင်းနာမည် သို့မဟုတ် YouTube link ပေးပါ။\nဥပမာ: /play shape of you")
        return
    
    query = " ".join(message.command[1:])
    await message.reply(f"🔍 {query} ရှာနေတယ်...")
    
    try:
        chat_id = message.chat.id
        
        if not query.startswith("http"):
            query = f"ytsearch:{query}"
        
        file = download_audio(query)
        
        await calls.play(
            chat_id,
            MediaStream(file)
        )
        await message.reply(f"🎵 {query} တီးနေပြီ!")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command("stop"))
async def stop(client, message: Message):
    try:
        await calls.leave_call(message.chat.id)
        await message.reply("⏹ သီချင်းရပ်လိုက်တယ်။")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

async def main():
    await userbot.start()
    await calls.start()
    await app.start()
    await asyncio.get_event_loop().run_forever()

if name == "__main__":
    asyncio.run(main())
