import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_payments_canada_rss():
    urls = [
        ('https://www.payments.ca/insights/newsroom', 'Newsroom'),
        ('https://www.payments.ca/insights/corporate-reports', 'Corporate Reports'),
        ('https://www.payments.ca/insights/research', 'Research'),
        ('https://www.payments.ca/insights/modernization', 'Modernization')
    ]
    
    # Create RSS structure
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    
    ET.SubElement(channel, 'title').text = 'Payments Canada - All Updates'
    ET.SubElement(channel, 'link').text = 'https://www.payments.ca/insights'
    ET.SubElement(channel, 'description').text = 'Combined feed from Newsroom, Corporate Reports, Research, and Modernization'
    ET.SubElement(channel, 'language').text = 'en'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    all_items = []
    seen_urls = set()
    
    for url, category in urls:
        try:
            print(f'Fetching {category}...')
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Build full URL
                if href.startswith('/'):
                    full_url = f'https://www.payments.ca{href}'
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                
                # Filter for article links and avoid duplicates
                if (full_url.startswith('https://www.payments.ca/') and 
                    full_url not in seen_urls and 
                    len(text) > 15 and
                    'insights' not in text.lower() and
                    'newsroom' not in text.lower()):
                    
                    seen_urls.add(full_url)
                    all_items.append({
                        'title': f'[{category}] {text}',
                        'link': full_url,
                        'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                    })
                    print(f'  Found: {text[:50]}...')
        
        except Exception as e:
            print(f'Error fetching {category}: {e}')
            continue
    
    print(f'\nTotal items found: {len(all_items)}')
    
    # Add items to RSS (limit to 50 most recent)
    for item_data in all_items[:50]:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = item_data['title']
        ET.SubElement(item, 'link').text = item_data['link']
        ET.SubElement(item, 'guid').text = item_data['link']
        ET.SubElement(item, 'pubDate').text = item_data['pubDate']
    
    # Write to file
    tree = ET.ElementTree(rss)
    ET.indent(tree, space='  ')
    tree.write('payments-canada-feed.xml', encoding='utf-8', xml_declaration=True)
    print(f'Payments Canada RSS feed generated successfully')

if __name__ == '__main__':
    generate_payments_canada_rss()
