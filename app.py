from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json

app = Flask(__name__)

# Load Excel data
df = pd.read_excel("test.xlsx")
df["FUEL SENSOR NUMBER"] = df["FUEL SENSOR NUMBER"].fillna("NO SENSOR")
df["Installation Date"] = pd.to_datetime(df["Installation Date"], errors='coerce')
df["Next Renewal Date"] = pd.to_datetime(df["Next Renewal Date"], errors='coerce')

# Load chart config
with open("config.json") as f:
    chart_config = json.load(f)

@app.route("/")
def dashboard():
    charts = []

    for chart in chart_config["charts"]:
        chart_type = chart["chart_type"]
        title = chart["title"]
        column = chart["column"]

        # Special transformation if defined
        if "value_mapping" in chart:
            def map_value(x):
                return chart["value_mapping"]["digit"] if str(x).isdigit() else chart["value_mapping"]["other"]
            df[chart["new_column"]] = df[column].apply(map_value)
            column = chart["new_column"]

        if chart_type == "pie":
            fig = px.pie(df, names=column, title=title)
        elif chart_type == "bar":
            bar_df = df[column].value_counts().reset_index()
            bar_df.columns = [column, "Count"]
            fig = px.bar(bar_df, x=column, y="Count", title=title)
        elif chart_type == "histogram":
            fig = px.histogram(df, x=column, title=title)
        else:
            continue

        charts.append(pio.to_html(fig, full_html=False))

    return render_template("dashboard.html", charts=charts)

if __name__ == "__main__":
    app.run(debug=True)
