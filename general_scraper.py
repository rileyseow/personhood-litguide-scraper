#imports
from urllib.request import urlopen as uReq  # Web client
from bs4 import BeautifulSoup as soup  # HTML data structure
from pathlib import Path
import os
import time
from datetime import datetime

# NOTES:
# 1. didn't include gradesaver for now: has irregular (non recursive) url hierarchy :/


#TO DO:
# timeouts are not functional right now, but i am keeping track of time values in the csv file.
# maybe make directory for each guide? (if so, make directories entirely before scraping, not as i go)
    # i don't see a way to do this without doing it as i go... ?
# maybe: change cwd stuff to path format

# note to self; timeout error is the error i'll get if they block me due to too many reqs
# if functions can go wrong, put in try block

""" CURRENTLY RUNNING ONLY ON LITCHARTS TO FIGURE OUT BUG: """

"""
kWebsites = {
    'LitCharts': 'https://www.litcharts.com/lit', # around 65,300 urls ?
    'Shmoop': 'https://www.shmoop.com/study-guides/literature', # around 85,300 urls
    'SparkNotes': 'https://www.sparknotes.com/lit', # around 36,300 urls
    'CliffsNotes': 'https://www.cliffsnotes.com/literature' # around 24,800 urls
} """
kWebsites = { 'LitCharts': 'https://www.litcharts.com/lit'
}
kBadPunct = {'/': '-',
             '<': '-',
             '>': '-',
             ':': '-',
             '"': '-',
             '\\': '-',
             '|': '-',
             '?': '-',
             '*': '-',
             ' ': '' }
# kBadPunct = '/<>:"\\|?*'

class Guide:
    """
    Class structure for every lit guide website.
    """
    def __init__(self, url, path, name):
        self.name = name #maybe unnecessary?
        self.root_url = url
        self.urls_left = {url}
        self.visited = set()
        self.guides_remaining = True
        self.directory = self.setup_dirs(path)

    def setup_dirs(self, path):
        # use Path.joinpath(NAME) to figure out the directory path (e.g. dh/guide_scraping/gradesaver/)
        # use Path.mkdir() to make a directory in the new path we just made
        # return the path to the new directory
        path = path.joinpath(self.name)
        path.mkdir()
        return path

    def get_page(self, csvFile):
        # Download one page from the set of all urls, adding it to the
        # set of visited urls, and updating all urls with any new urls
        # for the page

        # check that there still pages to scrape
        if len(self.urls_left) != 0:
            # find a page to get and then download it:
            ### note to self: .pop() randomly removes an element (sets are unordered)
            ###               and automatically removes an element from the set.
            page_url = self.urls_left.pop()

            ### opens the connection and downloads html page into local directory
            try:
                xClient = uReq(page_url)
            except Exception as e1:
                print(e1)
                # try again
                try:
                    xClient = uReq(page_url)
                except Exception as e2:
                    Print("Second try failed too :(")

            page_html = str(xClient.read())
            xClient.close()
            save_page(page_url, page_html, self.directory, self.name)

            # update the visited urls to include the one just downloaded
            self.visited.add(page_url)
            csvFile.write(page_url + ", ")

            # add all the (new) urls to the url set
            # * links must be internal & children to the "guides" section of the site
            #   eg.) we only want pages that start with "shmoop.com/study-guides/literature"
            uClient = uReq(page_url)
            page_soup = soup(uClient.read(), "html.parser")
            uClient.close()
            new_urls = page_soup.findAll("a", {"href": True})
            for url in new_urls:
                if url not in self.visited:
                    # the following lines are a bit more complicated because
                    # for some sites, internal html links are sometimes truncated
                    if self.root_url in url['href']:
                        self.urls_left.add(url['href'])
                    elif (self.name == 'Shmoop' and url['href'].startswith('/study-guides/literature')):
                        root = self.root_url.partition('/study-guides')[0]
                        self.urls_left.add(root + url['href'])
                    elif (self.name != 'Shmoop' and url['href'].startswith('/lit')):
                        root = self.root_url.partition('/lit')[0]
                        self.urls_left.add(root + url['href'])

        # returns
        if len(self.urls_left) == 0:
            self.guides_remaining = False
        return self.guides_remaining

def save_page(url, page, path, name):
    out_filename = url

    # replace kBadPunct characters with hyphens and truncate filenames to 50 chars
    out_filename = out_filename.translate(str.maketrans(kBadPunct))
    if url not in kWebsites.values():
        out_filename = out_filename[len(kWebsites[name]):]
    if len(out_filename) > 45:
        out_filename = out_filename[:45] + ".html"
    else:
        out_filename = out_filename + ".html"

    stemDir = os.getcwd()
    os.chdir(path)

    with open(out_filename, 'w') as f:
        try:
            f.write(page)
            f.close()
        except Exception as err:
            print(err)

    os.chdir(stemDir)


def main():
    # try to get data all in one pass alternating requests for downtime between sites
    # use time outs / second passes as necessary
    GuideObjList = []
    for guideName in kWebsites.keys():
        url = kWebsites[guideName]
        path = Path(os.getcwd())
        GuideObjList.append(Guide(url, path, guideName))

    g = open("downloaded_sites_list.csv", "w")
    headers = "site, url, time, errors \n"
    g.write(headers)

    counter = 0
    pagesRemain = True
    siteName = GuideObjList[0].name
    while True:
        g.write(siteName + ", ")
        t0 = time.time()
        try:
            pagesRemain = GuideObjList[0].get_page(g)
        except Exception as err:
            print(err)
            t1 = time.time()
            g.write(str(t1-t0) + ", ")
            g.write("ERROR\n")
        else:
            t1 = time.time()
            g.write(str(t1-t0) + ", ")
            g.write("none" + "\n")

        # terminal print values to keep track of stuff every now and then
        if counter % 400 == 0:
            print("\n")
            for guide in GuideObjList:
                print(guide.name + ": " + "Visited = " + str(len(guide.visited))
                      + ", Left = " + str(len(guide.urls_left)))
            print("\n")
        elif counter % 10 == 0:
            print("sites counted: " + str(counter))
            print(datetime.now())

        if pagesRemain == False:
            GuideObjList.remove(GuideObjList[0])
            print("Finished running for the " + siteName + " site. Yay!")

        if len(GuideObjList) == 0:
            g.close()
            break
        else:
            counter += 1
    """
    while True:
        index = counter % len(GuideObjList)
        siteName = GuideObjList[index].name
        g.write(siteName + ", ")
        t0 = time.time()
        try:
            pagesRemain = GuideObjList[index].get_page(g)
        except Exception as err:
            print(err)
            t1 = time.time()
            g.write(str(t1-t0) + ", ")
            g.write("ERROR\n")
        else:
            t1 = time.time()
            g.write(str(t1-t0) + ", ")
            g.write("none" + "\n")

        # terminal print values to keep track of stuff every now and then
        if counter % 400 == 0:
            print("\n")
            for guide in GuideObjList:
                print(guide.name + ": " + "Visited = " + str(len(guide.visited))
                      + ", Left = " + str(len(guide.urls_left)))
            print("\n")
        elif counter % 10 == 0:
            print("sites counted: " + str(counter))
            print(datetime.now())

        if pagesRemain == False:
            GuideObjList.remove(GuideObjList[index])
            print("Finished running for the " + siteName + " site. Yay!")

        if len(GuideObjList) == 0:
            g.close()
            break
        else:
            counter += 1
    """
    print("\nALL DONE! Wow.")



if __name__ == '__main__':
    main()
