import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from crawler import fetch_case, fetch_statutes, fetch_gazettes

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    # 1. Fetch docs
    case_ids = [267890, 267891, 267892, 267893, 267894]
    cases    = [fetch_case(cid) for cid in case_ids]
    statutes = fetch_statutes(limit=5)
    gazettes = fetch_gazettes(limit=5, year="2025")

    # 2. Build DataFrame
    df = pd.DataFrame(cases + statutes + gazettes)
    df.to_csv(f"{DATA_DIR}/kenya_law_full.csv", index=False)
    print(f"✅ Saved CSV → {DATA_DIR}/kenya_law_full.csv")

    # 3. Plot coverage heatmap
    df2 = df.dropna(subset=["year"])
    pivot = df2.pivot_table(
        index="type",
        columns="year",
        values="id",
        aggfunc="count",
        fill_value=0
    ).astype(int)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
    ax.set_title("Document Coverage by Type × Year")
    ax.set_ylabel("Doc Type")
    ax.set_xlabel("Year")

    img_path = f"{DATA_DIR}/coverage_heatmap.png"
    fig.savefig(img_path)
    print(f"✅ Saved heatmap → {img_path}")

if __name__ == "__main__":
    main()
