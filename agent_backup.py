"""
agent.py

QueryMate AI Data Analyst Agent

Gemini Version

Flow:

1. User asks question.
2. Gemini generates pandas code.
3. Code executes safely.
4. Result/chart returned to Streamlit.
"""

import os
import re
import queue
import time
import pandas as pd

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from google import genai


# =====================================
# CONFIGURATION
# =====================================

MAX_RETRIES = 3

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

EXEC_TIMEOUT = 10


# =====================================
# CODE EXECUTION WORKER
# =====================================

def execute_worker(code, df, output_queue):

    try:

        import numpy as np

        import matplotlib
        matplotlib.use("Agg")

        import matplotlib.pyplot as plt

        safe_builtins = {

            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "range": range,
            "print": print,

            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,

            "str": str,
            "int": int,
            "float": float,

            "round": round,
            "abs": abs,

        }

        local_vars = {

            "df": df,
            "pd": pd,
            "np": np,
            "plt": plt

        }

        exec(
            code,
            {
                "__builtins__": safe_builtins
            },
            local_vars
        )

        output_queue.put(
            {
                "result": local_vars.get("result"),
                "fig": local_vars.get("fig"),
                "error": None
            }
        )

    except Exception as e:

        output_queue.put(
            {
                "result": None,
                "fig": None,
                "error": str(e)
            }
        )



# =====================================
# DATA ANALYST AGENT
# =====================================

class DataAnalystAgent:

    def __init__(self, df, api_key=None):

        self.df = df.copy()

        self.api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
        )

        if not self.api_key:
            raise ValueError(
                "Gemini API Key missing"
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

        self.history = []

        print("=====================================")
        print("🔥 QUERYMATE AGENT LOADED")
        print("🔥 AGENT FILE:", __file__)
        print("🔥 DATAFRAME COLUMNS:")
        print(self.df.columns.tolist())
        print("=====================================")


    # =================================
    # COLUMN HELPERS
    # =================================

    def _has_column(self, column):

        return column in self.df.columns


    def _sales_column(self):

        if self._has_column("total_price"):
            return "total_price"

        for column in [
            "sales",
            "revenue",
            "sales_amount",
            "amount"
        ]:

            if self._has_column(column):
                return column

        return None


    def _date_column(self):

        for column in [
            "order_date",
            "date",
            "created_at",
            "order_datetime"
        ]:

            if self._has_column(column):
                return column

        return None


    # =================================
    # DETERMINISTIC QUERY ROUTER
    # =================================

    def _deterministic_query(self, question):

        q = question.lower().strip()

        print("🔥 QUERY:", question)

        sales_column = self._sales_column()

        date_column = self._date_column()


        # =================================
        # AVERAGE ORDER VALUE
        # =================================

        if (
            "average order value" in q
            or "average order amount" in q
            or "average value of an order" in q
        ):

            if (
                self._has_column("order_id")
                and sales_column
            ):

                print(
                    "🔥 ROUTE: AVERAGE ORDER VALUE"
                )

                return f'''
order_totals = (
    df.groupby("order_id")["{sales_column}"]
      .sum()
)

result = order_totals.mean()
'''


        # =================================
        # PIZZA QUESTIONS
        # =================================

        pizza_question = any(
            phrase in q
            for phrase in [
                "pizza",
                "pizza name",
                "pizza names"
            ]
        )


        ranking_question = any(
            word in q
            for word in [
                "most",
                "highest",
                "best",
                "top",
                "maximum",
                "largest"
            ]
        )


        quantity_question = any(
            phrase in q
            for phrase in [
                "quantity",
                "units",
                "units sold",
                "number sold"
            ]
        )


        # =================================
        # WHICH PIZZA SELLS THE MOST?
        # =================================

        if (
            pizza_question
            and ranking_question
            and self._has_column("pizza_name")
        ):

            if (
                quantity_question
                and self._has_column("quantity")
            ):

                metric = "quantity"

            elif sales_column:

                metric = sales_column

            else:

                metric = None


            if metric:

                match = re.search(
                    r"\btop\s+(\d+)",
                    q
                )

                if match:

                    limit = int(
                        match.group(1)
                    )

                else:

                    limit = 1


                print(
                    "🔥 ROUTE: PIZZA RANKING"
                )

                print(
                    "🔥 GROUP BY: pizza_name"
                )

                print(
                    "🔥 METRIC:",
                    metric
                )

                return f'''
result = (
    df.groupby(
        "pizza_name",
        as_index=False
    )["{metric}"]
    .sum()
    .sort_values(
        "{metric}",
        ascending=False
    )
    .head({limit})
)
'''


        # =================================
        # TOP CATEGORIES
        # =================================

        if (
            "category" in q
            and ranking_question
            and self._has_column("pizza_category")
        ):

            metric = (
                "quantity"
                if (
                    quantity_question
                    and self._has_column("quantity")
                )
                else sales_column
            )


            if metric:

                match = re.search(
                    r"\btop\s+(\d+)",
                    q
                )

                limit = (
                    int(match.group(1))
                    if match
                    else 1
                )


                print(
                    "🔥 ROUTE: CATEGORY RANKING"
                )

                return f'''
result = (
    df.groupby(
        "pizza_category",
        as_index=False
    )["{metric}"]
    .sum()
    .sort_values(
        "{metric}",
        ascending=False
    )
    .head({limit})
)
'''


        # =================================
        # TOP SIZES
        # =================================

        if (
            "size" in q
            and ranking_question
            and self._has_column("pizza_size")
        ):

            metric = (
                "quantity"
                if (
                    quantity_question
                    and self._has_column("quantity")
                )
                else sales_column
            )


            if metric:

                match = re.search(
                    r"\btop\s+(\d+)",
                    q
                )

                limit = (
                    int(match.group(1))
                    if match
                    else 1
                )


                print(
                    "🔥 ROUTE: SIZE RANKING"
                )

                return f'''
result = (
    df.groupby(
        "pizza_size",
        as_index=False
    )["{metric}"]
    .sum()
    .sort_values(
        "{metric}",
        ascending=False
    )
    .head({limit})
)
'''


        # =================================
        # MONTHLY SALES
        # =================================

        monthly_question = any(
            phrase in q
            for phrase in [
                "monthly sales",
                "sales by month",
                "sales per month",
                "sales each month",
                "sales for each month",
                "monthly revenue",
                "revenue by month"
            ]
        )


        if (
            monthly_question
            and sales_column
            and date_column
        ):

            print(
                "🔥 ROUTE: MONTHLY SALES"
            )

            return f'''
df["{date_column}"] = pd.to_datetime(
    df["{date_column}"]
)

monthly = (
    df.assign(
        month=df["{date_column}"].dt.month,
        month_name=df["{date_column}"].dt.month_name()
    )
    .groupby(
        ["month", "month_name"],
        as_index=False
    )["{sales_column}"]
    .sum()
    .sort_values(
        "month"
    )
)

result = monthly[
    ["month_name", "{sales_column}"]
]
'''


        # =================================
        # SALES BY PIZZA
        # =================================

        if (
            "sales by pizza" in q
            or "sales by pizza name" in q
            or "revenue by pizza" in q
        ):

            if (
                self._has_column("pizza_name")
                and sales_column
            ):

                print(
                    "🔥 ROUTE: SALES BY PIZZA"
                )

                return f'''
result = (
    df.groupby(
        "pizza_name",
        as_index=False
    )["{sales_column}"]
    .sum()
    .sort_values(
        "{sales_column}",
        ascending=False
    )
)
'''


        # =================================
        # TOTAL SALES
        # =================================

        total_sales_question = any(
            phrase in q
            for phrase in [
                "total sales",
                "total revenue",
                "total turnover",
                "total earnings"
            ]
        )


        has_dimension = any(
            phrase in q
            for phrase in [
                "by pizza",
                "by category",
                "by size",
                "by month",
                "monthly",
                "by date"
            ]
        )


        if (
            total_sales_question
            and sales_column
            and not has_dimension
        ):

            print(
                "🔥 ROUTE: TOTAL SALES"
            )

            return f'''
result = df["{sales_column}"].sum()
'''


        # =================================
        # NO DETERMINISTIC MATCH
        # =================================

        return None


    # =================================
    # BUILD GEMINI PROMPT
    # =================================

    def _build_system_prompt(self):

        columns = "\n".join(
            f"- {column}: {dtype}"
            for column, dtype
            in self.df.dtypes.items()
        )

        sample = (
            self.df
            .head(5)
            .to_string(index=False)
        )


        return f"""
You are QueryMate AI.

You are an expert pandas data analyst.

A pandas dataframe called df is available.

DATASET COLUMNS:

{columns}

SAMPLE DATA:

{sample}


==================================================
IMPORTANT
==================================================

The user's requested dimension determines
the GROUP BY column.

NEVER group by the first dataframe column.

NEVER automatically group by order_date.

Use the meaning of the user's question.


==================================================
PIZZA DATASET MAPPINGS
==================================================

pizza
pizza name
pizza names
which pizza

    -> pizza_name


sales
revenue
total sales
sales amount

    -> total_price


quantity
units sold
units

    -> quantity


category

    -> pizza_category


size

    -> pizza_size


date
daily

    -> order_date


month
monthly

    -> order_date


order

    -> order_id


==================================================
EXAMPLE
==================================================

User:

Which pizza sells the most?

Correct:

result = (
    df.groupby(
        "pizza_name",
        as_index=False
    )["total_price"]
    .sum()
    .sort_values(
        "total_price",
        ascending=False
    )
    .head(1)
)


WRONG:

df.groupby("order_date")


==================================================
TOP 5
==================================================

User:

Show top 5 pizza names by sales

Correct:

result = (
    df.groupby(
        "pizza_name",
        as_index=False
    )["total_price"]
    .sum()
    .sort_values(
        "total_price",
        ascending=False
    )
    .head(5)
)


==================================================
AVERAGE ORDER VALUE
==================================================

If order_id exists:

order_totals = (
    df.groupby("order_id")["total_price"]
    .sum()
)

result = order_totals.mean()


DO NOT use:

df["total_price"].mean()


==================================================
MONTHLY SALES
==================================================

Use numeric month ordering.

Never alphabetically sort month names.


==================================================
RULES
==================================================

1. Use only existing columns.
2. Never invent columns.
3. Always assign the final result to result.
4. For charts use fig.
5. Return Python code only.
6. Never explain the code.
"""


    # =================================
    # EXTRACT CODE
    # =================================

    def _extract_code(self, text):

        match = re.search(
            r"```(?:python)?\s*(.*?)```",
            text,
            re.DOTALL | re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

        return text.strip()


    # =================================
    # GEMINI GENERATION
    # =================================

    def _generate_code(self, question):

        # ---------------------------------
        # FIRST: DETERMINISTIC ROUTING
        # ---------------------------------

        code = self._deterministic_query(
            question
        )

        if code:

            print(
                "🔥 Deterministic code selected."
            )

            print(
                "🔥 FINAL CODE:"
            )

            print(code)

            return code


        # ---------------------------------
        # SECOND: GEMINI
        # ---------------------------------

        prompt = self._build_system_prompt()

        prompt += f"""

USER QUESTION:

{question}

Return ONLY executable Python code.
"""


        for attempt in range(MAX_RETRIES):

            try:

                print(
                    f"Using Gemini model: {GEMINI_MODEL}"
                )

                response = (
                    self.client
                    .models
                    .generate_content(
                        model=GEMINI_MODEL,
                        contents=prompt
                    )
                )

                code = self._extract_code(
                    response.text
                )


                # ---------------------------------
                # SALES COLUMN SAFETY
                # ---------------------------------

                if (
                    "total_revenue" in code
                    and self._has_column(
                        "total_price"
                    )
                ):

                    code = code.replace(
                        'df["total_revenue"]',
                        'df["total_price"]'
                    )

                    code = code.replace(
                        "df['total_revenue']",
                        "df['total_price']"
                    )


                print(
                    "🔥 GEMINI GENERATED CODE:"
                )

                print(code)

                return code


            except Exception as e:

                print(
                    "Gemini Error:",
                    str(e)
                )

                if (
                    "503" in str(e)
                    and attempt < MAX_RETRIES - 1
                ):

                    time.sleep(5)

                    continue

                raise RuntimeError(
                    f"Gemini Error: {e}"
                )


    # =================================
    # SECURITY CHECK
    # =================================

    def _safe_code(self, code):

        blocked = [
            "import ",
            "__",
            "open(",
            "exec(",
            "eval(",
            "compile",
            "subprocess",
            "socket",
            "requests",
            "os.",
            "sys."
        ]

        for item in blocked:

            if item in code:

                return False, item

        return True, None


    # =================================
    # EXECUTE CODE
    # =================================

    def _run_code(self, code):

        safe, reason = self._safe_code(
            code
        )

        if not safe:

            return {
                "result": None,
                "fig": None,
                "error":
                    f"Blocked code: {reason}"
            }


        output_queue = queue.Queue()


        try:

            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:

                future = executor.submit(
                    execute_worker,
                    code,
                    self.df,
                    output_queue
                )

                future.result(
                    timeout=EXEC_TIMEOUT
                )


            return output_queue.get()


        except TimeoutError:

            return {
                "result": None,
                "fig": None,
                "error":
                    "Execution timeout"
            }


        except Exception as e:

            return {
                "result": None,
                "fig": None,
                "error": str(e)
            }


    # =================================
    # FORMAT RESULT
    # =================================

    def _format_result(self, result):

        if isinstance(
            result,
            pd.DataFrame
        ):

            return result


        if isinstance(
            result,
            pd.Series
        ):

            return result.to_frame()


        return result


    # =================================
    # PUBLIC ASK METHOD
    # =================================

    def ask(self, question):

        attempts = 0

        last_error = None


        while attempts < MAX_RETRIES:

            attempts += 1


            try:

                code = self._generate_code(
                    question
                )


            except Exception as e:

                return {
                    "code": None,
                    "result": None,
                    "fig": None,
                    "error": str(e),
                    "attempts": attempts
                }


            output = self._run_code(
                code
            )


            if output["error"] is None:

                self.history.append({
                    "question": question,
                    "code": code
                })


                return {
                    "code": code,
                    "result":
                        self._format_result(
                            output["result"]
                        ),
                    "fig":
                        output["fig"],
                    "error": None,
                    "attempts":
                        attempts
                }


            last_error = output["error"]


        return {
            "code": None,
            "result": None,
            "fig": None,
            "error": last_error,
            "attempts": attempts
        }




    # =================================
    # BUILD PROMPT
    # =================================

    def _build_system_prompt(self):

        columns = "\n".join(
            [
                f"- {col}: {dtype}"
                for col, dtype in self.df.dtypes.items()
            ]
        )

        print("QUERYMATE COLUMNS:")
        print(self.df.columns.tolist())

        sample = (
            self.df
            .head(5)
            .to_string(index=False)
        )

        return f"""

You are QueryMate AI,
an expert Data Analyst.

You have a pandas dataframe called df.

Dataset Columns:

{columns}


Sample Data:

{sample}


RULES:

1. First understand the dataframe columns.

2. Use ONLY columns listed under Dataset Columns.

3. Never invent column names.

4. Before writing code, verify that every column exists.

5. For sales, revenue, amount, income,
   earnings or turnover:
   - Use the appropriate existing numeric column.
   - If "total_price" exists, use "total_price".
   - Never use an ID column for sales calculations.

6. If "quantity" exists and the user asks
   for units sold, use "quantity".

7. Never use:
   - total_revenue
   - revenue
   - sales_amount

   unless that column actually exists.

8. If the requested column does not exist,
   use the closest matching EXISTING column.

9. Always generate complete executable
   pandas code.

10. Always store the final answer in:

    result

11. For "this year", "current year",
    or "year to date":

    - Find the existing date column.
    - Common date columns may include:
      order_date, date, created_at, order_datetime.
    - Use ONLY a date column that actually exists.
    - Convert it using pd.to_datetime().
    - Filter using:

      pd.Timestamp.now().year

12. If the user asks:

    "What is the total sales this year?"

    and order_date and total_price exist,
    generate code equivalent to:

    df["order_date"] = pd.to_datetime(
        df["order_date"]
    )

    result = df.loc[
        df["order_date"].dt.year
        == pd.Timestamp.now().year,
        "total_price"
    ].sum()

13. IMPORTANT:

    If the user asks for TOTAL sales,
    return ONE total value.

    Do NOT group by month unless
    the user explicitly asks for monthly sales.

14. If the user asks for monthly sales,
    group by month.

15. For questions containing:

    top
    highest
    best
    most
    maximum

    group the data correctly,
    aggregate correctly,
    sort correctly,
    and return only the requested rows.

16. For product, category or name questions,
    use groupby on the appropriate existing column.

17. For charts,
    create a matplotlib figure called:

    fig

18. Do not explain anything.

19. Return ONLY Python code.


EXAMPLES


Question:
What is total revenue?

Code:

result = df["total_price"].sum()


Question:
What is the total sales this year?

Code:

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

result = df.loc[
    df["order_date"].dt.year
    == pd.Timestamp.now().year,
    "total_price"
].sum()


Question:
Show monthly sales this year

Code:

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

current_year = pd.Timestamp.now().year

result = (
    df[
        df["order_date"].dt.year
        == current_year
    ]
    .groupby(
        df["order_date"].dt.month_name()
    )["total_price"]
    .sum()
    .reset_index(name="Total Sales")
)


Question:
Show top 5 pizza names by sales

Code:

result = (
    df.groupby("pizza_name")["total_price"]
      .sum()
      .sort_values(ascending=False)
      .head(5)
      .reset_index(name="Total Sales")
)

"""


    # =================================
    # EXTRACT CODE
    # =================================

    def _extract_code(self, text):

        match = re.search(
            r"```(?:python)?(.*?)```",
            text,
            re.DOTALL
        )

        if match:

            return match.group(1).strip()

        return text.strip()


    # =================================
    # SECURITY CHECK
    # =================================

    def _safe_code(self, code):

        blocked = [

            "import ",
            "__",
            "open(",
            "exec(",
            "eval(",
            "compile",
            "subprocess",
            "socket",
            "requests",
            "os.",
            "sys."

        ]

        for item in blocked:

            if item in code:

                return False, item

        return True, None


    # =================================
    # RUN GENERATED CODE
    # =================================

    def _run_code(self, code):

        safe, reason = self._safe_code(code)

        if not safe:

            return {
                "result": None,
                "fig": None,
                "error":
                    f"Blocked code: {reason}"
            }

        output_queue = queue.Queue()

        try:

            with ThreadPoolExecutor(
                max_workers=1
            ) as executor:

                future = executor.submit(
                    execute_worker,
                    code,
                    self.df,
                    output_queue
                )

                future.result(
                    timeout=EXEC_TIMEOUT
                )

            return output_queue.get()

        except TimeoutError:

            return {
                "result": None,
                "fig": None,
                "error":
                    "Execution timeout"
            }

        except Exception as e:

            return {
                "result": None,
                "fig": None,
                "error":
                    str(e)
            }

    # =================================
    # GEMINI GENERATION
    # =================================

    def _generate_code(self, question):

        q = question.lower()

        # ---------------------------------
        # SALES / REVENUE INSTRUCTIONS
        # ---------------------------------

        if (
                "sales" in q
                or "revenue" in q
                or "turnover" in q
        ):
            question += """

    IMPORTANT SALES RULE:

    For sales/revenue calculations:

    - If "total_price" exists, ALWAYS use:
      df["total_price"]

    - Never use "total_revenue" unless that
      exact column exists in the dataframe.

    - Never use customer_id, order_id,
      pizza_id, or other ID columns
      for sales calculations.

    For "this year" or "current year":

    - If "order_date" exists, use order_date.
    - Convert order_date using pd.to_datetime().
    - Filter using:
      pd.Timestamp.now().year

    For total sales this year:

    1. Convert order_date to datetime.
    2. Filter rows to the current year.
    3. Sum total_price.
    4. Store the answer in result.
    5. Return ONE total number.

    Example:

    df["order_date"] = pd.to_datetime(df["order_date"])

    result = df.loc[
        df["order_date"].dt.year == pd.Timestamp.now().year,
        "total_price"
    ].sum()

    Do NOT group by month unless the user
    explicitly asks for monthly sales.

    """

        print("Modified Question:")
        print(question)

        # ---------------------------------
        # BUILD PROMPT
        # ---------------------------------

        prompt = self._build_system_prompt()

        prompt += f"""

    User Question:

    {question}

    """

        # ---------------------------------
        # GEMINI RETRIES
        # ---------------------------------

        for attempt in range(MAX_RETRIES):

            try:

                print(
                    f"Using Gemini model: {GEMINI_MODEL}"
                )

                response = (
                    self.client
                    .models
                    .generate_content(
                        model=GEMINI_MODEL,
                        contents=prompt
                    )
                )

                # ---------------------------------
                # EXTRACT GENERATED CODE
                # ---------------------------------

                code = self._extract_code(
                    response.text
                )

                # ---------------------------------
                # FIX WRONG SALES COLUMN
                # ---------------------------------

                if (
                        "total_revenue" in code
                        and "total_price" in self.df.columns
                ):
                    code = code.replace(
                        'df["total_revenue"]',
                        'df["total_price"]'
                    )

                    code = code.replace(
                        "df['total_revenue']",
                        "df['total_price']"
                    )

                # ---------------------------------
                # FORCE CORRECT "THIS YEAR"
                # ---------------------------------

                if (
                        (
                                "sales" in q
                                or "revenue" in q
                                or "turnover" in q
                        )
                        and (
                        "this year" in q
                        or "current year" in q
                )
                        and "total_price" in self.df.columns
                        and "order_date" in self.df.columns
                ):

                    code = """
    df["order_date"] = pd.to_datetime(
        df["order_date"]
    )

    result = df.loc[
        df["order_date"].dt.year
        == pd.Timestamp.now().year,
        "total_price"
    ].sum()
    """

                # ---------------------------------
                # FIX SIMPLE SALES QUESTION
                # ---------------------------------

                elif (
                        (
                                "sales" in q
                                or "revenue" in q
                                or "turnover" in q
                        )
                        and "total_price" in self.df.columns
                        and "total_price" not in code
                ):

                    code = """
    result = df["total_price"].sum()
    """

                # ---------------------------------
                # PRINT FINAL CODE
                # ---------------------------------

                print("Generated Code:")
                print(code)

                return code

            except Exception as e:

                error = str(e)

                print(
                    "Gemini Error:",
                    error
                )

                if "503" in error:

                    if attempt < MAX_RETRIES - 1:
                        time.sleep(5)

                        continue

                    raise RuntimeError(
                        "Gemini service is busy. "
                        "Please try again later."
                    )

                raise RuntimeError(
                    f"Gemini Error: {error}"
                )

    # =================================
    # FORMAT RESULT
    # =================================

    def _format_result(self, result):

        if isinstance(
            result,
            pd.DataFrame
        ):

            return result

        if isinstance(
            result,
            pd.Series
        ):

            return result.to_frame()

        return result


    # =================================
    # PUBLIC FUNCTION
    # =================================

    def ask(self, question):

        attempts = 0

        last_error = None

        while attempts < MAX_RETRIES:

            attempts += 1

            try:

                code = self._generate_code(
                    question
                )

            except Exception as e:

                return {
                    "code": None,
                    "result": None,
                    "fig": None,
                    "error": str(e),
                    "attempts": attempts
                }


            output = self._run_code(
                code
            )


            if output["error"] is None:

                self.history.append(
                    {
                        "question": question,
                        "code": code
                    }
                )

                return {

                    "code": code,

                    "result":
                        self._format_result(
                            output["result"]
                        ),

                    "fig":
                        output["fig"],

                    "error": None,

                    "attempts": attempts

                }


            last_error = output["error"]


        return {

            "code": None,

            "result": None,

            "fig": None,

            "error": last_error,

            "attempts": attempts

        }