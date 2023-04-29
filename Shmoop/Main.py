"""
File: Scrapes selected novel and character data from all novels on the Shmoop Literature Study Guides website.
      Creates and records data to 2 CSV files: shmoop_novel_data.csv and shmoop_character_data.csv.
"""

# Package / Dependency imports
import time
import csv
import asyncio

# Local file imports
import download
import scrape
import config


async def main():
    start_time = time.time()
    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Starting...")

    # Open 2 CSV files with headers to write to
    f = open("shmoop_novel_data.csv", "w")
    fWriter = csv.writer(f)
    fHeader = ["Novel ID", "Novel URL", "Title", "Author", "POV"]
    fWriter.writerow(fHeader)

    g = open("shmoop_character_data.csv", "w")
    gWriter = csv.writer(g)
    gHeader = ["Novel ID", "Character Name", "Character URL", "Character Description"]
    gWriter.writerow(gHeader)

    print(f"[{round(time.time() - start_time, 4)}s] (+2.5s) Initializing scrape of all Literature Study Guide catalog pages...")

    # Use asyncio to download all Literature Study Guide catalog pages (95x)
    root_url = "https://www.shmoop.com/study-guides/literature"
    catalogURLs = [root_url + "/index/?p=" + str(i) for i in range(1,96)]
    studyGuidePageHTMLs = await download.downloadAll(catalogURLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Logging Novel URL and Novel Title data...")

    # Use lxml to parse the catalog pages for Novel URL and Novel Title info
    novelURLs = scrape.catalogPages(studyGuidePageHTMLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+25s) Initializing scrape of all novel homepages...")

    # Use asyncio to download all novel pages
    novelHTMLs = await download.downloadAll(novelURLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+3s) Logging novel author data...")

    # Use lxml to parse the novel pages for Author and POV URL info
    POVURLs = scrape.novelPages(novelHTMLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+20s) Initializing scrape of all novel POV pages...")

    # Use asyncio to download all POV pages
    POVHTMLs = await download.downloadAll(POVURLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+3s) Logging novel POV data...")

    # Use lxml to parse the POV pages for POV info
    scrape.POVPages(POVHTMLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Initializing data read-out...")

    # Write out all rows of novel data to shmoop_novel_data.csv
    fWriter.writerows(config.fDataToWrite)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) -------------------------------------------------")
    print(f"[{round(time.time() - start_time, 4)}s] (+0s) DONE with all novel data.")
    print(f"[{round(time.time() - start_time, 4)}s] (+0s) -------------------------------------------------")

    print(f"[{round(time.time() - start_time, 4)}s] (+3s) Logging character name and character URL data...")

    # Use lxml to parse the novel pages for character name and character URL info
    characterURLs = scrape.novelPageCharacters(novelHTMLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+5-8mins) Initializing scrape of all character pages...")

    # Use asyncio to download all character pages
    characterHTMLs = await download.downloadAll(characterURLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+35s) Logging character description data...")

    # Use lxml to parse the character pages for character description info
    scrape.characterPages(characterHTMLs)

    print(f"[{round(time.time() - start_time, 4)}s] (+1s) Initializing data read-out...")

    # Write out all rows of character data to shmoop_character_data.csv
    gWriter.writerows(config.gDataToWrite)

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) DONE with all character data.")

    # Close the CSV file
    f.close()
    g.close()

    print(f"[{round(time.time() - start_time, 4)}s] (+0s) Finished.")



if __name__ == "__main__":
    asyncio.run(main())