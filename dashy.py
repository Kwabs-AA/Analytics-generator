import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from streamlit_extras.metric_cards import style_metric_cards

st.set_page_config(layout="wide")
st.header("📉 Data Administration and Analytics")

file_input = st.sidebar.file_uploader(
    label="Please upload the data you want to generate analysis about",
    accept_multiple_files=False
)

@st.cache_data
def get_data(file):
    if file_input:
        df = pd.read_csv(file)
        return df
    else:
        st.warning("Nothing to be displayed yet. Please upload a file to start.")
        return None
        
df = get_data(file_input)

def column_with_least_unique_values(df):
    unique_counts = df_selected.nunique() 
    least_unique_column = unique_counts.idxmin()  
    return least_unique_column

expense_name={"amount", "charge", "damage", "expenditure", "figure", "outlay", "payment", "price", "price tag", "rate", "tariff", "value", "worth","expense"}
main_name={"transaction", "deal", "auction", "sale", "bargain", "buy"," trade", "negotiation", "steal", "clearance"}

st.sidebar.divider()
if df is not None:
    df_selected = df.copy()
    st.sidebar.header("Unit header")
    unit = st.sidebar.text_input("Input unit eg: $, meter, km")
   
    unit_position = st.sidebar.radio(
         "Please select the location of the unit",
         options=("Left","Right"),
         horizontal=True,
    )
    if unit_position == "Left":
        left_unit = unit
        right_unit = ""
    if unit_position == "Right":
        right_unit = unit
        left_unit = ""

    st.sidebar.divider()

    st.sidebar.header("Remove any unwanted columns here")

    remove_col = st.sidebar.multiselect(
    "Please select the columns that you want to remove",
    options=df_selected.columns,
    )
    df_selected = df.drop(columns=remove_col)
    df = df_selected.reset_index(drop=True)

    st.sidebar.divider()

    st.sidebar.header("Please filter information here")
    st.divider()

    count = 2
    sales_index = 0
    expense_index = 0
    date_column = None
    for col in df.columns:
        col_len = len(df_selected.columns)
        for value in main_name:
            if (col.lower().__contains__(value)):
                sales_index = df.columns.tolist().index(col)

        for value in expense_name:
            if (col.lower().__contains__(value)):
                expense_index = df.columns.tolist().index(col)
        
        if (col.lower().__contains__('date')):
            date_column = col
            df_selected[col] = pd.to_datetime(df[col], format='mixed')
            df_selected['Year'] = df_selected[col].dt.year
            df_selected['Month'] = df_selected[col].dt.month_name()
        
        if col not in ['Year', 'Month']:
            categories = st.sidebar.multiselect(
                f"Filter by {col}",
                options=df[col].unique(),
                key=f"filter_{col}"
            )
            if categories:
                df_selected = df_selected[df[col].isin(categories)]

    if date_column:
        st.sidebar.divider()
        st.sidebar.header("Date Filters")
        
        month_filter = st.sidebar.multiselect(
        "Filter by Month",
        df_selected["Month"].sort_values(ascending=True).unique(),
        key="month_filter"
        )
        year_filter = st.sidebar.multiselect(
        "Filter by year",
        df_selected["Year"].sort_values(ascending=True).unique(),
        key="year_filter"
        )
        if year_filter:
            df_selected = df_selected.query("Year==@year_filter")

        if month_filter:
            df_selected = df_selected.query("Month==@month_filter")

        year_len = len(df_selected["Year"].unique())
        later_year = year_len - 1 if year_len > 0 else 0
    else:
        st.sidebar.warning("No date column detected in the data.")
        year_filter = []
        year_len = 0
        later_year = 0

    col1, col2 = st.columns(2)
    sub1, sub2 = st.columns(2)
    column1, column2, column3 = st.columns(3)
    
    with col1:
        main_col = st.selectbox(
            "Pick the column you want to compute",
            options=df_selected.columns,
            index=sales_index,
        )

    if date_column:
        with sub1:
            early_index = year_len - 2 if year_len > 2 else 0
            year1 = st.selectbox(
                "Please select the earlier year for comparison",
                options=year_filter if year_filter else df_selected["Year"].sort_values().unique(),
                index=early_index,
                key="year1_select"
            )

        with sub2:
            year2 = st.selectbox(
                "Please select the later year for comparison",
                options=year_filter if year_filter else df_selected["Year"].sort_values().unique(),
                index=later_year,
                key="year2_select"
            )
    else:
        st.warning("No date column available for year comparison.")
        year1 = year2 = None

    try:
        if main_col:
            if date_column:
                df_temp1 = df_selected.query("Year==@year1") if year1 else df_selected
                df_temp2 = df_selected.query("Year==@year2") if year2 else df_selected
                
                count_main = df_temp1[main_col].count()
                avg_main = df_temp1[main_col].mean()
                total_main = df_temp1[main_col].sum()
                
                count_main1 = df_temp2[main_col].count()
                avg_main1 = df_temp2[main_col].mean()
                total_main1 = df_temp2[main_col].sum()
                
                delta_count = f'{count_main1-count_main}' if year1 and year2 else None
                delta_avg = f'{avg_main1-avg_main:.2f}' if year1 and year2 else None
                delta_total = f'{total_main1-total_main:.2f}' if year1 and year2 else None
            else:
                count_main = df_selected[main_col].count()
                avg_main = df_selected[main_col].mean()
                total_main = df_selected[main_col].sum()
                delta_count = delta_avg = delta_total = None

            column1.metric(label=f"Number of {main_col}", value=f'{count_main}', delta=delta_count)
            column2.metric(label=f"Average {main_col}", value=f'{left_unit} {avg_main:.2f} {right_unit}', delta=delta_avg)
            column3.metric(label=f'Total {main_col}', value=f'{left_unit} {total_main:.2f} {right_unit}', delta=delta_total)
        else:
            st.warning("Please select a column to compute")
    except (ValueError,TypeError,NameError):
        st.warning("No computations can be performed. Please check your data and selections.")
   
    try:
        with col2:
            expense_col = st.selectbox(
                "Pick another column you want to compute",
                options=df_selected.columns,
                )
            
            count_sub=df_temp1[expense_col].count()
            avg_sub=df_temp1[expense_col].mean()
            total_sub=df_temp1[expense_col].sum()

            df_temp2=df_selected.query("Year==@year2")
            count_sub1=df_temp2[expense_col].count()
            avg_sub1=df_temp2[expense_col].mean()
            total_sub1=df_temp2[expense_col].sum()
                
            if expense_col:
                total_expense = float(df_selected[expense_col].sum())
                avg_expense = float(df_selected[expense_col].mean())
                column1.metric(label=(f"Number of {expense_col}"),value=(f'{df_selected[expense_col].count()}'),delta=f'{count_sub1-count_sub}')
                column2.metric(label=(f"Average {expense_col}"),value=f'{unit} {avg_expense:.2f}',delta=f'{avg_sub1-avg_sub: .2f}')
                column3.metric(label=(f'Total {expense_col}'),value=(f'{unit} {total_expense: .2f}'),delta=f'{total_sub1-total_sub: .2f}')

    except (ValueError,TypeError,NameError):
            st.warning("No computations can be made for the second column")
    style_metric_cards()
    st.markdown('##')

    try:
        st.header(f"Visuals for the {main_col}",)
        
        chart1,chart2,chart3 =st.columns(3)
        
        chart_options = st.multiselect(
            "Please choose the type of chart you want to generate",
            options=["Bar Chart", "Pie Chart", "Line Chart"],
            default=["Bar Chart","Pie Chart", "Line Chart"],
            key="chart_options"
        )
        with chart1:
            if "Bar Chart" in chart_options:
                bar_x = st.selectbox(
                    "Please select the x-axis label",
                    options=df_selected.columns,
                    key="bar_x",
                )
                bar_y = st.selectbox(
                    "Please select the y-axis label",
                    options=df_selected.columns,
                    index=sales_index,
                    key="bar_y"
                )
                bar_chart = px.bar(
                    df_selected,
                    x=bar_x,
                    y=bar_y,
                    template="plotly_white"
                )
                st.plotly_chart(bar_chart, use_container_width=True)

        least_unique_column = column_with_least_unique_values(df_selected)
        least_unique_index = df_selected.columns.get_loc(least_unique_column) 

        with chart2:
            if "Pie Chart" in chart_options:
                pie_x = st.selectbox(
                    "Please select the label for the pie chart",
                    options=df_selected.columns,
                    index=least_unique_index,
                    key="pie_x"
                )
                pie_y = st.selectbox(
                    "Please select the value for the pie chart",
                    options=df_selected.columns,
                    index=sales_index,
                    key="pie_y"
                )
                pie_chart = px.pie(
                    df_selected,
                    names=pie_x,
                    values=pie_y,
                    title=(f"{pie_x} and {pie_y}"),
                    template='plotly_white',
                )
                st.plotly_chart(pie_chart, use_container_width=True)

        with chart3:
            if "Line Chart" in chart_options:
                line_x = st.selectbox(
                    "Please select the x-axis label for the chart",
                    options=df_selected.columns,
                    key="line_x"
                )
                line_y = st.selectbox(
                    "Please select the y-axis label for the chart",
                    options=df_selected.columns,
                    index=sales_index,
                    key="line_y"
                )
                line_chart = px.scatter(
                    df_selected,
                    x=line_x,
                    y=line_y,
                    template='plotly_white'
                )

                st.plotly_chart(line_chart, use_container_width=True)
    except NameError:
        st.warning("Please select a column to compute before generating visuals")
        
    st.header("Filtered Data")
    for col in df_selected:
        if col == "Year":
            df_download=df_selected.drop(columns={"Year","Month"})
        else:
            df_download=df_selected
    st.dataframe(df_download,use_container_width=True)

    def convert_data(df):
        return df.to_csv(index=False).encode('UTF-8')
    
    xlsx=convert_data(df_download)

    st.download_button(label="📥 Download filtered data",data=xlsx,file_name="Filtered data.csv", mime='text/csv')

    if st.checkbox("Enable Predictive Analysis"):
        try:
            feature_cols = st.multiselect("Select Features", df_selected.columns)
            target_col = st.selectbox("Select Target Column", df_selected.columns)
            if feature_cols and target_col:
                X = df_selected[feature_cols]
                y = df_selected[target_col]
                model = LinearRegression().fit(X, y)
                predictions = model.predict(X)
                df_selected['Predictions'] = predictions
                st.line_chart(df_selected[['Predictions', target_col]])
        except ValueError:
            st.warning("Predictive analysis works on numerical columns")