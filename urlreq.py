# Importing necessary libraries
from urllib.parse import urlparse
import cachetools
import requests
import pyspeedtest
import asyncio
from pathlib import Path
import os

# Defining the URLReq class
class URLReq:
    # Defines instance variables
    URL = None
    SIZE = 0.0
    PATH = None
    SPEED = 0.0
    DONE = False
    
    # Cache with TTL of 300 seconds
    cache = cachetools.TTLCache(maxsize = 100, ttl = 300)
    
    # Defines the initialization function
    def __init__(self, url, size, ext = "bin"):
        self.URL = url
        self.SIZE = size
        
        # Parse the URL to get the file name
        parsed_url = urlparse(self.URL)
        filename = Path(parsed_url.path.split("/")[-1])
        title =  filename.stem
        
        self.PATH = f"C:/Users/ASUS/Downloads/{title}.{ext}"
    
    # Function to measure internet speed 
    async def get_speed(self): 
        loop = asyncio.get_event_loop() 
        speed = await loop.run_in_executor(None, self._measure_speed) 
        
        self.SPEED = speed 
        
        return speed 
    
    def _measure_speed(self): 
        try: 
            # Measure the download speed using pyspeedtest 
            test = pyspeedtest.SpeedTest("google.com") 
            speed = test.download() 
            
            return speed 
        except Exception: 
            return 1.0
    
    # Function to download file from the URL
    @cachetools.cached(cache)
    def get_file(self):
        # Function to get unique file name
        def get_unique(path):
            directory = os.path.dirname(path)
            filename = os.path.basename(path)
            name, ext = os.path.splitext(filename)
            unique_name = filename
            
            count = 1
            
            while os.path.exists(os.path.join(directory, unique_name)):
                unique_name = f"{name}({count}){ext}"
                count += 1
            
            path = os.path.join(directory, unique_name)
            
            return path
            
        # Numbering the file name
        self.PATH = get_unique(self.PATH)
        
        # Download the file in chunks 
        if self.SIZE >= 1024:
            with requests.get(self.URL, stream = True) as response:
                if response.status_code == 200:
                    response.raise_for_status()
                    
                    with open(self.PATH, "wb") as file:
                        for chunk in response.iter_content(chunk_size = 1024):
                            file.write(chunk)
                            
            self.DONE = True
        else:
            with requests.get(self.URL) as response:
                if response.status_code == 200:
                    with open(self.PATH, "wb") as file:
                        file.write(response.content)
                        
            self.DONE = True
            
        return
    
    # Function to calculate the size of the downloaded file  
    def get_cursize(self):
        try:
            # Get the current size of the downloaded file
            cursize = os.path.getsize(self.PATH)
        except Exception:
            cursize = 0.0
        
        # Calculate the percentage and time left for the download  
        try:
            percentage = (cursize / self.SIZE) * 100
        except Exception:
            percentage = 0.0
            
        try:
            timeleft = ((self.SIZE - cursize) / (self.SPEED))
        except Exception:
            timeleft = 0.0
        
        return (cursize, percentage, timeleft)
    
    # Function to call the output value  
    def __call__(self):
        return self.DONE
    