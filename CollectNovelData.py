"""
File: Scrapes selected data from all novels on the Shmoop Literature Study Guides website.
      Creates and writes to csv file.
"""

import requests
from bs4 import BeautifulSoup
import csv
import re

"""
Function: Finds Novel POV data if exists
Parameters: BeautifulSoup object to parse
Return: String with POV Description
        "EXC CODE 1" if POV href cannot be found
        "EXC CODE 2" if POV href exists but is not defined succinctly (requires manually navigating to 
        the POV page and looking at description paragraph text)
"""
def findNovelPov(soupObj):
    pov_url = soupObj.find("a", href=re.compile("narrator-point-of-view$"))
    if pov_url is None: return "EXC CODE 1"

    pov_url = pov_url.get("href")
    # Account for relative hrefs
    if (pov_url[0] == '/'):
        pov_url = "https://www.shmoop.com"+ pov_url

    # Navigate to the POV url page
    response = requests.get(pov_url)
    html = response.text
    soupObj = BeautifulSoup(html, "html.parser")

    pov = soupObj.find("h3")
    if pov is None: return "EXC CODE 2"
    return pov.text.strip()


"""
Function: Writes novel data to CSV file. CSV headers = Novel ID, Novel URL, Title, Author, POV.
Parameters:
Return:
"""
def writeCSV(writer, row):
    writer.writerow(row)

    # Return dummy value for now
    return 0

def main():
    #Initialize values
    # First / root Schmoop URL page
    root_url = "https://www.shmoop.com/study-guides/literature"
    # Novel ID counter
    id = 0
    # CSV file with headers
    f = open("shmoop_novel_data.csv", "w")
    writer = csv.writer(f)
    header = ["Novel ID", "Novel URL", "Title", "Author", "POV"]
    writeCSV(writer, header)

    # Go through all pages of Literature Study Guides (95x)
    # For each page, write all novel URLs and titles to the CSV file
    for i in range(1, 3): #change to 96
        page_url = root_url + "/index/?p=" + str(i)

        # Generate BeautifulSoup object to parse the page
        response = requests.get(page_url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Find all novel URLs and titles on the page
        urls = soup.findAll("a", attrs={"class": "details"})
        titles = soup.findAll("div", attrs={"class": "item-info"})

        for url, title in zip(urls, titles):
            novel_url = url.get("href")

            # Store the first three values for the novel in a list: ID, URL, and Title
            ch = [id, novel_url, title.text.strip()]
            id += 1
            # Print status data to console
            print("Currently scraping novel with ID ", str(id))

            # Navigate to each novel's page with BeautifulSoup
            # Then add Author and POV to the list of values
            response = requests.get(novel_url)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Look for author info
            author = soup.find("span", attrs={"class": "author-name"}).text.strip()
            ch.append(author)

            # Narrows down HTML area to LH nav bar for more efficient BS parsing
            analysisBarSoupObj = soup.find("div", attrs={"class": "nav-menu"})
            # Look for POV info
            pov = findNovelPov(analysisBarSoupObj)
            ch.append(pov)

            # Write the entire row of data to the CSV file
            writeCSV(writer, ch)

    # Close the CSV file
    f.close()


if __name__ == "__main__":
    main()