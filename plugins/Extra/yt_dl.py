from __future__ import unicode_literals

import os, requests, asyncio, math, time, wget
from pyrogram import filters, Client
from pyrogram.types import Message
from info import CHNL_LNK
from youtube_search import YoutubeSearch
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

# Function to load cookies from the cookies.json file
def load_cookies(cookies_path="https://github.com/Partik1165/UMESH-BOT/blob/6f3ea46d1bbc47e9a60992bc72ffbe78dac93b23/cookies.json"):
    if os.path.exists(cookies_path):
        with open(cookies_path, "r") as f:
            cookies = json.load(f)
        print("Cookies loaded successfully.")
        return cookies
    else:
        raise FileNotFoundError(f"Cookies file {cookies_path} not found.")

# Function to download the video or audio using cookies for authentication
def download_media_with_cookies(url, cookies_path="cookies.json", audio_only=False):
    cookies = load_cookies(cookies_path)
    
    ydl_opts = {
        "cookiefile": cookies_path,  # Use the cookies file for authentication
        "quiet": False,  # Enable verbosity to see logs
        "writeinfojson": True,  # Write metadata to a .json file
        "outtmpl": "%(title)s.%(ext)s",  # Output file name format
        "postprocessors": [],  # Default postprocessors
        "format": "bestaudio/best" if audio_only else "best",  # Download audio only if requested
        "geo_bypass": True,  # To bypass geo-restrictions
        "nocheckcertificate": True,  # To ignore SSL certificate errors
    }

    if audio_only:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegAudioConvertor",  # Converts to the best audio format available
            "preferredformat": "mp3",  # Converts the audio to MP3
        }]
        ydl_opts["format"] = "bestaudio/best"

    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Start downloading the video or audio
            ydl.download([url])
        except Exception as e:
            print(f"Error downloading video: {str(e)}")

# Function to extract the video URL or search query from the user's message
def get_video_url(message):
    text = message.strip()
    if text.startswith("http"):
        return text
    else:
        return f"https://www.youtube.com/results?search_query={message}"

# Function to get video information (metadata)
def get_video_info(url, cookies_path="cookies.json"):
    cookies = load_cookies(cookies_path)
    ydl_opts = {
        "cookiefile": cookies_path,
        "quiet": True,
        "writeinfojson": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            return info_dict
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")
            return None

# Function to save video metadata to a JSON file
def save_metadata_to_json(info_dict, filename="video_metadata.json"):
    with open(filename, 'w') as f:
        json.dump(info_dict, f, indent=4)
    print(f"Metadata saved to {filename}.")

# The main bot code using Pyrogram
async def rate_limit_retry(func, *args, **kwargs):
    """Helper function to retry a function after a flood wait."""
    while True:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Check if error is related to flood wait
            if "FLOOD_WAIT" in str(e):
                wait_time = int(str(e).split()[-1])  # Get the wait time from error
                print(f"Rate-limited, retrying after {wait_time} seconds.")
                await asyncio.sleep(wait_time + 1)  # Wait for the specified time
            else:
                raise e  # Raise other exceptions

@Client.on_message(filters.command(['song', 'mp3']) & filters.private)
async def song(client, message):
    user_id = message.from_user.id 
    user_name = message.from_user.first_name 
    rpk = "["+user_name+"](tg://user?id="+str(user_id)+")"
    
    query = ' '.join(message.command[1:])
    print(f"Searching for song: {query}")
    
    m = await message.reply(f"**Searching your song...!\n{query}**")
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f'thumb_{title}.jpg'
        
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, 'wb').write(thumb.content)
        
        performer = "[NETWORKS™]"
        duration = results[0]["duration"]
        
    except Exception as e:
        print(str(e))
        return await m.edit("Example: /song vaa vaathi song")
    
    await m.edit("**Downloading your song...!**")
    
    try:
        # Downloading using yt-dlp
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        
        # Converting duration to seconds
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        
        cap = f"**BY›› [UPDATE]({CHNL_LNK})**"
        
        await rate_limit_retry(client.send_audio, message.chat.id,
            audio=open(audio_file, "rb"),
            caption=cap,
            quote=False,
            title=title,
            duration=dur,
            performer=performer,
            thumb=thumb_name
        )
        
        await m.delete()

    except Exception as e:
        await m.edit("**🚫 Error downloading the song 🚫**")
        print(e)
    
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)


@Client.on_message(filters.command(["video", "mp4"]))
async def vsong(client, message: Message):
    urlissed = get_text(message)
    pablo = await client.send_message(message.chat.id, f"**𝙵𝙸𝙽𝙳𝙸𝙽𝙶 𝚈𝙾𝚄𝚁 𝚅𝙸𝙳𝙴𝙾** `{urlissed}`")
    
    if not urlissed:
        return await pablo.edit("Example: /video Your video link")     
    
    search = SearchVideos(f"{urlissed}", offset=1, mode="dict", max_results=1)
    mi = search.result()
    mio = mi["search_result"]
    mo = mio[0]["link"]
    thum = mio[0]["title"]
    fridayz = mio[0]["id"]
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    
    try:
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)
    except Exception as e:
        return await pablo.edit_text(f"**𝙳𝚘𝚠𝚗𝚕𝚘𝚊𝚍 𝙵𝚊𝚒𝚕𝚎𝚍 𝙿𝚕𝚎𝚊𝚜𝚎 𝚃𝚛𝚢 𝙰𝚐𝚊𝚒𝚗..♥️** \n**Error :** `{str(e)}`")       
    
    file_stark = f"{ytdl_data['id']}.mp4"
    capy = f"""**𝚃𝙸𝚃𝙻𝙴 :** [{thum}]({mo})\n**𝚁𝙴𝚀𝚄𝙴𝚂𝚃𝙴𝙳 𝙱𝚈 :** {message.from_user.mention}"""
    
    # Here, ensure consistent indentation
    await rate_limit_retry(client.send_video, message.chat.id,
        video=open(file_stark, "rb"),
        duration=int(ytdl_data["duration"]),
        file_name=str(ytdl_data["title"]),
        thumb=sedlyf,
        caption=capy,
        supports_streaming=True,        
        reply_to_message_id=message.id
    )
    
    await pablo.delete()
    
    # Clean up files
    for files in (sedlyf, file_stark):
        if files and os.path.exists(files):
            os.remove(files)
