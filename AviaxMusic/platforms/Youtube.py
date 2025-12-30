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

# --- DOWNLOAD LOGIC ---

async def download_song(link: str):
    """Uses your custom API to download the file"""
    video_id = link.split('v=')[-1].split('/')[-1].split('?')[0]
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)
    file_path = os.path.join(download_folder, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path
        
    api_url = f"http://152.42.187.207:8000/audio?url={link}"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Increased timeout to 60s because API might be slow
            async with session.get(api_url, timeout=60) as response:
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
            print(f"Download Error: {e}")
    return None

# --- MAIN CLASS ---

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def url(self, message: Message) -> Union[str, None]:
        """Improved URL extractor to handle all message types"""
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        
        for msg in messages:
            text = msg.text or msg.caption
            if not text:
                continue
            # Check for text links (hyperlinks)
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        """Fetches video metadata with error handling"""
        if videoid:
            link = self.base + link
            
        try:
            search = VideosSearch(link, limit=1)
            result = await search.next()
            
            if not result or not result.get("result"):
                # Return dummy data to prevent bot from crashing
                # This allows the download() function to still try its luck
                return "Unknown Title", "00:00", 0, "https://telegra.ph/file/default.jpg", "video_id"

            res = result["result"][0]
            title = res.get("title", "Music")
            duration_min = res.get("duration", "0:00")
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res.get("id")
            
            # Use 0 if time_to_seconds fails
            try:
                duration_sec = int(time_to_seconds(duration_min))
            except:
                duration_sec = 0
                
            return title, duration_min, duration_sec, thumbnail, vidid
            
        except Exception as e:
            print(f"Details Error: {e}")
            # Fallback data so the process doesn't stop
            return "YouTube Audio", "00:00", 0, "https://telegra.ph/file/default.jpg", "id"

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

        if songaudio or songvideo or video:
            await mystic.edit_text("🔄 **Processing via Private API...**")
            file_path = await download_song(link)
            if file_path:
                return file_path
            else:
                await mystic.edit_text("❌ **API Failed to provide file.**")
                return None
        return None
            
