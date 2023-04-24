"""
File: Scrapes selected character data from all novels on the Shmoop Literature Study Guides website.
      Creates and records data to shmoop_character_data.csv.
      Should be run after a complete and successful run of CollectNovelData.py

Global TODOs: Finish basic implementation. Add error checking. Run on entire dataset.
"""

import requests
from bs4 import BeautifulSoup, SoupStrainer
import csv
import re
import charset_normalizer


"""
Function: readCSV
Description: Reads in novel data from shmoop_novel_data.csv
Parameters: CSV reader object, int columns to read
Return: List of Lists for each row of data read from the CSV
"""
def readCSV(reader, colsToRead):
    # Exclude header row
    next(reader)

    slice = []
    for row in reader:
        colsSubset = []
        for i in range(colsToRead):
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


def main():
    # Initialize requests Session Object for all get requests
    requests_session = requests.Session()

    # Open CSV file with headers to write to
    f = open("shmoop_character_data.csv", "w")
    writer = csv.writer(f)
    header = ["Novel ID", "Character Name", "Character URL", "Character Description"]
    writeCSV(writer, header)

    print("Initializing data read-in...")

    # Read in a list of [Novel ID, Novel URL]s from shmoop_novel_data.csv
    f = open("shmoop_novel_data.csv", "r")
    reader = csv.reader(f)
    CSVNovelData = readCSV(reader, 2)

    print("Initializing scrape...")

    # For each novel...
    #for novel in CSVNovelData:
    for novel in CSVNovelData[:3]:
        # Generate BeautifulSoup object to parse the novel page for Character Name and Character Info
        # Use SoupStrainer to limit parsing to the LH nav bar
        response = requests_session.get(novel[1])
        html = response.text
        soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer("div", class_="nav-menu"))

        # Find all character tag elements
        parent = soup.find("a", href=re.compile("characters$")).find_next()
        characterElems = parent.findAll("li", class_=None)

        # For each character...
        for character in characterElems:
            # Find name and URL info
            name = character.text.strip()
            url = character.find("a").get("href")
            if url[0] == '/': url = "https://www.shmoop.com" + url

            # Store the first three values in a list: Novel ID, Character Name, and Character URL
            ch = [novel[0], name, url]

            """
            # Generate BeautifulSoup object to parse the character page URL for Character Description info
            response = requests_session.get(url)
            html = response.text
            soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer(_____))

            # Find description info and append to row data
            desc = soup.find(_____)
            ch.append(desc)
            """

            # Write entire row of character data to shmoop_character_data.csv
            writeCSV(writer, ch)

    # Close the CSV file
    f.close()


if __name__ == "__main__":
    main()