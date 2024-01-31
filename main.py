import time
from python_rucaptcha.re_captcha import ReCaptcha
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import logging

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.2470 YaBrowser/23.11.0.2470 Yowser/2.5 Safari/537.36'
}

# Определяем путь для сохранения, открываем файл path и записываем путь в переменную path
with open('path.txt', 'r', encoding='utf-8') as file:
    file = file.read()
    path = file.replace('\n', '')

# Открываем файл со ссылками и заносим ссылки в переменную urls
with open('urls.txt', 'r', encoding='utf-8') as file:
    urls = []
    for url in file:
        urls.append(url.replace('\n', ''))


def get_all_users(url):
    """
    получает ссылки на всех пользователей
    :return: Cписок ссылок
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    users_links = soup.findAll('a', class_='username')
    return users_links


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
    # chromeOptions.add_argument('--headless')
    return chromeOptions


def get_folder_name(url):
    """
    Функция возвращает имя папки для сохранения файлов
    :param url: ссылка на страницу
    :return: имя папки
    """
    chromeOptions = webdriver.ChromeOptions()
    f = open('headless.txt', 'r', encoding='utf-8')
    headless = f.read().replace('\n', '')
    if headless == "True":
        chromeOptions.add_argument('--headless')
    else:
        print()
    f.close()
    with webdriver.Chrome(options=chromeOptions) as browser:
        browser.get(url)
        time.sleep(2)
        folder_name = browser.find_elements(By.CLASS_NAME, 'chosen-single')[1].text
        return folder_name


with open('captcha_api_key.txt', 'r', encoding='utf-8') as f:
    captcha_token = f.read().replace('\n', '')

with open('sleep.txt', 'r', encoding='utf-8') as f:
    sleep_index = int(f.read().replace('\n', ''))

def main():
    try:
        print('[+][+][+][+][+] В РАБОТЕ [+][+][+][+][+]')
        logging_file = open('log.txt', 'a', encoding='utf-8')
        logging_file.write('[+][+][+][+][+] В РАБОТЕ [+][+][+][+][+] \n')
        logging_file.close()
        all_files = 0  # Подсчитыват сколько всего скачано файлов
        for url in urls:
            folder_name = get_folder_name(url)
            # получаю все ссылки на пользователей с файлами
            users_links = get_all_users(url)
            for link in users_links:
                username = link.text
                user_link = 'https://studfile.net' + link['href']
                logging_file = open('log.txt', 'a', encoding='utf-8')
                logging_file.write(f"Поиск файлов в {folder_name} \n")
                logging_file.close()
                print(f"Поиск файлов в {folder_name}")
                with webdriver.Chrome(options=set_chrome_options(path, folder_name)) as browser1:
                    browser1.get(user_link)
                    files = browser1.find_element(By.ID, 'files_list').find_elements(By.TAG_NAME, 'li')
                    files_list = []
                    for file in files:
                        # Проверка есть ли в переменной file объект div.folder. Если есть, то это папка, если нет, то это файл
                        try:
                            file.find_element(By.CSS_SELECTOR, 'div.folder')
                            underfolder_name = file.find_element(By.CLASS_NAME, 'name').text
                            # print(f"{underfolder_name} это папка")
                            file.click()
                            time.sleep(0.5)
                            files = file.find_elements(By.CLASS_NAME, 'file')
                            flag = False
                            for file in files:
                                filename = file.find_element(By.CLASS_NAME, 'name').text
                                if filename.endswith('.pdf') or filename.endswith('.doc') or filename.endswith(
                                        '.docx') or filename.endswith('rtf'):
                                    flag = True
                                    break
                            if flag is True:
                                with webdriver.Chrome(
                                        options=set_chrome_options(path, folder_name,
                                                                   underfolder_name)) as browser2:
                                    for file in files:
                                        filename = file.find_element(By.CLASS_NAME, 'name').text
                                        if filename.endswith('.pdf') or filename.endswith(
                                                '.doc') or filename.endswith('.docx') or filename.endswith('rtf'):
                                            filelink = 'https://studfile.net/preview/' + \
                                                       file.find_element(By.CLASS_NAME,
                                                                         'link_download').get_attribute(
                                                           'href').split('#')[1]
                                            if not os.path.exists(f"{path}\{folder_name}\{underfolder_name}"):
                                                os.makedirs(f"{path}\{folder_name}\{underfolder_name}")
                                            browser2.get(filelink)
                                            download_button = browser2.find_element(By.CLASS_NAME, 'link_download')
                                            file_size = float(
                                            browser2.find_element(By.CLASS_NAME, 'description').find_elements(
                                                By.CLASS_NAME, 'details')[-1].text[:4])
                                            file_format = \
                                            browser2.find_element(By.CLASS_NAME, 'description').find_elements(
                                                By.CLASS_NAME, 'details')[-1].text
                                            if 'Mб' in file_format:
                                                sleep_time = (file_size / 5) * sleep_index
                                            elif 'Кб' in file_format:
                                                sleep_time = 3
                                            sleep_time = (file_size / 5)*sleep_index
                                            if sleep_time<1:
                                                sleep_time=3
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
                                                print()
                                                all_files += 1
                                                time.sleep(sleep_time)
                                                print(f'Скачано {all_files} файлов')
                                                logging_file = open('log.txt', 'a', encoding='utf-8')
                                                logging_file.write(f"Скачано {all_files} файлов \n")
                                                logging_file.close()
                        except:
                            name = file.find_element(By.CLASS_NAME, 'name').text
                            if name.endswith('.pdf') or name.endswith(
                                    '.doc') or name.endswith('.docx') or name.endswith('rtf'):
                                filelink = 'https://studfile.net/preview/' + \
                                           file.find_element(By.CLASS_NAME,
                                                             'link_download').get_attribute(
                                               'href').split('#')[1]
                                with webdriver.Chrome(
                                        options=set_chrome_options(path, folder_name,)) as browser2:
                                    browser2.get(filelink)
                                    download_button = browser2.find_element(By.CLASS_NAME, 'link_download')
                                    file_size=float(browser2.find_element(By.CLASS_NAME, 'description').find_elements(By.CLASS_NAME, 'details')[-1].text[:4])
                                    file_format = browser2.find_element(By.CLASS_NAME, 'description').find_elements(
                                        By.CLASS_NAME, 'details')[-1].text
                                    if 'Mб' in file_format:
                                        sleep_time = (file_size / 5)*sleep_index
                                    elif 'Кб' in file_format:
                                        sleep_time=3
                                    if sleep_time < 1:
                                        sleep_time = 3
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
                                        print()
                                        all_files += 1
                                        time.sleep(sleep_time)
                                        print(f'Скачано {all_files} файлов')
                                        logging_file = open('log.txt', 'a', encoding='utf-8')
                                        logging_file.write(f"Скачано {all_files} файлов \n")
                                        logging_file.close()
    except Exception as ex:
        with open('fail_url.txt', 'a') as fail_file:
            fail_file.write(f'Аварийное завершение в категории {folder_name} пользователя {username} \n {ex} ')


main()
