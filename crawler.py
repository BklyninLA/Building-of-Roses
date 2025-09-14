import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import fitz  # PyMuPDF
from summarizer import ai_summary

BASE_URL    = "https://new.kenyalaw.org"
CASE_VIEW   = f"{BASE_URL}/caselaw/cases/view/"
STATUTES_UI = f"{BASE_URL}/legislation/acts"
GAZETTE_UI  = f"{BASE_URL}/gazettes"
HEADERS     = {"User-Agent": "KenyaLawBot/1.0"}

def fetch_case(case_id: int) -> dict:
    url  = f"{CASE_VIEW}{case_id}/"
    r    = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    title   = soup.find("h1").get_text(strip=True)
    court   = (soup.find("div", class_="court_name") or soup).get_text(strip=True)
    date    = (soup.find("div", class_="case_date") or soup).get_text(strip=True)
    body    = soup.find("div", class_="case_content")
    content = body.get_text("\n", strip=True) if body else ""
    summary = ai_summary(content)
    year    = date[:4] if len(date) >= 4 else None

    return {
        "type":    "case",
        "id":      str(case_id),
        "title":   title,
        "source":  court,
        "date":    date,
        "year":    year,
        "content": content,
        "summary": summary
    }

def fetch_statutes(limit: int = 5) -> list:
    r    = requests.get(STATUTES_UI, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links= soup.select("a[href*='/legislation/acts/view/']")[:limit]
    out  = []

    for a in links:
        href    = a["href"]
        detail  = urljoin(BASE_URL, href)
        r2      = requests.get(detail, headers=HEADERS)
        s2      = BeautifulSoup(r2.text, "html.parser")
        title   = s2.find("h1").get_text(strip=True)
        paras   = s2.select("div.legislation_content p")
        content = "\n".join(p.get_text(strip=True) for p in paras)
        summary = ai_summary(content)
        out.append({
            "type":    "statute",
            "id":      href.split("/")[-1],
            "title":   title,
            "source":  "Statute",
            "date":    None,
            "year":    None,
            "content": content,
            "summary": summary
        })
    return out

def fetch_gazettes(limit: int = 5, year: str = "2025") -> list:
    url   = f"{GAZETTE_UI}/{year}"
    r     = requests.get(url, headers=HEADERS)
    soup  = BeautifulSoup(r.text, "html.parser")
    links = soup.select("a[href*='/gazettes/view/']")[:limit]
    out   = []

    for a in links:
        href    = a["href"]
        detail  = urljoin(GAZETTE_UI, href)
        r2      = requests.get(detail, headers=HEADERS)
        s2      = BeautifulSoup(r2.text, "html.parser")
        title   = s2.find("h1").get_text(strip=True)
        date_div= s2.find("div", class_="gazette_date")
        date    = date_div.get_text(strip=True) if date_div else None

        pdf_link= s2.find("a", href=lambda h: h and h.endswith(".pdf"))["href"]
        pdf_url = urljoin(BASE_URL, pdf_link)
        pdf_r   = requests.get(pdf_url, headers=HEADERS)
        doc     = fitz.open(stream=pdf_r.content, filetype="pdf")
        text    = "".join(page.get_text() for page in doc)

        summary = ai_summary(text)
        out.append({
            "type":    "gazette",
            "id":      href.split("/")[-1],
            "title":   title,
            "source":  "Gazette",
            "date":    date,
            "year":    date[:4] if date else None,
            "content": text,
            "summary": summary
        })
    return out
