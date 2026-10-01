# IDAI2021000467-Tejasvi-Reddy-Kandimalla

# ⚽ Player Injuries & Team Performance Dashboard

Candidate Name: Tejasvi Reddy Kandimalla

Candidate Registration Number-: 1000467

CRS Name: Artificial Intelligence

Course Name: Unit 2- Mathematics for AI II

School Name: https://idai2021000467-tejasvi-reddy-kandimalla-h6ardcvq3h2ejen33bc3rs.streamlit.app/ 


An interactive Streamlit dashboard built for **FootLens Analytics** (Scenario 1, Mathematics for AI-II Summative Assessment). It shows technical directors and sports managers how player injuries affect team results and how players perform after they recover.

---

## What the Dashboard Analyses

The dashboard uses a dataset of player injuries and team performance across several seasons. Each record holds the player, club, position, age, injury type, injury start and return dates, the team's results and goal difference in matches before, during and after the injury, and the player's match ratings before and after.

It answers five questions:

1. **Which injuries led to the biggest team performance drop?** Injury types are ranked by how much the team's goal difference fell while the player was absent.
2. **What was the team's win/loss record during a player's absence?** Results and points per match are compared across the before, during and after phases.
3. **How did individual players perform after recovery?** Each player's average match rating after the injury is compared with the rating before it.
4. **Are there specific months or clubs with frequent injury clusters?** Injury counts are broken down by club and month.
5. **Which clubs suffer most due to injuries?** Clubs are compared on injury counts and average performance drop.

### Performance drop index

The main measure of injury impact is the **performance drop index**:

> Performance drop index = team's average goal difference **before** the injury − team's average goal difference **during** the player's absence

A **positive** value means the team did worse without the player. A **negative** value means the team did better.

---

## Key Features

- **Sidebar filters:** filter by club, season, injury type and player age. All charts and metrics update instantly.
- **Summary metrics:** injury cases, players injured, average days out, average team drop index and average rating change.
- **Five interactive Plotly visualisations** with hover details and zoom:
  1. **Bar chart:** the top 10 injuries with the highest team performance drop, with a minimum-cases slider so rare injuries don't dominate.
  2. **Line chart:** a chosen player's match ratings before and after a chosen injury, with average lines for each phase.
  3. **Heatmap:** injury frequency across months and clubs.
  4. **Scatter plot:** player age against performance drop index, coloured by position, with bubble size showing days out.
  5. **Leaderboard table:** comeback players ranked by rating improvement after injury.
- **Data download:** a button to download the filtered data as a CSV file.
- **Clear error handling:** the app shows a helpful message if the data file is missing or if the filters return no results.

---

## Screenshots

### Top 10 injuries with the highest team performance drop
<img width="1406" height="715" alt="image" src="https://github.com/user-attachments/assets/ab3a748c-e671-499d-938c-487d209840f1" />


### Player performance timeline (before and after injury)
<img width="1405" height="762" alt="image" src="https://github.com/user-attachments/assets/017b1ad7-9631-4324-8752-1d3afd9258f3" />


### Injury frequency across months and clubs
<img width="1337" height="547" alt="image" src="https://github.com/user-attachments/assets/163fc547-ae41-4eb5-b07f-9cacd81d1be3" />


### Player age vs. performance drop index
<img width="1390" height="745" alt="image" src="https://github.com/user-attachments/assets/e081d364-fb8b-49ab-a5fb-1370886c5ebd" />


### Comeback leaderboard
<img width="1376" height="673" alt="image" src="https://github.com/user-attachments/assets/1687fd16-1f20-4662-8d61-961a989b595f" />


---

## Data Preprocessing and Cleaning

The cleaning was done in Google Colab with pandas (see `notebooks/data_preprocessing.ipynb`). The result is `cleaned_player_injuries.csv`, which the dashboard reads.

- Loaded the dataset with pandas, treating markers such as `N.A.` as missing values (NaN).
- Renamed unclear columns for readability, for example `Name` to `player_name`, `Date of Injury` to `injury_start` and `Match1_before_injury_Player_rating` to `before_m1_rating`.
- Converted injury start and end dates to datetime format. Rows missing a date, or with a return date before the injury date, were removed, along with duplicate rows.
- Converted ratings and goal difference columns to numbers. Missing match values were kept as NaN so averages only use matches with data. Missing age and FIFA rating values were filled with the median.
- Standardised match result labels (win, draw, lose).
- Grouped the data by player name to calculate summary statistics for the three injury phases (before, during and after).

### Engineered columns

| Column | Meaning |
| --- | --- |
| `avg_rating_before`, `avg_rating_after` | Player's average match rating before and after the injury |
| `rating_change` | `avg_rating_after` minus `avg_rating_before` |
| `avg_gd_before`, `avg_gd_during`, `avg_gd_after` | Team's average goal difference in each phase |
| `avg_points_before`, `avg_points_during`, `avg_points_after` | Team's average points per match in each phase (win = 3, draw = 1, lose = 0) |
| `performance_drop_index` | `avg_gd_before` minus `avg_gd_during` |
| `points_drop_index` | `avg_points_before` minus `avg_points_during` |
| `injury_duration_days` | Days between injury start and return |
| `injury_month_name`, `injury_year` | Used for the injury frequency heatmap |

---

## Project Overview and Integration Details

1. **Colab notebook:** pandas loads the raw CSV, cleans it, creates the new columns and exports `cleaned_player_injuries.csv`.
2. **`app.py`:** Streamlit reads the cleaned CSV (cached with `st.cache_data`), applies the sidebar filters and passes the filtered data to the Plotly charts.
3. **Streamlit Community Cloud:** deploys `app.py` directly from this GitHub repository and installs the packages in `requirements.txt`.

**Tech stack:** Python, pandas, NumPy, Plotly, Streamlit, Google Colab, GitHub.

---

## Deployment Instructions

### Run locally

1. Download this repository as a ZIP from GitHub (Code → Download ZIP) and unzip it, or clone it with Git.
2. Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

3. The app opens in your browser at `http://localhost:8501`.

### Deploy on Streamlit Community Cloud

1. Make sure `app.py`, `requirements.txt` and `cleaned_player_injuries.csv` are in the root of this repository.
2. Go to [streamlit.io](https://streamlit.io/) and sign in with GitHub.
3. Click **Deploy an app** (or **Create app**).
4. Select this repository and the `main` branch, and set the main file path to `app.py`.
5. Click **Deploy**. After a minute or two the app is live at a public link.

---

## Repository Structure

```
├── app.py                        # Streamlit dashboard
├── requirements.txt              # Python packages
├── cleaned_player_injuries.csv   # Cleaned data used by the app
├── notebooks/
│   └── data_preprocessing.ipynb  # Data cleaning and feature engineering (Colab)
├── screenshots/                  # Dashboard screenshots
└── README.md
```

---

## Notes on Interpretation

- Goal difference is the main measure of team performance, so the drop index reflects match results, not just wins and losses.
- Averages rest on a small number of matches around each injury, so single cases should be read with care. The minimum-cases slider on the bar chart helps with this.
