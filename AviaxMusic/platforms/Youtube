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

# --- HELPER: API DOWNLOADER ---

async def download_song(link: str):
    """Downloads audio using your custom API"""
    if "&" in link:
        link = link.split("&")[0]
    
    video_id = link.split('v=')[-1].split('/')[-1]
    download_folder = "downloads"
    os.makedirs(download_folder, exist_ok=True)
    file_path = os.path.join(download_folder, f"{video_id}.mp3")

    if os.path.exists(file_path):
        return file_path
        
    api_url = f"http://152.42.187.207:8000/audio?url={link}"
    
    async with aiohttp.ClientSession() as session:
        try:
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
        except Exception:
            return None
    return None

# --- MAIN YOUTUBE CLASS ---

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.listbase = "https://youtube.com/playlist?list="

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message: Message) -> Union[str, None]:
        messages = [message]
        if message.reply_to_message:
            messages.append(message.reply_to_message)
        for msg in messages:
            text = msg.text or msg.caption
            if not text: continue
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        try:
            search = VideosSearch(link, limit=1)
            resp = await search.next()
            res = resp["result"][0]
            title = res["title"]
            duration_min = res["duration"]
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            vidid = res["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
            return title, duration_min, duration_sec, thumbnail, vidid
        except:
            # Fallback data to prevent "Failed to Process Query"
            vid_id = link.split('v=')[-1].split('/')[-1].split('?')[0]
            return "YouTube Audio", "04:00", 240, "https://telegra.ph/file/default.jpg", vid_id

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid: link = self.listbase + link
        try:
            plist = Playlist(link)
            while plist.hasMoreVideos:
                await plist.getNextVideos()
                if len(plist.videos) >= limit: break
            return [v['id'] for v in plist.videos[:limit]]
        except:
            return []

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid: link = self.base + link
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        res = result[query_type]
        return res["title"], res["duration"], res["thumbnails"][0]["url"].split("?")[0], res["id"]

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
        if videoid: link = self.base + link
        
        await mystic.edit_text("📥 **Fetching via Custom API Server...**")
        file_path = await download_song(link)
        
        if file_path:
            return file_path
        
        await mystic.edit_text("❌ **API Download Failed.**")
        return None
        
