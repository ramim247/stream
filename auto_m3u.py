import os
import requests
import re

NDUS_COOKIE = os.getenv('NDUS_COOKIE')
TMDB_API_KEY = "49fb1307dfa80e6b65c947be30a399e8"

def clean_movie_name(filename):
    # ফাইলের নাম থেকে এক্সটেনশন এবং অতিরিক্ত রেজ্যুলেশন ট্যাগ সরিয়ে পরিষ্কার নাম বের করা
    name = re.sub(r'\.\w+$', '', filename) # .mp4, .mkv ইত্যাদি রিমোভ
    name = re.sub(r'(1080p|720p|4K|HDRip|WEB-DL|BluRay|BRRip|x264|x265|HEVC).*', '', name, flags=re.IGNORECASE)
    name = name.replace('.', ' ').replace('_', ' ').strip()
    return name

def get_tmdb_poster(movie_title):
    try:
        clean_title = clean_movie_name(movie_title)
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(clean_title)}"
        response = requests.get(url)
        data = response.json()
        
        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        print(f"Poster fetch error for {movie_title}: {e}")
    
    # পোস্টার না পেলে ডিফল্ট ইমেজ
    return "https://via.placeholder.com/300x450.png?text=Movie"

def fetch_terabox_movies():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': f'ndus={NDUS_COOKIE};'
    }
    
    api_url = "https://www.terabox.com/api/list?dir=%2F&page=1&num=100"
    m3u_content = "#EXTM3U\n"
    
    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        
        if data.get('errno') == 0:
            file_list = data.get('list', [])
            for item in file_list:
                if item.get('category') == 1:  # ভিডিও ফাইল হলে
                    filename = item.get('server_filename', 'Movie')
                    dlink = item.get('dlink', '')
                    
                    # TMDB থেকে আসল পোস্টার ফেচ করা
                    poster_url = get_tmdb_poster(filename)
                    group = "Terabox Movies"
                    
                    m3u_content += f'#EXTINF:-1 tvg-name="{filename}" tvg-logo="{poster_url}" group-title="{group}",{filename}\n'
                    m3u_content += f'{dlink}\n'
                    
            with open("playlist.m3u", "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print("[✔] Auto M3U with TMDB Posters Generated Successfully!")
        else:
            print(f"[❌] Error fetching Terabox data: {data.get('errno')}")
            
    except Exception as e:
        print(f"[❌] Exception occurred: {e}")

if __name__ == "__main__":
    if NDUS_COOKIE:
        fetch_terabox_movies()
    else:
        print("[❌] NDUS_COOKIE secret is missing!")
