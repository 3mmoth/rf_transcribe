
from timestamps import extract_chapters
from get_download_url import get_download_url
from extract_sound import extract_wav_from_mp4


url = "https://regionostergotland.screen9.tv/media/t4fJlbzqCkayMBqqc30Xzw/Regionfullm%C3%A4ktige%20%C3%96sterg%C3%B6tland%202025-04-24"
# chapters = extract_chapters(url)
download_url = get_download_url(url)
print("✅ Hittade download-URL:", download_url)
extract_wav_from_mp4(download_url, "output.wav")
print("✅ Ljud extraherat till output.wav")
# for chapter in chapters:
#     print(f"{chapter['formatted_time']} - {chapter['title']}")