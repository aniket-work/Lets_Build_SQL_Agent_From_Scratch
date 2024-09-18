import pandas as pd

# Data from the image
data = {
    "index": [0, 1, 2, 3, 4],
    "work_year": [2023, 2023, 2023, 2023, 2023],
    "experience_level": ["SE", "MI", "MI", "SE", "SE"],
    "employment_type": ["FT", "CT", "CT", "FT", "FT"],
    "job_title": ["Principal Data Scientist", "ML Engineer", "ML Engineer", "Data Scientist", "Data Scientist"],
    "salary": [80000, 30000, 25500, 175000, 120000],
    "salary_currency": ["EUR", "USD", "USD", "USD", "USD"],
    "salary_in_usd": [85847, 30000, 25500, 175000, 120000],
    "employee_residence": ["ES", "US", "US", "CA", "CA"],
    "remote_ratio": [100, 100, 100, 100, 100],
    "company_location": ["ES", "US", "US", "CA", "CA"],
    "company_size": ["L", "S", "S", "M", "M"]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save as CSV
csv_path = "ds-salaries.csv"
df.to_csv(csv_path, index=False)

csv_path
