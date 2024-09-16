from datetime import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

DB_USER = "deliverable_taskforce"
DB_PASSWORD = "learn_sql_2024"
DB_HOSTNAME = "training.postgres.database.azure.com"
DB_NAME = "deliverable"

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:5432/{DB_NAME}")


@st.cache_data
def get_data():
    # Gemiddelde aantal reviews per dag per stad in 2023

    df = pd.read_sql_query(
        """
    SELECT res.colophon_data_city as city, rev.datetime::DATE as date, COUNT(*) as review_count
    FROM reviews rev inner join restaurants res on
    res.restaurant_id = rev.restaurant_id
    where res.colophon_data_city in ('Amsterdam','Rotterdam','Groningen')
    and EXTRACT(year from rev.datetime) = 2023
    GROUP BY res.colophon_data_city , date
                           """,
        con=engine,
    )

    df["date"] = pd.to_datetime(df["date"])
    return df


df = get_data()

start_time = datetime(year=2023, month=1, day=1, hour=00, minute=00, second=0)
end_time = datetime(year=2024, month=1, day=1, hour=00, minute=00, second=0)

min_date, max_date = st.slider(
    "Select dates", min_value=start_time, max_value=end_time, value=(start_time, end_time)
)

df = df[(df["date"] <= max_date) & (df["date"] >= min_date)]

pivoted_df = df.pivot(index="city", columns="date", values="review_count")

cities = st.multiselect("Choose city", ["Amsterdam", "Rotterdam", "Groningen"])

if not cities:
    st.error("Please select at least one city.")
else:
    # Filter het op tijd

    # Tabel met aantal reviews per dag
    piv_data = pivoted_df.loc[cities]
    st.write("### Number of reviews per day", piv_data.sort_index())

    # Bar chart met het gemiddelde per stad
    mean_df = df.drop(columns=["date"])
    mean_df = mean_df.groupby("city").mean()
    mean_df = mean_df.loc[cities]
    st.bar_chart(mean_df)

    # Plot van de ontwikkeling van het totaal aantal reviews in de tijd
    cumulative_df = piv_data.cumsum(axis=1)
    st.title("Cumulative Reviews per City in 2023")
    cumulative_df = cumulative_df.T

    st.line_chart(cumulative_df)
