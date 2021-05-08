from bs4 import BeautifulSoup
from bs4.element import Tag  # scrape
import requests
import re
import datetime


class Scrape:
    def __init__(self, file):
        self.url = "https://www.boatrace.jp/owpc/pc/data/racersearch/profile?toban="
        self.f_name = file

    def crawling(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) \
        AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'}
        url = self.url + self.f_name
        response = requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        with open(self.f_name, 'w', encoding='utf-8') as f:
            f.write(response.text)
        """
        try:
            with open(self.f_name, 'w', encoding="utf-8") as f:
                f.write(response.text)
        except FileNotFoundError:
            print("File Not Found")
        """

    def scraping(self):
        page = self.f_name
        data = []
        data_p = []
        grade_check = {"is-ippan":"一般", "is-G3b":"G3", "is-G2b":"G2", "is-G1b":"G1", "is-SGa":"SG"}
        grade_another = {"is-venus":"ヴィーナス", "is-rookie__3rdadd":"ルーキー", "is-lady":"レディース"}
        time_check = {"is-nighter": "🌘", "is-morning": "☀"}
        re_space = re.compile(r"\s+")
        with open(page, 'r') as html:  # 取得部
            soup = BeautifulSoup(html, 'html.parser')
            race_data = soup.find_all(class_='is-p10-0')    #出走データ全て取得
            racer_name = soup.find(class_='racer1_bodyName').text
            racer_name = re_space.sub(" ", racer_name)  #レーサー名のみ取得
        for d in race_data:
            if d == "": continue
            place = str(d.find("img")) #imgタグ内の開催地名の抜き出し
            place = re_space.sub("", place[9:14])
            place = place.replace("\"","")    #開催地名のみ
            grade = ""
            for c in grade_check.keys():   #グレードの抜き出し
                if not d.find(class_=c) :continue
                grade_tag = str(d.find(class_=c)).replace("<td class=\"is-p10-5 ", "")\
                    .replace("\"></td>", "").split(" ") #グレードがわかるタグを抜き出し
                grade = grade_check[c]
                if len(grade_tag) > 1:  #グレードオプションがある場合
                    grade += grade_another[grade_tag[1]]
                break
            venue = f"{place}({grade})"     #モーニングorナイターの場合、表記追加
            for t in time_check.keys():
                time_tag = str(d.find(class_=t)).replace("<td class=\"", "")\
                    .replace("\"></td>", "").split(" ")
                if time_tag[0] == t:
                    venue = f"{place}{time_check[t]}({grade})"
            d = re_space.sub("", d.text)
            data.append(d)
            data_p.append(venue)
            #return racer_name, [data_p, data]  # 開催地+データ
        return racer_name,[data_p, data]  # 開催地+データ

def generator(data):
    for d in data:
        yield d

def check(name,data,time):
    p = ""
    re_ZenHan = re.compile(r"[︰-＠一-龥Ａ-Ｚａ-ｚぁ-んァ-ンー]")
    re_num = re.compile(r"[0-9R～/\-]")
    data_gen = generator(data[1])
    #print(data_gen.__next__())
    #print(j.__next__())
    try:
        d = data_gen.__next__()
        if d[:10] == time:
            r_num = re_ZenHan.sub("", d[10:]).split("R")  # レース番号抽出、半角英数以外を消す
            r_name = re_num.sub("", d[10:])    #レース名のみ
            return f"☆{name}☆\n★{data[0][0]}★の\"{r_name}\"\n{r_num[0]}Rと{r_num[1]}Rに出るよ."
        else:
            #d = data_gen.__next__()
            r_name = re_num.sub("", d[10:])  # レース名のみ
            return f"△{name}は本日出場予定無し.\n次節は, {d[:21]}, ★{data[0][0]}★の\"{r_name}\"に出場予定"
    #except IndexError:
    except :
        return f"×{name}は斡旋情報の取得に失敗しました。斡旋情報が無い可能性があります。"
    """
    for d in data[1]:
        #print(name,d)
        try:    #サイト更新ない場合エラーになる可能性あり
            if d[:10]==time:
                r = re.sub(r"[︰-＠一-龥Ａ-Ｚａ-ｚぁ-んァ-ンー]", "", d[10:]).split("R") #レース番号抽出、半角英数以外を消す
                d = re.sub(r"[0-9R\-]", "", d[10:])
                p = f"☆{name}☆\n{data[0][i]}の{d}\n{r[0]}Rと{r[1]}Rに出るよ"
                return p
            else:
                p = f"{name}は出場予定無し"
        except IndexError:
            p = f"[{name}]取得エラー"
    """

    return p     

class Line_notify:
    def __init__(self, data):
        with open("LINE_access_token","r")as f:
            token = f.read()
        self.access_token = token
        self.data = data

    def send_message(self):
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": "Bearer " + self.access_token}

        message = f"\n{self.data}"
        payload = {"message":  message}

        r = requests.post(url, headers=headers, params=payload)


if __name__ == "__main__":
    todays_boat = "https://www.boatrace.jp/owpc/pc/race/index"
    favo_num = ["3188", "3992", "4330", "4556", "4737", "4969", "4947", "5012", "5028"]
    jptime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))  # UTC+9で日本時刻
    jptime = jptime.strftime('%Y/%m/%d %H:%M:%S').split(" ")    #フォーマット合わせ+時刻と分ける
    tmp = []
    p_now = ""
    p_next = ""
    p_error = ""
    for num in favo_num:
        scrape = Scrape(num)
        scrape.crawling()
        name,data = scrape.scraping()
        tmp.append(check(name,data,jptime[0]))

    for p in tmp:   #その日に走る選手を先に表示
        if p[0] == "☆":
            p_now += p + "\n\n"
        elif p[0] == "×":
            p_error += p + "\n\n"
        else:
            p_next += p + "\n\n"

    message = p_now + p_next + p_error + todays_boat

    Line_notify(message).send_message()
    #print(message)
