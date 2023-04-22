
# Literary Lab Webscraper

This is a Python webscraper that takes character data from Shmoop's Literature Study Guides (https://www.shmoop.com/study-guides/literature). 

Scraping Specifications: 
- 95 pages of ~12 novels per page
- Compiles all character data for each novel and writes it to .csv files
- Novel csv headers: 
    - novel_url
    - title
    - author
    - POV
- Character csv headers:
    - novel_url
    - character_url
    - character_name
    - character_desc

Uses imports requests, csv, re, and of course BeautifulSoup (https://www.crummy.com/software/BeautifulSoup/bs4/doc).

Originally written for the Literary Lab as part of a CESTA internship (Summer 2020). Being redone now for practice purposes.

Contributor: Riley Seow
