# Version 2 of Saigina-bot (designed for the Saiga's Empire discord server)
import copy
import io
import discord
import re
import time
import random
import requests
from pixivpy3 import *
import tweepy
from tweepy import asynchronous as async_tweepy


discordClient = discord.Client(intents=discord.Intents.all())
global general_chat_channel, \
    hall_of_fame_channel, \
    saigas_sanctuary_channel, \
    server_boosters_channel, \
    saiginas_playground_channel, \
    lootbox_channel


# produces a dictionary from a filename, follow configuration guide in README
def dictFromFilename(filename):
    with open(filename, 'r') as file:
        temp = {}
        for line in file.read().split('\n'):
            if line == "":
                continue
            line_split = line.split(':=')
            temp[line_split[0]] = line_split[1]
    return temp


# produces a list from a filename, follow configuration guide in README
def listFromFilename(filename):
    with open(filename) as file:
        return file.read().split('\n')


# initialize API setup
api_key_dict = dictFromFilename("config/apikeys")
# discord token
discord_token = api_key_dict["discord_token"]
# pixiv api
pixiv_token = api_key_dict["pixiv_token"]
pixiv_api = AppPixivAPI()


# set discord settings
discord_settings_dict = dictFromFilename("config/discordConfig")
gallery_category_id = int(discord_settings_dict["gallery_category_id"])
saigina_smug_emote = discord_settings_dict["saigina_smug_emote"]
saigina_feet_emote = discord_settings_dict["saigina_feet_emote"]
auth_users = listFromFilename("config/auth_user_ids")


# set general settings
general_settings_dict = dictFromFilename("config/generalSettings")
hall_of_fame_vote_thresh = int(general_settings_dict["hall_of_fame_vote_thresh"])
sticker_emote_vote_pass_thresh = int(general_settings_dict["sticker_emote_vote_pass_thresh"])
saigina_respond_chance_percent = int(general_settings_dict["saigina_respond_chance_percent"])


global nickname_registry_dictionary
global pinned_message_id_list
global pixiv_feet_pic_list
global joke_list
global joke_purg


class SaigaStream(async_tweepy.AsyncStreamingClient):
    async def on_tweet(self, tweet):
        link = "https://twitter.com/twitter/statuses/" + str(tweet.id)
        await saigas_sanctuary_channel.send(link)


def loadConfig():
    # discord config
    global general_chat_channel, \
        hall_of_fame_channel, \
        saigas_sanctuary_channel, \
        server_boosters_channel, \
        saiginas_playground_channel, \
        lootbox_channel

    general_chat_channel = discordClient.get_channel(int(discord_settings_dict["general_chat_channel_id"]))
    hall_of_fame_channel = discordClient.get_channel(int(discord_settings_dict["hall_of_fame_channel_id"]))
    saigas_sanctuary_channel = discordClient.get_channel(int(discord_settings_dict["saigas_sanctuary_channel_id"]))
    server_boosters_channel = discordClient.get_channel(int(discord_settings_dict["server_boosters_channel_id"]))
    saiginas_playground_channel = discordClient.get_channel(int(discord_settings_dict["saiginas_playground_channel_id"]))
    lootbox_channel = discordClient.get_channel(int(discord_settings_dict["lootbox_channel_id"]))


async def twitterApiConfigLoad():
    # twitter api setup
    twitter_bearer_token = api_key_dict["twitter_bearer_token"]
    twitter_stream_account_ids = dictFromFilename("config/twitter_stream_account_ids")
    twitterStreamRule = ""
    twitterStreamClient = SaigaStream(twitter_bearer_token)

    # remove all current active rules from twitter stream
    rules = await twitterStreamClient.get_rules()
    if rules.data is not None:
        ids = []
        for rule in rules.data:
            ids.append(rule.id)
        await twitterStreamClient.delete_rules(ids)

    # generate new rule for filter
    for item in twitter_stream_account_ids.keys():
        twitterStreamRule += "from:" + item + " "
    twitterStreamRule += "-is:retweet -is:reply -is:quote"
    await twitterStreamClient.add_rules(tweepy.StreamRule(twitterStreamRule))
    try:
        await twitterStreamClient.filter()
    except Exception as e:
        print(e)
        exit(0)


def loadResources():
    global nickname_registry_dictionary, pinned_message_id_list, pixiv_feet_pic_list, joke_list, joke_purg
    nickname_registry_dictionary = dictFromFilename("resources/name_registry")
    pinned_message_id_list = listFromFilename("resources/pinned_message_ids")
    pixiv_feet_pic_list = listFromFilename("resources/pixiv_feet_pic_link_list")
    joke_list = []
    for line in listFromFilename("resources/joke_list"):
        joke_list.append(line.split(":="))
    joke_purg = []


@discordClient.event
async def on_ready():
    print("Discord connection successful, SAIGINABOT launched.")
    loadResources()
    print("Resources loaded.")
    loadConfig()
    print("Configuration loaded.")
    await twitterApiConfigLoad()


@discordClient.event
async def on_message(message):
    global pixiv_feet_pic_list

    # ignore this message if it comes from self
    if message.author == discordClient.user:
        return

    user_id_string = str(message.author.id)

    # are you there saigina
    # technically deprecated, but I see no reason to remove this
    if message.content == "Are you there, Saigina?":
        await message.reply("Yup, I'm here!")
        return

    # hello saigina protocol
    if re.compile("[Hh]ello,? +[Ss]aigina!?").search(message.content):
        if user_id_string not in nickname_registry_dictionary:
            await message.channel.send("Hello! " + saigina_smug_emote)
        else:
            await message.channel.send("Hello, " + nickname_registry_dictionary[user_id_string] +
                                       ". " + saigina_smug_emote)

    # good morning saigina protocol
    if re.compile("[Gg]ood +[Mm]orning,? +[Ss]aigina!?").search(message.content):
        if user_id_string not in nickname_registry_dictionary:
            await message.channel.send("Good morning! " + saigina_smug_emote)
        else:
            await message.channel.send("Good morning, " + nickname_registry_dictionary[user_id_string] +
                                       ". " + saigina_smug_emote)

    # good night saigina protocol
    if re.compile("[Gg]ood +[Nn]ight,? +[Ss]aigina\.?").search(message.content):
        if user_id_string not in nickname_registry_dictionary:
            await message.channel.send("Good night " + saigina_smug_emote)
        else:
            await message.channel.send("Good night, " + nickname_registry_dictionary[user_id_string] +
                                        ". " + saigina_smug_emote)
        return

    # show feet protocol
    if re.compile("[Ss][Hh][Oo][Ww].+[Ff][Ee]{2}[Tt]").search(message.content) and \
            ("Saigina" in message.content or "saigina" in message.content):
        await message.channel.send(saigina_feet_emote + saigina_smug_emote)
        return

    # pixiv search by keyword
    pk_re = re.compile("[Ss]aigina,? +look +for +key(?:word)? +(.+)").search(message.content)
    if pk_re and message.channel.id == lootbox_channel.id:
        pixiv_api.auth(refresh_token=pixiv_token)
        async with message.channel.typing():
            result = pixiv_api.search_illust(pk_re.groups()[0], search_target='title_and_caption')
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
    if ps_re and message.channel.id == lootbox_channel.id:
        pixiv_api.auth(refresh_token=pixiv_token)
        async with message.channel.typing():
            result = pixiv_api.search_illust(ps_re.groups()[0])
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
    if re.compile("[Ss]aigina,? +tell +me +a +joke").search(message.content) and message.channel.id == general_chat_channel.id:
        global joke_list, joke_purg
        if len(joke_list) <= len(joke_purg) / 3:
            for joke in joke_purg:
                joke_list.append(joke)
            joke_purg = []
        chosen_num = random.randint(0, len(joke_list) - 1)
        chosen_joke = joke_list[chosen_num]
        joke_purg.append(joke_list[chosen_num])
        del joke_list[chosen_num]
        for part in chosen_joke:
            async with message.channel.typing():
                time.sleep(3)
                await message.channel.send(part)
        return

    # name request protocol
    nr_re = re.compile("[Ss]aigina,? call me ([^.]*)\.?").match(message.content)
    if nr_re:
        nickname_registry_dictionary[user_id_string] = nr_re.groups()[0]
        with open("resources/name_registry", "w+") as file:
            for key in nickname_registry_dictionary.keys():
                file.write(key + ":=" + nickname_registry_dictionary[key] + '\n')
        await message.reply("Sure thing, " + nr_re.groups()[0] + ". " + saigina_smug_emote)
        return

    # name verification protocol
    if re.compile("[Ss]aigina,? what do you call me\??").match(message.content):
        if user_id_string not in nickname_registry_dictionary:
            await message.reply("I don't know what to call you yet!")
        else:
            await message.reply("I call you " + nickname_registry_dictionary[user_id_string] +
                                ". " + saigina_smug_emote)
        return

    if re.compile("[Ss]aigina,? help!?").match(message.content):
        await message.channel.send("Hi, I'm Saigina! " + saigina_smug_emote + "\n"
                                   "I have a few commands: \n"
                                   "Good morning/night Saigina\n"
                                   "Saigina show feet\n"
                                   "What's up, Saigina?\n"
                                   "Saigina, tell me a joke\n"
                                   "Saigina, call me _. and Saigina, what do you call me?\n")
        return

    if message.channel.id == server_boosters_channel.id and (("emote" in message.content or "Emote" in message.content
                          or "sticker" in message.content or "Sticker" in message.content) and message.attachments):
        await message.add_reaction('✅')
        await message.add_reaction('❌')
        return

    if "saigina" in message.content or "Saigina" in message.content:
        if random.randint(1, 100) < saigina_respond_chance_percent:
            await message.channel.send("👁️👄👁️")
        return


@discordClient.event
async def on_raw_reaction_add(payload):
    user = await discordClient.fetch_user(int(payload.user_id))
    if user == discordClient.user:
        return
    reaction = payload.emoji
    channel = discordClient.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    uauthd = str(user.id) in auth_users
    # pins messages in the gallery and other fetish channels if they reach 5 reactions
    hall_of_fame_vote_thresh_PASSED = False
    for rxn in message.reactions:
        if rxn.count == hall_of_fame_vote_thresh:
            hall_of_fame_vote_thresh_PASSED = True
    if message.channel.category is not None and message.channel.category.id == gallery_category_id \
            and hall_of_fame_vote_thresh_PASSED:
        await move_pin(message)
    if channel.id == lootbox_channel.id and message.author == discordClient.user \
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
                tf.write(pixiv_feet_pic_list[int(rmname.groups()[0])] + "\n")
            del pixiv_feet_pic_list[int(rmname.groups()[0])]
            fp_rewrite()
        except Exception as e:
            print(e)
            await message.channel.send("Sorry! Something went wrong.")
            return
        await message.channel.send("Sorry! You won't be seeing that picture again. :x:")
    if channel.id == server_boosters_channel.id and ('❌' in reaction.name or '✅' in reaction.name) and message.author != discordClient.user:
        check = reaction_from_str('✅', message.reactions)
        ecks = reaction_from_str('❌', message.reactions)
        if check is None or ecks is None:
            return
        if check.count - (ecks.count - 1) == sticker_emote_vote_pass_thresh and is_unique_message(str(message.id)):
            await message.reply("This submission has passed the vote! "
                            "Attention <@668745400492097549> and <@254822619860172800>")


def fp_rewrite():
    tlfile = open("resources/pixiv_feet_pic_link_list", "w+")
    for i in range(0, len(pixiv_feet_pic_list) - 1):
        tlfile.write(pixiv_feet_pic_list[i])
        tlfile.write("\n")
    tlfile.write(pixiv_feet_pic_list[len(pixiv_feet_pic_list) - 1])
    tlfile.close()


def is_unique_message(message_id):
    if message_id in pinned_message_id_list:
        return False
    else:
        pinned_message_id_list.append(message_id)
        with open("resources/pinned_message_ids", "a") as tf:
            tf.write('\n' + message_id)
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
        await hall_of_fame_channel.send(content=content, embed=embeds)


def reaction_from_str(rxn, lst):
    for reaction in lst:
        if rxn in str(reaction.emoji):
            return reaction
    return None


try:
    discordClient.run(discord_token)
except KeyboardInterrupt:
    print("Goodnight, Saigina!")
    discordClient.close()
