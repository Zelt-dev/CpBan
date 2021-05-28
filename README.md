# Создатель этого скрипта => https://vk.com/dev.help

 __Меня зовут Витя, мне 15 лет))__
 
 
__Если вы хотите как-то меня отблагодарить или у вас появились вопросы, то можете написать мне в вк__

## Установка 
   * `pip install vk_api pytesseract colorama opencv-python beautifulsoup4 requests numpy`
   * `Идем сюда и качем нужную под вашу систему версию` https://github.com/UB-Mannheim/tesseract/wiki
  
  ![](https://user-images.githubusercontent.com/81006799/117576531-ff7cb500-b0ee-11eb-8d8e-f28b6f9683bc.png)
  
  `Тут выбираем этот пункт и ищем русский язык`
  
  ![](https://image.prntscr.com/image/2c-IvbJiSMW_O4q1Y2ogAA.png) 
  ![](https://image.prntscr.com/image/5TiqvyqpRpqfnP6600dr4Q.png)
  
  
  `ТУТ НУЖНО ЗАПОМНИТЬ ПУТЬ УСТАНОВКИ`
  `(его нужно потом указать в коде)`
  
  ![](https://image.prntscr.com/image/frIICweTSs2Sjp0pZkUNOg.png)


## Запуск
  * Создайте папку `"images"`
  * Укажите путь установки pytesseract в `config.py`

  ```python
  path = r'D:\OCR\tesseract'   # путь до exe файла pytesseract
  ```
  * Укажите токен от страницы в `config.py`
  ```python
  token = ""      # ваш токен
  ```


__Ну и как бы все на этом)__


__Удачного использования__ 
