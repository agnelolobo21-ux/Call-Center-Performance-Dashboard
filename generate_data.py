import pandas as pd
import random
from datetime import datetime, timedelta
NUM_AGENTS = 25
NUM_MONTHS = 6
WORKING_DAYS_PER_MONTH = 26
first_name = ["Sarah","Michael","David","Priya","Rahul","Ananya","James","Neha","Arjun","Kavya"]
last_name = ["Jenkins","Chang","Ross","Sharma","Verma","Iyer","Wilson","Gupta","Nair","Reddy"]

agents= []
for i in range(1,NUM_AGENTS + 1):
    agent_id = f"AGT-{i:03d}"
    name = f"{random.choice(first_name)} {random.choice(last_name)}"
    starting_tenure = random.randint(0,24)
    agents.append({"agent_id": agent_id, "name": name, "starting_tenure": starting_tenure})

# --- GENERATE CALL RECORDS ---

records = []
start_date = datetime(2026, 2, 1) #Month 1 start

for month_num in range(NUM_MONTHS):
    month_label = (start_date + timedelta(days=30 * month_num)).strftime("%B-%Y")

    for agent in agents:
        # tenure grows by 1 each month the agent has worked
        tenure_this_month = agent["starting_tenure"] + month_num

        #tenure influences performance up to a cap (experience curve, then plateaus)
        experience_factor = min(tenure_this_month / 18, 1.0) #maxes out around 18 months

        for day in range(1, WORKING_DAYS_PER_MONTH + 1):
            aht = round(random.gauss(320 - experience_factor * 70, 40), 1) #seconds
            aht = max(120, aht)

            csat_score = round(min(5, max(1, random.gauss(3 + experience_factor * 1.8, 0.7))), 1)

            qa_audit_score = round(min(100, max(50, random.gauss(65 + experience_factor * 30, 8))), 1)

            call_type = "Inbound" #Customer Support department

            resolution_status = random.choices(
                ["Resolved", "Escalated", "Pending", "Unresolved"],
                weights=[40 + experience_factor * 40, 20 - experience_factor * 10,
                         20 - experience_factor * 15, 20 - experience_factor * 15]
            )[0]

            records.append({
                "agent_id": agent["agent_id"],
                "agent_name": agent["name"],
                "month": month_label,
                "day": day,
                "tenure_months": tenure_this_month,
                "call_type": call_type,
                "aht_sec": aht,
                "csat_score": csat_score,
                "qa_audit_score": qa_audit_score,
                "resolution_status": resolution_status
            })

import numpy as np #add this near your other imports at the top if it's not already there

df = pd.DataFrame(records)

# --- Introduce messiness ---

# 1. Missing values (-3%) in three numeric columns
for col in ['aht_sec', 'csat_score','qa_audit_score']:
    missing_idx = df.sample(frac=0.03,  random_state=random.randint(1,9999)).index
    df.loc[missing_idx, col] = np.nan

# 2. Duplicate rows - pick 15 random rows and append copies of them
duplicate_rows=df.sample(n=15, random_state=random.randint(1,9999))
df = pd.concat([df, duplicate_rows], ignore_index=True)

# 3. Inconsistent casing in call_type - some rows become "INBOUND"
inconsistent_idx = df.sample(frac=0.05, random_state=random.randint(1,9999)).index
df.loc[inconsistent_idx, 'call_type'] = 'INBOUND'

# 4. Stray whitespace around some agent_name values
whitespace_idx = df.sample(frac=0.04, random_state=random.randint(1,9999)).index
df.loc[whitespace_idx, 'agent_name'] = df.loc[whitespace_idx, 'agent_name'].apply(lambda x: f" {x} ")

# 5. Unrealistic negative outliers in aht_sec
# Only pick rows where aht_sec is NOT already missing, so the outlier actually shows up
valid_rows = df[df['aht_sec'].notnull()]
outlier_idx = valid_rows.sample(n=5, random_state=random.randint(1, 9999)).index
df.loc[outlier_idx, 'aht_sec'] = -abs(df.loc[outlier_idx, 'aht_sec'])

# Shuffle so the messy rows aren't clustered at the bottom (more realistic)
df = df.sample(frac=1, random_state=random.randint(1, 9999)).reset_index(drop=True)

df.to_csv("01_Raw_Data/call_center_quality_data.csv", index=False)
print("Messy data generated and saved successfully!")