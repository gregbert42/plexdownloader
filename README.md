# plexdownloader

This is a tool that takes advantage of the PlexAPI to download movies from a plex server. This is very useful if you want to download movies or shows from one plex server to another. You can log into the the plex server either with a direct connection (e.g., port 32400) and a token or you can use the plex username and a password. This does NOT modify your plex library in any way. 

It requires that you create a file called "configuration.json", which as the name suggests, is a json-formatted configuration file

Here is an example configuration.json that uses a plex username and password:

```json
{
"connection":"plex",
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

It is also possible to use the enclosed encrypt.py tool to salt your password or token. Here is an example configuration.json

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
"""
