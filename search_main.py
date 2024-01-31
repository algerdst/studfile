import json
import sys
import time
from python_rucaptcha.re_captcha import ReCaptcha
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://studfile.net/all-vuz/'

all_files = 0

# Определяем путь для сохранения, открываем файл path и записываем путь в переменную path
with open('path.txt', 'r', encoding='utf-8') as file:
    file = file.read()
    path = file.replace('\n', '')

# Токен от rucaptcha
with open('captcha_api_key.txt', 'r', encoding='utf-8') as f:
    captcha_token = f.read().replace('\n', '')

# Индекс сна
with open('sleep.txt', 'r', encoding='utf-8') as f:
    sleep_index = int(f.read().replace('\n', ''))


def set_chrome_options(path, folder_name, underfolder_name=None):
    """
    Функция устанавливает опцию для вебдрайвера, которая отвечает
    за установку папки в которую будут сохраняться файлы
    :param path: Путь до папки
    :param folder_name: Имя папки
    :param underfolder_name: Имя подпапки, оно будет задаваться, если у юзера файлы лежат в папках
    :return: Возвращает экземпляр chromeoptions
    """
    chromeOptions = webdriver.ChromeOptions()
    if underfolder_name:
        prefs = {f"download.default_directory": f"{path}\{folder_name}\{underfolder_name}"}
        fullpath = f"{path}\{folder_name}\{underfolder_name}"
        chromeOptions.add_experimental_option("prefs", prefs)
    else:
        prefs = {f"download.default_directory": f"{path}\{folder_name}"}
        fullpath = f"{path}\{folder_name}"
        chromeOptions.add_experimental_option("prefs", prefs)
        # Проверяет существует ли такой путь, если нет, то создает его
        if not os.path.exists(f"{path}\{folder_name}"):
            os.makedirs(f"{path}\{folder_name}")
    f = open('headless.txt', 'r', encoding='utf-8')
    headless = f.read().replace('\n', '')
    if headless == "True":
        chromeOptions.add_argument('--headless')
    else:
        print()
    f.close()
    return chromeOptions


request=input('Введите запрос')


f = open('logging.json', 'r', encoding='utf-8')
dict_for_dump = json.load(f)
iteration = 1
f.close()

with webdriver.Chrome() as browser:
    browser.get(url)
    folder_name = request
    search_field = browser.find_element(By.ID, 'txtSearchGo')
    search_field.click()
    search_field.send_keys(request)
    time.sleep(1)
    search_button = browser.find_element(By.ID, 'btnSearchGo')
    search_button.click()
    time.sleep(3)
    try:
        browser.find_element(By.CLASS_NAME, 'too_many_files')
        print('НАЙДЕНО СЛИШКОМ МНОГО ФАЙЛОВ, УТОЧНИТЕ ПОИСКОВОЙ ЗАПРОС')
        time.sleep(60)
        sys.exit()
    except:
        print('[+][+][+][+][+] В РАБОТЕ [+][+][+][+][+]')
    files = browser.find_elements(By.CLASS_NAME, 'file')
    if not files:
        categories = browser.find_elements(By.CLASS_NAME, 'action-open-block')
        for category in categories:
            category.click()
            time.sleep(1.2)
        files = browser.find_elements(By.CLASS_NAME, 'file')
    folders = browser.find_elements(By.CLASS_NAME, 'folder')
    folderss = browser.find_elements(By.CLASS_NAME, 'folder_icon')
    total_folders = folders + folderss
    print(f'Найдено {len(files)} файлов по запросу {request}')

    #Обход всех файлов без папок
    with webdriver.Chrome(options=set_chrome_options(path, folder_name)) as browser1:
        for file in files:
            filename = file.text
            if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith(
                    '.docx') or filename.endswith('rtf'):
                filelink = file.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if filelink not in dict_for_dump:
                    if iteration == 1:
                        print(f'Начинаю скачивать с файла {filename}')
                        iteration += 1
                    browser1.get(filelink)
                    try:
                        file_size = float(
                            browser1.find_element(By.CLASS_NAME, 'description').find_elements(By.CLASS_NAME,
                                                                                              'details')[
                                -1].text[:4])
                    except:
                        continue
                    file_format = browser1.find_element(By.CLASS_NAME, 'description').find_elements(
                        By.CLASS_NAME, 'details')[-1].text
                    if 'Mб' in file_format:
                        sleep_time = (file_size / 5) * sleep_index
                    elif 'Кб' in file_format:
                        sleep_time = 3
                    if sleep_time < 1:
                        sleep_time = 3
                    download_button = browser1.find_element(By.CLASS_NAME, 'link_download')
                    download_button.click()
                    time.sleep(1)
                    try:
                        postbut = browser1.find_element(By.ID, 'postbut')
                        postbut.click()
                        response_area = browser1.find_element(By.ID, 'g-recaptcha-response-1')
                        browser1.execute_script("arguments[0].style.display = 'block';",
                                                response_area)
                        captcha_key = browser1.find_element(By.CSS_SELECTOR,
                                                            'div.g-recaptcha').get_attribute(
                            'data-sitekey')
                        recaptcha = ReCaptcha(
                            rucaptcha_key=captcha_token,
                            websiteURL=filelink,
                            websiteKey=captcha_key,
                            mathod='userrecaptcha'
                        )
                        print('Решаю капчу')
                        result = recaptcha.captcha_handler()
                        result = result['solution']['gRecaptchaResponse']
                        print('Капча Решена!')
                        logging_file = open('log.txt', 'a', encoding='utf-8')
                        logging_file.write('Капча Решена! \n')
                        logging_file.close()
                        response_area.send_keys(result)
                        postbut.click()
                        time.sleep(sleep_time)
                    except:
                        all_files += 1
                        time.sleep(sleep_time)
                        print(f'Скачано {all_files} файлов')
                        logging_file = open('log.txt', 'a', encoding='utf-8')
                        logging_file.write(f"Скачано {all_files} файлов \n")
                        logging_file.close()
                    dict_for_dump[filelink] = 'filelink'
                    f = open('logging.json', 'w', encoding='utf-8')
                    json_log = json.dump(dict_for_dump, f, indent=4, ensure_ascii=False)
                    f.close()
                else:
                    continue

    #Обход всех папок
    for folder in total_folders:
        folder_link = folder.find_element(By.TAG_NAME, 'a').get_attribute('href')
        with webdriver.Chrome(options=set_chrome_options(path,folder_name)) as browser1:
            browser1.get(folder_link)
            time.sleep(2)
            marker_folders = browser1.find_elements(By.CLASS_NAME, 'marker')
            if not marker_folders:
                marker_folders=browser1.find_elements(By.CLASS_NAME, 'folder')
            for marker_folder in marker_folders:
                marker_folder.click()
                time.sleep(1)
                folder_name = marker_folder.find_element(By.CLASS_NAME, 'name').text
                uls = browser1.find_elements(By.CSS_SELECTOR, 'ul.folder_content')
                for ul in uls:
                    marker_folder_files = ul.find_elements(By.CLASS_NAME, 'file')
                    if not marker_folder_files:
                        continue
                    else:
                        break
            with webdriver.Chrome(options=set_chrome_options(path, folder_name)) as browser2:
                for file in marker_folder_files:
                    filelink = 'https://studfile.net/preview/' + \
                               file.find_element(By.CLASS_NAME,
                                                 'link_download').get_attribute(
                                   'href').split('#')[1]
                    if filelink not in dict_for_dump:
                        browser2.get(filelink)
                        try:
                            filename = browser2.find_element(By.TAG_NAME, 'h1').text
                        except:
                            continue
                        fileformat = browser2.find_element(By.CSS_SELECTOR, 'span.path').text
                        filename = filename + fileformat
                        dict_for_dump[filelink] = 'filelink'
                        f = open('logging.json', 'w', encoding='utf-8')
                        json_log = json.dump(dict_for_dump, f, indent=4, ensure_ascii=False)
                        f.close()
                        if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith(
                                '.docx') or filename.endswith('rtf'):
                            try:
                                file_size = float(
                                    browser2.find_element(By.CLASS_NAME, 'description').find_elements(By.CLASS_NAME,
                                                                                                     'details')[
                                        -1].text[:4])
                            except:
                                continue
                            if iteration == 1:
                                print(f'Начинаю скачивать с файла {filename}')
                                iteration += 1
                            file_format = browser2.find_element(By.CLASS_NAME, 'description').find_elements(
                                By.CLASS_NAME, 'details')[-1].text
                            if 'Mб' in file_format:
                                sleep_time = (file_size / 5) * sleep_index
                            elif 'Кб' in file_format:
                                sleep_time = 3
                            if sleep_time < 1:
                                sleep_time = 3
                            download_button = browser2.find_element(By.CLASS_NAME, 'link_download')
                            download_button.click()
                            time.sleep(1)
                            try:
                                postbut = browser2.find_element(By.ID, 'postbut')
                                postbut.click()
                                response_area = browser2.find_element(By.ID, 'g-recaptcha-response-1')
                                browser2.execute_script("arguments[0].style.display = 'block';",
                                                       response_area)
                                captcha_key = browser2.find_element(By.CSS_SELECTOR,
                                                                   'div.g-recaptcha').get_attribute(
                                    'data-sitekey')
                                recaptcha = ReCaptcha(
                                    rucaptcha_key=captcha_token,
                                    websiteURL=filelink,
                                    websiteKey=captcha_key,
                                    mathod='userrecaptcha'
                                )
                                print('Решаю капчу')
                                result = recaptcha.captcha_handler()
                                result = result['solution']['gRecaptchaResponse']
                                print('Капча Решена!')
                                logging_file = open('log.txt', 'a', encoding='utf-8')
                                logging_file.write('Капча Решена! \n')
                                logging_file.close()
                                response_area.send_keys(result)
                                postbut.click()
                                time.sleep(sleep_time)
                            except:
                                all_files += 1
                                time.sleep(sleep_time)
                                print(f'Скачано {all_files} файлов')
                                logging_file = open('log.txt', 'a', encoding='utf-8')
                                logging_file.write(f"Скачано {all_files} файлов \n")
                                logging_file.close()
                        else:
                            continue



