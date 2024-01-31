import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os
import re
import zipfile
from io import StringIO
from lxml import html
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait


class HeadlessMonitor():

    def __init__(self):
        super().__init__()     

        self.path = "/media"        
        
        global PAUSED
        PAUSED = False

        self.checkedMode = 'add data & rename'    
        self.provider = 'Manga4Life'   
        self.filename = re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', 'Chapter')       

        print('Watching: ' + self.path +'\nMode: '+ self.checkedMode +'\nProvider: '+ self.provider +'\nNaming Scheme: %Manga% - %'+self.filename+'% %Number%.cbz')      

        if self.checkedMode == 'add data & rename' or self.checkedMode == 'only add data':
            ###start browser
            opts = Options()            
            opts.add_argument("--headless")
            #opts.binary_location = '/usr/local/bin/geckodriver'            
            opts.add_argument("--log fatal")
            #geckopath = '/usr/local/bin/geckodriver'
            geckopath = '/usr/local/bin/geckodriver'
            #geckopath = os.path.join(os.path.dirname(__file__), "geckodriver") 
            self.driver = webdriver.Firefox(service=Service(geckopath), options=opts)
            #self.driver = webdriver.Firefox(options=opts)
            print('\nBrowser started successfully\n')       

        self.lastMangaName = ''

        patterns = ["*.cbz", "*.zip"]
        ignore_patterns = None
        ignore_directories = False
        case_sensitive = True
        self.my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        print('Watchdog is ready.\nTo stop press "Ctrl" + "C"\n')
  
    def on_created(self, event):         
        global PAUSED
        # If PAUSED, exit
        if PAUSED is True:
            return

        # If not, pause anything else from running and continue
        PAUSED = True

        #time.sleep(5)
        isLocked = True
        while isLocked == True:
            try:
                with zipfile.ZipFile(event.src_path) as testfile:             
                    print('File ' + event.src_path + ' is okay')            
                
            except zipfile.BadZipFile:  
                time.sleep(2)                                          
                print('File ' + event.src_path + ' is not okay. Download may not be finished. Waiting...')                  
            else:
                isLocked = False
                # if mode = 0 or 1 get link and metaData
                mainFileDirectory = os.path.splitext(os.path.basename(event.src_path))[0]
                mangaName = ''
                searchNameSplit = mainFileDirectory.split(' - ')

                for length in range(len(searchNameSplit)-1):
                    if length != 0:
                        mangaName += ' - '            
                    mangaName += searchNameSplit[length]
                 
                volumeName = mainFileDirectory.split(' - ')[-1]                 

                #check if file already exists                                   
            
                if  self.checkedMode == 'only rename':  
                    newName = mangaName+ ' - ' + self.filename + ' '+ re.sub('.*?([0-9.]*)$',r'\1',volumeName)                              
                    if not os.path.exists(os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz')):                        
                        rename_zip = os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz')
                        os.rename(event.src_path, rename_zip)

                else:
                    
                    if self.lastMangaName != mangaName:                     
                        
                        if self.provider == 'Manga4Life':
                                        
                            url = 'http://manga4life.com/search/?sort=v&desc=true&name='+mangaName.replace(" ", "%20")                                       

                        elif self.provider == 'MyAnimeList':
                            url = 'https://myanimelist.net/manga.php?cat=manga&q='+mangaName.replace(" ", "%20")
                            
                        self.driver.get(url)
                        WebDriverWait(self.driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')      
                        raw_html = html.fromstring(self.driver.page_source)   

                        if self.provider == 'Manga4Life':                                
                            aname = raw_html.xpath('//a[@class="SeriesName ng-binding"]/text()')
                            ahref = raw_html.xpath('//a[@class="SeriesName ng-binding"]/@href')
                        elif self.provider == 'MyAnimeList':
                            aname = raw_html.xpath('//tr/td/a[@class="hoverinfo_trigger fw-b"]/strong/text()')
                            ahref = raw_html.xpath('//tr/td/a[@class="hoverinfo_trigger fw-b"]/@href')

                        if self.provider == 'Manga4Life':                                
                            foundurl = 'http://manga4life.com'+ahref[0]                                     

                        elif self.provider == 'MyAnimeList':
                            foundurl = ahref[0]


                        data = [aname[0], foundurl]

                        self.driver.get(data[1])
                        WebDriverWait(self.driver, 15).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                        raw_html = html.fromstring(self.driver.page_source)

                        if self.provider == 'Manga4Life':                         
                            aauthors = raw_html.xpath('//li[@class="list-group-item d-none d-md-block"]/span[text() = "Author(s):"]/following-sibling::a/text()')
                            agenre = raw_html.xpath('//li[@class="list-group-item d-none d-md-block"]/span[text() = "Genre(s):"]/following-sibling::a/text()')
                            ayear = raw_html.xpath('//li[@class="list-group-item d-none d-md-block"]/span[text() = "Released:"]/following-sibling::a/text()')
                            allsummary = raw_html.xpath('//li[@class="list-group-item d-none d-md-block"]/div/text()')[0]

                            allauthors = ''
                            allgenre = ''

                            for index in range(len(aauthors)):
                                allauthors = allauthors + aauthors[index]
                                if index != len(aauthors)-1:
                                    allauthors = allauthors + ', '
                                                

                            for index in range(len(agenre)):
                                allgenre = allgenre + agenre[index]
                                if index != len(agenre)-1:
                                    allgenre = allgenre + ', '                     

                        elif self.provider == 'MyAnimeList':
                            aauthors = raw_html.xpath('//div[@class="information-block di-ib clearfix"]/span[@class="information studio author"]/a/text()')
                            agenre = raw_html.xpath('//div[@class="spaceit_pad"]/span[text() = "Genres:"]/following-sibling::a/text()')
                            ayear = raw_html.xpath('//div[@class="spaceit_pad"]/span[text() = "Published:"]/following-sibling::text()[1]')
                            asummary = raw_html.xpath('//td/span[@itemprop="description"]/descendant::text()')                                    

                            allauthors = ''
                            allgenre = ''
                            allsummary = ''

                            for index in range(len(aauthors)):                      
                                allauthors = allauthors + str.upper(aauthors[index].split(',')[0]) + ' ' + aauthors[index].split(', ')[1]
                                if index != len(aauthors)-1:
                                    allauthors = allauthors + ', '
                                                

                            for index in range(len(agenre)):
                                allgenre = allgenre + agenre[index].replace(" ", "")
                                if index != len(agenre)-1:
                                    allgenre = allgenre + ', '

                            for index in range(len(asummary)):
                                allsummary = allsummary + asummary[index]

                        self.allMetaData = [data[0], allauthors, allgenre, allsummary, re.findall('(\d{4})',ayear[0])[0]]                       
                    
                    name = 'ComicInfo.xml'                
                    with StringIO() as f:                                
                        f.write('<?xml version="1.0"?>\n')
                        f.write('<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n')
                        f.write('    <Series>'+self.allMetaData[0]+'</Series>\n')
                                    
                        f.write("    <Volume>"+re.sub('.*?([0-9.]*)$',r'\1',volumeName)+"</Volume>\n")                        
                        
                        if self.checkedMode == 'only add data':
                            
                            f.write('    <Title>'+volumeName+'</Title>\n')
                        else:
                            f.write('    <Title>'+self.filename+' '+re.sub('.*?([0-9.]*)$',r'\1',volumeName)+'</Title>\n') # Chapter x

                        f.write('    <Writer>'+self.allMetaData[1]+'</Writer>\n')

                        f.write('    <Genre>'+self.allMetaData[2]+'</Genre>\n')

                        f.write('    <Summary>'+self.allMetaData[3]+'</Summary>\n')
                                                        
                        f.write('    <Year>'+self.allMetaData[4]+'</Year>\n')
                                
                        f.write('    <Manga>YesAndRightToLeft</Manga>\n')

                        f.write('</ComicInfo>')

                        content = f.getvalue()                                                                           
                     
                    doNothing = False 
                    doDelete = True
                    doRename = True
                    check_src_zip = event.src_path
                    with zipfile.ZipFile(check_src_zip, 'r', compression=zipfile.ZIP_DEFLATED) as check_src_zip_file:
                        if name in check_src_zip_file.namelist():

                            zipmode = 'w'
                            if self.checkedMode == 'add data & rename': 
                                newName = mangaName+ ' - ' + self.filename + ' '+ re.sub('.*?([0-9.]*)$',r'\1',volumeName)                                            

                                dest_zip = os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.tmp')

                                if event.src_path != os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz'):                                    
                                    rename_zip = os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz')
                                else:                                                                 
                                    doNothing = True                                                        
            
                            elif self.checkedMode == 'only add data':               
                                
                                dest_zip = os.path.splitext(event.src_path)[0]+'.tmp'
                                rename_zip = os.path.splitext(event.src_path)[0]+'.cbz'

                        else:                            
                            zipmode = 'a'
                            if self.checkedMode == 'add data & rename': 
                                newName = mangaName+ ' - ' + self.filename + ' '+ re.sub('.*?([0-9.]*)$',r'\1',volumeName)                                            

                                dest_zip = event.src_path 
                                
                                if event.src_path != os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz'):                                    
                                    doDelete = False
                                    rename_zip = os.path.join(os.path.dirname(event.src_path), re.sub(r'[\\/\:*"<>\|\%\$\^£]', '', newName)+'.cbz')                                     
                                else:                                                                                                           
                                    doDelete = False                                                                        
                                    doRename = False                                                
            
                            elif self.checkedMode == 'only add data':                                                                             
                                doDelete = False
                                dest_zip = event.src_path 

                    if not doNothing:
                        with zipfile.ZipFile(dest_zip, zipmode, compression=zipfile.ZIP_STORED) as dest_zip_file:                                     
                            
                            if zipmode == 'w':
                                src_zip = event.src_path     ###path of zip to extract from                 
                                                    
                                with zipfile.ZipFile(src_zip, 'r', compression=zipfile.ZIP_DEFLATED) as src_zip_file:                         
                                    for zitem in src_zip_file.namelist():
                                        if zitem != 'ComicInfo.xml':                                
                                            dest_zip_file.writestr(zitem, src_zip_file.read(zitem))
                                
                            dest_zip_file.writestr(name, content)
                            
                        if doDelete == True:                                                    
                            os.remove(src_zip) 

                        if doRename == True:                             
                            try:      
                                os.rename(dest_zip, rename_zip) 
                            except:
                                os.rename(dest_zip, os.path.splitext(rename_zip)[0] + '_duplicate.cbz')

                    if 'src_zip' in locals():
                        del src_zip 

                    if 'rename_zip' in locals():
                        del rename_zip

                    self.lastMangaName = mangaName
                    print('    Processed '+event.src_path+' as '+self.allMetaData[0])

        
        # Once finished, allow other things to run
        PAUSED = False
       
    def watcher(self):
        self.my_event_handler.on_created = self.on_created
    
        go_recursively = True
        self.my_observer = Observer()    
        self.my_observer.schedule(self.my_event_handler, self.path, recursive=go_recursively)

        self.my_observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.my_observer.stop()
            if self.checkedMode == 'add data & rename' or self.checkedMode == 'only add data':
                self.driver.quit()
        self.my_observer.join()

    def exit_handler(self):
        self.my_observer.stop()
        if self.checkedMode == 'add data & rename' or self.checkedMode == 'only add data':
            self.driver.quit()   
    

runHeadlessMonitor = HeadlessMonitor()
runHeadlessMonitor.watcher()    
