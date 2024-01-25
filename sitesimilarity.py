#-------------------------------------------------------------------------------------
# sitesimilariy - Tool to compare sites and discover real site IP's in order to bypass WAFs 
#-------------------------------------------------------------------------------------
# Author    : cucoo 
# Twitter   : @cucooOnX    
# Github    : cucooOnGitHub#
#-------------------------------------------------------------------------------------
# Description : This tool is based on Luke Stephens (hakluke) tool hakoriginfinder 
#               (see https://github.com/hakluke/hakoriginfinder). This tool accepts as 
#               input parameters, two files containing IP's or URL's and compares them
#               using the Levenshtein algorithm. The main difference between this version 
#               and Lukes version is that this one deals with multiple site comparisions in 
#               a single run and also caches already downloaded pages to reduce requests.
#
# Example :
#               python3 sitesimilarity.py ips.txt urls.txt
#           
#-------------------------------------------------------------------------------------
import requests
import Levenshtein
import sys
import concurrent.futures
from urllib.parse import urlparse
import logging
from multiprocessing import Manager
from urllib3.exceptions import InsecureRequestWarning

# Suppress warnings from urllib3 and requests libraries
logging.captureWarnings(True)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Cache to store fetched content
manager=Manager()
url_cache = manager.dict()

def read_file(filename):
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return content
    except:
        print(f"Error: Reading File '{filename}'")
        sys.exit(1)

def get_web_page(url, debug=False, ignore_ssl_errors=True):
    if debug:
        print(f"Fetching content from: {url}")

    # Check if the content is already in the cache
    if url in url_cache:
        if debug:
            print(f"Cache hit for: {url}")
        return url_cache[url]

    try:
        response = requests.get(url, verify=not ignore_ssl_errors, timeout=3)
        response.raise_for_status()
        content = response.text
        if debug:
            print(f"Cache hit for: {url}")
        
        # Store the content in the cache
        url_cache[url] = content

        return content
    except:
        # Log or handle the error silently
        if debug:
            print(f"Failed get page for: {url}")

        url_cache[url] = None
        return None

def calculate_similarity(text1, text2, threshold=0.9):
    levenshtein_distance = Levenshtein.distance(text1, text2)
    max_length = max(len(text1), len(text2))
    similarity_ratio = 1 - levenshtein_distance / max_length

    return similarity_ratio >= threshold

def compare_urls(url1, url2, threshold, executor, debug=False):
    # Check if the content is already in the cache
    if url1 in url_cache:
        if debug:
            print(f"Cache hit for: {url1}")
        
        content1 = url_cache[url1]
    else:
        content1 = get_web_page(url1, debug=debug)
    
    if url2 in url_cache:
        if debug:
            print(f"Cache hit for: {url2}")
        
        content2 = url_cache[url2]
    else:
        content2 = get_web_page(url2, debug=debug)
            
    if content1 is not None and content2 is not None:
        is_similar = calculate_similarity(content1, content2, threshold)
        if is_similar:
            print(f"Match: '{url1}' and '{url2}'")

def main():
    # Check if two filenames are provided as command-line arguments
    if len(sys.argv) != 3 and len(sys.argv) != 4 and len(sys.argv) != 5 and len(sys.argv) != 6:
        print("Usage: python script.py file1.txt file2.txt [threshold] [num_threads] [debug]")
        sys.exit(1)

    # Redirect stderr to subprocess.DEVNULL to suppress errors
    # sys.stderr = subprocess.DEVNULL

    # Read the contents of the two files
    file1_content = read_file(sys.argv[1])
    file2_content = read_file(sys.argv[2])

    # Split the content of each file into a list of URLs
    file1_urls = file1_content.splitlines()
    

    file2_urls = file2_content.splitlines()

    # Set the default threshold value
    default_threshold = 0.9

    # Check if a threshold value is provided as a command-line argument
    if len(sys.argv) >= 4:
        threshold = float(sys.argv[3])
    else:
        threshold = default_threshold

    # Set the default number of threads
    default_num_threads = 32

    # Check if the number of threads is provided as a command-line argument
    if len(sys.argv) >= 5:
        num_threads = int(sys.argv[4])
    else:
        num_threads = default_num_threads

    # Check if the debug flag is provided as a command-line argument
    debug = len(sys.argv) == 6 and sys.argv[5].lower() == 'true'

    if debug:
        print("Debug mode: Printing all operations.")
        print(f"Comparing with threshold {threshold} using {num_threads} threads.")

    # Compare each combination of HTTP and HTTPS URLs in file1 against file2 using threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for url1 in file1_urls:
            for url2 in file2_urls:
                # Create combinations of HTTP and HTTPS URLs 
                if not url1 or not url2:
                    continue 
                combinations = [
                    ("http://" + urlparse(url1).path, "http://" + urlparse(url2).path),
                    ("https://" + urlparse(url1).path, "https://" + urlparse(url2).path)
                ]

                for http_url1, http_url2 in combinations:
                    futures.append(executor.submit(compare_urls, http_url1, http_url2, threshold, executor, debug=debug))

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
