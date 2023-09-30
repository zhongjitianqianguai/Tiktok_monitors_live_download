with open("Tiktok_live_room_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    live_room_dict = eval(file.read())
with open("Tiktok_home_link_by_auto_get.txt", "r", encoding='utf-8') as file:
    home_links_dict = eval(file.read())

# 获取两个字典之间的差异信息
live_room_only_keys = live_room_dict.keys() - home_links_dict.keys()
home_links_only_keys = home_links_dict.keys() - live_room_dict.keys()
live_room_only_items = live_room_dict.items() - home_links_dict.items()
home_links_only_items = home_links_dict.items() - live_room_dict.items()

# 输出差异信息
print("live_room_dict 中独有的键名：", live_room_only_keys)
print("home_links_dict 中独有的键名：", home_links_only_keys)
print("live_room_dict 中独有的键值对：", live_room_only_items)
print("home_links_dict 中独有的键值对：", home_links_only_items)