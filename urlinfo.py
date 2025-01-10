# Importing necessary libraries
import requests
import cachetools
import asyncio
from urllib.parse import urlparse
from pathlib import Path

# Defining the MimeType class
class MimeType:
    # Defines instance variables
    URL = None
    SIGS = {}
    TYPES = {}
    EXT = None
    SIZE = None
    
    # Cache with TTL of 300 seconds
    cache = cachetools.TTLCache(maxsize = 100, ttl = 300)
    
    # Defines the initialization function
    def __init__(self, url):
        self.URL = url
        self.SIGS = {  # Dictionary mapping file signatures to file types
            bytes([0x53, 0x50, 0x30, 0x31]) : "bin",
            bytes([0x7F, 0x45, 0x4C, 0x46]) : "bin",
            bytes([0x00, 0x00, 0x01, 0x00]) : "ico",
            bytes([0x66, 0x74, 0x79, 0x70, 0x33, 0x67]) : "3gp",
            bytes([0x66, 0x74, 0x79, 0x70, 0x68, 0x65, 0x69, 0x63]) : "heic",
            bytes([0x66, 0x74, 0x79, 0x70, 0x6d]) : "heic",
            bytes([0x1F, 0x9D]) : "tar.z",
            bytes([0x1F, 0xA0]) : "tar.z",
            bytes([0x47, 0x49, 0x46, 0x38, 0x37, 0x61]) : "gif",
            bytes([0x47, 0x49, 0x46, 0x38, 0x39, 0x61]) : "gif",
            bytes([0x49, 0x49, 0x2A, 0x00]) : "tiff",
            bytes([0x4D, 0x4D, 0x00, 0x2A]) : "tiff",
            bytes([0x49, 0x49, 0x2B, 0x00]) : "tiff",
            bytes([0x4D, 0x4D, 0x00, 0x2B]) : "tiff",
            bytes([0xFF, 0xD8, 0xFF, 0xDB]) : "jpeg",
            bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01]) : "jpeg",
            bytes([0xFF, 0xD8, 0xFF, 0xEE]) : "jpeg",
            
            # TODO: FF D8 FF E1 ?? ?? 45 78 69 66 00 00. Change '??' with actual value
            bytes([0xFF, 0xD8, 0xFF, 0xE1, 0x00, 0x10, 0x45, 0x78, 0x69, 0x66, 0x00, 0x00]) : "jpeg",
            bytes([0xFF, 0xD8, 0xFF, 0xE0]) : "jpg",
            bytes([0x4D, 0x5A]) : "exe",
            bytes([0x5A, 0x4D]) : "exe",
            bytes([0x50, 0x4B, 0x03, 0x04]) : "zip",
            bytes([0x50, 0x4B, 0x05, 0x06]) : "zip",
            bytes([0x50, 0x4B, 0x07, 0x08]) : "zip",
            bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x00]) : "rar",
            bytes([0x52, 0x61, 0x72, 0x21, 0x1A, 0x07, 0x01, 0x00]) : "rar",
            bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]) : "png",
            bytes([0xCA, 0xFE, 0xBA, 0xBE]) : "class",
            bytes([0x25, 0x50, 0x44, 0x46, 0x2D]) : "pdf",
            bytes([0x4F, 0x67, 0x67, 0x53]) : "ogg",
            bytes([0x38, 0x42, 0x50, 0x53]) : "psd",
            
            # TODO: 52 49 46 46 ?? ?? ?? ?? 57 41 56 45. Change '??' with actual value
            bytes([0x52, 0x49, 0x46, 0x46, 0x00, 0x10, 0x20, 0x30, 0x57, 0x41, 0x56, 0x45]) : "wav", 
            
            # TODO: 52 49 46 46 ?? ?? ?? ?? 41 56 49 20. Change '??' with actual value
            bytes([0x52, 0x49, 0x46, 0x46, 0x00, 0x10, 0x20, 0x30, 0x41, 0x56, 0x49, 0x20]) : "avi",  
            bytes([0xFF, 0xFB]) : "mp3",
            bytes([0xFF, 0xF3]) : "mp3",
            bytes([0xFF, 0xF2]) : "mp3",
            bytes([0x49, 0x44, 0x33]) : "mp3",
            bytes([0x42, 0x4D]) : "bmp",
            bytes([0x43, 0x44, 0x30, 0x30, 0x31]) : "iso",
            bytes([0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]) : "doc",
            bytes([0x75, 0x73, 0x74, 0x61, 0x72, 0x00, 0x30, 0x30]) : "tar",
            bytes([0x75, 0x73, 0x74, 0x61, 0x72, 0x20, 0x20, 0x00]) : "tar",
            bytes([0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C]) : "7z",
            bytes([0x1F, 0x8B]) : "gz",
            bytes([0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00]) : "xz",
            bytes([0x1A, 0x45, 0xDF, 0xA3]) : "mkv",
            
            # TODO: 52 49 46 46 ?? ?? ?? ?? 57 45 42 50. Change '??' with actual value
            bytes([0x52, 0x49, 0x46, 0x46, 0x00, 0x10, 0x20, 0x30, 0x57, 0x45, 0x42, 0x50]) : "webp",
            bytes([0x47]) : "mpeg",
            bytes([0x00, 0x00, 0x01, 0xBA]) : "mpeg",
            bytes([0x00, 0x00, 0x01, 0xB3]) : "mpeg",
            bytes([0x66, 0x74, 0x79, 0x70, 0x69, 0x73, 0x6F, 0x6D]) : "mp4",
            bytes([0x66, 0x74, 0x79, 0x70, 0x4D, 0x53, 0x4E, 0x56]) : "mp4",
        }
        self.TYPES = {  # Define a dictionary to map MIME types to file extensions
            "video" : {
                "x-msvideo" : "avi",
                "mp4" : "mp4",
                "mpeg" : "mpeg",
                "ogg" : "ogv",
                "mp2t" : "ts",
                "webm" : "webm",
                "3gpp" : "3gp",
                "3gpp2" : "3g2"
            }, 
            "text" : {
                "css" : "css",  # Text types
                "csv" : "csv",
                "html" : "html",
                "calendar" : "ics",
                "javascript" : "js",
                "plain" : "txt",
                "xml" : "xml"
            }, 
            "audio" : {
                "aac" : "aac",  # Audio types
                "midi" : "midi",
                "x-midi" : "midi",
                "mpeg" : "mp3",
                "ogg" : "opus",
                "wav" : "wav",
                "webm" : "weba",
                "3gpp" : "3gp",
                "3gpp2" : "3g2"
            }, 
            "application" : {
                "x-abiword" : "abw",  # Application types
                "x-freearc" : "arc",
                "vnd.amazon.ebook" : "azw",
                "octet-stream" : self.get_actual(),
                "x-bzip" : "bz",
                "x-bzip2" : "bz2",
                "x-cdf" : "cda",
                "x-csh" : "csh",
                "msword" : "doc",
                "vnd.openxmlformats-officedocument.wordprocessingml.document" : "docx",
                "vnd.ms-fontobject" : "eot",
                "epub+zip" : "epub",
                "gzip" : "gz",
                "x-gzip" : "gz",
                "java-archive" : "jar",
                "json" : "json",
                "ld+json" : "jsonld",
                "vnd.apple.installer+xml" : "mpkg",
                "vnd.oasis.opendocument.presentation" : "odp",
                "vnd.oasis.opendocument.spreadsheet" : "ods",
                "vnd.oasis.opendocument.text" : "odt",
                "ogg" : "ogx",
                "pdf" : "pdf",
                "x-httpd-php" : "php",
                "vnd.ms-powerpoint" : "ppt",
                "vnd.openxmlformats-officedocument.presentationml.presentation" : "pptx",
                "vnd.rar" : "rar",
                "rtf" : "rtf",
                "x-sh" : "sh",
                "x-tar" : "tar",
                "vnd.visio" : "vsd",
                "xhtml+xml" : "xhtml",
                "vnd.ms-excel" : "xls",
                "vnd.openxmlformats-officedocument.spreadsheetml.sheet" : "xlsx",
                "xml" : "xml",
                "atom+xml" : "xml",
                "vnd.mozilla.xul+xml" : "xul",
                "x-zip-compressed" : "zip",
                "x-7z-compressed" : "7z"
            }, 
            "image" : {
                "apng" : "apng",  # Image types
                "avif" : "avif",
                "bmp" : "bmp",
                "gif" : "gif",
                "vnd.microsoft.icon" : "ico",
                "jpeg" : "jpeg",
                "png" : "png",
                "svg+xml" : "svg",
                "tiff" : "tiff",
                "webp" : "webp"
            },
            "font" : {
                "otf" : "otf",  # Font types
                "ttf" : "ttf",
                "woff" : "woff",
                "woff2" : "woff2"
            }
        }
    
    # Function to get the signature from the URL
    @cachetools.cached(cache)
    def get_signature(self):
        response = requests.get(self.URL, stream = True)
        signature = response.raw.read(4)
            
        return signature

    # Function to get the actual file type
    @cachetools.cached(cache)
    def get_actual(self):
        # Function to identify the actual file type
        def identify_type(signature):            
            return self.SIGS.get(signature[:4], "exe")
    
        signature = self.get_signature()
        actual_type = identify_type(signature)
        
        return actual_type
    
    # Function to get the size of the file
    async def get_size(self):
        response = requests.head(self.URL)
        
        if "Content-Length" in response.headers:
            self.SIZE = int(response.headers["Content-Length"])
            
            return
        
        self.SIZE = 0
        
        return

    # Function to get the file type
    async def get_type(self):        
        response = requests.head(self.URL)
        
        if "Content-Type" in response.headers:
            file_type = response.headers["Content-Type"]
            file_type = file_type.split("/")

            if file_type[0] in self.TYPES.keys():
                if file_type[1] in self.TYPES[file_type[0]].keys():
                    self.EXT = self.TYPES[file_type[0]][file_type[1]]
                    
                    return
        
        parsed_url = urlparse(self.URL)
        filename = Path(parsed_url.path.split("/")[-1])
        
        self.EXT = filename.suffix[1:]
        
        return
    
    # Function to call the output value   
    def __call__(self, get = False):
        if get:
            asyncio.run(self.get_type())
            asyncio.run(self.get_size())
        
        return self.EXT, self.SIZE
    
    # Function to call default values
    def __str__(self):
        string = f"""
        Class with values:
        - url: {self.URL}
        - type: {self.EXT}
        """
        
        return string
