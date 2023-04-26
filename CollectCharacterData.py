"""
File: Scrapes selected character data from all novels on the Shmoop Literature Study Guides website.
      Creates and records data to shmoop_character_data.csv.
      Should be run after a complete and successful run of CollectNovelData.py

Global TODOs: Improve efficiency (see CollectNovelData.py header comment)
"""

import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup, SoupStrainer
import csv
import re
import charset_normalizer


"""
Function: readCSV
Description: Reads in novel data from shmoop_novel_data.csv
Parameters: CSV reader object, int start column, int columns to read
Return: List of Lists for each row of data read from the CSV
"""
def readCSV(reader, startCol, colsToRead):
    # Exclude header row
    next(reader)

    slice = []
    for row in reader:
        colsSubset = []
        for i in range(startCol, startCol + colsToRead):
            colsSubset.append(row[i])
        slice.append(colsSubset)
    return slice


"""
Function: writeCSV
Description: Writes character data to CSV file. 
             For reference: CSV headers = Novel ID, Character Name, Character URL, Character Description.
Parameters: CSV writer object, list (row of data to write)
Return: int (0, dummy value)
"""
def writeCSV(writer, row):
    writer.writerow(row)

    # Return dummy value for now
    return 0


"""
Function: downloadLink
Description: Uses asyncio / aiohttp library to download a url passed as an argument
Parameters: aiohttp.ClientSession() object, string (url to download)
Return: HTML text of one URL page
"""
async def downloadLink(session, url):
    async with session.get(url) as resp:
        html = await resp.text()
        return html


async def main():

    # Initialize values
    start_time = time.time()
    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Starting...")
    novelID = 0
    dataToWrite = []
    characterURLs = []

    # Open CSV file with headers to write to
    f = open("shmoop_character_data.csv", "w")
    writer = csv.writer(f)
    header = ["Novel ID", "Character Name", "Character URL", "Character Description"]
    writeCSV(writer, header)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Initializing data read-in...")

    # Read in a list of Novel URLs from shmoop_novel_data.csv
    f = open("shmoop_novel_data.csv", "r")
    reader = csv.reader(f)
    CSVNovelURLs = readCSV(reader, 1, 1)
    # Flatten list since readCSV will return a list of lists but we only read in one column
    CSVNovelURLs = [url for subList in CSVNovelURLs for url in subList]

    print(f"[{round(time.time() - start_time, 4)}s] (+30-40s) Initializing scrape of all novel homepages...")

    # Use asyncio to download all novel pages
    # Note: Can toggle limit of aiohttp simultaneous connections between 10-20 (default 100).
    # If blocked from server, try reducing limit.)
    my_conn = aiohttp.TCPConnector(limit=20, ssl=False)
    # Increase the timeout from default 300s to 600s.
    my_timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(connector=my_conn, timeout=my_timeout) as session:
        tasks = [asyncio.ensure_future(downloadLink(session, url)) for url in CSVNovelURLs]
        novelHTMLs = await asyncio.gather(*tasks, return_exceptions=True)

    print(f"[{round(time.time() - start_time, 4)}s] (+10s) Logging Character Name and Character URL data...")

    for page in novelHTMLs:
        # Generate BeautifulSoup object to parse the novel page for Character Name and Character URL info
        # Use SoupStrainer to limit parsing to the LH nav bar
        soup = BeautifulSoup(page, "lxml", parse_only=SoupStrainer("div", class_="nav-menu"))

        # Find all character tag elements
        try:
            parent = soup.find("a", href=re.compile("characters$")).find_next()
            characterElems = parent.findAll("li", class_=None)
        except:
            characterElems = ["EXC CODE 1"]

        # Find name and URL info for each character
        for character in characterElems:
            if character == "EXC CODE 1":
                name = "EXC CODE 1"
                url = "EXC CODE 1"
            else:
                # Edge case: "The Princess Bride" incorrectly lists William Goldman (the author) as a character.
                # Clicking his name leads to a dead ERR_TOO_MANY_REDIRECTS page and crashes this code.
                # Thus, do not identify him as a character.
                if character.find("a").get("href").endswith("william-goldman"): continue

                name = character.text.strip()
                url = character.find("a").get("href")
                if url[0] == '/': url = "https://www.shmoop.com" + url

            # Store the first three values in a list: Novel ID, Character Name, and Character URL
            dataToWrite.append([novelID, name, url])
            characterURLs.append(url)

        novelID += 1

    print(f"[{round(time.time() - start_time, 4)}s] (+4-5mins) Initializing scrape of all character pages...")

    # Use asyncio to download all character pages
    my_conn2 = aiohttp.TCPConnector(limit=20, ssl=False)
    async with aiohttp.ClientSession(connector=my_conn2, timeout=my_timeout) as session2:
        tasks2 = [asyncio.ensure_future(downloadLink(session2, url)) for url in characterURLs]
        characterHTMLs = await asyncio.gather(*tasks2, return_exceptions=True)

    print(f"[{round(time.time() - start_time,4)}s] (+1-2mins) Logging character description data...")

    for character, html in zip(dataToWrite, characterHTMLs):
        # Generate BeautifulSoup object to parse the character's page for Character Description info
        soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer("div", class_="content-wrapper"))

        # Find description info (raw HTML, no cleanup) and append to row data
        try:
            desc = soup.findChild().findChild()
        except:
            desc = "EXC CODE 2"

        character.append(desc)

    print(f"[{round(time.time() - start_time, 4)}s] (+2s) Initializing data read-out...")

    # Write out all rows of character data to shmoop_character_data.csv
    for row in dataToWrite:
        writeCSV(writer, row)

    # Close the CSV file
    f.close()

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Finished.")


if __name__ == "__main__":
    asyncio.run(main())