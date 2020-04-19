#!/usr/bin/python3
#### Version 0.1
#### April 19th 2020


from plexapi import utils
import sys,json,pprint,os
import downloader

def crypt(direction,input,key):
    from cryptography.fernet import Fernet
    f = Fernet(key)
    if (direction=='e'): output = f.encrypt(input.encode('utf-8')).decode('utf-8') #never used in this code.
    if (direction=='d'):
        try: output = f.decrypt(input.encode('utf-8')).decode('utf-8')
        except:
            print ("Invalid decryption key")
            exit(1)
    return output

def readfile(fname):
    try:
        with open(fname, 'r') as readFile: data=json.load(readFile)
        readFile.close()
    except:
        print("Error:", sys.exc_info())
        exit (1)
    return data

def search(server,target):
    from plexapi.video import Episode, Movie, Show
    VALID_TYPES = (Movie, Episode, Show)
    results = server.search(target)
    items = [i for i in results if i.__class__ in VALID_TYPES] #adds any keys found that have a valid type
    if (len(items)==0): return False                           #in case nothing is found, abort the loop, dont ask to make a choice
    for item in items:
        if isinstance (item,Episode): item.title = item.grandparentTitle + ' - ' + item.title   #adds on the show title for episodes
    items = utils.choose('Choose your item', items, lambda x: '(%s) %s' % (x.type.title(), x.title[0:60])) #imported code
    if not isinstance(items, list): items = [items]            #converts items to a list if it already isnt a list
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

def connect_plex(configuration):
    from plexapi.myplex import MyPlexAccount
    from plexapi.server import PlexServer
    if (configuration['connection']=="direct"):
        print ("Connecting Directly")
        baseurl = configuration['url']
        token = configuration['token']
        server = PlexServer(baseurl, token)
    else:
        account = MyPlexAccount(configuration['username'],configuration['password'])
        if (configuration['servername']=='choose'):
            servers = servers = [s for s in account.resources() if 'server' in s.provides]
            server_choice=utils.choose('Choose a Server', servers, 'name')
            configuration['servername']=server_choice.name
        print ("Connecting to %s" % configuration['servername'])
        server = account.resource(configuration['servername']).connect()  # returns a PlexServer instance
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

def add_items(items,configuration):
    items_to_dl=[]
    item_row={}
    for item in items:
        for part in item.iterParts():
            go = True
            while (go):
                filename = '%s.%s' % (item._prettyfilename(), part.container) # borrowed code, next few lines
                url = item._server.url('%s?download=1' % part.key)
                print ("Filename: %s\t%s\t%.2f MB" % (filename, item.title, part.size/1E6))
                query = input ("Add this file to queue? (y/n/exit): ")
                if (query[:1].lower() == "y"):
                    splitfile = part.file.split('/')
                    if (item.type == "movie"):  dirname = configuration['movie_dir'] + '/' + splitfile[len(splitfile)-2]
                    elif ((item.type == 'show') or (item.type == 'episode')):
                        dirname = configuration['show_dir'] + '/' + splitfile[len(splitfile)-3] + '/' + splitfile[len(splitfile)-2]
                    else:
                       print ("Unknown Type encountered",item.type)
                       exit(1)
                    item_row['title']=item.title
                    item_row['size']=part.size
                    item_row['dir']=dirname
                    item_row['url']=url
                    item_row['token']=item._server._token
                    item_row['filename']=filename
                    item_row['session']=item._server._session
                    item_row['type']=item.type
                    items_to_dl.append(item_row)
                    go = False
                elif (query.lower() == 'exit'): return False
                elif (query.lower() == 'inspect'):
                    print ("Inspection of item:")
                    inspct(item)
                    print ("Inspection of part:")
                    inspct(part)
                elif (query[:1].lower() == 'n'): go = False
    return (items_to_dl)

def download_items(items_to_dl):
    rate_limit = input("Enter download speed limit, or press enter for none (in kb/sec): ")
    if (rate_limit == ''): rate_limit="1E10"
    rate_limit = float(rate_limit)
    for row in items_to_dl:
        url=row['url']
        token=row['token']
        filename=row['filename']
        session=row['session']
        savepath=row['dir']
        downloader.download_with_rate(url, token=token, filename=filename, savepath=savepath,  session=session, showstatus=True, rate_limit=rate_limit)
    return

def config (fname):
    configuration = readfile(fname)
    if "pwkey" in configuration: configuration['password']=crypt('d',configuration['password'],configuration['pwkey'])
    if "tokenkey" in configuration: configuration['token']=crypt('d',configuration['token'],configuration['tokenkey'])
    if "movie_dir" not in configuration: configuration['movie_dir']=os.getcwd()
    if "show_dir" not in configuration: configuration['show_dir']=os.getcwd()
    if "servername" not in configuration: configuration['servername']='choose'
    if "connection" not in configuration:
        print ("Connection not specified in configuration file")
        exit (1)
    return configuration

def search_prompt(server,configuration):
    go = True
    items_to_dl=[]
    while (go):
        searchfor = input("Enter item to search for, 'list' current queue 'download' or 'exit': ")
        if (not searchfor): continue # no input entered
        elif searchfor.lower() == 'download': go = False
        elif searchfor.lower() == 'exit': return False
        elif searchfor.lower() == 'list':
            print ("---------------------------------------------------------------------------------")
            print ("%i items in queue" % len(items_to_dl))
            for item in items_to_dl: print ("%s\t%.02f MB" % (item['title'],item['size']/1E6))
            print ("---------------------------------------------------------------------------------")
        else:
            found = search(server,searchfor)         #calls subroutine to search for whatever was entered, returns a key
            if (not found): print ("Nothing found that matches your input ")
            new_list = add_items(found,configuration)  #adds it to the list with proper attributes
            if (new_list == 'exit'): return False
            else:
                items_to_dl += new_list              #adds it to the list
                print ("Item added to download queue")
    return items_to_dl

def main(args):
    configuration = config(sys.path[0]+'/'+'configuration.json')
    server = connect_plex(configuration)
    items_to_dl  = search_prompt(server,configuration)
    if (items_to_dl): download_items(items_to_dl)
    exit(0)

if __name__== "__main__":
    main(sys.argv)
