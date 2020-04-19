#!/usr/bin/python3
from plexapi import utils
import sys,json,pprint,os
import downloader

#create directory with movie title

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
    items = utils.choose('Choose your item: ', items, lambda x: '(%s) %s' % (x.type.title(), x.title[0:60])) #imported code
    if not isinstance(items, list): items = [items]  #converts items to a list if it already isnt a list
    item=[]
    for i in items:
        if isinstance(i, Show):
            display = lambda i: '%s %s %s' % (i.grandparentTitle, i.seasonEpisode, i.title)
            selected_eps = utils.choose('Choose episode: ', i.episodes(), display)
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

def inspct(thing):
    try:
        print (thing)
        print ("Dict-->",thing.__dict__)
        print ("Keys-->",thing.__dict__.keys())
    except:
        print("Error:", sys.exc_info())
        return False
    return True

def add_items(items):
    items_to_dl=[]
    item_row={}
#    print ("I've been given this to download",items)
    for item in items:
        for part in item.iterParts():
            go = True
            while (go):
                filename = '%s.%s' % (item._prettyfilename(), part.container) # borrowed code, next few lines
                url = item._server.url('%s?download=1' % part.key)
                print ("Filename: %s\t%s\t%.2f MB" % (filename,item.title,part.size/1E6))
                query = input ("Add this file to queue? (y/n/exit): ")
                if (query[:1].lower() == "y"):
                    splitfile = part.file.split('/')
                    dirname = splitfile[len(splitfile)-2]
                    item_row['dir']=dirname
                    item_row['url']=url
                    item_row['token']=item._server._token
                    item_row['filename']=filename
                    item_row['session']=item._server._session
                    item_row['type']=item.type
                    items_to_dl.append(item_row)
                    go = False
                elif (query.lower() == 'exit'): return 'exit'
                elif (query.lower() == 'inspect'):
                    print ("Inspection of item:")
                    inspct(item)
                    print ("Inspection of part:")
                    inspct(part)
                elif (query[:1].lower() == 'n'): go = False
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
        savepath=os.getcwd()
        if (row['type'] == "movie"): savepath=savepath + '/' + row['dir']
        downloader.download_with_rate(url, token=token, filename=filename, savepath=savepath,  session=session, showstatus=True, rate_limit=rate_limit)
    return

def main(args):
    go=True
    items_to_dl=[]
    credentials = readfile(sys.path[0]+'/'+'credentials.json')
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
