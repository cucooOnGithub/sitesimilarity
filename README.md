# sitesimilarity
Tool to compare sites and discover real site IP's in order to bypass WAFs 

# How does it work?

This tool is based on Luke Stephens (hakluke) tool hakoriginfinder (see https://github.com/hakluke/hakoriginfinder). This tool accepts as input parameters, two files containing IP's or URL's and compares them using the Levenshtein algorithm. You can set the threshold for comparision (default is 0.9) to be more loose or thight and you can also specify the number of threads to use (default is 32).

The main difference between this version and Lukes version is that this one deals with multiple site comparisions in 
a single run and also caches already downloaded pages to reduce requests.

# Usage

Imagine that you have a list of websites all protected by reverse proxy WAF and you want to find the real IP's of those sites. 

In this scenario one can first find a list of ips belonging to the company that owns the websites and compare the sites on those IP's with the website list, using sitesimilarity tool to acomplish that.

The command has the following format:

python3 sitesimilariy.py file1 file2 [threshold] [threads] [debug]

Where:

    file1       : File containing for instance a list of ips to match
    file2       : File containing for instance a list of urls to match
    threshold   : Optional Levenshtein distance threshold, being a value between 0 (complete unmatch) and 1 
                  (full match). The default value is 0.9.
    threads     : Optional number of threads to distribute work. Default value is 32.
    debug       : Optional debug parameter that shows aditional prints for debug purposes. Default is false

Example: 

```
    python3 sitesimilarity.py ips.txt urls.txt 
```

# Output

The output will consist of the input pairs that did match accordingly to the setted threshold.

# Output example

```
    #python3 sitesimilarity.py ips.txt urls.txt

    Match: 1.2.3.4 and www.url1.com
    Match: 4.3.2.1 and www.url2.com

```

# Installation

Just copy the python scritp to a location in your environment path.
