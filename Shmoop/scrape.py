"""
File: Scrapes HTML pages for relevant info using library lxml.html (with xpath).
"""

# lxml.html comes with built-in xpath 1.0.0
import lxml.html

# Charset-normalizer deals with character encoding detection.
# Imported for faster parsing based on something I read online. Unsure if it makes a real difference.
import charset_normalizer

# Local file imports
import config


"""
Function: catalogPages
Description: Uses lxml to parse catalog pages for Novel URL and Novel Title info.
             (All novels scraped will have URLs and titles, so no error checking required.)
             Stores a list of novel info (ID, url, and title) to global variable fDataToWrite.
Parameters: list (strings of catalog HTML pages to parse)
Return: list of all Novel URLs found in parsing the page
"""
def catalogPages(catalogPageHTMLs):
    novelID = 0
    allNovelURLs = []

    for pageHTML in catalogPageHTMLs:
        root = lxml.html.fromstring(pageHTML)
        urls = root.xpath("//a[@class='details']/@href")
        titles = root.xpath("//div[@class='item-info']/text()")

        # For each novel on the page...
        for url, title in zip(urls, titles):
            # Store the first three values in a list: ID, URL, and Title
            config.fDataToWrite.append([novelID, url, title.strip()])
            allNovelURLs.append(url)

            # Increment Novel ID counter
            novelID += 1

    return allNovelURLs


"""
Function: catalogPages
Description: Uses lxml to parse novel homepages for Author and POV URL info.
             Appends author name info to relevant index row of global variable fDataToWrite.
Parameters: list (strings of novel HTML pages to parse)
Return: list of all POV URLs found in parsing the page
"""
def novelPages(novelPageHTMLs):
    allPOVURLs = []

    for novel, html in zip(config.fDataToWrite, novelPageHTMLs):
        root = lxml.html.fromstring(html)

        # Find author and append to row data
        # If author name does not exist, will return boolean False
        author = root.xpath("//span[@class='author-name']/descendant-or-self::*/text()")
        if len(author) == 0:
            novel.append("EXC CODE 1")
        else:
            novel.append("".join(author).strip())

        # Find POV page URL, if exists
        pov_url = root.xpath("//a[contains(@href, 'narrator-point-of-view')]/@href")
        if len(pov_url) == 0:
            novel.append("EXC CODE 1")
        else:
            # Account for relative hrefs
            if (pov_url[0][0] == '/'):
                pov_url = "https://www.shmoop.com" + pov_url[0]
            allPOVURLs.append(pov_url)
            novel.append("placeholder")

    return allPOVURLs


"""
Function: POVPages
Description: Uses lxml to parse novel POV pages for POV info.
             Appends POV info to relevant index row of global variable fDataToWrite.
             
             Logs "EXC CODE 1" if POV href cannot be found and
                  "EXC CODE 2" if POV href exists but is not defined succinctly
                  (requires manually navigating to the POV page and looking at description paragraph text)
                  
Parameters: list (strings of POV HTML pages to parse)
Return: void
"""
def POVPages(POVPageHTMLs):
    index = 0

    for novel in config.fDataToWrite:
        if novel[-1] == "EXC CODE 1":
            continue
        else:
            # Use lxml to parse the POV page for POV description data
            root = lxml.html.fromstring(POVPageHTMLs[index])
            index += 1
            pov = root.xpath("//h3[1]/descendant-or-self::*/text()")
            if len(pov) == 0:
                novel[-1] = "EXC CODE 2"
            else:
                novel[-1] = "".join(pov).strip()


"""
Function: novelPageCharacters
Description: Uses lxml to parse novel homepages for character name and character URL info.
             Stores a list of character info (novel ID, character name, and character url) to global variable gDataToWrite.
Parameters: list (strings of novel HTML pages to parse)
Return: list of all character page URLs found in parsing the page
"""
def novelPageCharacters(novelPageHTMLs):
    novelID = 0
    allCharacterURLs = []

    for page in novelPageHTMLs:
        root = lxml.html.fromstring(page)

        # Find all character tag elements
        characterElems = root.xpath("//a[contains(@href, 'characters')]/following-sibling::ul[1]/li[not(@class)]")
        if len(characterElems) == 0:
            characterElems = ["EXC CODE 2"]

        # Find name and URL info for each character
        for character in characterElems:
            if character == "EXC CODE 2":
                name = "EXC CODE 2"
                url = "EXC CODE 2"
            else:
                # Edge case: "The Princess Bride" incorrectly lists William Goldman (the author) as a character.
                # Clicking his name leads to a dead ERR_TOO_MANY_REDIRECTS page and crashes this code.
                # Thus, do not identify him as a character.
                if character.xpath("./a/@href")[0].endswith("william-goldman"): continue

                name = character.xpath("./a/descendant-or-self::*/text()")
                name = "".join(name).strip()
                url = character.xpath("./a/@href")[0]
                if url[0] == '/': url = "https://www.shmoop.com" + url

                allCharacterURLs.append(url)

            # Store the first three values in a list: Novel ID, Character Name, and Character URL
            config.gDataToWrite.append([novelID, name, url])

        novelID += 1

    return allCharacterURLs


"""
Function: characterPages
Description: Uses lxml to parse character pages for character description info.
             Appends description info to relevant index row of global variable gDataToWrite.
Parameters: list (strings of character HTML pages to parse)
Return: void
"""
def characterPages(characterPageHTMLs):
    characterPageHTMLsIndex = 0

    for character in config.gDataToWrite:
        if character[1] == "EXC CODE 2":
            character.append("EXC CODE 2")
            continue
        else:
            # Use lxml to parse the character's page for Character Description info
            root = lxml.html.fromstring(characterPageHTMLs[characterPageHTMLsIndex])

            # Find description info (raw HTML, no cleanup) and append to row data
            desc = root.xpath("//div[@class='content-wrapper']/*[1]")
            if len(desc) == 0:
                character.append("EXC CODE 2")
            else:
                # Raw HTML
                descStr = lxml.html.tostring(desc[0], encoding='unicode', method='html')
                # Minimal cleanup: Shmoop's random line-breaks
                descStr = descStr.replace("\r\n", " ").replace("\n", " ").replace("  ", " ")
                # Append to row data
                character.append(descStr)

            characterPageHTMLsIndex += 1