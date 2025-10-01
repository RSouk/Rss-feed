import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import sys

def generate_payments_canada_rss():
    print("=== Starting Payments Canada RSS Generation ===")
    
    urls = [
        ('https://www.payments.ca/insights/newsroom', 'Newsroom'),
        ('https://www.payments.ca/insights/corporate-reports', 'Corporate Reports'),
        ('https://www.payments.ca/insights/research', 'Research'),
        ('https://www.payments.ca/insights/modernization', 'Modernization')
    ]
    
    try:
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
                print(f'Fetching {category} from {url}...')
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(url, timeout=30, headers=headers)
                response.raise_for_status()
                print(f'  Status: {response.status_code}')
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find all links
                links = soup.find_all('a', href=True)
                print(f'  Found {len(links)} total links')
                
                count = 0
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
                    
                    # Filter for article links
                    if (full_url.startswith('https://www.payments.ca/') and 
                        full_url not in seen_urls and 
                        len(text) > 10 and
                        full_url != url):
                        
                        seen_urls.add(full_url)
                        all_items.append({
                            'title': f'[{category}] {text}',
                            'link': full_url,
                            'pubDate': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                        })
                        count += 1
                        if count <= 3:  # Show first 3
                            print(f'    - {text[:60]}...')
                
                print(f'  Added {count} items from {category}')
            
            except Exception as e:
                print(f'ERROR fetching {category}: {str(e)}')
                import traceback
                traceback.print_exc()
                continue
        
        print(f'\n=== Total items found: {len(all_items)} ===')
        
        if len(all_items) == 0:
            print("WARNING: No items found! Feed will be empty.")
        
        # Add items to RSS (limit to 50)
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
        print(f'\n=== Feed written successfully to payments-canada-feed.xml ===')
        
    except Exception as e:
        print(f'FATAL ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    generate_payments_canada_rss()
