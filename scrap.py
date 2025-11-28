import logging
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from time import sleep
from downloader import Downloader
logging.basicConfig(level=logging.INFO)

class Scrap(Downloader):
    _content_org_encoding: str = 'iso-8859-1'
    _base_url: str
    _html_content: str
    _clue: str
    
    _success_list: list[dict]
    _target_tag_list: list
    _result: list[dict] = []
    
    _bs: BeautifulSoup
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    
    def __init__(self, base_url: str, clue: str) -> None:
        super().__init__(self._logger)
        if self._is_in_venv():
            self._base_url = base_url
            self._clue = clue
        else:
            self._logger.error("No virtual environment detected!\n")

    def do(self) -> None:
        self._logger.info("Getting html content from source..")
        self.__request_html_content()
        if self._html_content:
            self.__parse_to_bs()
            self._logger.info("Finished!\nConverting to target link lists..")
            self.__target_tags()
            if len(self._result) > 0:
                self._logger.info(f"Finished! Fetched: {len(self._result)}")
                self._logger.info("Downloading the list of audio file")
                success_list = self.__start_downloading()
                if len(success_list) > 0:
                    self._logger.info(f"Downloaded {len(success_list)} audios")
                    self._logger.info("Saving to dataset.json file for later access")
                    self._write_to_json(success_list=success_list)
                    self._logger.info("Write finished!")
            else:
                self._logger.error("Sorry can't download audio list, check internet access and try again.")

    def __start_downloading(self) -> list[dict]:
        success_list: list[dict] = []
        for t in self._result:
            if self._download_and_convert_to_opus(t['link'], save_path="audios", filename=t['title']):
                success_list.append({
                  "title": t['title'],
                  "sayartaw": t['sayartaw'],
                  "description":
                      "ဗုဒ္ဓဘာသာ၏ အခြေခံသီရိဝင် အယူအဆများကို ဝင်ရိုးအဖြစ်ရှင်းလင်းပြောကြားထားသော အဆိုအထားပါသည်။",
                  "audioPath":
                      f"assets/audios/{t['title']}",
                  "srtPath": None,
                  "imagePath": None,
                  "isBookMark": False,
                })
        return success_list
    
    def _write_to_json(self, success_list: list[dict]) -> None:
         with open("dataset.json", "w") as f:
            f.write(json.dumps(success_list))
    
    def __request_html_content(self) -> None:
        try:
            with open("temp.html", "r+") as f:
                self._html_content = f.read()
                if self._html_content: 
                    return
                response = requests.get(self._base_url) 
                f.write(response.text)
                self.__request_html_content()
        except FileNotFoundError as e:
            with open("temp.html", "w") as f:
                pass
            return self.__request_html_content()
    
    def __parse_to_bs(self) -> None:
        self._bs = BeautifulSoup(self._html_content, features="lxml")
        del self._html_content

    def __target_tags(self) -> None:
        self._target_tag_list = self._bs.find_all(href=re.compile(self._clue))
        for link in self._target_tag_list[1:]:
            text = link.text.strip()  
            readable_text = text.encode(self._content_org_encoding, errors='ignore').decode('utf-8', errors='ignore')
            readable_text =  re.sub(r'[\t\n-]+', lambda m: m.group(0)[0], readable_text)
            parse_title = self.__parse_title_author(readable_text)
            if(parse_title):
                self._result.append({
                    "title": parse_title[0],
                    "sayartaw": parse_title[1],
                    "link": link['href']
                })
        del self._target_tag_list
        self._logger.info(f"fetched {len(self._result)}")
        
    def __parse_title_author(self, text: str) -> tuple | None:
        parts = text.split("။")
        if len(parts) > 1:
            text_part = parts[1].strip()
            del parts
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
    
    def _is_in_venv(self) -> bool:
        return sys.base_prefix != sys.prefix
    
if __name__ == "__main__":
    scrap = Scrap(base_url="https://dhammadownload.com/Chanting-mp3.htm", clue="https://dhammadownload.com/MP3Library")
    scrap.do()
     