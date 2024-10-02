import argparse
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
import re
import time


def remove_trailing_slash(s):
    # Check if the string ends with a "/" and remove it
    if s.endswith("/"):
        return s[:-1]
    return s

def check_same_domain(url1, url2):
    #Parse the URLs and extract the netloc
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    
    return domain1 == domain2

# Define a function to clean ascii extra characters generally found in website
def clean_text(text):
    # Remove \u200b (Zero Width Space) and \xa0 (Non-breaking Space)
    return re.sub(r'[\u200b\xa0]', '', text.strip())

def output_data_raw(all_website_text, output_file_name):
    print(all_website_text)
    with open(output_file_name, 'w') as f:
        for text in all_website_text:
            f.write(text + '\n')
    print(f"Raw data written to {output_file_name}")
    
def output_data_formatted(content_by_heading, output_file_name):
    with open(output_file_name, 'w') as f:
        for heading, paragraphs in content_by_heading.items():
            f.write(f"Heading: {heading}\n")
            f.write("Content:\n")
            for paragraph in paragraphs:
                f.write(paragraph + '\n')
            f.write("\n")
    print(f"Formatted data written to {output_file_name}")
    #writes output to .txt file
    # Format data for RAG application
    '''
    formatted_data = []

    for heading, paragraphs in content_by_heading.items():
        # Join paragraphs under each heading into a single string
        combined_text = ' '.join(paragraphs)
        
        # Create a dictionary for each document
        document = {
            "title": heading,
            "text": combined_text
        }
        
        # Append the formatted document to the list
        formatted_data.append(document)

    # Print formatted data
    for doc in formatted_data:
        print(doc)
    '''
def main():
    parser = argparse.ArgumentParser(description="Simple python script to try and get company website info")
    parser.add_argument("url", type=str, help="URL for website to inchworm")  
    parser.add_argument("--output_file_name", type=str, help="Output file name", default="output.txt")
    parser.add_argument("--text_type", type=str, help="How to format output text",default="raw")
    parser.add_argument("--travel_level", type=int, help="How many levels deep to search for links", default=3)

    # Parse the arguments
    args = parser.parse_args()
    initial_link = args.url
    link_list = [
        {'link': remove_trailing_slash(initial_link), 'traveled':False, 'level': 1}
    ]
    
    all_website_text=[]
    content_by_heading = {}
    current_heading = None
    #loop over untraveled pages until all are traveled
    while (result := next( (l for l in link_list if l.get("traveled") == False), None)):
        print(f"Traversing {result['link']}")

        #If this link level is greater than the travel level we continue loop and set traveled to true
        if result['level'] > args.travel_level:
            result["traveled"] = True
            continue 

        #Get html body
        html = urlopen(result['link']).read()
        soup = BeautifulSoup(html,'html.parser')
        
        #Extract and loop through all links on page if they are valid http or https
        #This portion of the regex: (?!.*\.\w+$).*$ just ignores common file extensions
        #So that we don't try and grab a PDF or JPG by mistake
        for link in soup.findAll('a', attrs={'href': re.compile(r"^(https?://)(?!.*\.\w+$).*$")}):

            #If any link is not yet in our list we will add it to the link list
            #also make sure it's in the same domain as our initial link, otherwise we dont want it
            if not any(d.get('link') == link.get('href') for d in link_list) and check_same_domain(link.get('href'),initial_link):
                print("Adding new link: " + link.get('href'))
                link_list.append({"link":link.get('href'), "traveled": False, 'level': result['level'] + 1 })

        #remove common junk
        for unwanted in soup.select('ad, nav, footer'):
            unwanted.decompose()

        #Only search for relevant tags
        meaningful_tags = soup.select('h1, h2, h3, p, article, div.main-content')
        
        if args.text_type == 'raw':
            for element in meaningful_tags:
                #Only grab raw text, don't try to categorize
                all_website_text.append(clean_text(element.get_text(strip=True)))
        elif args.text_type == 'formatted':
            for element in meaningful_tags:
                if element.name in ['h1','h2','h3']:
                    #Update the current heading and create a kv pair with the heading and empty array
                    current_heading = element.get_text(strip=True)
                    content_by_heading[current_heading]=[]
                    #paragraphs.append(f"**{element.get_text(strip=True)}**")
                if element.name == 'p' and current_heading:
                    #Add clean text if not blank
                    if ct:=clean_text(element.get_text(strip=True)):
                        content_by_heading[current_heading].append(ct)


        result["traveled"] = True
    if args.text_type == 'raw':
        output_data_raw(all_website_text, args.output_file_name)
    elif args.text_type == 'formatted':
        output_data_formatted(content_by_heading, args.output_file_name)

if __name__ == "__main__":
    main()