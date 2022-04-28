#from importlib.machinery import PathFinder
#from importlib.resources import path
import requests
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import concurrent.futures

#https://www.mediawiki.org/wiki/API:Links#Example_1:_Fetch_all_the_links_in_a_page
S = requests.Session()

URL = "https://en.wikipedia.org/w/api.php"

def checkArticle(article):

    PARAMS = {
    "action": "query",
    "format": "json",
    "titles": article,
    "prop": "links",
    "pllimit": "max"
    }

    response = S.get(url=URL, params=PARAMS)
    DATA = response.json()  

    PAGES = DATA["query"]["pages"]

    if ("-1" in PAGES):
        print("\nNothing was found with", article, "\n")
        return False
    
    print("Article",article,"was found\n")
    return True

def saveLinks(article, loop):

    page_titles = []

    if loop.visited:
        return

    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": article,
        "prop": "links"
    }

    #https://www.mediawiki.org/wiki/API:Links

    response = S.get(url=URL, params=PARAMS)
    DATA = response.json()

    PAGES = DATA["query"]["pages"]

    if "-1" not in PAGES:
        for k, v in PAGES.items():
            for l in v["links"]:
                page_titles.append(l["title"])
                
    #https://stackoverflow.com/questions/14882571/how-to-get-all-urls-in-a-wikipedia-page
    while "continue" in DATA:

        PARAMS = {
        "action": "query",
        "format": "json",
        "titles": article,
        "prop": "links",
        "plcontinue": DATA["continue"]["plcontinue"]            
        }

        response = S.get(url=URL, params=PARAMS)
        DATA = response.json()
        PAGES = DATA["query"]["pages"]

        if "-1" not in PAGES:
            for key, val in PAGES.items():
                for link in val["links"]:
                    page_titles.append(link["title"])

    print("%d titles found." % len(page_titles))
    #print(page_titles)
    return page_titles 

def findPath(starting_article, target_article):

    road = {}
    road[starting_article] = [starting_article]
    URLS = []
    URLS.append(starting_article)
    loop = Loop([], False)

    try:
        while loop.visited == False:
            #https://docs.python.org/3/library/concurrent.futures.html
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

                if not loop.visited:
                    future_to_url = {executor.submit(saveLinks, i, loop): i for i in URLS}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    link = future_to_url[future]
                    data = future.result()

                    if data != []:
                        for d in data:
                            if (d == target_article):
                                loop.visited = True
                                loop.road = road[link] + [d]
                                print("Found it", loop.road,"\n")
                                return loop.road

                            if d not in road and d != link:
                                print(d)
                                road[d] = road[link] + [d]
                                URLS.append(d)

    except Exception as error:
        print(error)

#https://stackoverflow.com/questions/53621682/multi-threaded-xml-rpc-python3-7-1
class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
   pass

class Loop:
    def __init__(self, loop, visited):
        self.loop = loop
        self.visited = visited

def run_server(host="localhost", port=8000):
    server_addr = (host, port)
    server = SimpleThreadedXMLRPCServer(server_addr, allow_none=True)

    server.register_function(checkArticle)
    server.register_function(saveLinks)
    server.register_function(findPath)

    print("\n Listening on", host,"port", port,"\n")

    server.serve_forever()

if __name__ == "__main__":
    run_server()