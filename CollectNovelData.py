"""
File: Scrapes selected data from all novels on the Shmoop Literature Study Guides website.
      Creates and records data to shmoop_novel_data.csv.
"""

import asyncio
import aiohttp
import time
import lxml.html
import csv
import re
import charset_normalizer


"""
Function: writeCSV
Description: Writes novel data to CSV file. 
             For reference: CSV headers = Novel ID, Novel URL, Title, Author, POV.
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
    # Initialize values: Root URL and Novel ID counter
    root_url = "https://www.shmoop.com/study-guides/literature"
    id = 0
    dataToWrite = []
    novelURLs = []
    POVURLs = []

    # Open CSV file with headers to write to
    f = open("shmoop_novel_data.csv", "w")
    writer = csv.writer(f)
    header = ["Novel ID", "Novel URL", "Title", "Author", "POV"]
    writeCSV(writer, header)

    start_time = time.time()
    print(f"[{round(time.time() - start_time, 4)}s] (+2.5s) Initializing scrape of all Literature Study Guide catalog pages...")

    # Use asyncio to download all Literature Study Guide catalog pages (95x)
    # Note: Can toggle limit of aiohttp simultaneous connections between 10-20 (default 100).
    # If blocked from server, try reducing limit.)
    my_conn = aiohttp.TCPConnector(limit=20, ssl=False)
    # Increase the timeout from default 300s to 600s.
    my_timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(connector=my_conn, timeout=my_timeout) as session:
        tasks = []
        for i in range(1, 96):
            page_url = root_url + "/index/?p=" + str(i)
            tasks.append(asyncio.ensure_future(downloadLink(session, page_url)))
        studyGuidePageHTMLs = await asyncio.gather(*tasks, return_exceptions=True)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Logging Novel URL and Novel Title data...")

    for pageHTML in studyGuidePageHTMLs:
        # Use lxml to parse the catalog page for Novel URL and Novel Title info
        # All novels scraped will have URLs and titles, so no error checking required
        root = lxml.html.fromstring(pageHTML)
        urls = root.xpath("//a[@class='details']/@href")
        titles = root.xpath("//div[@class='item-info']/text()")

        # For each novel on the page...
        for url, title in zip(urls, titles):
            # Store the first three values in a list: ID, URL, and Title
            dataToWrite.append([id, url, title.strip()])
            novelURLs.append(url)

            # Increment Novel ID counter
            id += 1

    print(f"[{round(time.time() - start_time, 4)}s] (+15s) Initializing scrape of all novel pages...")

    # Use asyncio to download all novel pages
    my_conn2 = aiohttp.TCPConnector(limit=20, ssl=False)
    async with aiohttp.ClientSession(connector=my_conn2, timeout=my_timeout) as session2:
        tasks2 = [asyncio.ensure_future(downloadLink(session2, url)) for url in novelURLs]
        novelHTMLs = await asyncio.gather(*tasks2, return_exceptions=True)

    print(f"[{round(time.time() - start_time, 4)}s] (+3s) Logging novel author data...")

    for novel, html in zip(dataToWrite, novelHTMLs):
        # Use lxml to parse the novel page for Author and POV info
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
            POVURLs.append(pov_url)
            novel.append("placeholder")

    print(f"[{round(time.time() - start_time, 4)}s] (+20s) Initializing scrape of all novel POV pages...")

    # Use asyncio to download all POV pages
    my_conn3 = aiohttp.TCPConnector(limit=20, ssl=False)
    async with aiohttp.ClientSession(connector=my_conn3, timeout=my_timeout) as session3:
        tasks3 = [asyncio.ensure_future(downloadLink(session3, url)) for url in POVURLs]
        POVHTMLs = await asyncio.gather(*tasks3, return_exceptions=True)

    print(f"[{round(time.time() - start_time, 4)}s] (+3s) Logging novel POV data...")

    # Logs "EXC CODE 1" if POV href cannot be found and
    #      "EXC CODE 2" if POV href exists but is not defined succinctly
    #      (requires manually navigating to the POV page and looking at description paragraph text)
    i = 0
    for novel in dataToWrite:
        if novel[-1] == "EXC CODE 1":
            continue
        else:
            # Use lxml to parse the POV page for POV description data
            root = lxml.html.fromstring(POVHTMLs[i])
            i += 1
            pov = root.xpath("//h3[1]/descendant-or-self::*/text()")
            if len(pov) == 0:
                novel[-1] = "EXC CODE 2"
            else:
                novel[-1] = "".join(pov).strip()

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Initializing data read-out...")

    # Write out all rows of character data to shmoop_novel_data.csv
    for row in dataToWrite:
        writeCSV(writer, row)

    # Close the CSV file
    f.close()

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Finished.")


if __name__ == "__main__":
    asyncio.run(main())
