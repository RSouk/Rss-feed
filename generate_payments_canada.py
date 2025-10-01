import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET

def generate_payments_canada_rss():
    urls = [
        'https://www.payments.ca/insights/newsroom',
        'https://www.payments.ca/insights/corporate-reports',
        'https://www.payments.ca/insights/research',
        'https://www.payments.ca/insights/modernization'
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
    
    for url in urls:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract links - adjust selectors based on actual page structure
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Filter for content links
                if href and len(text) > 15 and 'insights' in href:
                    full_url = f'https://www.payments.ca{href}' if not href.startswith('http') else href
                    
                    # Avoid duplicates
                    if full_url not in [item['link'] for item in all_items]:
                        all_items.append({
                            'title': text,
                            'link': full_url,
                            'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                        })
        
        except Exception as e:
            print(f'Error fetching {url}: {e}')
            continue
    
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
    print(f'Payments Canada RSS feed generated with {len(all_items[:50])} items')

if __name__ == '__main__':
    generate_payments_canada_rss()
