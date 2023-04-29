"""
File: Asynchronously accesses and downloads website content using libraries asyncio and aiohttp.
"""

import asyncio
import aiohttp


"""
Function: downloadLink
Description: Uses asyncio / aiohttp library to download the html of one url passed as an argument
Parameters: aiohttp.ClientSession() object, string (url to download)
Return: HTML text of one URL page
"""
async def downloadLink(session, url):
    async with session.get(url) as resp:
        html = await resp.text()
        return html


"""
Function: downloadAll
Description: Uses asyncio / aiohttp library to download the htmls of multiple urls passed as an argument.
             Makes a call to downloadLink.
Parameters: list (urls to download)
Return: HTML text of all pages
"""
async def downloadAll(URLList):
    # Set up a TCP connector
    # Note: Can toggle limit of aiohttp simultaneous connections between 10-20 (default 100).
    # If blocked from server, try reducing limit.
    my_conn = aiohttp.TCPConnector(limit=20, ssl=False)
    # Increase the timeout from default 300s to 900s.
    my_timeout = aiohttp.ClientTimeout(total=900)

    async with aiohttp.ClientSession(connector=my_conn, timeout=my_timeout) as session:
        tasks = [asyncio.ensure_future(downloadLink(session, url)) for url in URLList]
        return await asyncio.gather(*tasks, return_exceptions=True)