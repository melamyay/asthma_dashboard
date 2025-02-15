import requests
from bs4 import BeautifulSoup

def fetch_asthma_data():
    """
    Scrapes the WHO asthma fact sheet and extracts relevant sections:
    - Overview
    - Impact
    - Symptoms
    - Causes
    - Treatment

    Returns:
        dict: A dictionary where keys are section titles and values are cleaned content.
    """

    url = "https://www.who.int/news-room/fact-sheets/detail/asthma"

    response = requests.get(url)
    if response.status_code != 200:
        print(f" Failed to retrieve the page. HTTP Status Code: {response.status_code}")
        return {}

    # Parse HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Define sections to extract
    sections = ["Overview", "Impact", "Symptoms", "Causes", "Treatment"]
    extracted_data = {}

    # Iterate through <h2> tags to find sections
    for header in soup.find_all('h2'):
        section_title = header.get_text(strip=True)

        if section_title in sections:
            content = []
            sibling = header.find_next_sibling()

            while sibling and sibling.name != "h2":
                text = sibling.get_text(strip=True).replace("\n", " ")
                text = " ".join(text.split())

                if sibling.name == "p":
                    content.append(text)
                elif sibling.name == "ul":  # Bullet point list
                    bullet_points = ["- " + li.get_text(strip=True) for li in sibling.find_all("li")]
                    content.extend(bullet_points)
                elif sibling.name == "div" and text:
                    content.append(f"- {text}")

                sibling = sibling.find_next_sibling()

            if content:
                extracted_data[section_title] = "\n".join(content)

    return extracted_data

if __name__ == "__main__":
    asthma_data = fetch_asthma_data()

    if asthma_data:
        print("\n Extracted WHO Asthma Data:\n")
        for section, content in asthma_data.items():
            print(f"\n**{section}**\n{content}\n")
