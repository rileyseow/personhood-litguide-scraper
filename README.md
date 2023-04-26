
# Literary Lab Webscraper

This is a Python webscraper that takes character data from Shmoop's Literature Study Guides (https://www.shmoop.com/study-guides/literature). 

Scraping Specifications: 
- Compiles novel data (95 pages of ~12 novels per page) and writes it to shmoop_novel_data.csv
- Compiles character data for each novel (13547 characters total) and writes it to shmoop_character_data.csv
- Novel csv header columns: 
    - Novel ID
    - Novel URL
    - Title
    - Author
    - POV
- Character csv header columns:
    - Novel ID
    - Character URL
    - Character Name
    - Character Description
- Error codes:
    - "EXC CODE 1": Relevant value was not found
    - "EXC CODE 2": Relevant value was found, but is otherwise complicated. May involve longer paragraph text than expected, be found in a different location than expected, etc. Recommended: manual correction during data clean-up.
- Expansions in progress:
    - Replacing bs4 scraping with the lower-level lxml library (optimization)
    - Expanding scraper to other study guide websites: LitCharts, SparkNotes, and CliffNotes (scalability)

Uses imports asyncio, aiohttp, time, csv, re, charset_normalizer, and BeautifulSoup (https://beautiful-soup-4.readthedocs.io/en/latest/) with SoupStrainer.

Originally written for the Literary Lab as part of a CESTA internship (Summer 2020). Being redone now for practice purposes.

Contributor: Riley Seow
