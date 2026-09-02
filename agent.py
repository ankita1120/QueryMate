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
    You are QueryMate AI, an expert pandas data analyst.

    A pandas dataframe called df is available.

    DATASET COLUMNS:
    {columns}

    SAMPLE DATA:
    {sample}


    IMPORTANT RULES
    ================

    1. Use ONLY columns that actually exist in df.

    2. NEVER invent a column name.

    3. Before generating code, check the DATASET COLUMNS above.

    4. Always store the final answer in a variable called:
       result

    5. Return ONLY executable Python code.
       Do NOT explain the code.

    6. Do not use markdown code fences.

    7. For charts, create the matplotlib figure in:
       fig


    SALES RULES
    ================

    8. When the user asks about:
       - sales
       - revenue
       - turnover
       - earnings
       - sales amount

       use the appropriate existing numeric column.

    9. If total_price exists, use:
       df["total_price"]

    10. NEVER use:
        total_revenue
        revenue
        sales_amount

        unless those exact columns actually exist.

    11. NEVER use an ID column such as:
        order_id
        pizza_id
        customer_id

        as a sales amount.


    QUANTITY RULES
    ================

    12. If the user asks about:
        - quantity
        - units sold
        - number of units

        and quantity exists, use:
        df["quantity"]


    DATE RULES
    ================

    13. For date questions, use an existing date column.

    14. Possible date columns include:
        order_date
        date
        created_at
        order_datetime

        BUT ONLY use one if it actually exists.

    15. Convert date columns with:

        pd.to_datetime()


    CURRENT YEAR RULE
    ================

    16. If the user asks:
        - this year
        - current year
        - year to date

        find the existing date column and filter using:

        pd.Timestamp.now().year


    17. Example:

        df["order_date"] = pd.to_datetime(
            df["order_date"]
        )

        result = df.loc[
            df["order_date"].dt.year
            == pd.Timestamp.now().year,
            "total_price"
        ].sum()


    TOTAL SALES RULE
    ================

    18. If the user asks:

        "What is the total sales?"

        return ONE total value.

        Example:

        result = df["total_price"].sum()


    19. If the user asks:

        "What is the total sales this year?"

        filter the current year first, then calculate the total.

        Example:

        df["order_date"] = pd.to_datetime(
            df["order_date"]
        )

        result = df.loc[
            df["order_date"].dt.year
            == pd.Timestamp.now().year,
            "total_price"
        ].sum()


    MONTHLY SALES RULE
    ================

    20. ONLY group by month when the user explicitly asks for:

        - monthly sales
        - sales by month
        - sales per month
        - revenue by month
        - monthly revenue

    21. For monthly questions, preserve chronological month order.

    22. Example:

        df["order_date"] = pd.to_datetime(
            df["order_date"]
        )

        result = (
            df.groupby(
                df["order_date"].dt.month,
                as_index=False
            )["total_price"]
            .sum()
            .sort_values("order_date")
        )


    PIZZA RULES
    ================

    23. If the user asks:

        "Which pizza sells the most?"

        and pizza_name exists, group by:

        pizza_name


    24. If the user asks for pizza sales, use:

        df.groupby("pizza_name")["total_price"].sum()


    25. Example:

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


    TOP N RULES
    ================

    26. If the user asks:

        "Show top 5 pizza names by sales"

        use:

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


    27. For words such as:

        top
        highest
        best
        most
        maximum
        largest

        identify the correct dimension from the user's question.

    28. Do NOT automatically group by order_date.

    29. Do NOT automatically group by the first dataframe column.


    CATEGORY RULES
    ================

    30. If the user asks about categories and
        pizza_category exists, use:

        pizza_category


    SIZE RULES
    ================

    31. If the user asks about pizza sizes and
        pizza_size exists, use:

        pizza_size


    AVERAGE ORDER VALUE
    ================

    32. If the user asks:

        "What is the average order value?"

        and order_id and total_price exist:

        order_totals = (
            df.groupby("order_id")["total_price"]
            .sum()
        )

        result = order_totals.mean()

    33. Do NOT simply use:

        df["total_price"].mean()

        because an order may contain multiple rows.


    FINAL REQUIREMENTS
    ================

    34. The final answer MUST always be assigned to:

        result

    35. Use only existing dataframe columns.

    36. Generate complete executable pandas code.

    37. Return ONLY Python code.
    """


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