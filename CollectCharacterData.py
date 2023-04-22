import requests
from bs4 import BeautifulSoup
import csv
import re

"""
grabbing characters of one novel on schmoop and writing to csv
"""
def main():
    ## 1. in main page
    root_url = "https://www.shmoop.com/study-guides/literature"
    response = requests.get(root_url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    #title
    novelTitle = soup.find("div", attrs={"class": "item-info"}).text.strip()
    print(novelTitle)

    #url
    novelUrl = soup.find("a", attrs={"class": "details"}).get("href")
    print(novelUrl)

    ## 2. in novel page
    novel_url = novelUrl
    response = requests.get(novel_url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")


    #author
    novelAuthor = soup.find("span", attrs={"class": "author-name"}).text.strip()
    print(novelAuthor)

    # character url(s) + name(s)
    parentElem = soup.find("a", href=re.compile("characters$")).find_next()
    characterElems = parentElem.findAll("li")
    characterUrls = []
    characterNames = []
    for character in characterElems:
        # name(s)
        name = character.text.strip()
        characterNames.append(name)
        print(name)

        #url(s)
        url = character.find("a").get("href")
        if (url[0] == '/'):
            url = "https://www.shmoop.com" + url  # accounts for relative hrefs
        characterUrls.append(url)
        print(url)

    #pov
    novelPovUrl = soup.find("a", href=re.compile("narrator-point-of-view$")).get("href")
    if (novelPovUrl[0] == '/'):
        novelPovUrl = "https://www.shmoop.com"+ novelPovUrl #accounts for relative hrefs
    print(novelPovUrl)

    ## 3. in POV page
    pov_url = novelPovUrl
    response = requests.get(pov_url)
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    novelPov = soup.find("h3").text.strip()
    print(novelPov)

    #character description
    ## 4. in individual character page
    #####FINISH LATER

    """
    CSV headings: novel_url, title, author, POV, 
    character_url, character_name, character_desc
    """
    #writing to csv file
    f = open("shmoop_character_data.csv", "w")
    writer = csv.writer(f)

    header = ["Novel URL", "Title", "Author", "POV", "Character URL", "Character Name"]
    writer.writerow(header)

    for i in range(len(characterNames)):
        ch = [novelUrl, novelTitle, novelAuthor, novelPov, characterUrls[i], characterNames[i]]
        writer.writerow(ch)

    f.close()

if __name__ == "__main__":
    main()