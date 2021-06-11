from discord import Emoji, Intents
from discord.ext.commands import Bot, Context
from discord_components import (
    DiscordComponents,
    Button,
    ButtonStyle,
    InteractionType,
    Select,
    Option,
)
import discord
from numpy import zeros
from copy import deepcopy
from asyncio import TimeoutError

client = Bot(command_prefix="!", intents=Intents.all())
ddb = DiscordComponents(client)


@client.event
async def on_ready():
    print("ready!")


@client.command("게임")
async def 게임(ctx: Context):
    class Board:
        def __init__(self, other=None):
            self.fields = zeros((3, 3))  # user: 1 bot: 2
            self.user = 1
            self.bot = 2
            if other:
                self.__dict__ = deepcopy(other.__dict__)

        def check_winner(self):
            def check_line_finish(line):
                if bool(line[0]) and (line[0] == line[1] == line[2]):
                    return line[0]
                else:
                    return False

            # Check horizontal
            for line in self.fields:
                res = check_line_finish(line)
                if res:
                    return res

            # Check vertical
            for i in [
                list(map(lambda line: line[0], self.fields)),
                list(map(lambda line: line[1], self.fields)),
                list(map(lambda line: line[2], self.fields)),
            ]:
                res = check_line_finish(i)
                if res:
                    return res

            # Check diagonal
            for i in [
                [self.fields[0][0], self.fields[1][1], self.fields[2][2]],
                [self.fields[0][2], self.fields[1][1], self.fields[2][0]],
            ]:
                res = check_line_finish(i)
                if res:
                    return res

            return False

        def check_tie(self):
            for line in self.fields:
                if 0 in line:
                    return False
            return True

        def move(self, x, y):
            b = Board(self)
            b.fields[x][y] = b.user
            b.user, b.bot = b.bot, b.user
            return b

        def minimax(self, player):
            if self.check_winner():
                if player:
                    return (-1, None)
                else:
                    return (1, None)
            elif self.check_tie():
                return (0, None)
            elif player:
                best = (-2, None)
                for i in range(9):
                    x, y = i // 3, i % 3
                    if not self.fields[x][y]:
                        value = self.move(x, y).minimax(not player)[0]
                        if value > best[0]:
                            best = (value, (x, y))
                return best
            else:
                best = (2, None)
                for i in range(9):
                    x, y = i // 3, i % 3
                    if not self.fields[x][y]:
                        value = self.move(x, y).minimax(not player)[0]
                        if value < best[0]:
                            best = (value, (x, y))
                return best

    game = Board()
    turn = True  # user: True bot: False

    def get_buttons():
        res = []
        _id = 0
        for line in game.fields:
            res2 = []
            for i in line:
                if not i:
                    res2.append(Button(style=ButtonStyle.gray, label=" ", id=str(_id)))
                elif i == 1:
                    res2.append(Button(style=ButtonStyle.green, label="‎", id=str(_id), emoji="⭕"))
                elif i == 2:
                    res2.append(Button(style=ButtonStyle.red, label="‎", id=str(_id), emoji="❌"))
                _id += 1
            res.append(res2)
        return res

    m = await ctx.send(f'{"당신의" if turn else "봇"} 턴이다! 아래 버튼을 클릭해! ', components=get_buttons())
    while True:
        r = game.check_winner()
        if r:
            await m.edit("너는 이겼어!" if r == 1 else "봇이 이겼어!", components=get_buttons())
            break
        turn = True
        await m.edit(f'{"당신의" if turn else "봇"} 턴이드아! 아래 버튼을 클릭해!', components=get_buttons())

        try:
            res = await client.wait_for("button_click", timeout=60)
        except TimeoutError:
            await m.edit("봇이 이겼어!ㅋㅋ", components=get_buttons())
            break

        if (res.user.id != ctx.author.id) or bool(
            game.fields[int(res.component.id) // 3][int(res.component.id) % 3]
        ):
            await res.respond(type=InteractionType.DeferredUpdateMessage)
            continue

        game = game.move(int(res.component.id) // 3, int(res.component.id) % 3)
        r = game.check_winner()

        if r:
            await res.respond(
                type=InteractionType.UpdateMessage,
                content="너가 이겼어! 짝짝" if r == 1 else "봇이 이겼어! ㅋㅎㅋㅎ",
                components=get_buttons(),
            )
            break

        turn = False

        try:
            i, j = game.minimax(True)[1]
        except TypeError:
            await res.respond(
                type=InteractionType.UpdateMessage, content=f"동점!", components=get_buttons()
            )
            break
        else:
            await res.respond(
                type=InteractionType.UpdateMessage,
                content=f'{"너의" if turn else "봇"} 턴이다! 아래 버튼을 클릭해!',
                components=get_buttons(),
            )
        game = game.move(i, j)

@client.listen()
async def on_message(message):
    if message.content.startswith("!건의"):
        author = client.get_user(int(525295194677968901))
        choice = message.content.split(" ")
        msg = message.content[4: ]
        msgsender = message.author
        msgguild = message.guild.name
        msgchannel = message.channel.name

        if msg[0:4] == "http" or msg[0:5] == "https" or msg[0:3] == "www":
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="자곱봇 건의", value="""
            건의장이 전송되지 않았습니다!
            건의장 미전송 사유: 링크 사용
            """, inline=False)
            embed.set_thumbnail(url="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FdhFXEV%2FbtqEOaCVWlv%2FxbKPxv8Mskgsvlf3jwiEIK%2Fimg.png")
            await message.channel.send(embed=embed)
        elif msg == "":
            embed = discord.Embed(color=0xff0000)
            embed.add_field(name="자곱봇 건의", value="""
            건의장이 전송되지 않았습니다!
            건의장 미전송 사유: 내용 없음
            """, inline=False)
            embed.set_thumbnail(url="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FdhFXEV%2FbtqEOaCVWlv%2FxbKPxv8Mskgsvlf3jwiEIK%2Fimg.png")
            await message.channel.send(embed=embed)
        else:
            invites = await message.channel.create_invite(destination = message.channel, xkcd = True, max_uses = 100)
            embed = discord.Embed(color=0x00ff00)
            embed.add_field(name="자곱봇 건의", value="""
            피슝! 건의장이 도착했어요!
            건의장 내용: {}
            건의한 사람: {}
            건의장을 보낸 서버: {}
            건의장을 보낸 채널: {}
            건의장을 보낸 채널 초대링크: {}
            """.format(msg, msgsender, msgguild, msgchannel, invites), inline=False)
            embed.set_thumbnail(url="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FdhFXEV%2FbtqEOaCVWlv%2FxbKPxv8Mskgsvlf3jwiEIK%2Fimg.png")
            await author.send(embed=embed)

            embed = discord.Embed(color=0x00ff00)
            embed.add_field(name="자곱봇 건의", value="""
            건의장이 정상적으로 전송되었습니다!
            건의장 내용: {}
            건의한 사람: {}
            건의장을 보낸 서버: {}
            건의장을 보낸 채널: {}
            """.format(msg, msgsender, msgguild, msgchannel), inline=False)
            embed.set_thumbnail(url="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fk.kakaocdn.net%2Fdn%2FdhFXEV%2FbtqEOaCVWlv%2FxbKPxv8Mskgsvlf3jwiEIK%2Fimg.png")
            await message.channel.send(embed=embed)
@client.command()
async def 건의(ctx, *, msg):
    print(msg)
    file = open("건의.txt", "a+")
    file.write(str("\n") + str(ctx.author) + str(":") + str(msg))
    file.close
    #await ctx.send(str(msg) + str("라고 발빠른 자곱이가 전해줄께요!"))
@client.command()
async def 건의장초기화(ctx):
    file = open("건의.txt", "w")
    file.write("")
    file.close
    await ctx.send("건의장을 초기화 했어요!")
@client.command()
async def 건의장읽기(ctx):
    file = open("건의.txt")
    await ctx.send(file.read())

client.run("ODE3OTk5NjUzNTAwNzQ3ODA2.YERriw.kOQVizWTMBp0iM-P11_BlD9TBsA")