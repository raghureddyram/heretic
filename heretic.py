# Design a python function that will visit all subdomains of a website ("https://www.spacejam.com/1996/") by
# following links on the website starting from its home page. Here are the rules that the function should follow
# 1. Keep track of all links seen in this matter, as well as all links visited. Print these at the end.
# 2. Do not visit links if they leave the domain provided (i.e. do not follow absolute links to instagram,
# facebook, etc). Still record these links as seen.
# 3. Treat a link that starts with http as absolute
# 4. Treat a link that starts with / as relative from the perspective of the base website domain
# (i.e. base_url = "https://base.com/", link = "/page" --> "https://base.com/page"
# 5. Treat all other links as siblings to current url
# (i.e. current_url = "https://base.com/page/1", link="2" --> https://base.com/page/2")
# 6. Resolve links with paths containing '../' to ones without '../' This can be treated similarly to how folder
# navigation in command line works
# (i.e. "https://base.com/pages/2/../../other_pages/1" --> https://base.com/other_pages/1)
# 7. If a link contains #, ignore # and anything following it
# 8. Only follow into links that either have no file ending or end in '.html'
# For this task, your base_url is "https://www.spacejam/com/1996/" Please provide the code to perform this task,
# the outputs of the number of links visited & seen, and a paragraph explaining your implementation.
# Here is a helper function for gathering links from a url



# The SubdomainCrawler is a Python class designed to visit all subdomains of a given website, 
# starting from a specified base URL (e.g., "https://www.spacejam.com/1996/"). 
# It follows internal links recursively while keeping track of both visited and seen links. 
# The crawl method is the main driver, starting with the base URL and continuing through all internal links within the same domain. 
# External links are not followed but are still recorded as seen.

# The class handles various types of links using helper functions such as __normalize_link, 
# which converts relative and sibling links to absolute URLs. 
# The __resolve_dot_segments function processes paths with ../ or ./ segments, ensuring proper path normalization,
# similar to command-line folder navigation. Additionally, 
# the crawler only follows links that either end with .html or have no file extension, 
# checked via the __is_crawlable helper function.

# Fragments (anything after #) are stripped using simple string manipulation to prevent revisiting the same page multiple times 
# with different fragment identifiers. The results include the total number of unique links visited and all links seen.

import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse, urljoin
import os
import pdb

class SubdomainCrawler:
    def __init__(self, base_url="https://www.spacejam.com/1996/"):
        """
        Initializes the SubdomainCrawler object.
        - `visited`: a set to keep track of all visited URLs to avoid revisiting.
        - `seen`: a set to track all URLs seen during the crawl, including external links.
        - `base_url`: the initial URL from which the crawl starts.
        """
        self.visited = set()
        self.seen = set()
        self.base_url = base_url

    def crawl(self, url=None):
        """
        Crawls the website starting from the base_url.
        - Visits each URL and recursively follows internal links (within the same domain).
        - Skips external links and marks them as seen.
        """
        if url is None:
            url = self.base_url

        if url in self.visited:
            return 

        self.visited.add(url)
        print(f"Visiting: {url}")

        available_links = self.__get_http_from_website(url)
        for link in available_links:
            crawlable_path = link.split('#')[0]  # no need to follow to an ID location
            full_link = self.__absolute_link(url, crawlable_path)
            parsed_link = urlparse(full_link)

            if not self.__is_current_domain(parsed_link):
                self.seen.add(full_link)
                continue
            if self.__is_crawlable(full_link, parsed_link):
                self.seen.add(full_link)
                self.crawl(full_link)
            else:
                self.seen.add(full_link)

        return {"seen_count": len(self.seen), "visited_count": len(self.visited)}

    def __get_http_from_website(self, url: str):
        """
        Fetches all links from a given URL.
        - Makes up to 3 attempts to request the page and extract all 'a' tag links.
        - Returns a list of links extracted from the page.
        """
        links = []
        for _ in range(3):
            try:
                r = requests.get(url)
                for link in BeautifulSoup(r.content, "html.parser", parse_only=SoupStrainer('a')):
                    if link.has_attr('href'):
                        links.append(link['href'])
                return links
            except Exception:
                pass
        return links

    def __is_current_domain(self, parsed_link):
        """
        Checks if the provided link belongs to the same domain as the base URL.
        - Compares the domain (netloc) of the parsed link and the base URL.
        """
        return parsed_link.netloc == urlparse(self.base_url).netloc

    def __normalize_link(self, current_url, link):
        """
        Normalizes a link based on its type:
        - Absolute links (starting with 'http') are returned as-is.
        - Relative links (starting with '/') are resolved relative to the base domain.
        - Sibling links are resolved relative to the current URL.
        """
        if link.startswith("http"):
            return link
        elif link.startswith("/"):
            return urljoin(self.base_url, link)
        else:
            return urljoin(current_url, link)

    def __resolve_dot_segments(self, url):
        """
        Resolves dot segments ('../', './') in the URL path similar to how file navigation works.
        - Uses os.path.normpath to normalize the URL path and remove unnecessary segments.
        """
        parsed_url = urlparse(url)
        path = os.path.normpath(parsed_url.path)
        return parsed_url._replace(path=path).geturl()

    def __absolute_link(self, current_url, path):
        """
        Converts a relative or sibling link to an absolute URL by normalizing it.
        - Uses the current URL and the provided path, then resolves dot segments.
        """
        normalized = self.__normalize_link(current_url, path)
        return self.__resolve_dot_segments(normalized)

    def __is_crawlable(self, full_link, parsed_link):
        """
        Determines if a link is crawlable based on whether it has already been seen,
        if it ends in '.html', or if it has no file extension.
        
        Args:
        - full_link: The absolute URL of the link.
        - parsed_link: A parsed URL (result of urlparse).

        Returns:
        - bool: True if the link is crawlable, False otherwise.
         """
        # Check if the link has an HTML ending or no file extension
        return full_link not in self.seen and (parsed_link.path.endswith('.html') or '.' not in os.path.basename(parsed_link.path))



test = SubdomainCrawler()
print(test.crawl())

def test_all_visited_domains_same_as_base_domain(input_set, base_url):
    domains = [urlparse(item).netloc for item in input_set]
    base_domain = urlparse(base_url).netloc
    return all(domains) and domains[0] == base_domain

def test_not_all_seen_domains_same(input_set):
    domain = [urlparse(item).netloc for item in input_set]
    return all(domain)

assert test_all_visited_domains_same_as_base_domain(test.visited, test.base_url) == True
assert test_not_all_seen_domains_same(test.seen) == False
