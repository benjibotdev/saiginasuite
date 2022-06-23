import time

from pixivpy3 import *

# general settings
search_tags = ["裸足裏", "足指", "裸足", "足フェチ"]
lfile = open("resources/pixiv_feet_pic_link_list", "a")
pfile = open("resources/pixiv_feet_pick_purged_link_list", "r")
purged_links = pfile.read().split('\n')
pfile.close()

# pixivpy settings
api = AppPixivAPI()
api.auth(refresh_token="EWw3dal-w0BRZIYETcpw0uUWOBBjARdsbwEziZzeZ3Q")


def fp_refresh() -> list:
    ret = []
    for n in range(1, 8):
        sd = "2021-" + str(n) + "-01"
        ed = "2021-" + str(n + 1) + "-01"
        print(sd, ed)
        offset = 0
        result = api.search_illust(search_tags, offset=offset, start_date=sd, end_date=ed)
        while result is not None and result["next_url"] is not None:
            for illust in result["illusts"]:
                if user_filter(illust["user"]["id"]) and tag_filter(illust["tags"]) \
                        and illust["image_urls"]["large"] not in purged_links:
                    ret.append(illust["image_urls"]["large"])
            offset = offset + len(result["illusts"])
            result = api.search_illust(search_tags, offset=offset, start_date=sd, end_date=ed)
            try:
                while 'error' in result:
                    print("Pausing for rate limit...")
                    time.sleep(10)
                    result = api.search_illust(search_tags, offset=offset, start_date=sd, end_date=ed)
                    print(result)
            except:
                print(result)
                exit(1)
        print(len(ret))

    return ret


def tag_filter(tags_in):
    tag_bl = ["loli", "boy", "shota", "mature", "shotacon", "yaoi", "male", "futa", "futanari", "dickgirl", "furry",
              "kemono"]
    for tag_in in tags_in:
        for otag in tag_bl:
            if otag in tag_in["name"] or (tag_in["translated_name"] is not None and otag in tag_in["translated_name"]):
                return False

    return True


def user_filter(user_in):
    user_bl = [28544318, 2230396, 65756342, 16221870, 42865690]
    for user in user_bl:
        if user == user_in:
            return False
    return True


'''
res = api.search_illust(search_tags, start_date="2020-2-01", end_date="2020-3-01")
print(res["illusts"])
exit(0)
'''
lnk_lst = fp_refresh()
lfile.write('\n')
for i in range(0, len(lnk_lst) - 1):
    lfile.write(lnk_lst[i])
    lfile.write('\n')
lfile.write(lnk_lst[len(lnk_lst) - 1])
lfile.close()
