
import json

import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AI DataViz Agent",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Enterprise Text-to-SQL & DataViz Agent")

N8N_WEBHOOK_URL = st.sidebar.text_input(
    "n8n Webhook URL",
    value="http://localhost:5678/webhook/text-to-sql"
)

user_query = st.chat_input(
    "Ask a question about your business data..."
)

if user_query:
    st.chat_message("user").write(user_query)

    with st.spinner("Validating SQL and executing query..."):
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json={"question": user_query},
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            # Debug: inspect the complete n8n response
            with st.expander("Debug: Raw n8n Response"):
                st.json(result)

            # Normalize a single-item list into an object
            if isinstance(result, list):
                if (
                    len(result) == 1
                    and isinstance(result[0], dict)
                ):
                    result = result[0]
                else:
                    st.error(
                        "n8n returned a list instead of one JSON "
                        "object. Check the Respond to Webhook node."
                    )
                    st.stop()

            if not isinstance(result, dict):
                st.error("Expected a JSON object from n8n.")
                st.stop()

            # Security guardrail
            if result.get("is_safe") is not True:
                st.error(
                    "🚨 Query rejected by the security guardrail."
                )
                st.write(
                    result.get("reason", "SQL marked unsafe.")
                )
                st.stop()

            executed_sql = result.get("sql", "")
            rows = result.get("data", [])

            # Display generated SQL
            with st.expander("View Generated & Validated SQL"):
                st.code(executed_sql, language="sql")

            # Parse serialized JSON, if necessary
            if isinstance(rows, str):
                try:
                    rows = json.loads(rows)
                except json.JSONDecodeError:
                    st.error(
                        "The data field contains invalid JSON."
                    )
                    st.stop()

            if isinstance(rows, dict):
                rows = [rows]

            if not isinstance(rows, list):
                st.error(
                    "Invalid response: data must be a list of rows."
                )
                st.stop()

            if not rows:
                st.warning(
                    "The query returned 0 rows. "
                    "Inspect the SQL and raw response above."
                )
                st.stop()

            if not all(isinstance(row, dict) for row in rows):
                st.error(
                    "Invalid data format: each row must be a JSON object."
                )
                st.stop()

            # Convert results into a DataFrame
            df = pd.DataFrame(rows)

            # Convert numeric strings such as "3" into actual numbers
            for col in df.columns:
                if (
                    pd.api.types.is_object_dtype(df[col])
                    or pd.api.types.is_string_dtype(df[col])
                ):
                    converted = pd.to_numeric(
                        df[col], errors="coerce"
                    )

                    # Convert only if every non-null value is numeric
                    non_null = df[col].notna()
                    if non_null.any() and converted[non_null].notna().all():
                        df[col] = converted

            st.chat_message("assistant").write(
                f"Returned {len(df)} row(s)."
            )

            # Identify column types
            date_cols = [
                col for col in df.columns
                if "date" in col.lower()
                or "time" in col.lower()
            ]

            numeric_cols = df.select_dtypes(
                include="number"
            ).columns.tolist()

            categorical_cols = df.select_dtypes(
                include=["object", "category", "string"]
            ).columns.tolist()

            col1, col2 = st.columns([2, 1])

            with col1:
                # KPI: one row with one numeric value
                if len(df) == 1 and len(numeric_cols) == 1:
                    metric_col = numeric_cols[0]
                    metric_value = df[metric_col].iloc[0]

                    st.subheader("📌 Key Metric")
                    st.metric(
                        label=metric_col.replace("_", " ").title(),
                        value=(
                            f"{metric_value:,.2f}"
                            if isinstance(
                                metric_value,
                                float
                            )
                            and not metric_value.is_integer()
                            else f"{metric_value:,.0f}"
                            if pd.notna(metric_value)
                            and isinstance(
                                metric_value,
                                (int, float)
                            )
                            else str(metric_value)
                        )
                    )

                # Time-series chart
                elif date_cols and numeric_cols:
                    st.subheader("📈 Time-Series Trend")

                    chart_df = df.copy()
                    date_col = date_cols[0]

                    chart_df[date_col] = pd.to_datetime(
                        chart_df[date_col],
                        errors="coerce"
                    )

                    chart_df = chart_df.dropna(
                        subset=[date_col]
                    ).sort_values(date_col)

                    if not chart_df.empty:
                        st.line_chart(
                            chart_df.set_index(date_col)[numeric_cols]
                        )
                    else:
                        st.warning(
                            "No valid dates available for charting."
                        )
                        st.dataframe(
                            df, use_container_width=True
                        )

                # Category comparison chart
                elif categorical_cols and numeric_cols:
                    st.subheader("📊 Category Comparison")

                    category_col = categorical_cols[0]

                    st.bar_chart(
                        df.set_index(category_col)[numeric_cols]
                    )

                # Fallback table
                else:
                    st.subheader("📋 Data Table")
                    st.dataframe(
                        df, use_container_width=True
                    )

            with col2:
                st.subheader("Raw Data Table")
                st.dataframe(
                    df, use_container_width=True
                )

        except requests.exceptions.Timeout:
            st.error(
                "n8n did not respond within 60 seconds."
            )

        except requests.exceptions.RequestException as e:
            st.error(
                f"Error connecting to n8n: {e}"
            )

        except (ValueError, TypeError) as e:
            st.error(
                f"Could not process the n8n response: {e}"
            )
