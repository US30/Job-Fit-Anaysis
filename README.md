# Automated Resume and JD Fit Analyzer 

A Streamlit application that analyzes a candidate's resume against a job description to calculate a percentage fit score. You can paste a JD manually or fetch it from a URL using the built-in scraper. The analysis is based on a weighted comparison of skills, years of experience, and expected salary (CTC).

Now includes LLM-powered features:

- Auto-detect mandatory skills from the JD using a zero-shot classifier
- Auto-extract minimum required experience (years) from the JD

> This tool provides a quantitative measure to help recruiters and hiring managers quickly screen and prioritize candidates.

![image](https://github.com/US30/Job-Fit-Anaysis/blob/main/appui.png)

---

## How It Works

The final fit score is a weighted average with a mandatory-skills gate:

- **Mandatory Skills Rule**: If any mandatory skill is missing from the resume, the candidate is marked **Not Fit** and scoring stops.
- **Skills Fit (50%)**: Computed only from non-mandatory JD skills that appear in the resume.
- **Experience Fit (30%)**: Full score if candidate experience ≥ JD minimum; otherwise `(candidate / minimum) * 100`.
- **CTC Fit (20%)**: Full score if expected CTC ≤ JD max; otherwise `(JD max / expected) * 100`.

Skill extraction uses spaCy pattern matching over a curated skills list (`skills_db.json`). PDF text is extracted from the uploaded resume and matched against JD skills.

LLM assistance (in `llm_analyzer.py`):

- Uses Hugging Face Transformers zero-shot classification (`facebook/bart-large-mnli`) to classify skills as "mandatory" vs "nice-to-have" based on surrounding JD context
- Extracts minimum years of experience from the JD text

---

## Tech Stack

- **Backend & Logic**: Python
- **Web UI**: Streamlit
- **NLP**: spaCy (`en_core_web_sm`) for skill extraction
- **LLM**: Hugging Face Transformers + PyTorch (zero-shot classification via `facebook/bart-large-mnli`)
- **PDF Parsing**: PyPDF2
- **Web Scraping**: Requests + BeautifulSoup (generic selectors; may need site-specific tweaks)
- **Data Store (optional)**: MongoDB Atlas (helpers present; not enabled by default)

---

## Getting Started

Follow these instructions to get the project running locally.

### Prerequisites

- Python 3.11 (recommended)
- Git
- (Optional) MongoDB Atlas account if you plan to enable persistence

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/US30/Job-Fit-Anaysis.git
   cd Job-Fit-Anaysis
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Required Libraries**
   ```bash
   # Core app deps
   pip install streamlit spacy PyPDF2 requests beautifulsoup4 python-dotenv watchdog

   # LLM deps (first run will download ~1.6 GB model)
   pip install "transformers[sentencepiece]" torch accelerate safetensors

   # spaCy English model
   python -m spacy download en_core_web_sm
   ```

4. **(Optional) Configure MongoDB (Atlas)**
   The app runs without a database by default. If you want to persist outputs, create a `.env` file and add:
   ```
   MONGO_URI="mongodb+srv://<username>:<password>@<cluster>/<db>?retryWrites=true&w=majority"
   ```
   Then wire the helpers in `database.py` from your `app.py` if needed (see below).

### ⚠️ Important Security Note

The `.gitignore` should exclude `.env`. Never commit credentials to version control.

---

## How to Run the Application

With your virtual environment activated, start the Streamlit application:

```bash
streamlit run app.py
```

Your browser should open the running app.

Workflow highlights:

- In the left column, fetch a JD via URL or paste it manually
- Click "🤖 Auto-detect Skills & Experience (with LLM)" to populate mandatory skills and JD experience automatically
- Review and edit the populated "Mandatory Skills" and "Minimum Years of Experience" if needed
- Upload a resume (PDF) and click "Analyze Final Fit"

---

## Using the URL Scraper

1. In the left column, enter a job posting URL and click **Fetch & Parse Job Description**.
2. If parsing succeeds, the JD text area populates with the scraped content; otherwise, an error is shown.
3. You can always edit or overwrite the JD content manually.

Notes:
- The scraper (`job_scraper.py`) is generic and uses common container selectors. You may need to customize the HTML selectors for specific sites.
- Some sites block bots or require auth. If errors occur, try a different source or paste the JD manually.

---

## Files of Interest

- `app.py`: Streamlit UI and orchestration
- `analysis.py`: Scoring logic and mandatory skills rule
- `resume_parser.py`: PDF text extraction (PyPDF2)
- `skill_extractor.py`: Skill extraction via spaCy patterns using `skills_db.json`
- `job_scraper.py`: Generic JD scraper using Requests + BeautifulSoup
- `llm_analyzer.py`: LLM helpers
  - `find_mandatory_skills_with_llm(jd_text, all_skills)`
  - `find_experience_with_llm(jd_text)`
- `database.py`: Optional MongoDB helpers (`connect_to_mongo`, `save_analysis_data`)

---

## Enabling MongoDB Persistence (Optional)

The app does not write to MongoDB by default. To enable it:

1. Ensure `.env` contains a valid `MONGO_URI`
2. In `app.py`, import and create a connection once at startup:
   ```python
   from database import connect_to_mongo, save_analysis_data
   db = connect_to_mongo()
   ```
3. After computing results, save them:
   ```python
   save_analysis_data(db, job_description={"text": st.session_state.jd_text}, candidate_profile={"experience": candidate_experience_input, "expected_ctc": candidate_ctc_input}, analysis_result=details)
   ```

If the connection succeeds, you'll see "Successfully connected to MongoDB Atlas!" in the terminal logs.

---

## Troubleshooting

- First run is slow / large download: the zero-shot model (~1.6 GB) is downloaded on first use
- macOS on Apple Silicon: Transformers will use `mps` (Metal) if available; CPU fallback is automatic
- ModuleNotFoundError: Make sure your venv is active and all installs succeeded
- Port already in use: run `streamlit run app.py --server.port=8502`

---

## Future Improvements

- Advanced skill matching (aliases, embeddings, semantic similarity)
- Site-specific scrapers or a pluggable scraping strategy
- Batch analysis and a results dashboard
- REST API backend and separate frontend

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
