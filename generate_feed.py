import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_osfi_rss():
    url = 'https://www.osfi-bsif.gc.ca/en/news'
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Create RSS structure
        rss = ET.Element('rss', version='2.0')
        channel = ET.SubElement(rss, 'channel')
        
        ET.SubElement(channel, 'title').text = 'OSFI News'
        ET.SubElement(channel, 'link').text = url
        ET.SubElement(channel, 'description').text = 'News from the Office of the Superintendent of Financial Institutions'
        ET.SubElement(channel, 'language').text = 'en'
        ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # Extract news links
        links = soup.find_all('a', href=True)
        seen = set()
        count = 0
        
        for link in links:
            if count >= 50:  # Limit to 50 items
                break
                
            href = link['href']
            text = link.get_text(strip=True)
            
            if '/en/news/' in href and href not in seen and len(text) > 10:
                seen.add(href)
                full_url = f'https://www.osfi-bsif.gc.ca{href}' if not href.startswith('http') else href
                
                item = ET.SubElement(channel, 'item')
                ET.SubElement(item, 'title').text = text
                ET.SubElement(item, 'link').text = full_url
                ET.SubElement(item, 'guid').text = full_url
                ET.SubElement(item, 'pubDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                
                count += 1
        
        # Write to file
        tree = ET.ElementTree(rss)
        ET.indent(tree, space='  ')
        tree.write('feed.xml', encoding='utf-8', xml_declaration=True)
        print(f'RSS feed generated successfully with {count} items')
        
    except Exception as e:
        print(f'Error generating feed: {e}')
        raise

if __name__ == '__main__':
    generate_osfi_rss()
