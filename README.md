# Job Description Skill Fit Analysis PoC

A simple Proof of Concept (PoC) application that analyzes a candidate's profile against a job description to calculate a percentage fit score. The analysis is based on a weighted comparison of skills, years of experience, and expected salary (CTC).

> This tool provides a quantitative measure to help recruiters and hiring managers quickly screen and prioritize candidates.

![image](https://user-images.githubusercontent.com/11333333/193247053-12547148-529a-4f51-8b01-9f9361622321.png)
*(Note: Replace the above image link with a screenshot of your actual application once it's running.)*

---

## How It Works

The final fit score is a weighted average of three key parameters:

*   **Skills Fit (50% Weight):** Compares the list of required skills in the Job Description (JD) with the skills listed in the candidate's profile.
    *   *Formula: `(Number of Matching Skills / Total Skills in JD) * 100`*
*   **Experience Fit (30% Weight):** Compares the candidate's years of experience with the minimum requirement in the JD. The fit is capped at 100% if the candidate's experience exceeds the requirement.
    *   *Formula: `(Candidate Experience / JD Experience) * 100`*
*   **CTC Fit (20% Weight):** Compares the candidate's expected salary with the budget defined in the JD. The fit is 100% if the expectation is within budget, otherwise it is scaled down.
    *   *Formula: `(JD Budget / Candidate Expectation) * 100`*

The results of each analysis are saved as separate documents in a MongoDB Atlas database for potential future reference.

---

## Tech Stack

*   **Backend & Logic:** Python
*   **Web Framework:** Streamlit
*   **Database:** MongoDB Atlas
*   **Python Libraries:**
    *   `pymongo` for database connectivity.
    *   `python-dotenv` for managing environment variables.

---

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   Python 3.7+
*   Git
*   A free MongoDB Atlas account and a cluster set up.

### Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/job-fit-poc.git
    cd job-fit-poc
    ```

2.  **Create and Activate a Virtual Environment**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Required Libraries**
    A `requirements.txt` file is included for easy installation.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    This project uses a `.env` file to store the database connection string securely.
    *   Rename the example file from `.env.example` to `.env`.
    *   Open the new `.env` file and replace the placeholder with your actual MongoDB Atlas connection string.

    ```
    # .env file
    MONGO_URI="mongodb+srv://<your_username>:<your_password>@<your_cluster_address>/"
    ```

### ⚠️ Important Security Note

The `.gitignore` file is configured to **ignore** the `.env` file. This is intentional.

**DO NOT, under any circumstances, commit or push your `.env` file to GitHub.** It contains your secret database credentials.

---

## How to Run the Application

With your virtual environment activated and the `.env` file configured, start the Streamlit application with the following command:

```bash
streamlit run app.py
```

Your web browser should automatically open a new tab with the running application. You can now input the job and candidate details and see the analysis in real-time.

---

## Future Improvements

This PoC provides a solid foundation. Future enhancements could include:
*   **Advanced Skill Matching:** Use NLP to account for skill aliases (e.g., "JS" and "JavaScript") or related technologies.
*   **Resume Parsing:** Automatically extract skills, experience, and other data from uploaded PDF or DOCX resumes.
*   **Batch Analysis:** Allow for matching one job description against a list of candidates from the database.
*   **Dashboard:** Create a dashboard to view and filter all saved candidates and their fit scores for various roles.
*   **REST API:** Separate the backend logic into a REST API (using Flask or FastAPI) and a dedicated frontend (using React, Vue, etc.).

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
