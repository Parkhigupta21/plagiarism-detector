import requests

from bs4 import BeautifulSoup

from googlesearch import search

from .semantic_similarity import semantic_similarity


# ============================================
# SEARCH INTERNET
# ============================================

def search_web(query):

    try:

        results = []

        for url in search(

            query,

            num_results=5

        ):

            results.append(url)

        return results

    except Exception as e:

        print(e)

        return []


# ============================================
# EXTRACT WEBSITE TEXT
# ============================================

def extract_website_text(url):

    try:

        headers = {

            "User-Agent":
            "Mozilla/5.0"
        }

        response = requests.get(

            url,

            headers=headers,

            timeout=10
        )

        soup = BeautifulSoup(

            response.text,

            "html.parser"
        )

        paragraphs = soup.find_all("p")

        text = " ".join(

            p.get_text()

            for p in paragraphs
        )

        return text[:5000]

    except Exception as e:

        print(e)

        return ""


# ============================================
# GLOBAL PLAGIARISM CHECK
# ============================================

def global_plagiarism_check(uploaded_text):

    results = []

    highest_score = 0

    # Use first meaningful chunk
    query = uploaded_text[:300]

    urls = search_web(query)

    for url in urls:

        try:

            website_text = extract_website_text(
                url
            )

            if not website_text:

                continue

            score = semantic_similarity(

                uploaded_text,

                website_text
            )

            results.append({

                "url": url,

                "score": float(score)
            })

            if score > highest_score:

                highest_score = float(score)

        except Exception as e:

            print(e)

    return {

        "overall_score": float(highest_score),

        "sources": results
    }