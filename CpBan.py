import vk_api, time, pytesseract, cv2, os, requests, threading, numpy as np
from colorama import Fore, Back
from colorama import init
pytesseract.pytesseract.tesseract_cmd = r'D:\OCR\tesseract'   # путь до exe файла pytesseract
os.system('')
init(autoreset=True)


def main(token, bad1, group_id):
    try:
        bad = bad1
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        row = {}
        wall = vk.wall.get(owner_id=group_id, filter='all', offset=1, count=2)
        try:
            row.update({group_id: wall['items'][0]['id']})
        except IndexError:
            pass
        while True:
            for group_id, latest_post_id in row.items():
                wall = vk.wall.get(owner_id=group_id, count=2)
                post = None
                try:
                    print(Fore.GREEN + "Ожидание поста...")
                    post = wall['items'][1]
                    time.sleep(2)
                    print("\033[A                             \033[A")
                except:
                    pass
                if post:
                    if post['id'] > latest_post_id:
                        row.update({group_id: post['id']})
                        a = vk.wall.get(owner_id=group_id, count=2)
                        try:
                            if a['items'][0]['is_pinned'] == 1:
                                post_id = a['items'][1]['id']
                        except:
                            post_id = a['items'][0]['id']
                        print(Fore.GREEN + "Обнаружен пост, жду набор комментариев с цп")
                        time.sleep(15)
                        print(Fore.GREEN + "Проверка поста -- "+str(post_id))
                        listComment_id = []
                        comment(vk, group_id, post_id, bad, listComment_id, 0)
                        for i in range(50):
                            time.sleep(20)
                            comment(vk, group_id, post_id, bad, listComment_id, 0)
    except Exception as e:
        print(e)


def comment(vk, group_id, post_id, bad, listComment_id, if3):
    try:
        count = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=1)['count']
        print(Fore.GREEN + "Всего комментариев "+str(count))                                                                                     # получаем кол-во комментариев
        if count > 100:                                                                                                              # если больше чем 99
            comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=100, sort='desc', thread_items_count=10)                              # без сдвига
            send_to_check(vk, count, comm, group_id, bad, listComment_id, 0)
            count = count-100
            if count < 101:                                                                                                         # если коммментов стало меньше чем 100
                comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=100, thread_items_count=10)            # со сдвигом
                send_to_check(vk, count, comm, group_id, bad, listComment_id, 0)
            elif count > 100:                                                                                                        # если комментов осталось больше 100
                x = 0
                while count > 100:
                    comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=x+100, thread_items_count=10)
                    send_to_check(vk, count, comm, group_id, bad, listComment_id, 0)
                    count = count-100
                    x = x+100
                    if count < 101:                                                                                                 # если коммментов стало меньше чем 101
                        comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=x, thread_items_count=10)      # со сдвигом
                        send_to_check(vk, count, comm, group_id, bad, listComment_id, 0)
        elif count < 101:                                                                                   # если комментов изначально меньше 101
            comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', thread_items_count=10)        # получаем комментарии
            send_to_check(vk, count, comm, group_id, bad, listComment_id, 0)
    except Exception as e:
        print(e)
        pass
    

def send_to_check(vk, count, comm, group_id, bad, listComment_id, if3):
    for i in range(count):
        try:
            check(vk, group_id, bad, comm['items'][i]['attachments'][0]['photo']['sizes'][6]['url'], comm['items'][i]['id'], comm['items'][i]["from_id"], listComment_id, 0)
            if comm['items'][i]['thread']['count'] != 0:
                for x in range(comm['items'][i]['thread']['count']):
                        check(vk, group_id, bad, comm['items'][i]['thread']['items'][x]['attachments'][0]['photo']['sizes'][6]['url'], comm['items'][i]['thread']['items'][x]['id'], comm['items'][i]['thread']['items'][x]["from_id"], listComment_id, 0)
        except:
            pass


def check(vk, group_id, bad, url, comment_id, id, listComment_id, if3):
    x = 0
    try:
        r = requests.get(url)                                                                       # получаем фотку
        imagesfolder = 'images/'+str(comment_id)+str(id)+'.jpg'                                                # путь до фотки
        with open(imagesfolder, 'wb') as f:                                                         # загрузка фотки
            f.write(r.content)
        img = cv2.imread(imagesfolder)
        img = cv2.resize(img, None, fx=1.2, fy=1.7, interpolation=cv2.INTER_CUBIC)
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        prpp = pytesseract.image_to_string(img, lang='rus+eng')                                      # распознование текста с фотки
        prpp = prpp.lower()
        for i in range(len(bad)):                                                 # проверка запрещенных слов в тексте
            if bad[i] in prpp:
                bad_found = bad[i]
                x = x+1
        if x > 0:
            if comment_id in listComment_id:
                pass
            else:
                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                listComment_id.append(comment_id)
                print(Fore.RED + " Зарепортил[-] из-за: "+bad_found)
                x = 0
        else:
            if id > 651000000:
                if comment_id in listComment_id:
                    pass
                else:
                    vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                    listComment_id.append(comment_id)
                    print(Fore.RED + " Зарепортил[-] из-за недавно созданной страницы")
            else:
                ug = vk.users.get(user_ids=id, fields="has_photo")
                if ug[0]['has_photo'] == 0:
                    if comment_id in listComment_id:
                        pass
                    else:
                        vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                        listComment_id.append(comment_id)
                        print(Fore.RED + " Зарепортил[-] из-за отсутствия фотки")
                else:
                    if if3 == 0:
                        pass
                    elif if3 ==1:
                        ug = vk.users.get(user_ids=id, fields="online")
                        if ug[0]['online'] == 0:
                            if comment_id in listComment_id:
                                pass
                            else:
                                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                                listComment_id.append(comment_id)
                                print(Fore.RED + " Зарепортил[-] из-за оффлайна(возможно взломанный акк или бот)")
                        else:
                            listComment_id.append(comment_id)
    except Exception as e:
        print(e)
        pass



# 2 скрипт для проверки обычных комментариев



def main1(token, bad, group_id):
    try:
        listComment_id = []
        while True:
            group_id = group_id
            vk_session = vk_api.VkApi(token=token)
            vk = vk_session.get_api()
            getwall = vk.wall.get(owner_id=group_id, count=10)    # получаем пост
            print(Fore.YELLOW + "\n\n\nНачало работы 1 скрипта")
            for i in range(5):
                post_id = getwall['items'][i]['id']    # получаем пост id
                print(Fore.YELLOW + "Проверка поста -- "+str(post_id))
                comment1(vk, group_id, post_id, bad, listComment_id)    # выполняем функцию
            print("Ожидание 15 минут\n\n\n")
            time.sleep(60*15)
    except Exception as e:
        print(e)
        pass


def comment1(vk, group_id, post_id, bad, listComment_id):
    try:
        count = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=1)['count']
        print(Fore.GREEN + "Всего комментариев "+str(count))                                                                                     # получаем кол-во комментариев
        if count > 100:                                                                                                              # если больше чем 100
            comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=100, sort='desc')                              # без сдвига
            send_to_check1(vk, count, comm, group_id, bad, listComment_id)
            count = count-100
            if count < 101:                                                                                                         # если коммментов стало меньше чем 100
                comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=100)            # со сдвигом
                send_to_check1(vk, count, comm, group_id, bad, listComment_id)
            elif count > 100:                                                                                                        # если комментов осталось больше 100
                x = 0
                while count > 100:
                    comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=x+100)
                    send_to_check1(vk, count, comm, group_id, bad, listComment_id)
                    count = count-100
                    if count < 101:                                                                                                 # если коммментов стало меньше чем 101
                            comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc', offset=x)      # со сдвигом
                            send_to_check1(vk, count, comm, group_id, bad, listComment_id)
        elif count < 101:                                                                                   # если комментов изначально меньше 101
            comm = vk.wall.getComments(owner_id=group_id, post_id=post_id, count=count, sort='desc')        # получаем комментарии
            send_to_check1(vk, count, comm, group_id, bad, listComment_id)
    except Exception as e:
        print(e)
        pass


def send_to_check1(vk, count, comm, group_id, bad,listComment_id):
    for i in range(count):
        try:
            check1(vk, group_id, bad, comm['items'][i]['text'], comm['items'][i]['id'], listComment_id)
            if comm['items'][i]['thread']['count'] != 0:
                for x in range(comm['items'][i]['thread']['count']):
                        check1(vk, group_id, bad, comm['items'][i]['thread']['items'][x]['text'], comm['items'][i]['thread']['items'][x]['id'], listComment_id)
        except:
            pass


def check1(vk, group_id, bad, text, comment_id, listComment_id):
    x = 0
    try:
        for i in range(len(bad)):
            if bad[i] in text:
                bad_found = bad[i]
                x = x+1
        if x > 0:
            if comment_id in listComment_id:
                pass
            else:
                vk.wall.reportComment(owner_id=group_id, comment_id=comment_id, reason=0)
                listComment_id.append(comment_id)
                print (Fore.RED + text+" Зарепортил[-] из-за: "+bad_found)
                x = 0
            pass
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    # список для проверки комментариев
    bad = 'https', 't.me', 'vk.com', 'получи,стикер', 'instag', 'youtube', 'халява', 'прайм', 'в лс', '#слив', 'вас обмануть', 'теле2', 'переходи', 'стин', 'стене'
    # список для проверки текста на фото
    bad1 = 'пиш', 'брауз', 'тел', 'дет', 'цп', 'порн', 'смот', 'вбив', 'лет', 'det', 'cp', 'porn', 'pish', 'tel', 'слив', 'sliv', 'школ', 'tg', 'lvl', 'ищи', 'вбей', 'стин', 'закре','поиск','стене'

    token = "" # ваш токен
    while True:
        print(Fore.RED + Back.BLACK + "Автор: https://vk.com/dev.help"+ Fore.YELLOW + Back.BLACK +"\nВыберите режим работы...\n")
        inp = input(Fore.GREEN + Back.BLACK + "1. Бесконечный режим 2 скриптов\n2. Проверка на ссылки в 5 последних постах через каждые 15 минут\n3. Проверка последнего поста и последущая проверка новых постов на цп\n")
        if inp == '1':
            inp1 = input(Fore.YELLOW + Back.BLACK + "\n\n\nВыберите группу:\n1.Рифмы и Панчи\n2.MDK\n3.Леонардо Дайвинчик\n4.4ch\n5.Корпорация зла\n0.Другая...\n")
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
            try:
                if group_id[0] == "-":
                    t1 = threading.Thread(target=main1, args=(token, bad, group_id,))
                    print(Fore.YELLOW + Back.BLACK + "Запуск первого скрипта...")
                    t1.start()
                    time.sleep(20)
                    print(Fore.YELLOW + Back.BLACK + "\n\n\nЗапуск второго скрипта...")
                    vk_session = vk_api.VkApi(token=token)
                    vk = vk_session.get_api()
                    listComment_id = []

                    a = vk.wall.get(owner_id=group_id, count=2)
                    if a['items'][0]['is_pinned'] == 1:
                            post_id = a['items'][1]['id']
                    else:
                        post_id = a['items'][0]['id']
                    print(Fore.YELLOW + Back.BLACK + "Проверка последнего поста...")
                    comment(vk, group_id, post_id, bad1, listComment_id, 1)
                    print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                    main(token, bad1, group_id)
            except:
                pass

        elif inp == '2':
            inp1 = input(Fore.YELLOW + Back.BLACK + "\n\n\nВыберите группу:\n1.Рифмы и Панчи\n2.MDK\n3.Леонардо Дайвинчик\n4.4ch\n5.Корпорация зла\n0.Другая...\n")
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
            try:
                if group_id[0] == "-":
                    main1(token, bad, group_id)
                    print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                else:
                    print(Fore.RED + Back.BLACK + "Введите точные данные") 

            except Exception as e:
                print(e)
                pass


        elif inp == '3':
            inp1 = input(Fore.YELLOW + Back.BLACK + "\n\n\nВыберите группу:\n1.Рифмы и Панчи\n2.MDK\n3.Леонардо Дайвинчик\n4.4ch\n5.Корпорация зла\n0.Другая...\n")
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

            try:
                if group_id[0] == "-":
                    vk_session = vk_api.VkApi(token=token)
                    vk = vk_session.get_api()
                    listComment_id = []
                    a = vk.wall.get(owner_id=group_id, count=2)
                    try:
                        if a['items'][0]['is_pinned'] == 1:
                            post_id = a['items'][1]['id']
                    except:
                        post_id = a['items'][0]['id']
                    print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                    comment(vk, group_id, post_id, bad1, listComment_id, 1)
                    main(token, bad1, group_id)
                    print(Fore.YELLOW + Back.BLACK + "Запуск скрипта...")
                else:
                    print(Fore.RED + Back.BLACK + "Введите точные данные")

            except Exception as e:
                print(e)
                pass
