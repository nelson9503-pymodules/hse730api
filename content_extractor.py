import requests
import html2text


class ContentExtactor:

    def __init__(self):
        pass

    def extract(self, ad_type: str, id: int) -> dict:
        """
        ad_type: buy or rent
        """
        self.ad_type = ad_type
        self.id = id
        url = "https://www.house730.com/{}-property-{}.html".format(
            ad_type, id)
        lines = self.__request_page(url)
        self.results = {}
        self.__check_title(lines)
        self.__check_region_district(lines)
        self.__check_estate(lines)
        self.__check_photo_link(lines)
        self.__check_price(lines)
        self.__check_real_area(lines)
        self.__check_build_area(lines)
        self.__check_room(lines)
        self.__check_floor(lines)
        self.__check_address(lines)
        self.__check_phase(lines)
        self.__check_block_room(lines)
        self.__check_post_date(lines)
        self.__check_post_due_date(lines)
        self.__check_contact_type(lines)
        self.__check_contact_person(lines)
        self.__check_contact_phone(lines)
        return self.results

    def __request_page(self, url) -> list:
        r = requests.get(url)
        lines = html2text.html2text(r.text).split("\n")
        return lines

    def __check_title(self, lines: list):
        for line in lines:
            if line[:3] == "###":
                self.results["title"] = line.replace("### ", "")
                break

    def __check_region_district(self, lines: list):
        for line in lines:
            if line[:4] == "[主頁]":
                txts = self.__extract_between(line, "[", "]")
                if txts[1] == "買樓":
                    self.results["ad_type"] = "buy"
                elif txts[1] == "租樓":
                    self.results["ad_type"] = "rent"
                self.results["region"] = txts[2]
                self.results["district"] = txts[3]

    def __check_estate(self, lines: list):
        if not "district" in self.results:
            return
        keywords = "[" + self.results["district"] + "]"
        for line in lines:
            if line[:len(keywords)] == keywords:
                txts = self.__extract_between(line, "[", "]")
                if len(txts) >= 2:
                    self.results["estate"] = txts[1]
                break

    def __check_photo_link(self, lines: list):
        photos = []
        for line in lines:
            if "  * ![]" in line and "img.house730.com" in line:
                txts = self.__extract_between(line, "(", ")")
                if len(txts) >= 1 and not txts[0] in photos:
                    photos.append(txts[0])
        self.results["photos"] = photos

    def __check_price(self, lines: list):
        for line in lines:
            if line[:3] in ["**售", "**租"]:
                txts = self.__extract_between(line, "$", "*")
                if len(txts) >= 1:
                    price = txts[0]
                    price = price.replace(",", "")
                    if "萬" in price:
                        price = price.replace("萬", "")
                        price = float(price) * 10000
                    elif "億" in price:
                        price = price.replace("億", "")
                        price = float(price) * 100000000
                    self.results["price"] = price
                break

    def __check_real_area(self, lines: list):
        for line in lines:
            if line[:4] == "實用面積":
                if "呎" in line:
                    index = line.index("呎") - 1
                    area = ""
                    while index > 0 and self.__is_number(line[index]):
                        area = line[index] + area
                        index -= 1
                break

    def __check_build_area(self, lines: list):
        for line in lines:
            if line[:4] == "建築面積":
                if "呎" in line:
                    index = line.index("呎") - 1
                    area = ""
                    while index > 0 and self.__is_number(line[index]):
                        area = line[index] + area
                        index -= 1
                break

    def __check_room(self, lines: list):
        for line in lines:
            if "間隔" in line and "房" in line:
                index = line.index("房") - 1
                room = ""
                while index > 0 and self.__is_number(line[index]):
                    room = line[index] + room
                    index -= 1
                if not room == "":
                    self.results["room"] = room
                break

    def __check_floor(self, lines: list):
        for line in lines:
            if "層數" in line:
                if "高層" in line:
                    self.results["floor"] = "高層"
                elif "中層" in line:
                    self.results["floor"] = "中層"
                elif "低層" in line:
                    self.results["floor"] = "低層"
                break

    def __check_address(self, lines: list):
        for line in lines:
            if line[:4] == "樓盤地址":
                self.results["adress"] = line.replace("樓盤地址 ", "")
                break

    def __check_phase(self, lines: list):
        for line in lines:
            if line[:2] == "期數":
                phase = line.replace("期數", "")
                phase = phase.replace("\\--", "")
                phase = phase.replace(" ", "")
                if not phase == "":
                    self.results["phase"] = phase
                break

    def __check_block_room(self, lines: list):
        for line in lines:
            if "座位" in line and "單位" in line:
                if "座" in line:
                    index = line.index("座") - 1
                    block = ""
                    while self.__is_number(line[index]) or self.__is_letter(line[index]):
                        block = line[index] + block
                        index -= 1
                    if not block == "":
                        self.results["block"] = block
                if "室" in line:
                    index = line.index("室")
                    flat = ""
                    while self.__is_number(line[index]) or self.__is_letter(line[index]):
                        flat = line[index] + flat
                        index -= 1
                    if not flat == "":
                        self.results["flat"] = flat
                break

    def __check_post_date(self, lines: list):
        for line in lines:
            if "刊登/續期日" in line:
                self.results["post_date"] = line.replace("刊登/續期日", "")
                break

    def __check_post_due_date(self, lines: list):
        for line in lines:
            if "放盤到期日" in line:
                self.results["post_due_date"] = line.replace("放盤到期日", "")
                break
    
    def __check_contact_type(self, lines: list):
        for i in range(len(lines)):
            line = lines[i]
            if "共" in line and "條留言" in line:
                self.results["contant_type"] = lines[i+2].replace("盤", "").replace("自讓", "")
                break
    
    def __check_contact_person(self, lines: list):
        for i in range(len(lines)):
            line = lines[i]
            if "共" in line and "條留言" in line:
                for i2 in range(i, len(lines)):
                    line = lines[i2]
                    if "(javascript:void\(0\);)" in line:
                        i3 = i2 + 1
                        while len(lines[i3]) == 0 or lines[i3][0] == " ":
                            i3 += 1
                        self.results["contant_person"] = lines[i3]
                        break
                break
    
    def __check_contact_phone(self, lines: list):
        for i in range(len(lines)):
            line = lines[i]
            if "共" in line and "條留言" in line:
                for i2 in range(i, len(lines)):
                    line = lines[i2]
                    if "(javascript:void\(0\);)" in line:
                        i3 = i2 + 1
                        while not len(lines[i3]) >= 2 or not lines[i3][:2] == "__":
                            i3 += 1
                        phone = lines[i3].replace("__", "")
                        self.results["contant_phone"] = phone.split(" ")[0]
                        break
                break
            

    def __is_number(self, txt: str) -> bool:
        if txt in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            return True
        return False

    def __is_letter(self, txt: str) -> bool:
        if txt.upper() in ["A", "B", "C", "D", "E", "F", "G",
                           "H", "I", "J", "K", "L", "M", "N",
                           "O", "P", "Q", "R", "S", "T", "U",
                           "V", "W", "X", "Y", "Z"]:
            return True
        return False

    def __extract_between(self, txt: str, left: str, right: str):
        result = []
        record = False
        cache = ""
        for t in txt:
            if t == left:
                cache = ""
                record = True
            elif t == right:
                if not cache == "":
                    result.append(cache)
                record = False
            elif record == True:
                cache += t
        return result
