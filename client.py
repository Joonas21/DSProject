import xmlrpc.client


server = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)

def main():
    print("\nWelcome to WikiCrawler! \n")

    while True:

        starting_article = input("Give first article: ") 
        target_article = input("Give target article: ")

        if (len(starting_article) == 0 or len(target_article) == 0):
            print("\nYou must give valid articles for search \n")
            continue

        first_article = server.checkArticle(starting_article)
        second_article = server.checkArticle(target_article)

        if first_article == False and second_article == False:
            print("Both articles", starting_article,"and", target_article,"where not found\n")
            continue
        
        elif first_article == False:
            print("First article", starting_article,"was not found\n")
            continue

        elif second_article == False:
            print("Target article", target_article,"was not found\n")
            continue 

        else:

            if(starting_article == target_article):
                print("You are clearly a funny one, both articles are tha same\nso theres no steps to take we are alreadt there :)\n")
                print("Ending program, thanks for playing!\n")
                return

            else:

                path = server.findPath(starting_article, target_article)
                
                print("This is the shortest path between articles:\n", path)
                print("Ending program, thanks for playing!\n")
                return  

main()