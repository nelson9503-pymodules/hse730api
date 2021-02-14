import requests
import html2text


class CoverExtractor:

    def __init__(self):
        pass

    def extract(self, ad_type: str, page: int) -> dict:
        """
        ad_type: buy, rent
        """
        self.ad_type = ad_type
        url = "https://www.house730.com/{}/g{}".format(self.ad_type, page)
        lines = self.__request_page(url)
        self.results = {}
        for i in range(len(lines)):
            line = lines[i]
            if len(line) > 0 and line[0] == "[" and not "![]" in line:
                if "(/buy-property-" in line or "(/rent-property-" in line:
                    self.result = {}
                    line_slice = lines[i:i+15]
                    self.__check_title_url_id(line_slice)
                    self.__check_estate_district(line_slice)
                    self.__check_real_area(line_slice)
                    self.__check_build_area(line_slice)
                    self.__check_price(line_slice)
                    self.results[self.result["id"]] = self.result
        return self.results

    def __check_title_url_id(self, lines: list):
        for line in lines:
            if "(/buy-property-" in line or "(/rent-property-" in line:
                txt = line.split("]")[0]
                txt = txt.split("[")[1]
                self.result["title"] = txt
                txt = line.split("](")[1]
                txt = txt.split(" ")[0]
                self.result["property_url"] = "https://www.house730" + txt
                self.result["id"] = txt.replace(
                    "/rent-property-", "").replace("/buy-property-", "").replace(".html", "")
                break

    def __check_estate_district(self, lines: list):
        for line in lines:
            if len(line) > 0 and line[:2] == "__":
                txt = line.split("](")[0]
                txt = txt.split("[")[1]
                self.result["district"] = txt
                txt = line.split("__")[-1]
                txt = txt.split("](")[0]
                txt = txt.replace(" ", "").replace("[", "").replace("]", "")
                self.result["estate"] = txt
                break

    def __check_real_area(self, lines: list):
        for line in lines:
            if len(line) > 0 and line[0] == "實":
                size = ""
                if "呎" in line:
                    index = line.index("呎") - 1
                    while self.__is_number(line[index]):
                        size = line[index] + size
                        index -= 1
                    if not size == "":
                        self.result["real_area"] = size
                        break

    def __check_build_area(self, lines: list):
        for line in lines:
            if len(line) > 0 and line[0] == "建":
                size = ""
                if "呎" in line:
                    index = line.index("呎") - 1
                    while self.__is_number(line[index]):
                        size = line[index] + size
                        index -= 1
                    if not size == "":
                        self.result["build_area"] = size
                        break

    def __check_price(self, lines: list):
        for line in lines:
            if "**售" in line or "**租" in line:
                price = ""
                for t in line:
                    if self.__is_number(t):
                        price += t
                    if t == "萬":
                        price += "0000"
                if not price == "":
                    self.result["price"] = price
                    break

    def __is_number(self, txt: str):
        if txt in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return True
        return False

    def __request_page(self, url) -> list:
        r = requests.get(url)
        lines = html2text.html2text(r.text).split("\n")
        return lines
