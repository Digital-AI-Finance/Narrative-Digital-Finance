# Zenodo Upload Guide - SNSF Compliance

**Project:** Narrative Digital Finance (SNSF Grant IZCOZ0_213370)
**Last Updated:** December 27, 2025

## SNSF Open Research Data Requirements

**Zenodo is explicitly approved** by SNSF as a generalist data repository.

### What MUST Be Shared (SNSF Mandate)

| Category | SNSF Requirement | From This Project |
|----------|------------------|-------------------|
| **Data underlying publications** | All data enabling reproducibility | `publications.json`, `authors.json` |
| **Metadata** | Authors, dataset descriptions, DOIs | `project_research_outputs.json` |
| **Documentation** | README files explaining data | `wiki_content/Methodology.md`, `Datasets.md` |
| **Code/Software** | When applicable to reproduce results | `fetch_openalex.py`, `generate_accurate_report.py` |

### When to Share
- **As soon as publication is available** - data must be on FAIR-compliant repository
- **Pre-registration allowed** - can reserve DOI before publication

### DOI Requirements
- All shared data MUST receive persistent identifiers (DOIs)
- DOIs should be included in corresponding articles
- DataCite recommended for managing citable datasets

---

## Assets Ready for Zenodo Upload

### REQUIRED by SNSF (when publishing)

| Asset | Path | Why Required |
|-------|------|--------------|
| Publication data | `repo/data/publications.json` | Data underlying publications |
| Author metrics | `repo/data/authors.json` | Reproducibility of team analysis |
| Research outputs | `repo/data/project_research_outputs.json` | Complete project metadata |
| OpenAlex fetcher | `repo/scripts/fetch_openalex.py` | Code to reproduce data collection |

### RECOMMENDED (Documentation)

| Asset | Path | Value |
|-------|------|-------|
| Methodology | `wiki_content/Methodology.md` | Research methods documentation |
| Datasets description | `wiki_content/Datasets.md` | FAIR data documentation |
| Report generator | `FinalScientificReport/generate_accurate_report.py` | SNSF template automation |
| SNSF Report | `FinalScientificReport/Form_Scientific_Report_IC_ACCURATE.docx` | Official project report |

### NOT REQUIRED (Optional)

| Asset | Path | Notes |
|-------|------|-------|
| README | `repo/README.md` | Already on GitHub |
| Application docs | `Application/*.docx` | Historical, not research output |
| Scraping scripts | `scrape_website.py` | Utility, not research |

### Papers Already on Repositories

| Paper | Repository | Action |
|-------|------------|--------|
| TOPol | OSF (osf.io/nr94j) | Link only, already has ID |
| Multimodal Influence | SSRN 4698153 | Link only |
| Reaction Times HFT | SSRN 5112295 | Link only |

---

## SNSF FAIR Compliance Checklist

- [ ] Findable: DOI assigned via Zenodo
- [ ] Accessible: Public repository, no registration required
- [ ] Interoperable: Standard formats (JSON, Python, Markdown)
- [ ] Reusable: CC BY license, documentation included

---

## When Ready to Upload

1. Bundle required + recommended assets
2. Add metadata:
   - Title: "Narrative Digital Finance - Research Data and Code"
   - Authors: All team members with ORCIDs
   - Keywords: narrative economics, NLP, financial markets, structural breaks
   - Grant: SNSF IZCOZ0_213370
3. Choose license: CC BY 4.0 (recommended by SNSF)
4. Upload to Zenodo -> receive DOI
5. Add DOI to publications and website

---

## Sources

- [SNSF Open Research Data](https://www.snf.ch/en/dMILj9t4LNk8NwyR/topic/open-research-data)
- [SNSF Approved Repositories](https://www.snf.ch/en/WtezJ6qxuTRnSYgF/topic/open-research-data-which-data-repositories-can-be-used)
- [SNSF Open Access Info](https://www.snf.ch/en/MDecEyLJgpSTk0cU/page/open-access-information-for-researchers)
