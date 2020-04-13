def download_with_rate(url, token, filename=None, savepath=None, session=None, chunksize=4024,
             unpack=False, mocked=False, showstatus=False, rate_limit=None):
    import time,os,logging
    from tqdm import tqdm
    from plexapi import compat
    log = logging.getLogger('plexapi')

    """ Helper to download a thumb, videofile or other media item. Returns the local
        path to the downloaded file.

       Parameters:
            url (str): URL where the content be reached.
            token (str): Plex auth token to include in headers.
            filename (str): Filename of the downloaded file, default None.
            savepath (str): Defaults to current working dir.
            chunksize (int): What chunksize read/write at the time.
            mocked (bool): Helper to do evertything except write the file.
            unpack (bool): Unpack the zip file.
            showstatus(bool): Display a progressbar.

        Example:
            >>> download(a_episode.getStreamURL(), a_episode.location)
            /path/to/file
    """
    # fetch the data to be saved
    session = session or requests.Session()
    headers = {'X-Plex-Token': token}
    response = session.get(url, headers=headers, stream=True)
    # make sure the savepath directory exists
    savepath = savepath or os.getcwd()
    compat.makedirs(savepath, exist_ok=True)

    # try getting filename from header if not specified in arguments (used for logs, db)
    if not filename and response.headers.get('Content-Disposition'):
        filename = re.findall(r'filename=\"(.+)\"', response.headers.get('Content-Disposition'))
        filename = filename[0] if filename[0] else None

    filename = os.path.basename(filename)
    fullpath = os.path.join(savepath, filename)
    # append file.ext from content-type if not already there
    extension = os.path.splitext(fullpath)[-1]
    if not extension:
        contenttype = response.headers.get('content-type')
        if contenttype and 'image' in contenttype:
            fullpath += contenttype.split('/')[1]

    # check this is a mocked download (testing)
    if mocked:
        log.debug('Mocked download %s', fullpath)
        return fullpath

    # save the file to disk
    log.info('Downloading: %s', fullpath)
    if showstatus:  # pragma: no cover
        total = int(response.headers.get('content-length', 0))
        bar = tqdm(unit='B', unit_scale=True, total=total, desc=filename)

    rate_limit = rate_limit * 1000 #(go from bytes to kilobytes per second)
    start_time=time.time() #when it starts.
    with open(fullpath, 'wb') as handle:
        for chunk in response.iter_content(chunk_size=chunksize):
            handle.write(chunk)
            if showstatus: bar.update(len(chunk))
            elapsed_time = time.time() - start_time
            speed = (chunksize/elapsed_time)
            pauser_timer = (((speed/rate_limit)-1)*elapsed_time)
            if ((pauser_timer) > 0): time.sleep(pauser_timer)
            start_time=time.time() #reset start time

    if showstatus:  # pragma: no cover
        bar.close()
    # check we want to unzip the contents
    if fullpath.endswith('zip') and unpack:
        with zipfile.ZipFile(fullpath, 'r') as handle:
            handle.extractall(savepath)

    return fullpath


