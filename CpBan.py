import time
import os

import vk_api
import cv2
import pytesseract
import requests
import threading
import numpy as np

from colorama import Fore, Back
from colorama import init
from config import token, bad_text, bad_text_on_photo, path
from log import log_to_tg
from datetime import datetime


pytesseract.pytesseract.tesseract_cmd = path   # путь до exe файла pytesseract
os.system('')
init(autoreset=True)


def main(token, group_id):
    try:
        list_id = []
        dict_of_last_id = {}

        vk_session = vk_api.VkApi(token=token)      # вход с помощью токена
        vk = vk_session.get_api()

        wall = vk.wall.get(owner_id=group_id, filter='all', offset=1, count=2)
        dict_of_last_id.update({group_id: wall['items'][0]['id']})
        print(Fore.GREEN + "Обнаружен пост, жду набор комментариев с цп")
        print(Fore.GREEN + "Проверка поста -- "+str(wall['items'][0]['id']))

        while True:
            check_post = vk.wall.get(owner_id=group_id, count=2)
            try:
                if check_post['items'][0]['is_pinned'] == 1:
                    post_id = check_post['items'][1]['id']
            except:
                post_id = check_post['items'][0]['id']

            for group_id, latest_post_id in dict_of_last_id.items():
                if post_id > latest_post_id:
                    print(Fore.GREEN + "Обнаружен пост, жду набор комментариев с цп")
                    print(Fore.GREEN + "Проверка поста -- "+str(post_id))
                    list_id = []
                elif post_id < latest_post_id:
                    print(Fore.RED + "\nПост удален начинаю проверку по предыдущему посту")
                    print(Fore.RED + "Проверка поста -- "+str(post_id) + "\n")
                    list_id = []

                dict_of_last_id.update({group_id: post_id})
                get_comments(vk, group_id, post_id, list_id, 1)
                time.sleep(5)
    except Exception as e:
        print(e)
        pass


def main1(token, group_id):
    list_id = []
    while True:
        group_id = group_id
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        getwall = vk.wall.get(owner_id=group_id, count=10)    # получаем пост
        print(Fore.YELLOW + "\n\n\nНачало работы 1 скрипта")
        for i in range(5):
            post_id = getwall['items'][i]['id']    # получаем пост id 5 последних постов
            print(Fore.YELLOW + "Проверка поста -- " + str(post_id))
            get_comments1(vk, group_id, post_id, list_id)    # выполняем функцию
        print("Ожидание 15 минут\n\n\n")
        time.sleep(60*15)


def get_comments(vk, group_id, post_id, list_id, if3):
        count = vk.wall.getComments(owner_id=group_id,
                                    post_id=post_id, count=1)['count']
        print(Fore.GREEN + "Всего комментариев "+str(count))             # получаем кол-во комментариев
        
        if count > 100:               # если больше чем 99
            comment = vk.wall.getComments(owner_id=group_id,
                                        post_id=post_id,
                                        count=100,
                                        sort='desc',
                                        thread_items_count=10)               # без сдвига
            send_to_check(vk, count, comment, group_id, list_id, if3)
            count = count-100
            
            if count < 101:            # если коммментов стало меньше чем 100
                comment = vk.wall.getComments(owner_id=group_id,
                                            post_id=post_id,
                                            count=count,
                                            sort='desc',
                                            offset=100,
                                            thread_items_count=10)            # со сдвигом
                send_to_check(vk, count, comment, group_id, list_id, if3)
            
            elif count > 100:                # если комментов осталось больше 100
                x = 0
                while count > 100:
                    comment = vk.wall.getComments(owner_id=group_id,
                                                post_id=post_id,
                                                count=count,
                                                sort='desc',
                                                offset=x+100,
                                                thread_items_count=10)        # со сдвигом + 100
                    send_to_check(vk, count, comment, group_id, list_id, if3)
                    count = count-100
                    x += 100
                    
                    if count < 101:                  # если коммментов стало меньше чем 101
                        comment = vk.wall.getComments(owner_id=group_id,
                                                    post_id=post_id,
                                                    count=count,
                                                    sort='desc',
                                                    offset=x,
                                                    thread_items_count=10)      # со сдвигом
                        send_to_check(vk, count, comment, group_id, list_id, if3)
        
        elif count < 101:                                   # если комментов изначально меньше 101
            comment = vk.wall.getComments(owner_id=group_id,
                                        post_id=post_id,
                                        count=count,
                                        sort='desc',
                                        thread_items_count=10)        # получаем комментарии
            send_to_check(vk, count, comment, group_id, list_id, if3)


def get_comments1(vk, group_id, post_id, list_id):
    count = vk.wall.getComments(owner_id=group_id, post_id=post_id,count=1)['count']
    print(Fore.GREEN + "Всего комментариев " + str(count))                    # получаем кол-во комментариев
    
    if count > 100:                                                            # если больше чем 100
        comment = vk.wall.getComments( owner_id=group_id,
                                    post_id=post_id,
                                    count=100,
                                    sort='desc')                              # без сдвига
        send_to_check_text(vk, count, comment, group_id, list_id)
        count = count-100
        
        if count < 101:                                                      # если коммментов стало меньше чем 100
            comment = vk.wall.getComments( owner_id=group_id,
                                        post_id=post_id,
                                        count=count,
                                        sort='desc',
                                        offset=100)            # со сдвигом
            send_to_check_text(vk, count, comment, group_id, list_id)
        
        elif count > 100:                                                   # если комментов осталось больше 100
            x = 0
            while count > 100:
                comment = vk.wall.getComments( owner_id=group_id,
                                            post_id=post_id,
                                            count=count,
                                            sort='desc',
                                            offset=x + 100)             # со сдвигом + 100
                send_to_check_text(vk, count, comment, group_id, list_id)
                count = count-100
                if count < 101:                                                  # если коммментов стало меньше чем 101
                        comment = vk.wall.getComments( owner_id=group_id,
                                                    post_id=post_id,
                                                    count=count,
                                                    sort='desc', offset=x)      # со сдвигом
                        send_to_check_text(vk, count, comment, group_id, list_id)
    
    elif count < 101:                                                      # если комментов изначально меньше 101
        comment = vk.wall.getComments(owner_id=group_id,
                                    post_id=post_id,
                                    count=count,
                                    sort='desc')        # получаем комментарии
        send_to_check_text(vk, count, comment, group_id, list_id)


def send_to_check(vk, count, comment, group_id, list_id, if3):
    for i in range(count):
        """======================================================
        Проверка текста в комментарии и его ветке ответов """
        try:
            if bool(comment['items'][i]['text']) is True:
                check_text(vk, group_id,
                comment['items'][i]['text'],
                comment['items'][i]['id'],
                comment['items'][i]['from_id'],
                list_id)
        except:
            pass

        try:
                if bool(comment['items'][i]['thread']['count'] > 0) is True:
                    x = 0
                    for x in range(comment['items'][i]['thread']['count']+1):
                        check_text(vk, group_id,
                        comment['items'][i]['thread']['items'][x]['text'],
                        comment['items'][i]['thread']['items'][x]['id'],
                        comment['items'][i]['thread']['items'][x]['from_id'],
                        list_id)
        except:
            pass
        """======================================================
        Проверка фото в комментарие и его ветке ответов """
        try:
            if bool(comment['items'][i]['attachments'][0]['photo']['sizes'][6]['url']) is True:
                check_photo(vk, group_id,
                    comment['items'][i]['attachments'][0]['photo']['sizes'][6]['url'],
                    comment['items'][i]['id'],
                    comment['items'][i]["from_id"],
                    list_id, if3)
        except:
            pass

        try:
            if bool(comment['items'][i]['thread']['count'] > 0) is True:
                x = 0
                for x in range(comment['items'][i]['thread']['count']+1):
                    check_photo(vk, group_id,
                    comment['items'][i]['thread']['items'][x]['attachments'][0]['photo']['sizes'][6]['url'],
                    comment['items'][i]['thread']['items'][x]['id'],
                    comment['items'][i]['thread']['items'][x]["from_id"],
                    list_id, if3)
        except:
            pass
        """======================================================
        Проверка видео в комментарии и его ветке ответов """
        try:
            if bool(comment['items'][i]['attachments'][0]['video']) is True:
                check_video(vk, group_id,
                comment['items'][i]["attachments"][0]["video"]["title"],
                comment['items'][i]['id'],
                comment['items'][i]['from_id'],
                comment['items'][i]["attachments"][0]["video"]['description'],
                comment['items'][i]["attachments"][0]["video"]['owner_id'],
                comment['items'][i]["attachments"][0]["video"]['id'],
                list_id, if3)
        except:
            pass

        try:
            if bool(comment['items'][i]['thread']['count'] > 0) is True:
                x = 0
                for x in range(comment['items'][i]['thread']['count']+1):
                    check_video(vk, group_id,
                    comment['items'][i]['thread']['items'][x]["attachments"][0]["video"]["title"],
                    comment['items'][i]['thread']['items'][x]['id'],
                    comment['items'][i]['thread']['items'][x]['from_id'],
                    comment['items'][i]['thread']['items'][x]["attachments"][0]["video"]['description'],
                    comment['items'][i]['thread']['items'][x]["attachments"][0]["video"]['owner_id'],
                    comment['items'][i]['thread']['items'][x]["attachments"][0]["video"]['id'],
                    list_id, if3)
        except:
            pass


def send_to_check_text(vk, count, comment, group_id, list_id):
    for i in range(count):
        try:
            check_text(vk, group_id,
            comment['items'][i]['text'],
            comment['items'][i]['id'],
            list_id)

            if comment['items'][i]['thread']['count'] != 0:
                for x in range(comment['items'][i]['thread']['count']+1):
                    check_text(vk, group_id,
                    comment['items'][i]['thread']['items'][x]['text'],
                    comment['items'][i]['thread']['items'][x]['id'],
                    list_id)
        except:
            pass


def check_video(vk, group_id, title, comment_id, id, description, owner_id, video_id, list_id, if3):
    global bad_text
    x = 0
    for i in range(len(bad_text)):                     # проверка запрещенных слов в названии
        if bad_text[i] in title:
            bad_found = bad_text[i]
            x += 1

    if str(id) not in list_id:
        if x > 0:

                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                list_id.append(str(id))
                ug = vk.users.get(user_ids=id)
                f_name = ug[0]['first_name']
                l_name = ug[0]['last_name']
                info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [в названии видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за: "+bad_found
                print(info)
                log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))

        elif x == 0:
                if id > 651000000:
                        vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                        list_id.append(str(id))
                        ug = vk.users.get(user_ids=id)
                        f_name = ug[0]['first_name']
                        l_name = ug[0]['last_name']
                        info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за недавно созданной страницы"
                        print(info)
                        log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))
                else:
                    users_get = vk.users.get(user_ids=id, fields="has_photo")
                    if users_get[0]['has_photo'] == 0:
                            vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                            list_id.append(str(id))
                            ug = vk.users.get(user_ids=id)
                            f_name = ug[0]['first_name']
                            l_name = ug[0]['last_name']
                            info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за отсутствия авы"
                            print(info)
                            log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))
                    else:
                        if if3 == 0:
                            pass
                        elif if3 == 1:
                            users_get = vk.users.get(user_ids=id, fields="online")
                            if users_get[0]['online'] == 0:
                                    vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                    list_id.append(str(id))
                                    ug = vk.users.get(user_ids=id)
                                    f_name = ug[0]['first_name']
                                    l_name = ug[0]['last_name']
                                    info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за оффлайна(возможно взломанный акк или бот)"
                                    print(info)
                                    log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))
                            else:
                                x = 0 
                                for q in range(len(bad_text)):
                                    if bad_text[q] in description:
                                        bad_found = bad_text[q]
                                        x += 1
                                if x > 0:
                                    vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                    list_id.append(str(id))
                                    ug = vk.users.get(user_ids=id)
                                    f_name = ug[0]['first_name']
                                    l_name = ug[0]['last_name']
                                    info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [в описании видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за: "+bad_found+"     "+description
                                    print(info)
                                    log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))

                                elif x == 0:
                                    video = vk.video.getComments(owner_id=owner_id, video_id=video_id)
                                    count = video['count']
                                    x = 0
                                    for l in range(count):
                                        text = video['items'][l]['text']
                                        for i in range(len(bad_text)):
                                            if bad_text[i] in text:
                                                bad_found = bad_text[i]
                                                x += 1
                                    if x > 0:
                                        vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                        list_id.append(str(id))
                                        ug = vk.users.get(user_ids=id)
                                        f_name = ug[0]['first_name']
                                        l_name = ug[0]['last_name']
                                        info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [в комментариях под видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за: "+bad_found+"    "+text
                                        print(info)
                                        log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))
                                    else:
                                        if if3 == 0:
                                            pass
                                        elif if3 == 1:
                                            users_get = vk.users.get(user_ids=id, fields="online")
                                            if users_get[0]['online'] == 0:
                                                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                                list_id.append(str(id))
                                                ug = vk.users.get(user_ids=id)
                                                f_name = ug[0]['first_name']
                                                l_name = ug[0]['last_name']
                                                info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [Видео, "+ f_name + " " + l_name +"] Зарепортил[+] из-за оффлайна(возможно взломанный акк или бот)"
                                                print(info)
                                                log_to_tg(info, None, 'https://vk.com/video'+str(owner_id)+'_'+str(id))
                                            else:
                                                list_id.append(str(id))


def check_photo(vk, group_id, url, comment_id,
                id, list_id, if3):
    global bad_text_on_photo
    try:
        try:
            r = requests.get(url, stream=True).raw
        except:
            pass   
        img = np.asarray(bytearray(r.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        img = cv2.resize(img, None, fx=1.2, fy=1.7, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]                                                                 # получаем фотку                                        # путь до фотки

        prpp = pytesseract.image_to_string(img, lang='rus+eng')                                      # распознование текста с фотки
        prpp = prpp.lower()
        x = 0
        for i in range(len(bad_text_on_photo)):                                                # проверка запрещенных слов в тексте
            if bad_text_on_photo[i] in prpp:
                bad_found = bad_text_on_photo[i]
                x += 1

        if str(id) not in list_id:
            if x > 0:
                    vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                    list_id.append(str(id))
                    ug = vk.users.get(user_ids=id)
                    f_name = ug[0]['first_name']
                    l_name = ug[0]['last_name']
                    info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [фото, "+ f_name + " " + l_name +"] Зарепортил[+] из-за: "+bad_found
                    print(info)
                    log_to_tg(info, url, None)
            else:
                if id > 651000000:
                        vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                        list_id.append(str(id))
                        ug = vk.users.get(user_ids=id)
                        f_name = ug[0]['first_name']
                        l_name = ug[0]['last_name']
                        info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [фото, "+ f_name + " " + l_name +"] Зарепортил[+] из-за недавно созданной страницы"
                        print(info)
                        log_to_tg(info, url, None)
                else:
                    users_get = vk.users.get(user_ids=id, fields="has_photo")
                    if users_get[0]['has_photo'] == 0:
                            vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                            list_id.append(str(id))
                            ug = vk.users.get(user_ids=id)
                            f_name = ug[0]['first_name']
                            l_name = ug[0]['last_name']
                            info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [фото, "+ f_name + " " + l_name +"] Зарепортил[+] из-за отсутствия авы"
                            print(info)
                            log_to_tg(info, url, None)
                    else:
                        if if3 == 0:
                            pass
                        elif if3 == 1:
                            users_get = vk.users.get(user_ids=id, fields="online")
                            if users_get[0]['online'] == 0:
                                    vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                    list_id.append(str(id))
                                    ug = vk.users.get(user_ids=id)
                                    f_name = ug[0]['first_name']
                                    l_name = ug[0]['last_name']
                                    info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [фото, "+ f_name + " " + l_name +"] Зарепортил[+] из-за оффлайна(возможно взломанный акк или бот)"
                                    print(info)
                                    log_to_tg(info, url, None)
                            else:
                                list_id.append(str(id))

    except Exception as e:
        print(e)
        pass


def check_text(vk, group_id, text, comment_id, id, list_id):
    global bad_text
    try:
        x = 0
        for i in range(len(bad_text)):
            if bad_text[i] in text:
                bad_found = bad_text[i]
                x += 1
        if str(id) not in list_id:
            if x > 0:
                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                list_id.append(str(id))
                ug = vk.users.get(user_ids=id)
                f_name = ug[0]['first_name']
                l_name = ug[0]['last_name']
                info = datetime.now().strftime("%H:%M:%S")+Fore.RED + " [текст, "+ f_name + " " + l_name +"] Зарепортил[+] из-за: "+bad_found+"      "+text
                print(info)
                log_to_tg(info, None, None)
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    while True:
        try:
            print(Fore.RED + Back.BLACK + "Автор: https://vk.com/dev.help" + Fore.YELLOW + Back.BLACK +
                "\nВыберите режим работы...\n")
            inp = input(Fore.GREEN + Back.BLACK +
                                                    "1. Бесконечный режим 2 скриптов\n" +
                                                    "2. Проверка на ссылкив 5 последних постах через каждые 15 минут\n" +
                                                    "3. Проверка последнего поста и последущая проверка новых постов на цп\n")

            inp1 = input(Fore.YELLOW + Back.BLACK + "\n\n\nВыберите группу:\n" +
                                                        "1.Рифмы и Панчи\n" +
                                                        "2.MDK\n" +
                                                        "3.Леонардо Дайвинчик\n" +
                                                        "4.4ch\n" +
                                                        "5.Корпорация зла\n" +
                                                        "0.Другая\n")
            if inp1 == "1":
                group_id = "-28905875"
            elif inp1 == "2":
                group_id = "-57846937"
            elif inp1 == "3":
                group_id = "-91050183"
            elif inp1 == "4":
                group_id = "-45745333"
            elif inp1 == "5":
                group_id = "-29246653"
            elif inp1 == "0":
                print(Fore.YELLOW + Back.BLACK + "Вставьте id группы С МИНУСОМ...")
                group_id = input()
            else:
                print(Fore.RED + Back.BLACK + "Введите точные данные")

            if inp == '1':
                while True:
                    if group_id[0] == "-":
                        t1 = threading.Thread(target=main1, args=(token, group_id,))
                        print(Fore.YELLOW + Back.BLACK + "Запуск первого скрипта...")
                        t1.start()
                        time.sleep(20)
                        print(Fore.YELLOW + Back.BLACK + "\n\n\nЗапуск второго скрипта...")
                        main(token, group_id)

            elif inp == '2':
                while True:
                    if group_id[0] == "-":
                        print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                        main1(token, group_id)
                    else:
                        print(Fore.RED + Back.BLACK + "Введите точные данные")

            elif inp == '3':
                while True:
                    if group_id[0] == "-":
                        print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                        main(token, group_id)
                    else:
                        print(Fore.RED + Back.BLACK + "Введите точные данные")

        except Exception as e:
                print(e)
                pass
