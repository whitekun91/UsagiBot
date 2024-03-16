import random
import urllib
import urllib.request
from urllib.request import Request
import discord
import bs4

def maesil_picture(bucket):
    embed = discord.Embed(color=0x00ff00)
    rand = random.randrange(1, 178)
    if rand == 29:
        image_bucket = bucket.blob('매실이/' + str(rand) + '.gif')
    else:
        image_bucket = bucket.blob('매실이/' + str(rand) + '.jpg')
    image_bucket.make_public()
    embed.set_image(url=image_bucket.public_url)
    return embed


def weather_information(message):
    learn = message.content.split(" ")
    location = learn[1]
    enc_location = urllib.parse.quote(location + '날씨')
    hdr = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=1&ie=utf8&query=' + enc_location
    req = Request(url, headers=hdr)
    html = urllib.request.urlopen(req)
    bsObj = bs4.BeautifulSoup(html, "html.parser")
    todayBase = bsObj.find('div', {'class': 'main_info'})

    todayTemp1 = todayBase.find('span', {'class': 'todaytemp'})
    todayTemp = todayTemp1.text.strip()  # 온도

    todayValueBase = todayBase.find('ul', {'class': 'info_list'})
    todayValue2 = todayValueBase.find('p', {'class': 'cast_txt'})
    todayValue = todayValue2.text.strip()  # 밝음,어제보다 ?도 높거나 낮음을 나타내줌

    todayFeelingTemp1 = todayValueBase.find('span', {'class': 'sensible'})
    todayFeelingTemp = todayFeelingTemp1.text.strip()  # 체감온도

    todayMiseaMongi1 = bsObj.find('div', {'class': 'sub_info'})
    todayMiseaMongi2 = todayMiseaMongi1.find('div', {'class': 'detail_box'})
    todayMiseaMongi3 = todayMiseaMongi2.find('dd')
    todayMiseaMongi = todayMiseaMongi3.text  # 미세먼지

    tomorrowBase = bsObj.find('div', {'class': 'table_info weekly _weeklyWeather'})
    tomorrowTemp1 = tomorrowBase.find('li', {'class': 'date_info'})
    tomorrowTemp2 = tomorrowTemp1.find('dl')
    tomorrowTemp3 = tomorrowTemp2.find('dd')
    tomorrowTemp = tomorrowTemp3.text.strip()  # 오늘 오전,오후온도

    tomorrowAreaBase = bsObj.find('div', {'class': 'tomorrow_area'})
    tomorrowMoring1 = tomorrowAreaBase.find('div', {'class': 'main_info morning_box'})
    tomorrowMoring2 = tomorrowMoring1.find('span', {'class': 'todaytemp'})
    tomorrowMoring = tomorrowMoring2.text.strip()  # 내일 오전 온도

    tomorrowValue1 = tomorrowMoring1.find('div', {'class': 'info_data'})
    tomorrowValue = tomorrowValue1.text.strip()  # 내일 오전 날씨상태, 미세먼지 상태

    tomorrowAreaBase = bsObj.find('div', {'class': 'tomorrow_area'})
    tomorrowAllFind = tomorrowAreaBase.find_all('div', {'class': 'main_info morning_box'})
    tomorrowAfter1 = tomorrowAllFind[1]
    tomorrowAfter2 = tomorrowAfter1.find('p', {'class': 'info_temperature'})
    tomorrowAfter3 = tomorrowAfter2.find('span', {'class': 'todaytemp'})
    tomorrowAfterTemp = tomorrowAfter3.text.strip()  # 내일 오후 온도

    tomorrowAfterValue1 = tomorrowAfter1.find('div', {'class': 'info_data'})
    tomorrowAfterValue = tomorrowAfterValue1.text.strip()

    embed = discord.Embed(
        title=learn[1] + ' 날씨 정보',
        description=learn[1] + '날씨 정보입니다.',
        colour=discord.Colour.gold()
    )

    embed.add_field(name='현재온도', value=todayTemp + '˚', inline=True)  # 현재온도
    embed.add_field(name='체감온도', value=todayFeelingTemp, inline=True)  # 체감온도
    embed.add_field(name='현재상태', value=todayValue, inline=True)  # 밝음,어제보다 ?도 높거나 낮음을 나타내줌
    embed.add_field(name='현재 미세먼지 상태', value=todayMiseaMongi, inline=True)  # 오늘 미세먼지
    embed.add_field(name='오늘 오전/오후 날씨', value=tomorrowTemp, inline=True)  # 오늘날씨 # color=discord.Color.blue()
    return embed


def sortition(message, image_bucket):
    message_str = message.content.split(" ")
    startnum = int(message_str[1])
    endnum = int(message_str[2])

    if len(message_str) == 3:
        count = 1
    else:
        count = int(message_str[3])

    embed = discord.Embed(title='추첨 결과', color=0x00ff00)
    embed.set_thumbnail(url=image_bucket.public_url)
    ranlist = [i for i in range(startnum, endnum + 1)]

    result = random.sample(ranlist, count)
    result.sort()

    for i in range(count):
        embed.add_field(name="당첨번호", value=result[i], inline=True)
    return embed


def lottery(bucket):
    image_bucket = bucket.blob('etc_image/rabbit.png')
    image_bucket.make_public()

    embed = discord.Embed(title='로또 결과', color=0x00ff00)
    embed.set_thumbnail(url=image_bucket.public_url)

    ranlist = [i for i in range(1, 46)]
    result = random.sample(ranlist, 6)
    result.sort()
    for i in range(6):
        embed.add_field(name="당첨번호", value=result[i], inline=True)
    return embed


def goldsaucer():
    embed = discord.Embed(title='이번주 골드소서 복권번호', color=0x00ff00)
    for i in range(3):
        ranlist = [i for i in range(1, 10)]
        result = []
        for j in range(4):
            sampling = random.sample(ranlist, 1)
            result.append(sampling[0])
        embed.add_field(name="{} 번째 복권".format(i + 1), value=result, inline=True)
    return embed