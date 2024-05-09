import argparse

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from dash import Dash, html, dcc

from entities import PurchasedItem


def remove_refunds(df: pd.DataFrame) -> pd.DataFrame:

    return df[(df.refunded == False)].copy()


def make_overview(df: pd.DataFrame) -> html.Div:

    customer_for_n_years = max(df.year.max() - df.year.min(), 1)
    total_spent_excl_refunds = df[(df.refunded == False)].price.sum()

    refunded = df[(df.refunded == True)].price.sum()

    avg_spent_per_year = total_spent_excl_refunds / customer_for_n_years

    top_n = 10

    most_expensive: list[PurchasedItem] = (
        df.sort_values("price", ascending=False).head(top_n).to_dict("records")
    )

    most_expensive_list = html.Ol(
        [
            html.Li(
                [
                    html.I(item["description"][:60]),
                    "... for ",
                    html.Strong(item["price"]),
                    " in ",
                    item["year"],
                ]
            )
            for item in most_expensive
        ]
    )

    content = [
        html.P(
            [
                "You've been a customer for ",
                html.Strong(customer_for_n_years),
                " year(s) and ordered ",
                html.Strong(len(df)),
                " items from Amazon at an average price per item of ",
                html.Strong(f"{total_spent_excl_refunds / len(df):.02f}"),
            ]
        ),
        html.P(
            [
                "In total you spent: ",
                html.Strong(f"{total_spent_excl_refunds:.02f}"),
                " (excluding refunds), that means on average ",
                html.Strong(f"{avg_spent_per_year:.02f}"),
                " per year",
            ]
        ),
        html.P(
            [
                "You've been refunded ",
                html.Strong(refunded),
                " for products that you returned (excl. digital refunds).",
            ]
        ),
        html.P(
            [
                f"The {top_n} most expensive items you've bought are:",
                most_expensive_list,
            ]
        ),
    ]

    return dbc.Card(
        children=[dbc.CardHeader("Summary"), dbc.CardBody(children=content)],
        class_name="mb-2",
    )


def make_price_histogram_chart(df: pd.DataFrame) -> dcc.Graph:

    fig = px.histogram(df, x="price", nbins=20)
    return dcc.Graph(figure=fig)


def make_yoy_spending_chart(df: pd.DataFrame) -> dcc.Graph:

    df = remove_refunds(df.copy())
    df["total"] = df.price
    agg = df.sort_values("year").groupby("year").sum("total").reset_index()

    fig = px.bar(agg, x="year", y="total")

    return dcc.Graph(figure=fig)


def make_yoy_spending_chart_by_category(df: pd.DataFrame) -> dcc.Graph:

    df = remove_refunds(df.copy())
    df["total"] = df.price
    agg = (
        df.sort_values(["year", "category"])
        .groupby(["year", "category"])
        .sum("total")
        .reset_index()
    )

    fig = px.bar(agg, x="year", y="total", color="category")

    return dcc.Graph(figure=fig)


def make_spending_by_day_of_week_chart(df: pd.DataFrame) -> dcc.Graph:

    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    df = remove_refunds(df.copy())
    df["total"] = df.price
    df["day"] = df.day_of_week.apply(lambda x: days[x])

    agg = (
        df.sort_values(["day_of_week", "day", "category"])
        .groupby(["day_of_week", "day", "category"])
        .sum("total")
        .reset_index()
    )

    fig = px.bar(agg, x="day", y="total", color="category")

    return dcc.Graph(figure=fig)


def build_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description=(
            "Visualize the parser output in a webapp, by default it will be hosted on"
            " http://127.0.0.1:8050,"
            " you can update that through the HOST and PORT environment variables."
        )
    )

    parser.add_argument(
        "REPORT_FILE", type=str, help="Path to the output of the parser"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable the Dash Debug functionality.",
    )

    return parser


def main() -> None:

    parser = build_parser()

    args = parser.parse_args()

    data_path = args.REPORT_FILE

    data = pd.read_json(data_path)
    data["price"] = data["price"].astype("float")

    app = Dash(
        name="Amazon Analysis",
        title="Amazon Analysis",
        update_title="Amazon Analysis",
        external_stylesheets=[dbc.themes.LUMEN],
    )
    app.layout = html.Div(
        children=[
            dbc.Container(
                children=[
                    html.H1("Amazon Purchase Analysis"),
                    make_overview(data),
                    html.H3("Year over Year spending"),
                    make_yoy_spending_chart(data),
                    html.H3("Year over Year spending by category"),
                    make_yoy_spending_chart_by_category(data),
                    html.H3("Spending by day of week"),
                    make_spending_by_day_of_week_chart(data),
                    html.H3("Price Histogram"),
                    make_price_histogram_chart(data),
                ]
            )
        ]
    )

    app.run(debug=args.debug)


if __name__ == "__main__":
    main()
