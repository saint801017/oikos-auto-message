import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ✅ 1) 말씀산책 최신 정보 가져오기
def get_latest_bible_stroll():
    url = "https://www.youngnak.net/rev_kws_bible_stroll/"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # 유튜브 링크
    iframe = soup.find("iframe")
    youtube_link = None
    if iframe:
        src = iframe.get("src")
        if "/embed/" in src:
            video_id = src.split("/embed/")[1].split("?")[0]
            youtube_link = f"https://www.youtube.com/watch?v={video_id}"
        else:
            youtube_link = src

    # 자세히 보기 링크
    detail_link = None
    for a in soup.find_all("a"):
        if "자세히 보기" in a.get_text(strip=True):
            detail_link = a.get("href")
            break

    if detail_link and detail_link.startswith("/"):
        detail_link = "https://www.youngnak.net" + detail_link

    return youtube_link, detail_link


# ✅ 2) 말씀산책 상세 페이지에서 본문 추출
def extract_bible_from_detail(detail_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(detail_url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # 제목
    title_tag = soup.select_one("div.avia_textblock p strong")
    bible_title = None
    if title_tag:
        bible_title = title_tag.parent.get_text(strip=True)

    # 절별 본문
    verses = []
    table = soup.select_one("table.vod_phrase")
    if table:
        for tr in table.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                verses.append(f"{th.get_text(strip=True)} : {td.get_text(strip=True)}")

    return bible_title, verses


# ✅ 3) 오디오바이블 오늘의 말씀 제목
def get_today_audio_bible_title():
    url = "http://www.youngnak.net/bible-hymn/audiobible/"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.select_one("h3.audio_bible_tit b")
    if title_tag:
        return title_tag.get_text(strip=True)

    return None


# ✅ 4) 오이코스 새벽기도회 최신 정보
def get_latest_oikos_morning():
    url = "https://www.youngnak.net/oikos_morning/"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    # 유튜브 링크
    iframe = soup.find("iframe")
    youtube_link = None
    if iframe:
        src = iframe.get("src")
        if "/embed/" in src:
            video_id = src.split("/embed/")[1].split("?")[0]
            youtube_link = f"https://www.youtube.com/watch?v={video_id}"
        else:
            youtube_link = src

    # 자세히 보기 링크
    detail_link = None
    for a in soup.find_all("a"):
        if "자세히 보기" in a.get_text(strip=True):
            detail_link = a.get("href")
            break

    if detail_link and detail_link.startswith("/"):
        detail_link = "https://www.youngnak.net" + detail_link

    return youtube_link, detail_link


# ✅ 5) 오이코스 상세 페이지에서 묵상 본문 추출
def extract_oikos_bible(detail_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(detail_url, headers=headers)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    bible_title = None
    for p in soup.find_all("p"):
        # br → 줄바꿈
        for br in p.find_all("br"):
            br.replace_with("\n")

        text = p.get_text("\n", strip=True)
        lines = text.split("\n")

        for i, line in enumerate(lines):
            if "묵상을 위한 본문" in line:
                # 다음 줄이 성경 본문 제목
                if i + 1 < len(lines):
                    bible_title = line.replace("묵상을 위한 본문 /", "").strip() + " " + lines[i+1].strip()
                else:
                    bible_title = line.replace("묵상을 위한 본문 /", "").strip()
                break

        if bible_title:
            break

    # 절별 본문
    verses = []
    table = soup.select_one("table.vod_phrase")
    if table:
        for tr in table.find_all("tr"):
            th = tr.find("th")
            td = tr.find("td")
            if th and td:
                verses.append(f"{th.get_text(strip=True)} : {td.get_text(strip=True)}")

    return bible_title, verses


# ✅ 6) 전체 메시지 조립
def build_message():
    # ✅ 한글 요일 변환
    weekday_map = {
        "Mon": "월",
        "Tue": "화",
        "Wed": "수",
        "Thu": "목",
        "Fri": "금",
        "Sat": "토",
        "Sun": "일"
    }

    today_raw = datetime.now()
    weekday_eng = today_raw.strftime("%a")
    weekday_kor = weekday_map[weekday_eng]
    today = today_raw.strftime(f"%Y년 %m월 %d일({weekday_kor})")

    # ✅ 말씀산책
    stroll_youtube, stroll_detail = get_latest_bible_stroll()
    stroll_title, stroll_verses = extract_bible_from_detail(stroll_detail)
    clean_stroll_title = stroll_title.replace("묵상을 위한 본문 /", "").strip()

    # ✅ 오디오바이블
    audio_title = get_today_audio_bible_title()

    # ✅ 오이코스
    oikos_youtube, oikos_detail = get_latest_oikos_morning()
    oikos_title, oikos_verses = extract_oikos_bible(oikos_detail)

    message = f"""▪영락 오이코스▪
{today}

📖 김운성목사와 함께하는 말씀산책
{stroll_youtube}

묵상을 위한 본문 : {clean_stroll_title}

"""

    for v in stroll_verses:
        message += v + "\n"

    message += f"""
📗 오늘의 성경 읽기 {audio_title}
http://www.youngnak.net/bible-hymn/audiobible/

🌞오이코스 새벽기도회
{oikos_youtube}

묵상을 위한 본문 : {oikos_title}

"""

    for v in oikos_verses:
        message += v + "\n"

    return message


# ✅ 실행
if __name__ == "__main__":
    print(build_message())
