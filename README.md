# plexdownloader

Current version: 0.1

This is a tool that takes advantage of the PlexAPI to download movies from a plex server. This is very useful if you want to download movies or shows from one plex server to another. You can log into the the plex server either with a direct connection (e.g., port 32400) and a token or you can use the plex username and a password. This does NOT modify your plex library in any way. This is my first attempt to share some of my python work. The plexapi had bits and pieces of this, but needed to be strung together and I also added many enhancements, such as a bandwidth limiter. I appreciate your feedback, and of course any contributions.

It requires that you create a file called "configuration.json", which as the name suggests, is a json-formatted configuration file. This file should be placed in the same directory as where the script is run from

Here is an example configuration.json that uses a plex username and password:

```json
{
"connection":"plexservice",
"username":"<your_plex_username_here>",
"password":"<your password here>",
"servername":"choose",
"show_dir":"/plex_library_directory/where/you/want/to/save/shows",
"movie_dir":"/plex_library_directory/where/you/want/to/save/shows"
}
```
and an example configuration.json using the direct connection method

```json
{
"connection":"direct",
"url":"http://<ip address of the plex server>:32400",
"token":"<plex token>",
"show_dir":"/plex_library_directory/where/you/want/to/save/shows",
"movie_dir":"/plex_library_directory/where/you/want/to/save/shows"
}
```
Note that the DIRECT method seems to be considerably faster in most situations, since it does not rely on the plex service

#Variations

When you use the plexservice, you can either use 'choose' as the value of your servername (as per above), or you can simply write the name of your server to save a step

If you leave 'show_dir' or 'movie_dir' undefined, it will simply use the current directory.

It is possible to use the enclosed encrypt.py tool to salt your password or token. Here is an example configuration.json

```json
{
"connection":"direct",
"url":"http://<ip address of the plex server>:32400",
"token":"<encrypted plex token>",
"tokenkey":"<key for encrypted token>",
"show_dir":"/plex_library_directory/where/you/want/to/save/shows",
"movie_dir":"/plex_library_directory/where/you/want/to/save/shows"
}
```

you can do the same with a password, using the dictionary entry "pwkey" instead of "tokenkey"

external dependencies (i.e., must be pip installed)
- plexapi
- cryptography.fernet


#Instructions

Run script  - e.g., from command line: ./plexdownloader.py

```
Connecting Directly
Connected
Enter item to search for, 'list' current queue 'download' or 'exit':
```

Here, you should enter a search term. It can be a move or episode title, a show title, or even an actor. It will search all the plex tags. So say you type in "Mr. Robot". It should return any matching items from your plex server

```
Enter item to search for, 'list' current queue 'download' or 'exit': Mr. Robot

  0: Mr. Robot s04e01 401 Unauthorized
  1: Mr. Robot s04e02 402 Payment Required
  2: Mr. Robot s04e03 403 Forbidden
  3: Mr. Robot s04e04 404 Not Found
  4: Mr. Robot s04e05 405 Method Not Allowed
  5: Mr. Robot s04e06 406 Not Acceptable
  6: Mr. Robot s04e07 407 Proxy Authentication Required
  7: Mr. Robot s04e08 408 Request Timeout
  8: Mr. Robot s04e09 409 Conflict
  9: Mr. Robot s04e10 410 Gone
  10: Mr. Robot s04e11 eXit
  11: Mr. Robot s04e12 Series Finale (1)
  12: Mr. Robot s04e13 Series Finale (2)

Choose episode:
```

As a next step, you need to choose which episode you want (if it is unsure of what show you are looking for, it will prompt you first). So now, select an episode. It will give you information about that episode, and ask you to confirm

```
Choose episode: 12
Filename: Mr..Robot.s04e13.mkv  Series Finale (2)       1864.63 MB
Add this file to queue? (y/n/exit):
```

Now you can choose to add it to the queue. It will confirm that it has been added, then give you a chance to select additional items to download, lits your current download queue, or start the download. Note that there is an undocumented option to 'inspect' the episode at this point, which is more of a debug feature but you may also find it helpful

```
Add this file to queue? (y/n/exit): y
Item added to download queue
Enter item to search for, 'list' current queue 'download' or 'exit':
```

If you select to download, it will ask you if you wish to set a bandwidth limit - this is very useful if you dont want to swamp the bandwidth of either connection side. Here, i enter a limit of 100 kb/sec. That will take a long time, but fine if you plan to leave it unattended 

```
Enter item to search for, 'list' current queue 'download' or 'exit': download
Enter download speed limit, or press enter for none (in kb/sec): 100
Mr..Robot.s04e13.mkv:   0%|                                                  | 495k/1.86G [00:03<5:10:23, 100kB/s]
```

When it is done, you can select to exit

