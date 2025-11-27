from bs4 import BeautifulSoup
import requests
import re

def get_html_content(url: str) -> None:
    with open("temp.html", "r+") as f:
        if len(f.read()) >= 0: 
            pass
        else:
            response = requests.get(url) 
            f.write(response.text)
    
def get_audio_links() -> list:
    with open("temp.html", "r") as f:
        bs = BeautifulSoup(f, features="lxml")
        bs.original_encoding
    target_link = bs.find_all(href=re.compile("https://dhammadownload.com/MP3Library"))
    target_links: list = []
    for link in target_link[1:]:
        text = link.text.strip()  
        readable_text = text.encode('iso-8859-1', errors='ignore').decode('utf-8', errors='ignore')
        readable_text =  re.sub(r'[\t\n-]+', lambda m: m.group(0)[0], readable_text)
        parse_title = parse_title_author(readable_text)
        if(parse_title):
            target_links.append({
                "title": parse_title[0],
                "sayartaw": parse_title[1],
                "link": link['href']
            })
    print(f"fetched {len(target_links)}")
    return target_links


def parse_title_author(text: str) -> tuple | None:
    parts = text.split("။")
    if len(parts) > 1:
        text_part = parts[1].strip()
        text_part = re.sub(r'[\t\n]+', ' ', text_part) 
        text_part = re.sub(r'-+', '-', text_part)
        text_part = text_part.strip()
        if '-' in text_part:
            split_text = [t.strip() for t in text_part.split('-', 1)]
            if len(split_text) == 1:
                split_text.append("")
        else:
            split_text = [text_part, ""]
        return (split_text[0], split_text[1])
    else:
        return (parts[0], '')


            
if __name__ == "__main__":
    import json
    get_html_content("https://dhammadownload.com/Chanting-mp3.htm")
    with open("data_collection.json", "w") as f:
        f.write(json.dumps(get_audio_links()))
    # parse_title_author("၁။ ပဋ္ဌာန်းအမွှန်းပါဠိတော်-မင်းကွန်းဆရာတော် 	ဦးဝိစိတ္တသာရာဘိဝံသ")