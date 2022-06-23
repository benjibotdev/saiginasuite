# a simple bot for Saiga's Empire
# look I know this code is terrible don't judge me I'm lazy
import io
import discord
import re
import ast
import time
import random
import requests
from pixivpy3 import *
import tweepy
from tweepy import asynchronous

# saigina settings
hofthresh = 5
sbsthresh = 6

with open("resources/name_registry", "r") as f:
    names_dict = ast.literal_eval(f.read())
with open("resources/pixiv_feet_pic_link_list", "r") as f:
    img_lnk_lst = f.read().split('\n')
with open("resources/pinned_message_ids", "r") as f:
    dmid_list = f.read().split('\n')

auth_users = ["Benjibot#7111", "Grone#8036", "Saiga#0417"]
dtok = "ODYyMDgxMjA4NDQyODE0NDc0.YOTJsA.J4G32yRCuoTzEMDeMkDa4NcLtC4"
hof_id = 880896332481585173
saiga_sanct_id = 809995546009796668
saigina_playground_id = 867150686583652416

tauth = tweepy.OAuthHandler("TPu14J4NowHd0ALlrrvHOVyss", "IeQDwV9V2D5roFGomozWVXyPEDoGnXY8xB8vWBVd0Ox8NBrIji")
tauth.set_access_token("TPu14J4NowHd0ALlrrvHOVyss", "vTJJL0cO4u6ighCBfi87oP05mcgoxbI9fz6xFxnplWQpE")
tapi = tweepy.API(tauth)
saiga_twt_acct_ids = {"1108266112649740288": "LewdSaiga"}#, "1437352141539192832": "SoftSaiga"}


# discord settings
client = discord.Client()
hof = client.get_channel(hof_id)
sanct = client.get_channel(saiga_sanct_id)
plgrnd = client.get_channel(saigina_playground_id)
saigina_smug_id = "<:saigina_smug:926352839146614824>"

# pixivpy settings
ptok = "EWw3dal-w0BRZIYETcpw0uUWOBBjARdsbwEziZzeZ3Q"
api = AppPixivAPI()
api.auth(refresh_token=ptok)


@client.event
async def on_ready():
    global hof, sanct, plgrnd
    print("Logged in as " + client.user.name + "!")
    print(client.user.id)
    print('------')
    hof = client.get_channel(hof_id)
    sanct = client.get_channel(saiga_sanct_id)
    plgrnd = client.get_channel(saigina_playground_id)


@client.event
async def on_message(message):
    global img_lnk_lst
    IS_DEBUG_CHAN = "saiginas-playground" in str(message.channel)
    uauthd = str(message.author) in auth_users

    '''
    if "test" in message.content:
        print(message.channel.id)
        return
    '''
    # ignore this message if it comes from self
    if message.author == client.user:
        return

    # are you there saigina
    if message.content == "Are you there, Saigina?":
        await message.reply("Yup, I'm here!")
        return

    # TODO hello saigina protocol

    # good morning saigina protocol
    if re.compile("[Gg]ood +[Mm]orning,? +[Ss]aigina!?").search(message.content):
        if str(message.author).encode('utf-8') not in names_dict:
            await message.channel.send("Good morning!" + saigina_smug_id)
        else:
            await message.channel.send("Good morning, " + names_dict[str(message.author).encode('utf-8')] +
                                       ". " + saigina_smug_id)

    # good night saigina protocol
    if re.compile("[Gg]ood +[Nn]ight,? +[Ss]aigina\.?").search(message.content):
        if str(message.author).encode('utf-8') not in names_dict:
            await message.channel.send("Good night " + saigina_smug_id)
        else:
            await message.channel.send("Good night, " + names_dict[str(message.author).encode('utf-8')] +
                                        ". " + saigina_smug_id)
        return

    # show feet protocol
    if re.compile("[Ss][Hh][Oo][Ww].+[Ff][Ee]{2}[Tt]").search(message.content) and \
            ("Saigina" in message.content or "saigina" in message.content):
        await message.channel.send("<:saigina_foot:867580399605514240>" + saigina_smug_id)
        return

    # search for feet pics protocol
    if re.compile("[Ss]aigina,? +look +for +feet").search(message.content) \
            and ("lootbox" in message.channel.name or IS_DEBUG_CHAN):
        try:
            async with message.channel.typing():
                img_lnk_num = random.randint(0, len(img_lnk_lst))
                img_req = requests.get(img_lnk_lst[img_lnk_num], headers={'Referer': 'https://app-api.pixiv.net/'}, stream=True)
                img_file = io.BytesIO(img_req.content)
                img_file.name = "LBV2image" + str(img_lnk_num) + ".jpg"
                await message.channel.send(file=discord.File(img_file))
        except Exception as e:
            print(e)
            await message.channel.send("Sorry, something went wrong. Try again!")
        return

    pk_re = re.compile("[Ss]aigina,? +look +for +key(?:word)? +(.+)").search(message.content)
    if pk_re:
        api.auth(refresh_token=ptok)
        async with message.channel.typing():
            result = api.search_illust(pk_re.groups()[0], search_target='title_and_caption')
            try:
                if result is not None and "error" not in result:
                    if len(result["illusts"]) == 0:
                        await message.channel.send("Sorry! I didn't find any results.")
                        return
                    else:
                        img_req = requests.get(random.choice(result["illusts"])["image_urls"]["large"],
                                               headers={'Referer': 'https://app-api.pixiv.net/'}, stream=True)
                        img_file = io.BytesIO(img_req.content)
                        img_file.name = "psearch.jpg"
                        await message.channel.send(file=discord.File(img_file))
                else:
                    print(result)
                    await message.channel.send("Sorry! Something went wrong.")
            except Exception as e:
                print(e)
                await message.channel.send("Sorry! Something went wrong.")
            finally:
                return

    # search pixiv with tags protocol
    # search_target='exact_match_for_tags'
    # search_target='title_and_caption'
    ps_re = re.compile("[Ss]aigina,? +look +for +(.+)").search(message.content)
    if ps_re and ("lootbox" in str(message.channel) or IS_DEBUG_CHAN):
        api.auth(refresh_token=ptok)
        async with message.channel.typing():
            result = api.search_illust(ps_re.groups()[0])
            try:
                if result is not None and "error" not in result:
                    if len(result["illusts"]) == 0:
                        await message.channel.send("Sorry! I didn't find any results.")
                        return
                    else:
                        img_req = requests.get(random.choice(result["illusts"])["image_urls"]["large"],
                                               headers={'Referer': 'https://app-api.pixiv.net/'}, stream=True)
                        img_file = io.BytesIO(img_req.content)
                        img_file.name = "psearch.jpg"
                        await message.channel.send(file=discord.File(img_file))
                else:
                    print(result)
                    await message.channel.send("Sorry! Something went wrong.")
            except Exception as e:
                print(e)
                await message.channel.send("Sorry! Something went wrong.")
            finally:
                return

    # whats up saigina protocol
    if re.compile("[Ww]hat['‘’]?s? +up,? +[Ss]aigina\??").search(message.content):
        resps = ["Tired.. Need a foot massage", "Ready for a nap.", "Doing good and I hope you are too!",
                 "Drinking some monster energy~", "I'm horny..", "Sucked some toes, hby?",
                 "Had to pose like a french girl for Saiga again~", "I'm stuck!",
                 "Eh I spilled water all over me, now I'm wet <:saigina_facial:833546674973704192>",
                 "Not much, was just taking pics for my OnlyFans",
                 "I met Dan Schneider and he seems like a cool dude..",
                 "Just a nice night for a walk, nothing clean~", "I just came back from Olive Garden",
                 "Eating my secret pie :pie:", "I'm naked.. I need your clothes, your boots, and your motorcycle.",
                 "I gotta go wash my feet real quick, brb", "Sorry not now, I've got to return some video tapes!",
                 "I had my feet tickled today ><", "Just feeling a little hot..",
                 "I like you <:ZOINKSS:803744649188868106>", "Had a shitty meal at IHOPS!",
                 "<a:catjam:871238826587213844>"]
        if str(message.author) == "Grone#8036":
            resps.append("Not much, but how's your homeroom teacher <:kawa_smug:827657702498238505>")
        await message.reply(random.choice(resps))
        return

    # joke protocol
    if re.compile("[Ss]aigina,? +tell +me +a +joke").search(message.content) and ("general-chat" in message.channel.name or IS_DEBUG_CHAN):
        jokes_dict = {"What did the toaster say to the slice of bread?": "\"I want you inside me.\"",
        "What does the cannibal have in the shower?": "Head & Shoulders.",
        "Two men broke into a drugstore and stole all the Viagra.":
        "The police put out an alert to be on the lookout for the two hardened criminals.",
        "Why shouldn’t you write with a broken pen?": "Because it’s pointless.",
        "What's my favorite fruit?": "Toe-mato!",
        "If you prostitute yourself to someone with a foot fetish, you have sold your sole..": None,
        "What goes in hard and dry, and then comes out wet and soft?": "Chewing gum.",
        "What do sprinters eat before a race?": "Nothing, they fast.",
        "Why did Princess Peach begin to choke?": "Because Mario came down the wrong pipe."}
        chosen_joke = random.choice(list(jokes_dict.keys()))
        await message.channel.send(chosen_joke)
        if jokes_dict[chosen_joke] is None:
            return
        time.sleep(6)
        await message.channel.send(jokes_dict[chosen_joke])
        return

    # name request protocol
    nr_re = re.compile("[Ss]aigina,? call me ([^.]*)\.?").match(message.content)
    if nr_re:
        names_dict[str(message.author).encode('utf-8')] = nr_re.groups()[0]
        tfile = open("resources/name_registry", "w+")
        tfile.write(str(names_dict))
        tfile.close()
        await message.reply("Sure thing, " + nr_re.groups()[0] + ". " + saigina_smug_id)
        return

    # name verification protocol
    if re.compile("[Ss]aigina,? what do you call me\??").match(message.content):
        if str(message.author).encode('utf-8') not in names_dict:
            await message.reply("I don't know what to call you yet!")
        else:
            await message.reply("I call you " + names_dict[str(message.author).encode('utf-8')] +
                                ". " + saigina_smug_id)
        return

    if re.compile("[Ss]aigina,? help!?").match(message.content):
        await message.channel.send("Hi, I'm Saigina! " + saigina_smug_id + "\n"
                                   "I have a few commands: \n"
                                   "Good morning/night Saigina\n"
                                   "Saigina show feet\n"
                                   "What's up, Saigina?\n"
                                   "Saigina, tell me a joke\n"
                                   "Saigina, call me _. and Saigina, what do you call me?\n")
    if ("server-boosters" in message.channel.name or IS_DEBUG_CHAN) and (("emote" in message.content or "Emote" in message.content
                          or "sticker" in message.content or "Sticker" in message.content) and message.attachments):
        await message.add_reaction('✅')
        await message.add_reaction('❌')


@client.event
async def on_raw_reaction_add(payload):
    reaction = payload.emoji
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    user = await client.fetch_user(int(payload.user_id))
    cname = str(channel.category)
    uauthd = str(user) in auth_users
    IS_DEBUG_CHAN = "saiginas-playground" in channel.name
    # pins messages in the gallery and other fetish channels if they reach 5 reactions
    if ("Gallery" in cname or "Other Fetish" in cname or IS_DEBUG_CHAN) \
            and ("❤" in reaction.name and [x for x in message.reactions if "❤" in str(x.emoji)][0].count == hofthresh):
        await move_pin(message)
    if "boosters" in str(channel) or IS_DEBUG_CHAN:
        check = reaction_from_str('✅', message.reactions)
        ecks = reaction_from_str('❌', message.reactions)
        if check is None or ecks is None:
            return
        if check.count - (ecks.count - 1) == sbsthresh and is_unique_message(str(message.id)):
            await message.reply("This submission has passed the vote! "
                            "Attention <@668745400492097549> and <@254822619860172800>")
    if "lootbox" in str(channel) and message.author == client.user \
            and str(payload.emoji.name) == "❌" and uauthd:
        await message.delete()
        try:
            if not message.attachments:
                return
            if re.compile("psearch.jpg").search(str(message.attachments[0])):
                return
            rmname = re.compile("LBV2image([0-9]{1,4})\.jpg").search(str(message.attachments[0]))
            if not rmname:
                await message.channel.send("That image is from an older lootbox.")
                return
            with open("resources/pixiv_feet_pick_purged_link_list", "a") as tf:
                tf.write(img_lnk_lst[int(rmname.groups()[0])] + "\n")
            del img_lnk_lst[int(rmname.groups()[0])]
            fp_rewrite()
        except Exception as e:
            print(e)
            await message.channel.send("Sorry! Something went wrong.")
            return
        await message.channel.send("Sorry! You won't be seeing that picture again. :x:")
    if str(payload.emoji.name) == "❌" and message.author == client.user and uauthd:
        await message.delete()
        return


def fp_rewrite():
    tlfile = open("resources/pixiv_feet_pic_link_list", "w+")
    for i in range(0, len(img_lnk_lst) - 1):
        tlfile.write(img_lnk_lst[i])
        tlfile.write("\n")
    tlfile.write(img_lnk_lst[len(img_lnk_lst) - 1])
    tlfile.close()


def is_unique_message(message_id):
    if message_id in dmid_list:
        return False
    else:
        dmid_list.append(message_id)
        with open("resources/pinned_message_ids", "a") as tf:
            tf.write(message_id + "\n")
        return True


async def move_pin(message):
    if is_unique_message(str(message.id)):
        content = message.content
        for attachment in message.attachments:
            content += '\n' + attachment.url
        if len(message.embeds) > 0:
            embeds = message.embeds[0]
        else:
            embeds = None
        mp_re = re.compile("(<@.?\d{18}>)")
        temp = mp_re.search(content)
        while temp:
            content = content.replace(temp.groups()[0], "")
            temp = mp_re.search(content)
        # await message.channel.send(content=content, embed=embeds)
        await hof.send(content=content, embed=embeds)


def reaction_from_str(rxn, lst):
    for reaction in lst:
        if rxn in str(reaction.emoji):
            return reaction
    return None


class SaigaStream(tweepy.asynchronous.AsyncStream):
    async def on_status(self, status):
        if status.user.id_str not in saiga_twt_acct_ids.keys() or status.is_quote_status or "RT" == status.text[:2] or status.in_reply_to_status_id is not None:
            return
        link = "https://twitter.com/" + status.user.screen_name + '/status/' + status.id_str
        await sanct.send(link)


tstream = SaigaStream("TPu14J4NowHd0ALlrrvHOVyss", "IeQDwV9V2D5roFGomozWVXyPEDoGnXY8xB8vWBVd0Ox8NBrIji",
                        "1368842761890324481-05j2eQEMj3yVGRBmDrVvwu2NKfcnib",
                        "vTJJL0cO4u6ighCBfi87oP05mcgoxbI9fz6xFxnplWQpE")
tstream.filter(follow=saiga_twt_acct_ids.keys())


try:
    client.run(dtok)
except KeyboardInterrupt:
    print("Goodnight, Saigina!")
    client.close()
