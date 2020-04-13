#!/usr/bin/python3
from plexapi import utils
import sys,json,pprint,os
import downloader

#Future improvement: show size before downloading...

def crypt(direction,input,key):
    from cryptography.fernet import Fernet
    #key = Fernet.generate_key()
    f = Fernet(key)
    if (direction=='e'): output = f.encrypt(input.encode('utf-8')).decode('utf-8')
    if (direction=='d'):
        try: output = f.decrypt(input.encode('utf-8')).decode('utf-8')
        except:
            print ("Invalid decryption key")
            exit(1)
    return output

def readfile(fname):
    credentials={}
    with open(fname, 'r') as readFile:
        data=json.load(readFile)
    readFile.close()
    return data

def show_info (server):
    print (server)
    print (server.clients())
    for client in server.clients():
        print(client.title)
    print (server.account)

def search(server,target):
    from plexapi.video import Episode, Movie, Show
    VALID_TYPES = (Movie, Episode, Show)
    results = server.search(target)
    items = [i for i in results if i.__class__ in VALID_TYPES] #imported code
    if (len(items)==0): return False  #in case nothing is found, abort the loop, dont ask to make a choice
    items = utils.choose('Choose result', items, lambda x: '(%s) %s %s' % (x.type.title(), x.title[0:60], x.title[0:60])) #imported code
    if not isinstance(items, list): items = [items]  #converts items to a list if it already isnt a list
    item=[]
    for i in items:
        if isinstance(i, Show):
            display = lambda i: '%s %s %s' % (i.grandparentTitle, i.seasonEpisode, i.title)
            selected_eps = utils.choose('Choose episode', i.episodes(), display)
            if isinstance(selected_eps, list): item += selected_eps
            else: item.append(selected_eps)
        else: item.append(i) #If its not a show (doesnt have episodes), just adds directly
    if not isinstance(items, list): items = [items]  #converts items to a list if it already isnt a list
    return item #now a list again, so technically items

def connect_plex(credentials):
    from plexapi.myplex import MyPlexAccount
    from plexapi.server import PlexServer
    if (credentials.get('connection','')=="direct"):
        print ("Connecting Directly")
        baseurl = credentials['url']
        token = credentials['token']
        server = PlexServer(baseurl, token)
    else:
        account = MyPlexAccount(credentials['username'],credentials['password'])
        if (credentials['servername']=='choose'):
            servers = servers = [s for s in account.resources() if 'server' in s.provides]
            server_choice=utils.choose('Choose a Server', servers, 'name')
            credentials['servername']=server_choice.name
        print ("Connecting to %s" % credentials['servername'])
        server = account.resource(credentials['servername']).connect()  # returns a PlexServer instance
        token=account.authenticationToken
    print ("Connected")
    return (server)

def add_items(items):
    items_to_dl=[]
    item_row={}
#    print ("I've been given this to download",items)
    for item in items:
        for part in item.iterParts():
            filename = '%s.%s' % (item._prettyfilename(), part.container) # borrowed code, next few lines
            url = item._server.url('%s?download=1' % part.key)
            print ("Filename: %s\t%s" % (filename,item.title))
            query = input ("Is this the file you want? (y/n/exit): ")
            if (query[:1].lower() == "y"):
                item_row['url']=url
                item_row['token']=item._server._token
                item_row['filename']=filename
                item_row['session']=item._server._session
                items_to_dl.append(item_row)
            elif (query.lower() == 'exit'): filepaths='exit'
    return (items_to_dl) 

def download_items(items_to_dl):
    rate_limit = input("Enter download speed limit, or press zero for none (in kb/sec): ")
    if (rate_limit == ''): rate_limit="1E10"
    rate_limit = float(rate_limit)
    for row in items_to_dl:
        url=row['url']
        token=row['token']
        filename=row['filename']
        session=row['session']
        downloader.download_with_rate(url, token=token, filename=filename, savepath=os.getcwd(),  #token by my trial and error
                                       session=session, showstatus=True, rate_limit=rate_limit)
    return

def main(args):
    go=True
    items_to_dl=[]
    credentials = readfile('credentials.json')
    if "password" in credentials: credentials['password']=crypt('d',credentials['password'],credentials['pwkey'])
    if "token" in credentials: credentials['token']=crypt('d',credentials['token'],credentials['tokenkey'])
    server = connect_plex(credentials)
#    show_info(server)
    while (go):
        print ("%i items in queue" % len(items_to_dl))
        searchfor = input("Enter item to search for, or 'download' or 'exit': ")
        if (not searchfor): continue
        elif (searchfor.lower()=='exit'): go=False
        elif (searchfor.lower()=='download'): go=False
        else:
            found = search(server,searchfor)
            if (not found):
                print ("nothing found")
                continue
            new_list=add_items(found)
            if (new_list=='exit'): go=False
            else:
                items_to_dl += new_list
                print ("Item added to download queue")
    if (searchfor.lower()=='download'): download_items(items_to_dl)
    exit(0)

if __name__== "__main__":
    main(sys.argv)
