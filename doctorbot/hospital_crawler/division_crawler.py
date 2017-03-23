import requests
import re
from lxml import etree


class DivisionCrawler(object):
    def __init__(self):
        self.division = []

    def crawl_search_result(self):
        url = "https://www.ntuh.gov.tw/MedicalTeams/%E9%86%AB%E5%B8%AB%E6%9F%A5%E8%A9%A2_table.aspx"
        r = requests.get(url)
        html = r.content.decode('utf-8')
        page = etree.HTML(html)

        result = []
        for division in page.xpath("//tr"):
            result.append(division.xpath(".//text()"))

        # Preprocessing doctor cloumn

        c = 0
        fs = []
        ss = []
        ts = []
        inin = []
        res = []
        for row in result:
            i = False
            temp = "".join(row)
            if (temp.find('部') != -1 or temp.find('中心') != -1 or temp.find('醫院') != -1):
                inin = [fs, ss, ts]
                if (ts != []):
                    res.append(inin)
                fs = []
                ss = []
                ts = []
                inin = []
                if (temp.find('部') != -1):
                    a = temp.index('部')
                elif (temp.find('中心') != -1):
                    a = temp.index('心')
                else:
                    a = temp.index('院')
                fs = temp[0:a + 1]
                if (temp.find('專') != -1):
                    b = temp.index('專')
                    ss = temp[a + 1:b]
                    ts = temp[b:]
            else:
                tempts = [ts, temp]
                ts = "".join(ts)
        inin = [fs, ss, ts.split("、")]
        res.append(inin)

        # Preprocessing disease cloumn

        parse_list = []
        first_row = ["division", "disease", "doctor"]
        parse_list.append(first_row)

        for index, row in enumerate(res):
            if index != 0:
                new_row = []
                for i, col in enumerate(row):
                    if i != 1:
                        new_row.append(col)
                    else:
                        splited_list = col.split("、")
                        clean_list = []
                        for item in splited_list:
                            clean_list.extend(re.split('（|\(|\)|）', item))
                        new_row.append(list(filter(None, clean_list)))
                parse_list.append(new_row)

        return parse_list

def main():
    dc = DivisionCrawler()
    dc.crawl_search_result()

if __name__ == '__main__':
    main()
