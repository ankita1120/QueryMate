"""
app.py
Streamlit front-end for QueryMate AI Data Analyst

Run:
    streamlit run app.py
"""
import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from profiler import DataProfiler
from suggestions import generate_questions
from agent import DataAnalystAgent
from smart_analyzer import SmartAnalyzer
from visualizer import DataVisualizer
from cleaner import DataCleaner
from insight_generator import InsightGenerator
from dashboard_builder import DashboardBuilder
from overview import DatasetOverview
from report_generator import ReportGenerator
from ml_recommender import MLRecommender
from chart_recommender import ChartRecommender
from chat_memory import ChatMemory
from file_loader import FileLoader
from database_loader import DatabaseLoader
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy import text
from mysql_connection import (
    get_mysql_server_connection,
    get_mysql_connection
)






load_dotenv()


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="QueryMate AI Data Analyst",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 QueryMate AI - Data Analyst")
st.caption(
    "Upload any CSV dataset and analyze it using natural language."
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.header("⚙️ Setup")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", "")
    )

    data_source = st.radio(
        "Select Data Source",
        ["CSV/Excel", "MySQL"]
    )

    if data_source == "CSV/Excel":

        uploaded_files = st.file_uploader(
            "Upload Dataset(s)",
            type=["csv", "xlsx", "xls"],
            accept_multiple_files=True
        )

    elif data_source == "MySQL":

        st.info("Using MySQL Connection")


# -----------------------------
# Load Dataset
# -----------------------------

try:

    # ==========================
    # CSV / Excel
    # ==========================

    if data_source == "CSV/Excel":

        if not uploaded_files:
            st.warning("⚠️ Please upload CSV or Excel file.")
            st.stop()

        file = uploaded_files[0]

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        else:
            df = pd.read_excel(file)

        st.success(
            f"✅ Loaded: {file.name}"
        )

        st.dataframe(df.head())


    # ==========================
    # MySQL
    # ==========================

    elif data_source == "MySQL":

        # Connect to MySQL server
        server_engine = get_mysql_server_connection()

        # --------------------------
        # Get all databases
        # --------------------------
        databases = pd.read_sql(
            "SHOW DATABASES",
            server_engine
        )

        system_databases = [
            "information_schema",
            "mysql",
            "performance_schema",
            "sys"
        ]

        database_list = [
            db for db in databases.iloc[:, 0].tolist()
            if db not in system_databases
        ]

        database_name = st.selectbox(
            "Select MySQL Database",
            database_list
        )

        if database_name:

            # Connect to selected database
            engine = get_mysql_connection(
                database_name
            )

            # --------------------------
            # Get tables
            # --------------------------
            tables = pd.read_sql(
                "SHOW TABLES",
                engine
            )

            if len(tables) == 0:

                st.warning(
                    "No tables found in this database."
                )


            else:

                table_list = tables.iloc[:, 0].tolist()

                table_name = st.selectbox(
                    "Select MySQL Table",
                    table_list
                )

                if table_name:
                    query = f"""
                    SELECT *
                    FROM `{table_name}`
                    """

                    df = pd.read_sql(
                        query,
                        engine
                    )

                    st.success(
                        f"✅ Database: {database_name} | Table: {table_name}"
                    )

                    st.dataframe(
                        df
                    )

                    st.write("Columns:")
                    st.write(df.columns.tolist())


            # ==========================
            # CHECK DATASET
            # ==========================

            if "df" not in locals():
                st.warning(
                    "⚠️ Please load a dataset first."
                )

                st.stop()

            st.write(
                f"📊 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns"
            )


    # ==========================
    # Dataset Information
    # ==========================

    if "df" in locals():

        st.write(
            f"📊 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns"
        )

    else:

        st.warning(
            "⚠️ Please load a dataset first."
        )


except Exception as e:

    st.error(
        f"❌ Data loading error:\n{e}"
    )


# =========================
# Dataset Overview
# =========================

st.subheader("📌 Dataset Overview")

try:

    overview = DatasetOverview(df)

    overview_data = overview.generate()

    for key, value in overview_data.items():
        st.write(f"**{key}:** {value}")

except Exception as e:

    st.error(
        f"Overview generation error: {e}"
    )

## =========================
# QueryMate Dashboard
# =========================

st.subheader("📊 QueryMate AI Dashboard")

try:
    dashboard = DashboardBuilder(df)

    kpis = dashboard.generate_kpis()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Rows", kpis.get("Total Rows", 0))

    with col2:
        st.metric("Total Columns", kpis.get("Total Columns", 0))

    with col3:
        st.metric("Missing Values", kpis.get("Missing Values", 0))

    with col4:
        st.metric("Duplicate Rows", kpis.get("Duplicate Rows", 0))

except Exception as e:
    st.error(f"Dashboard error: {e}")



# -----------------------------
# Dataset Preview
# -----------------------------

st.subheader("📄 Dataset Preview")

st.dataframe(
    df.head(10),
    use_container_width=True
)

st.info(
    f"Showing first 10 rows of {len(df)} total rows"
)

st.write(
    "📌 Columns:",
    list(df.columns)
)

# -----------------------------
# Automatic Dataset Profiling
# -----------------------------

try:

    profiler = DataProfiler(df)

    profile_report = profiler.profile()

except Exception as e:

    st.error(
        f"Profiling error: {e}"
    )

    st.stop()




## -----------------------------
# Profile Report
# -----------------------------

st.subheader("📊 Dataset Profile")

try:

    rows = profile_report.get("rows", 0)
    columns = profile_report.get("columns", 0)
    duplicates = profile_report.get("duplicates", 0)
    missing = profile_report.get("total_missing_values", 0)
    memory = profile_report.get("memory_usage_mb", 0)
    quality = profile_report.get("quality_score", 0)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Rows", rows)

    with col2:
        st.metric("Columns", columns)

    with col3:
        st.metric("Duplicates", duplicates)

    with col4:
        st.metric("Missing Values", missing)

    with col5:
        st.metric("Memory (MB)", f"{memory} MB")

    with col6:
        st.metric("Quality Score", f"{quality}%")

except Exception as e:

    st.error(f"Profile display error: {e}")

# -----------------------------
# Dataset Structure
# -----------------------------

st.subheader("📂 Dataset Structure")

col1, col2, col3 = st.columns(3)


with col1:

    st.write("**🔢 Numeric Columns**")

    st.write(
        profile_report.get(
            "numeric_columns",
            []
        )
    )


with col2:

    st.write("**📝 Categorical Columns**")

    st.write(
        profile_report.get(
            "categorical_columns",
            []
        )
    )


with col3:

    st.write("**📅 Datetime Columns**")

    st.write(
        profile_report.get(
            "datetime_columns",
            []
        )
    )


# -----------------------------
# Column Information
# -----------------------------

st.subheader("📌 Column Information")

try:

    profile_df = pd.DataFrame(
        profile_report.get(
            "column_details",
            []
        )
    )

    st.dataframe(
        profile_df,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Column information error: {e}"
    )

# -----------------------------
# Numeric Statistics
# -----------------------------

st.subheader("📈 Numeric Statistics")

numeric_stats = profile_report.get(
    "numeric_statistics",
    {}
)

if numeric_stats:

    numeric_df = pd.DataFrame(
        numeric_stats
    ).T

    st.dataframe(
        numeric_df,
        use_container_width=True
    )

else:

    st.info(
        "No numeric columns found."
    )


# -----------------------------
# Data Cleaning Assistant
# -----------------------------

st.subheader("🧹 Data Cleaning Assistant")

try:

    cleaner = DataCleaner(df)

    missing = cleaner.missing_values_report()

    duplicates = cleaner.duplicate_report()


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Missing Values",
            sum(missing.values())
        )


    with col2:

        st.metric(
            "Duplicate Rows",
            duplicates
        )


    if missing:

        st.write("Missing Value Details:")

        st.json(missing)

    else:

        st.success(
            "No missing values found."
        )


    if duplicates > 0:

        st.warning(
            f"{duplicates} duplicate rows detected."
        )

    else:

        st.success(
            "No duplicate rows found."
        )


    if st.button("✨ Clean Dataset"):

        cleaned_df = cleaner.clean_dataset()

        st.success(
            "Dataset cleaned successfully!"
        )

        st.dataframe(
            cleaned_df.head(10),
            use_container_width=True
        )


except Exception as e:

    st.error(
        f"Cleaning error: {e}"
    )


# -----------------------------
# Automatic Visualizations
# -----------------------------

st.subheader("📊 Data Visualizations")

visualizer = DataVisualizer(df)


# Matplotlib Charts
visualization_charts = visualizer.numeric_charts()


if visualization_charts:

    for chart in visualization_charts:

        st.pyplot(chart)

else:

    st.info(
        "No numeric columns available for charts."
    )


# Correlation Heatmap

heatmap = visualizer.correlation_chart()


if heatmap:

    st.subheader(
        "🔥 Correlation Heatmap"
    )

    st.pyplot(
        heatmap
    )

# =========================
# AI Insights
# =========================

insight_engine = InsightGenerator(df)

insights = insight_engine.generate_basic_insights()

st.subheader("💡 AI Dataset Insights")

for insight in insights:
    st.write(insight)


# -----------------------------
# Categorical Statistics
# -----------------------------

st.subheader("📝 Categorical Statistics")


categorical_stats = profile_report.get(
    "categorical_statistics",
    {}
)


if categorical_stats:

    categorical_df = pd.DataFrame(
        categorical_stats
    ).T


    st.dataframe(
        categorical_df,
        use_container_width=True
    )

else:

    st.info(
        "No categorical columns found."
    )


# -----------------------------
# AI Suggested Questions
# -----------------------------

st.subheader("🤖 AI Suggested Questions")

try:

    questions = generate_questions(df)

    if questions:

        for question in questions:

            st.write(
                f"• {question}"
            )

    else:

        st.info(
            "No suggested questions available."
        )


except Exception as e:

    st.error(
        f"Question generation error: {e}"
    )



# =========================
# Automatic AI Chart Selection
# =========================

st.subheader("🤖 AI Recommended Charts")

chart_ai = ChartRecommender(df)

recommended_charts = chart_ai.recommend_charts()


for chart in recommended_charts:

    st.plotly_chart(
        chart,
        use_container_width=True
    )


# =========================
# Conversation Memory
# =========================

if "memory" not in st.session_state:

    st.session_state.memory = ChatMemory()


memory = st.session_state.memory


# -----------------------------
# ML Model Suggestions
# -----------------------------

st.subheader("🧠 ML Model Recommendations")


try:

    recommender = MLRecommender(df)

    recommendations = recommender.recommend()


    if recommendations:

        for item in recommendations:

            st.write(
                f"✅ {item}"
            )

    else:

        st.info(
            "No ML recommendations available."
        )


except Exception as e:

    st.error(
        f"ML Recommendation Error: {e}"
    )



# -----------------------------
# Ask QueryMate AI
# -----------------------------

st.subheader("🤖 Ask QueryMate AI")


# Show previous conversation

if memory.get_history():

    st.subheader("🧠 Conversation History")

    for chat in memory.get_history():

        st.write(
            "👤 **You:**",
            chat["question"]
        )

        st.write(
            "🤖 **QueryMate:**",
            chat["answer"]
        )


question = st.text_input(
    "Ask a question about your dataset",
    placeholder="Example: What is the total revenue?"
)


if st.button("Analyze Dataset"):

    if not api_key:

        st.error(
            "Please enter your Gemini API Key."
        )


    elif not question.strip():

        st.warning(
            "Please enter a question."
        )


    else:

        try:

            agent = DataAnalystAgent(
                df=df,
                api_key=api_key
            )


            with st.spinner(
                "QueryMate is analyzing your dataset..."
            ):

                response = agent.ask(
                    question
                )


            if response["error"]:

                st.error(
                    response["error"]
                )


            else:

                st.success(
                    "✅ Analysis Complete!"
                )

                st.subheader(
                    "📊 QueryMate Result"
                )


                # Save chat memory

                memory.add(
                    question,
                    str(response["result"])
                )


                if response["result"] is not None:


                    if isinstance(
                        response["result"],
                        pd.DataFrame
                    ):

                        st.dataframe(
                            response["result"],
                            use_container_width=True
                        )


                    else:

                        st.write(
                            response["result"]
                        )


                if response["fig"] is not None:

                    st.subheader(
                        "📈 Visualization"
                    )

                    st.pyplot(
                        response["fig"]
                    )


                with st.expander(
                    "🧩 Generated Python Code"
                ):

                    st.code(
                        response["code"],
                        language="python"
                    )


        except Exception as e:

            st.error(
                f"Error: {e}"
            )

# =========================
# Report Generator
# =========================

st.subheader("📄 Generate Report")

if st.button("Create Analysis Report"):

    try:

        reporter = ReportGenerator(
            df=df,
            insights=insights,
            profile=profile_report
        )

        report_file = reporter.generate()

        st.success(
            "Report generated successfully!"
        )

        with open(report_file, "rb") as file:

            st.download_button(
                label="⬇️ Download Report",
                data=file,
                file_name="QueryMate_Report.pdf",
                mime="application/pdf"
            )

    except Exception as e:

        st.error(
            f"Report error: {e}"
        )
