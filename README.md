# inchworm
Python script for crawling small websites and parsing relevant text. Text can be saved raw (default) or HTML headers can be used to infer website structure. Initial wrote this to categorize bodies of text on website for usage in downstream RAG application.

This was used to get company information for small websites. Think local business splash pages with a few pages like Contact, About Us, History, Press, etc. In those applications I would use this script to download company info that I could ask questions about using OpenAI.

Not intended for use on large scale websites

# Reuired Libraries
Beautiful Soup

# Usage
Invoke script using
```
python inchworm.py myurl --travel_level=3

--travel_level = how many levels of links  to crawl
--output_file_name = text file name
--text_type = grouped by header or raw text
```