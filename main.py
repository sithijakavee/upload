import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
from database import DB
import mysql.connector
import uuid
from datetime import datetime
import json


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/top")
def read_root(count: int = None, sortby: str = ""):
    if sortby == "":
        html_text = requests.get(f'https://hqporner.com/top').text
    elif sortby == "month":
        html_text = requests.get(f'https://hqporner.com/top/month').text
    elif sortby == "week":
        html_text = requests.get(f'https://hqporner.com/top/week').text
    soup = BeautifulSoup(html_text, 'html.parser')
    videos = soup.find_all('div', class_="6u")
    data = []
    id = 0
    for video in videos:
        if count != None:
            if count == 0:
                break
            else:
                image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
                image = image.replace('"', "")

                link = video.find("a", class_="image")['href']
                link = link.replace('/hdporn/', '').replace('.html', '')
                title = (video.find("h3", class_="meta-data-title")
                         ).find("a").text
                time = video.find(
                    "span", class_="icon fa-clock-o meta-data").text
                case = {"id": id, 'link': link, 'image': image,
                        "title": title, "duration": time}
                data.append(case)
                id += 1
            count = count - 1

        else:
            image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
            image = image.replace('"', "")

            link = video.find("a", class_="image")['href']
            link = link.replace('/hdporn/', '').replace('.html', '')
            title = (video.find("h3", class_="meta-data-title")).find("a").text
            time = video.find("span", class_="icon fa-clock-o meta-data").text
            case = {"id": id, 'link': link, 'image': image,
                    "title": title, "duration": time}

            db = DB.connect()
            cursor = db.cursor()
            sql = "insert into videos (video_id, link, image, title, duration) values(%s,%s,%s,%s,%s)"
            val = (id, link, image, title, time)
            cursor.execute(sql, val)
            db.commit()
            print(cursor.rowcount, "record inserted.")

            data.append(case)
            id += 1
    return (data)


@app.get("/")
def read_root(count: int = None):
    db = DB.connect()
    page = 277
    while True:
        html_text = requests.get(f'https://hqporner.com/hdporn/{page}').text
        soup = BeautifulSoup(html_text, 'html.parser')
        videos = soup.find_all('div', class_="6u")
        if videos == []:
            break
        else:
            data = []
            id = 0
            for video in videos:
                if count != None:
                    if count == 0:
                        break
                    else:
                        image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
                        image = image.replace('"', "")
                        link = video.find("a", class_="image")['href']
                        link = link.replace(
                            '/hdporn/', '').replace('.html', '')
                        title = (video.find(
                            "h3", class_="meta-data-title")).find("a").text
                        time = video.find(
                            "span", class_="icon fa-clock-o meta-data").text
                        case = {"id": id, 'link': link, 'image': image,
                                "title": title, "duration": time}
                        data.append(case)
                        id += 1
                    count = count - 1
                else:
                    image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
                    image = image.replace('"', "")
                    link = video.find("a", class_="image")['href']
                    link = link.replace('/hdporn/', '').replace('.html', '')
                    html_text = requests.get(f'https://hqporner.com/hdporn/{link}.html').text
                    soup = BeautifulSoup(html_text, 'html.parser')
                    a_tags = soup.find_all('a', class_='tag-link click-trigger')
                    star_li = soup.find('li', class_='icon fa-star-o')
                    tags = []
                    for tag in a_tags:
                        tags.append(tag.text)
                    if star_li:
                        stars_a = star_li.find_all('a', class_='click-trigger')
                        stars = []     
                        for star in stars_a:
                            stars.append(star.text)
                            tags.append(star.text)    
                    else:
                        stars = []
                    
                    title = (video.find("h3", class_="meta-data-title")
                             ).find("a").text
                    duration = video.find(
                        "span", class_="icon fa-clock-o meta-data").text
                    now = datetime.now()
 
                    time = now.strftime("%d/%m/%Y %H:%M:%S")

                    case = {"id": id, 'link': link, 'image': image,
                            "title": title, "duration": time}

                    
                    cursor = db.cursor()
                    
                    sql = "insert ignore into videos (video_id, link, image, title, duration, stars, tags) values(%s,%s,%s,%s,%s,%s,%s)"
                    video_id = str(uuid.uuid1())
                    val = (video_id, link, image, title, duration, json.dumps(stars), json.dumps(tags))
                    cursor.execute(sql, val)
                    db.commit()
                    print(cursor.rowcount, "record inserted.")

                    data.append(case)
                    id += 1
        page += 1
    return (data)

@app.get("/search")
def read_root(query: str):
    html_text = requests.get(f'https://hqporner.com/?q={query}').text
    soup = BeautifulSoup(html_text, 'html.parser')
    videos = soup.find_all('div', class_="6u")
    data = []
    id = 0
    for video in videos:
        image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
        image = image.replace('"', "")
        l = len(image)
        last_2 = image[l - 2:]
        if last_2 == "jp":
            image = image.replace("jp", "jpg")
        link = video.find("a", class_="image")['href']
        link = link.replace('/hdporn/', '').replace('.html', '')
        title = (video.find("h3", class_="meta-data-title")).find("a").text
        time = video.find("span", class_="icon fa-clock-o meta-data").text
        case = {"id": id, 'link': link, 'image': image,
                "title": title, "duration": time}
        data.append(case)
        id += 1

    return (data)


@app.get("/categories")
def categories():
    html_text = requests.get('https://hqporner.com/categories').text
    soup = BeautifulSoup(html_text, 'lxml')
    atags = soup.find_all('a', class_="image featured atfib")
    title = soup.find_all('h3')
    data = []
    id = 0

    for atag in atags:
        link = atag['href']
        link = link.replace("/category/", "")
        image = atag.find("img")['src']
        splitted = link.split("/")
        title = splitted[-1].replace("-", " ")
        case = {"id": id, 'link': link, 'image': image, "title": title}
        data.append(case)
        id += 1

    return data


@app.get("/category")
def category(c: str):
    html_text = requests.get(f'https://hqporner.com/category/{c}').text
    soup = BeautifulSoup(html_text, 'lxml')
    videos = soup.find_all('div', class_="6u")
    data = []
    id = 0
    for video in videos:
        image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
        image = image.replace('"', "")
        l = len(image)
        last_2 = image[l - 2:]
        if last_2 == "jp":
            image = image.replace("jp", "jpg")
        link = video.find("a", class_="image")['href']
        link = link.replace('/hdporn/', '').replace('.html', '')
        title = (video.find("h3", class_="meta-data-title")).find("a").text
        time = video.find("span", class_="icon fa-clock-o meta-data").text
        case = {"id": id, 'link': link, 'image': image,
                "title": title, "duration": time}
        data.append(case)
        id += 1

    return data


@app.get("/video")
def video(vu: str):

    html_text = requests.get(f'https://hqporner.com/hdporn/{vu}.html').text
    soup = BeautifulSoup(html_text, 'lxml')
    div = soup.find('div', id='playerWrapper')
    title = soup.find('h1', class_='main-h1').text
    video = f'''https:{div.find('iframe')['src']}'''
    date = soup.find('li', class_='icon fa-calendar').text
    time = soup.find('li', class_='icon fa-clock-o').text
    star_li = soup.find('li', class_='icon fa-star-o')
    stars_a = star_li.find_all('a', class_='click-trigger')
    stars = []
    stars_link = []
    for star in stars_a:
        stars.append(star.text)
        # stars_link = stars_link.replace("/actress/", "")

        stars_link.append(star['href'].replace("/actress/", ""))

    return [{"id": "0", 'link': video, "title": title, "date": date, "time": time, "stars": stars, "stars_link": stars_link}]


@app.get("/stars")
def stars(actress: str = ""):
    html_text = requests.get(f'https://hqporner.com/actress/{actress}').text
    soup = BeautifulSoup(html_text, 'lxml')
    videos = soup.find_all('div', class_="6u")
    data = []
    id = 0
    for video in videos:
        image = f"""https:{video.find('div', class_="w403px")['onmouseleave'].replace("defaultImage", "").replace("(", "").replace(")", "")[1:-15]}"""
        image = image.replace('"', "")
        l = len(image)
        last_2 = image[l - 2:]
        if last_2 == "jp":
            image = image.replace("jp", "jpg")
        link = video.find("a", class_="image")['href']
        link = link.replace('/hdporn/', '').replace('.html', '')
        title = (video.find("h3", class_="meta-data-title")).find("a").text
        time = video.find("span", class_="icon fa-clock-o meta-data").text
        case = {"id": id, 'link': link, 'image': image,
                "title": title, "duration": time}
        data.append(case)
        id += 1

    return data


@app.get("/girls")
def girls():
    html_text = requests.get('https://hqporner.com/girls').text
    soup = BeautifulSoup(html_text, 'lxml')
    atags = soup.find_all('a', class_="image featured atfib")
    title = soup.find_all('h3')
    data = []
    id = 0

    for atag in atags:
        link = atag['href'].replace("/actress/", "")
        image = atag.find("img")['src']
        splitted = link.split("/")
        title = splitted[-1].replace("-", " ")
        case = {"id": id, 'link': link, 'image': image, "title": title}
        data.append(case)
        id += 1

    return data
