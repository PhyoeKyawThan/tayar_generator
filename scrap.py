import logging
import os
import sys
import re
import importlib
import requests
from bs4 import BeautifulSoup
from time import sleep

logging.basicConfig(level=logging.INFO)

class Scrap:
    _content_org_encoding: str = 'iso-8859-1'
    _base_url: str
    _html_content: str
    _clue: str
    
    _target_tag_list: list
    _result: list[dict]
    
    _bs: BeautifulSoup
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    
    def __init__(self, base_url: str, clue: str) -> None:
        if self._is_in_venv():
            self._base_url = base_url
            self._clue = clue
        else:
            self._logger.error("No virtual environment detected!\n")

    def do(self) -> None:
        self._logger.info("Getting html content from source..")
        self._request_html_content()
        if self._html_content:
            self._logger.info("Finished!\nConverting to target link lists..")
            self._target_tags()
            if len(self._result) > 0:
                self._logger.info(f"Finished! Fetched: {len(self._result)}")
                
    def _request_html_content(self) -> None:
        with open("temp.html", "r+") as f:
            if len(f.read()) >= 0: 
                self._html_content = f.read()
            else:
                response = requests.get(self._base_url) 
                f.write(response.text)
                self._request_html_content()
    
    def _parse_to_bs(self) -> None:
        self._bs = BeautifulSoup(self._html_content, features="lxml")
        del self._html_content

    def _target_tags(self) -> None:
        self._target_tag_list = self._bs.find_all(href=re.compile(self._clue))
        for link in self._target_tag_list[1:]:
            text = link.text.strip()  
            readable_text = text.encode(self._content_org_encoding, errors='ignore').decode('utf-8', errors='ignore')
            readable_text =  re.sub(r'[\t\n-]+', lambda m: m.group(0)[0], readable_text)
            parse_title = self._parse_title_author(readable_text)
            if(parse_title):
                self._result.append({
                    "title": parse_title[0],
                    "sayartaw": parse_title[1],
                    "link": link['href']
                })
        del self._target_tag_list
        self._logger.info(f"fetched {len(self._result)}")
        
    def _parse_title_author(self, text: str) -> tuple | None:
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
     
# def _init_scrap(self, module: dict) -> None:
    #     module_name: str = list(module.keys())[0]
    #     module_def: str = list(module.values())[0]
    #     try:
    #         self._bs4 = importlib.import_module(module_name)pass
    #     except ModuleNotFoundError as e:
    #         self._logger.error(f"{module_def} not found. trying to install...")
    #         os.system(f"pip install {module_name}")