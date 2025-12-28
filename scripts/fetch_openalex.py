"""
OpenAlex API Fetcher for Narrative Digital Finance Project
Fetches author profiles and publications for all team members
"""

import requests
import json
from pathlib import Path
from datetime import datetime
import time

# Configuration
BASE_URL = "https://api.openalex.org"
EMAIL = "joerg.osterrieder@bfh.ch"  # For polite pool access
OUTPUT_DIR = Path(__file__).parent.parent / "data"

# Team members configuration
TEAM_MEMBERS = [
    {
        "name": "Joerg Osterrieder",
        "orcid": "0000-0003-0189-8636",
        "role": "Principal Investigator",
        "affiliation": "Bern Business School / University of Twente",
        "google_scholar": "https://scholar.google.com/citations?user=ocRaXoIAAAAJ",
        "ssrn": "https://papers.ssrn.com/sol3/cf_dev/AbsByAuth.cfm?per_id=2618281",
        # Search by name with filter for more works (disambiguation issue with ORCID)
        "search_terms": ["Joerg Osterrieder"],
        "min_works": 100  # Filter to find the correct profile
    },
    {
        "name": "Gabin Taibi",
        "orcid": "0000-0002-0785-6771",
        "role": "PhD Researcher",
        "affiliation": "Bern Business School / University of Twente",
        "search_terms": ["Gabin Taibi"]
    },
    {
        "name": "Lennart John Baals",
        "orcid": "0000-0002-7737-9675",
        "role": "PhD Researcher",
        "affiliation": "Bern Business School / University of Twente",
        "search_terms": ["Lennart Baals", "Lennart John Baals"],
        "researchgate": "https://www.researchgate.net/scientific-contributions/Lennart-John-Baals-2218848188",
        "linkedin": "https://www.linkedin.com/in/lennart-john-baals-a621aa193/"
    },
    {
        "name": "Yiting Liu",
        "orcid": "0009-0006-9554-8205",  # Correct ORCID for BFH/UT researcher
        "role": "PhD Researcher",
        "affiliation": "Bern Business School / University of Twente",
        "search_terms": ["Yiting Liu"],
        "ut_profile": "https://people.utwente.nl/yiting.liu",
        "msca_profile": "https://www.digital-finance-msca.com/people/yiting-liu"
    },
    {
        "name": "Marius Jan Klein",
        "orcid": None,  # Will search by name
        "role": "Team Member",
        "affiliation": "Bern Business School",
        "search_terms": ["Marius Jan Klein"],  # More specific to avoid wrong matches
        "skip_openalex": True  # Limited online presence, skip API search
    }
]


def make_request(url, params=None):
    """Make API request with polite pool email"""
    if params is None:
        params = {}
    params["mailto"] = EMAIL

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_author_by_orcid(orcid):
    """Fetch author data by ORCID"""
    url = f"{BASE_URL}/authors/https://orcid.org/{orcid}"
    return make_request(url)


def fetch_author_by_name(name, min_works=None):
    """Fetch author data by name search"""
    url = f"{BASE_URL}/authors"
    params = {
        "search": name,
        "per_page": 10
    }
    # Add filter for minimum works if specified
    if min_works:
        params["filter"] = f"works_count:>{min_works}"

    result = make_request(url, params)
    if result and result.get("results"):
        # Return first result (best match)
        return result["results"][0]
    return None


def fetch_works_by_author(author_id, per_page=100):
    """Fetch all works by author ID"""
    url = f"{BASE_URL}/works"
    params = {
        "filter": f"authorships.author.id:{author_id}",
        "per_page": per_page,
        "sort": "publication_year:desc"
    }
    result = make_request(url, params)
    if result:
        return result.get("results", [])
    return []


def process_author(member):
    """Process a single team member"""
    print(f"Processing: {member['name']}")

    # Check if we should skip OpenAlex search
    if member.get("skip_openalex"):
        print(f"  Skipping OpenAlex search (limited online presence)")
        return {
            "name": member["name"],
            "role": member["role"],
            "affiliation": member["affiliation"],
            "openalex_found": False,
            "google_scholar": member.get("google_scholar"),
            "ssrn": member.get("ssrn")
        }

    author_data = None
    min_works = member.get("min_works")

    # If min_works is specified, search by name first (to get the right profile)
    if min_works and member.get("search_terms"):
        for term in member["search_terms"]:
            author_data = fetch_author_by_name(term, min_works=min_works)
            if author_data:
                print(f"  Found via name search with min_works filter")
                break

    # Try ORCID if no result yet and no min_works filter
    if not author_data and member.get("orcid") and not min_works:
        author_data = fetch_author_by_orcid(member["orcid"])

    # Fall back to name search without min_works filter
    if not author_data and member.get("search_terms"):
        for term in member["search_terms"]:
            author_data = fetch_author_by_name(term)
            if author_data:
                break

    if not author_data:
        print(f"  No OpenAlex data found for {member['name']}")
        return {
            "name": member["name"],
            "role": member["role"],
            "affiliation": member["affiliation"],
            "openalex_found": False,
            "google_scholar": member.get("google_scholar"),
            "ssrn": member.get("ssrn")
        }

    # Extract author metrics
    author_info = {
        "name": member["name"],
        "display_name": author_data.get("display_name", member["name"]),
        "role": member["role"],
        "affiliation": member["affiliation"],
        "openalex_found": True,
        "openalex_id": author_data.get("id"),
        "orcid": member.get("orcid") or author_data.get("orcid"),
        "works_count": author_data.get("works_count", 0),
        "cited_by_count": author_data.get("cited_by_count", 0),
        "h_index": author_data.get("summary_stats", {}).get("h_index", 0),
        "i10_index": author_data.get("summary_stats", {}).get("i10_index", 0),
        "2yr_mean_citedness": author_data.get("summary_stats", {}).get("2yr_mean_citedness", 0),
        "google_scholar": member.get("google_scholar"),
        "ssrn": member.get("ssrn"),
        "last_known_institutions": []
    }

    # Get institutions
    if author_data.get("last_known_institutions"):
        for inst in author_data["last_known_institutions"][:3]:
            author_info["last_known_institutions"].append({
                "name": inst.get("display_name"),
                "country": inst.get("country_code")
            })

    print(f"  Found: {author_info['works_count']} works, {author_info['cited_by_count']} citations, h-index: {author_info['h_index']}")

    return author_info


def process_work(work):
    """Extract relevant fields from a work"""
    # Get DOI
    doi = work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None

    # Get venue/source
    source = work.get("primary_location", {}).get("source", {})
    venue = source.get("display_name", "") if source else ""

    # Get authors
    authors = []
    for authorship in work.get("authorships", [])[:10]:  # Limit to first 10 authors
        author = authorship.get("author", {})
        authors.append(author.get("display_name", "Unknown"))

    # Get abstract
    abstract_inverted = work.get("abstract_inverted_index", {})
    abstract = ""
    if abstract_inverted:
        # Reconstruct abstract from inverted index
        word_positions = []
        for word, positions in abstract_inverted.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join([wp[1] for wp in word_positions])

    return {
        "id": work.get("id"),
        "title": work.get("title", "Untitled"),
        "year": work.get("publication_year"),
        "doi": doi,
        "doi_url": work.get("doi"),
        "authors": authors,
        "authors_str": ", ".join(authors[:5]) + ("..." if len(authors) > 5 else ""),
        "venue": venue,
        "cited_by_count": work.get("cited_by_count", 0),
        "type": work.get("type", ""),
        "open_access": work.get("open_access", {}).get("is_oa", False),
        "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
        "concepts": [c.get("display_name") for c in work.get("concepts", [])[:5]],
        "pdf_url": work.get("open_access", {}).get("oa_url")
    }


def fetch_all_data():
    """Main function to fetch all data"""
    print("=" * 60)
    print("OpenAlex Data Fetcher for Narrative Digital Finance")
    print("=" * 60)
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    authors_data = []
    all_publications = []
    seen_work_ids = set()

    for member in TEAM_MEMBERS:
        author_info = process_author(member)
        authors_data.append(author_info)

        # Fetch works if we found the author
        if author_info.get("openalex_id"):
            works = fetch_works_by_author(author_info["openalex_id"])
            print(f"  Fetched {len(works)} publications")

            for work in works:
                work_id = work.get("id")
                if work_id not in seen_work_ids:
                    seen_work_ids.add(work_id)
                    processed = process_work(work)
                    processed["team_member"] = member["name"]
                    all_publications.append(processed)

        # Rate limiting
        time.sleep(0.2)
        print()

    # Sort publications by year (desc) and citations (desc)
    all_publications.sort(key=lambda x: (x.get("year") or 0, x.get("cited_by_count", 0)), reverse=True)

    # Calculate summary stats
    total_citations = sum(a.get("cited_by_count", 0) for a in authors_data)
    total_works = len(all_publications)
    max_h_index = max((a.get("h_index", 0) for a in authors_data), default=0)

    summary = {
        "fetched_at": datetime.now().isoformat(),
        "total_team_members": len(authors_data),
        "total_unique_publications": total_works,
        "total_citations": total_citations,
        "max_h_index": max_h_index,
        "data_source": "OpenAlex API",
        "project": {
            "name": "Narrative Digital Finance",
            "grant": "IZCOZ0_213370",
            "funding": "236,118 CHF",
            "duration": "August 2023 - August 2026",
            "funder": "Swiss National Science Foundation (SNSF)"
        }
    }

    # Save data
    authors_file = OUTPUT_DIR / "authors.json"
    publications_file = OUTPUT_DIR / "publications.json"
    summary_file = OUTPUT_DIR / "summary.json"

    with open(authors_file, "w", encoding="utf-8") as f:
        json.dump(authors_data, f, indent=2, ensure_ascii=False)
    print(f"Saved authors data to {authors_file}")

    with open(publications_file, "w", encoding="utf-8") as f:
        json.dump(all_publications, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(all_publications)} publications to {publications_file}")

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved summary to {summary_file}")

    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Team Members: {len(authors_data)}")
    print(f"  Unique Publications: {total_works}")
    print(f"  Total Citations: {total_citations}")
    print(f"  Max h-index: {max_h_index}")
    print("=" * 60)

    return authors_data, all_publications, summary


if __name__ == "__main__":
    fetch_all_data()
