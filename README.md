# pyMergeTagger

## Description

Sees if a new manga in the .cbz format has been added to the folder. Automatically generates a ComicInfo.xml and places it inside the .cbz. 
The metadata is gathered from Manga4Life. Other sources are planned.

Can be paired with FMD2 and Komga or Kavita.

Existing files are not modified.

Example docker-compose:
```dockerfile
services:
    pymergetagger:
        image: realblack7/pymergetagger:latest
        container_name: pyMergeTagger
        volumes:
            -/path/to/my-manga-folder:/media
        restart: unless-stopped
```
## Todos
- [ ] output to a webpage using flask
- [ ] port pyQT GUI to a webpage to edit existing files manually
- [ ] add more metadata providers like mangaUpdates, mal, aniList, mangaDex, comicvine
- [ ] mix/aggregate metadata from different providers

## Docker
The container can be pulled from [https://hub.docker.com/r/realblack7/pymergetagger](https://hub.docker.com/r/realblack7/pymergetagger)
