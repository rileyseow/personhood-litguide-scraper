"""
File: Scrapes selected data from all novels on the Shmoop Literature Study Guides website.
      Creates and records data to shmoop_novel_data.csv.

Global TODOs: Improve efficiency with profiler
              Potential leads: Switch out requests library for an async one
                               Switch out bs4 for lxml entirely
"""

import requests
from bs4 import BeautifulSoup, SoupStrainer
import csv
import re
import charset_normalizer

"""
Function: findNovelPov
Description: Finds Novel POV data if exists
Parameters: BeautifulSoup object (to parse), requests Session object to make a get request
Return: String with POV Description
        "EXC CODE 1" if POV href cannot be found
        "EXC CODE 2" if POV href exists but is not defined succinctly (requires manually navigating to 
        the POV page and looking at description paragraph text)
"""
def scrapePOVData(soupObj, requests_session):
    pov_url = soupObj.find("a", href=re.compile("narrator-point-of-view$"))
    if pov_url is None: return "EXC CODE 1"

    pov_url = pov_url.get("href")
    # Account for relative hrefs
    if (pov_url[0] == '/'):
        pov_url = "https://www.shmoop.com" + pov_url

    # Navigate to the POV page
    response = requests_session.get(pov_url)
    html = response.text
    soupObj = BeautifulSoup(html, "lxml", parse_only=SoupStrainer("h3"))

    pov = soupObj.find("h3")
    if pov is None: return "EXC CODE 2"
    return pov.text.strip()


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


def main():
    # Initialize values
    root_url = "https://www.shmoop.com/study-guides/literature"
    # Novel ID counter
    id = 0
    # Requests Session Object for all get requests
    requests_session = requests.Session()
    # CSV file with headers
    f = open("shmoop_novel_data.csv", "w")
    writer = csv.writer(f)
    header = ["Novel ID", "Novel URL", "Title", "Author", "POV"]
    writeCSV(writer, header)

    print("Initializing scrape...")

    # Go through all pages of Literature Study Guides (95x)
    for i in range(1, 96):
        page_url = root_url + "/index/?p=" + str(i)

        # Generate BeautifulSoup object to parse the page
        response = requests_session.get(page_url)
        html = response.text
        soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer(["a", "div"]))

        # Find all novel URLs and titles on the page
        # All novels scraped will have URLs and titles, so no error checking required
        urls = soup.findAll("a", class_="details")
        titles = soup.findAll("div", class_="item-info")

        # For each novel on the page...
        for url, title in zip(urls, titles):
            novel_url = url.get("href")

            # Store the first three values in a list: ID, URL, and Title
            ch = [id, novel_url, title.text.strip()]

            # Print status data to console
            if id % 10 == 0: print("ID ", str(id))
            # Increment Novel ID counter
            id += 1

            # Navigate to each novel's page with BeautifulSoup
            # Then add Author and POV to the list of values
            response = requests_session.get(novel_url)
            html = response.text
            soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer(["span", "div"]))

            # Look for author info
            try:
                author = soup.find("span", class_="author-name").text.strip()
            except:
                author = "EXC CODE 1"
            ch.append(author)

            # Look for POV info
            # Narrows down HTML area to LH nav bar for parsing
            analysisBarSoupObj = soup.find("div", class_="nav-menu")
            pov = scrapePOVData(analysisBarSoupObj, requests_session)
            ch.append(pov)

            # Write the entire row of data to the CSV file
            writeCSV(writer, ch)

    # Close the CSV file
    f.close()


if __name__ == "__main__":
    main()
