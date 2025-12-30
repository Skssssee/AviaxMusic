import os
import re
import asyncio
import aiohttp
import aiofiles
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch, Playlist
from AviaxMusic.utils.formatters import time_to_seconds

# --- CUSTOM API DOWNLOADER ---

async def download_song(link: str):
    """Downloads audio using your custom API"""
    if "?si=" in link:
        link = link.split("?si=")[0]
    
    video_id = link.split('v=')[-1].split('/')[-1]
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)
    file_path = os.path.join(download_folder, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path
        
    api_url = f"http://152.42.187.207:8000/audio?url={link}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api_url, timeout=30) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                if data.get("status") == "success":
                    download_link = data.get("audio")
                    
                    async with session.get(download_link) as file_res:
                        if file_res.status == 200:
                            async with aiofiles.open(file_path, mode='wb') as f:
                                await f.write(await file_res.read())
                            return file_path
        except Exception as e:
            print(f"API Download Error: {e}")
    return None

# --- MAIN CLASS ---

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            search = VideosSearch(link, limit=1)
            resp = await search.next()
            if not resp or not resp.get("result"):
                return None, None, None, None, None
            
            res = resp["result"][0]
            title = res.get("title", "Unknown Title")
            duration_min = res.get("duration", "0:00")
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res.get("id")
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            
            return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            print(f"Details Error: {e}")
            return None

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        # Use Custom API for Audio
        if songaudio or songvideo:
            await mystic.edit_text("⏳ **Fetching from Custom Server...**")
            file_path = await download_song(link)
            if file_path:
                return file_path
            
            # If API fails, send error instead of crashing
            await mystic.edit_text("❌ **Server Error: Could not process audio.**")
            return None
        
        return None

    # Helper to clean URLs from Telegram messages
    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        
        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]
        return None
        
