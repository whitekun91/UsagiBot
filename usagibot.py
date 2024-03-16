import ssl

import discord
import random

from function import main_function

'''디스코드 봇 : 매실이'''
client = discord.Client()
token = ''

'''디스코드 봇 : '''
client_2 = discord.Client()
member_list = dict()

'''매실이봇 초기화 코드'''
# @app.route('/')
@client.event
async def on_ready():
    print(client.user.id)
    print("ready")
    game = discord.Game("털갈이 끝나고 똥 먹기")
    await client.change_presence(status=discord.Status.online, activity=game)

'''매실이봇 명령어 코드'''
@client.event
async def on_message(message):
    '''매실이 사진 소환'''
    if message.content == '==매실':
        embed = main_function.maesil_picture(bucket)
        await message.delete(delay=20)
        await message.channel.send(embed=embed)

    '''날씨'''
    if message.content.startswith("==날씨"):
        try:
            embed = main_function.weather_information(message)
            await message.channel.send(embed=embed)
        except:
            pass
    
    ''' 추첨번호 만들기 '''
    if message.content.startswith('==추첨'):
        image_bucket = bucket.blob('etc_image/rabbit.png')
        image_bucket.make_public()
        try:
            embed = main_function.sortition(message, image_bucket)
            await message.channel.send(embed=embed)
        except:
            pass

    '''랜덤 숫자 6개 비복원 추출'''
    if message.content == '==로또':
        embed = main_function.lottery(bucket)
        await message.channel.send(embed=embed)

    '''랜덤 숫자 4개 복원 추출 연속 3번하기'''
    if message.content == '==골소':
        embed = main_function.goldsaucer()
        await message.channel.send(embed=embed)

    ''' 추첨 리스트 삽입 / 삭제 / 조회 코드 '''
    if message.content.startswith('==추첨업'):
        message_str = message.content.split(" ")
        if len(message_str) == 1:
            if not member_list:
                embed = discord.Embed(title='추첨업리스트', color=0x00ff00)
                embed.add_field(name="명단리스트", value='추가된 명단이 없습니다.', inline=True)
                await message.channel.send(embed=embed)
            else:
                try:
                    embed = discord.Embed(title='추첨업리스트', color=0x00ff00)
                    playstr = "\n\n"
                    for key, value in dict(sorted(member_list.items())).items():
                        playstr += str(key) + " : " + value + "\n"
                    embed.add_field(name="명단리스트", value=playstr, inline=True)
                    await message.channel.send(embed=embed)
                except:
                    pass
        else:
            if message_str[1] == '삭제':
                if message.author.name == 'White' or message.author.name == 'Ranko Kanzaki':
                    try:
                        if len(message_str) == 2:
                            await message.channel.send('숫자 입력해~~똥똥똥')
                        else:
                            num_index = int(message_str[2])
                            if num_index <= 0:
                                await message.channel.send('다시 입력해~~똥똥똥')
                            else:
                                del member_list[num_index]
                                for j in range(1, len(list(member_list.keys())) + 1):
                                    member_list[j] = list(member_list.values())[j - 1]
                                del member_list[len(list(member_list.keys()))]
                    except:
                        pass
            elif message_str[1] == '전체삭제':
                if message.author.name == 'White' or message.author.name == 'Ranko Kanzaki':
                    member_list.clear()
            else:
                try:
                    await message.delete()
                    mention_name = message_str[1]
                    key = len(list(member_list.keys())) + 1
                    member_list[key] = mention_name
                    embed = discord.Embed(title='추첨업리스트', color=0x00ff00)
                    playstr = "\n\n"
                    for key, value in dict(sorted(member_list.items())).items():
                        playstr += str(key) + " : " + value + "\n"
                    embed.add_field(name="명단리스트", value=playstr, inline=True)
                    await message.channel.send(embed=embed, delete_after=8)
                except:
                    pass

    ''' 똥겜 리스트 삽입 / 삭제 / 조회 코드 '''
    if message.content.startswith('==똥겜업'):
        message_str = message.content.split(" ")
        # 리스트 조회
        if len(message_str) == 1:
            try:
                embed = discord.Embed(title='똥겜업리스트', color=0x00ff00)
                users_ref = db.collection(u'ddong_game')
                docs = users_ref.stream()
                playstr = "\n\n"
                for doc in docs:
                    playstr += str(doc.id) + " : " + u'{}'.format(doc.to_dict()['name']) + "\n"
                embed.add_field(name="똥겜리스트", value=playstr, inline=True)
                await message.channel.send(embed=embed)
            except:
                pass

        # 삽입 및 삭제
        else:
            # 삭제
            if message_str[1] == '삭제':
                if len(message_str) == 2:
                    await message.channel.send('알파벳 입력해~~똥똥똥')
                else:
                    try:
                        num_index = int(ord(message_str[2]) - 96)
                        if num_index <= 0 or num_index > len(list(db.collection(u'ddong_game').stream())):
                            await message.channel.send('다시 입력해~~똥똥똥')
                        else:
                            if len(list(db.collection(u'ddong_game').stream())) == num_index:
                                db.collection(u'ddong_game').document(u'{}'.format(chr(ord('`') + num_index))).delete()
                            else:
                                db.collection(u'ddong_game').document(u'{}'.format(chr(ord('`') + num_index))).delete()
                                users_ref = db.collection(u'ddong_game')
                                docs = users_ref.stream()
                                for doc in docs:
                                    if int(ord(doc.id) - 96) > num_index:
                                        game_name = doc.to_dict()['name']
                                        data = {u'name': u'{}'.format(game_name)}
                                        db.collection(u'ddong_game').document(u'{}'.format(doc.id)).delete()
                                        db.collection(u'ddong_game').document(u'{}'.format(chr(ord(doc.id) - 1))).set(
                                            data)
                    except:
                        pass
            # 삽입
            else:
                try:
                    mention_name = message_str[1]
                    users_ref = db.collection(u'ddong_game')
                    doclen = len(list(users_ref.stream()))
                    data = {u'name': mention_name}
                    db.collection(u'ddong_game').document(u'{}'.format(chr(ord('`') + doclen + 1))).set(data)
                except:
                    pass


    '''Sub 명령어'''
    if message.content == '==이마빡':
        embed = sub_function.headback(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==제리인사':
        embed = sub_function.jerry(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==제리인사총':
        embed = sub_function.jerrygun(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==관짝':
        await message.channel.send('https://www.youtube.com/watch?v=j9V78UbdzWI')

    if message.content == '==조용':
        embed = sub_function.quiet(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==인오박':
        embed = sub_function.grandzeul(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==틀':
        embed = sub_function.teulddak(bucket)
        await message.channel.send(embed=embed)

    if message.content == '==수갑':
        embed = sub_function.sugap(bucket)
        await message.channel.send(embed=embed)

    '''아오지탄광용'''
    if message.content == '==채굴':
        if message.channel.id == 710324075750228038 or message.channel.id == 710741188432494592 or message.channel.id == 613791013634310151:
            embed = discord.Embed(color=0x00ff00)
            rand = random.randrange(1, 12)
            if rand == 11:
                image_bucket = bucket.blob('mining/성공짤.jpg')
                my_name = discord.utils.get(message.guild.members, name="Ranko Kanzaki")
                embed.set_image(url=image_bucket.public_url)
                await message.channel.send("{}, 이 동무 성공했다우~~".format(my_name.mention), embed=embed)
            else:
                image_bucket = bucket.blob('mining/' + str(rand) + '.jpg')
                image_bucket.make_public()
                embed.set_image(url=image_bucket.public_url)
                await message.channel.send("날래날래 더 캐라우", embed=embed)


    '''관리자용'''
    if message.content.startswith('==환영'):
        if message.author.name == 'White Atmosphere' or message.author.name == 'Ranko Kanzaki':
            await message.channel.send('닉변 예쁘게 해주시고 좌측에 파김치 이용가이드읽고 하단에 좋아요 :thumbsup:  눌러주세요!')

    if message.content.startswith('==투표'):
        if message.author.name == 'White Atmosphere' or message.author.name == 'Ranko Kanzaki':
            vote = message.content.split(' ')
            for i in range(2, len(vote)):
                if i == 2:
                    await message.add_reaction('1️⃣')
                elif i == 3:
                    await message.add_reaction('2️⃣')
                elif i == 4:
                    await message.add_reaction('3️⃣')
                elif i == 5:
                    await message.add_reaction('4️⃣')
                elif i == 6:
                    await message.add_reaction('5️⃣')

    if message.content == '==white':
        embed = discord.Embed(color=0x00ff00)
        rand = random.randrange(1, 201)
        gacha_1 = [1, 4, 7, 15, 18, 30, 40, 50, 100, 103, 120, 130, 140, 150, 143, 160, 163, 180, 183]
        gacha_2 = [2, 5, 8, 16, 19, 55, 60, 101, 104, 141, 144, 151, 152, 161, 164, 181, 184]
        gacha_3 = [3, 6, 9, 17, 20, 25, 45, 65, 102, 105, 142, 145, 162, 165, 182, 185]
        print(rand)
        if rand in gacha_1:
            image_bucket = bucket.blob('etc_image/화이트5.jpg')
        elif rand in gacha_2:
            image_bucket = bucket.blob('etc_image/화이트4.jpg')
        elif rand in gacha_3:
            image_bucket = bucket.blob('etc_image/화이트3.jpg')
        else:
            image_bucket = bucket.blob('etc_image/화이트2.jpg')
        image_bucket.make_public()
        embed.set_image(url=image_bucket.public_url)
        await message.channel.send(embed=embed)


    if message.content == "==헬프":
        embed = discord.Embed(title="매실이봇 명령어 리스트", description='매실이봇 사용설명서', color=0x00ff56)
        embed.add_field(name="==매실", value="매실이사진", inline=True)
        embed.add_field(name="==날씨+지역", value="현재지역날씨", inline=True)
        embed.add_field(name="--------------------------------------------------------------------------------",
                        value="\u200b", inline=False)
        embed.add_field(name="==로또", value="로또번호생성", inline=True)
        embed.add_field(name="==골소", value="골드소서복권번호", inline=True)
        embed.add_field(name="==추첨 + 시작숫자 + 끝숫자 + 추첨할 숫자(없으면 1)", value="추첨번호생성", inline=True)
        embed.add_field(name="--------------------------------------------------------------------------------",
                        value="\u200b", inline=False)
        embed.add_field(name="==추첨업 + 닉네임", value="추첨대상자리스트 추가", inline=True)
        # embed.add_field(name="==추첨업 삭제 + 번호", value="추첨대상자리스트 삭제", inline=True)
        embed.add_field(name="==추첨업", value="추첨대상자리스트", inline=True)
        embed.add_field(name="--------------------------------------------------------------------------------",
                        value="\u200b", inline=False)
        embed.add_field(name="==똥겜업 + 게임이름", value="똥겜리스트 추가", inline=True)
        embed.add_field(name="==똥겜업 삭제 + 리스트번호", value="똥겜리스트 삭제", inline=True)
        embed.add_field(name="==똥겜업", value="똥겜리스트", inline=True)
        await message.delete(delay=15)
        await message.channel.send(embed=embed, delete_after=15)


    if message.content == "==헬프2":
        embed = discord.Embed(title="매실이봇 명령어 리스트", description='매실이봇 사용설명서2', color=0x00ff56)
        embed.add_field(name="==제리인사", value="제리인사", inline=True)
        embed.add_field(name="==제리인사총", value="제리인사총", inline=True)
        embed.add_field(name="==이마빡", value="이마빡", inline=True)
        embed.add_field(name="==인오박", value="인오박", inline=True)
        embed.add_field(name="==조용", value="조용히", inline=True)
        embed.add_field(name='==틀', value='라떼이즈홀스', inline=True)
        embed.add_field(name='==수갑', value='철컹철컹', inline=True)
        embed.add_field(name="==관짝", value="관짝댄스", inline=True)
        await message.delete(delay=15)
        await message.channel.send(embed=embed, delete_after=15)

    if message.content == "==헬프관리자":
        embed = discord.Embed(title="매실이봇 관리자 전용 명령어 리스트", color=0x00ff56)
        embed.add_field(name="==환영", value="Welcome", inline=True)
        embed.add_field(name="==투표+제목+1~5번까지내용", value="Vote", inline=True)        
        embed.add_field(name="--------------------------------------------------------------------------------",
                        value="\u200b", inline=False)       
        embed.add_field(name="==white", value="화이트", inline=True)
        await message.channel.send(embed=embed)


client.run(token)
