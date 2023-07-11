from datetime import timedelta
import os.path
import subprocess
from files import to_share_variables as share
import time
import sys
import requests
import string
from bs4 import BeautifulSoup
from multiprocessing import Pool
from functools import partial
from fake_useragent import UserAgent
import re
from random import choices, choice


def extract_url(data):
    match = ''
    pattern = r"(?P<url>https://i\.imgur.com/(\w)+\.(jpeg|png|gif|avif|svg)\\)"
    try:
        match = re.search(pattern, data).group('url').replace('\\', '')
        return match
    except (BaseException, re.error):
        return match


def picture_search_imgur(soup, current_url):
    out = ''
    output = f"{current_url}"
    data = soup.find("script").getText()
    if data != '':
        url_download = extract_url(data)
        save_picture(url_download)
        out = current_url
        output = f"{share.green}GOOD{share.reset}-->{current_url}"
    return out, output


def picture_search_prnt(soup, current_url):
    out = ''
    output = f"{current_url}"
    src = soup.find("meta", {"property": "og:image"})["content"]
    if src[:4] == "http" and len(src.rsplit("/", 1)[1]) < 15:
        if check_available_site(src):
            save_picture(src)
            out = current_url
            output = f"{share.green}GOOD{share.reset}-->{current_url}"
    return out, output


site_features = {
    "imgur.com": {
        "func": picture_search_imgur,
        "resource": "https://imgur.com/gallery/"
    },
    "prnt.sc": {
        "func": picture_search_prnt,
        "resource": "http://prnt.sc/"
    }
}


def check_available_site(site):
    header = {"User-agent": UserAgent().random}
    try:
        host_answer = requests.get(site, headers=header, timeout=3)
        host_answer.raise_for_status()
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError):
        print("Check error site!")
        return False
    else:
        if host_answer.status_code != 200:
            return False
        return True


def open_folder_result():
    response = input(f"Do you want open folder with results? [{share.green}Yes/No{share.reset}]: ")
    if response.lower() in ("yes", "y"):
        path = os.path.realpath('./pictures')
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])


def result_parse(start, cnt_success_links):
    hh, mm, ss = str(timedelta(seconds=int(time.time() - start))).split(':')
    print(f"===========================================\n"
          f"\n\n"
          f"{share.magenta}{'Ready for:':15} {hh} hours {mm} minutes {ss} seconds\n"
          f"{'Found links:':15} {cnt_success_links}\n"
          f"{'Folder size:':15} {get_size_all_files()}kb{share.reset}\n")


def create_url(site, threads, method, qnt):
    target_chars = string.digits + string.ascii_letters
    success_links = []
    start = time.time()
    host = site_features[site]["resource"]
    while True:
        urls = tuple((host + ''.join(choices(target_chars, k=choice((5, 6, 7)))) for _ in range(20)))
        result, success_links = multi_check(site, urls, threads, method, qnt, start, success_links)
        if not result:
            result_parse(start, len(success_links))
            break
    open_folder_result()


def multi_check(site, urls, threads, method, qnt, start, success_links):
    with Pool(processes=threads) as pool:
        try:
            size = get_size_all_files()
            if method == "time":
                assert time.time() - start < qnt
            elif method == "links":
                assert len(success_links) < qnt
            elif method == "size":
                assert size <= qnt
            link = pool.map(partial(checking_url, site, method, qnt, start, len(success_links), size), urls)
            [success_links.append(i) for i in link if i != '' and i not in success_links]

        except AssertionError:
            pool.terminate()
            pool.join()
            return False, success_links
        except Exception as error:
            print(f'Unable to get the result: {error}')
        except KeyboardInterrupt as error:
            print(f"Stopped script! (multi_check): {error}")
            sys.exit(0)
        else:
            return True, success_links


def check_qnt(method, **data):
    if method == "links":
        return data[method] < data['qnt']
    elif method == "time":
        return data[method] < data['qnt']
    elif method == 'size':
        return data[method] < data['qnt']


def save_picture(download_url):
    header = {"User-Agent": UserAgent().random}
    res = requests.get(download_url, headers=header, timeout=2)
    name = download_url.rsplit('/', 1)[1]
    folder_pictures = os.path.abspath('pictures')
    with open(os.path.join(folder_pictures, name), 'wb') as handler:
        handler.write(res.content)


def get_size_all_files():
    return int(sum(os.path.getsize(os.path.join('./pictures/', f)) for f in os.listdir('./pictures/')) / 1024)


def checking_url(site, method, qnt, start, cnt_links, size, url):
    out = ''
    output = url
    if not check_qnt(method, time=time.time() - start, links=cnt_links, size=size, qnt=qnt):
        print(output)
        return out

    try:
        time.sleep(1)
        host_answer = requests.get(url, headers={"User-agent": UserAgent().random}, timeout=2)
        host_answer.raise_for_status()
    except KeyboardInterrupt as error:
        print(f"Stopped script! (checking_url): {error}")
        time.sleep(3)
        sys.exit(0)
    except (requests.exceptions.RequestException,
            requests.exceptions.Timeout,
            requests.exceptions.TooManyRedirects,
            ValueError):
        requests.session().close()
        return out
    else:
        output = url
        if host_answer.status_code != 404:
            soup = BeautifulSoup(host_answer.content, 'html.parser')
            out, output = site_features[site]['func'](soup, url)
        host_answer.close()
    finally:
        print(output)
        return out
