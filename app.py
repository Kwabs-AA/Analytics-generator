import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.cache_data
def get_data():
    df=pd.read_csv('./data/train.csv',index_col=0)
    return df

df=get_data()

df=df.rename(columns={"Ship Mode":"ShipMode"})
df=df.rename(columns={"Sub-Category":"sub_category"})
df=df.rename(columns={"Customer Name":"customer_Name"})

st.sidebar.header("please filter here")
ShipMode=st.sidebar.multiselect(
    "Please select shipping mode",
    options=df['ShipMode'].unique(),
    default=df['ShipMode'].unique()
)

#sidebar radio
Category=st.sidebar.radio(
    "Please choose your category",
    options=df['Category'].unique()
)

sub_category=st.sidebar.multiselect(
    "Please choose the sub category",
    options=df['sub_category'].unique()
)

city=st.sidebar.multiselect(
    "Please the city you want to filter out",
    options=df['City'].unique()
    )

df_select=df.query(
    "ShipMode==@ShipMode & Category==@Category & sub_category==@sub_category & City==@city"
    )

if df_select.empty:
    st.warning("No data available base on current filtering session")
    st.stop()

st.title("Business Dashboard")
st.markdown('##')


average_price=int(df_select['Sales'].mean())
product_count=df_select.shape[0]
Total_sales=int(df_select["Sales"].sum())



first_coulmn, second_coulmn, third_coulmn =st.columns(3)
with first_coulmn:
    st.subheader("Average Prices")
    st.subheader(f"US $ {average_price:,}")
with second_coulmn:
    st.subheader("Number of Products")
    st.subheader(f"{product_count:,} items")
with third_coulmn:
    st.subheader("Total Sales")
    st.subheader(f"US $ {Total_sales:,}")


st.divider()

left_coulmn,right_coulmn = st.columns(2)

with left_coulmn:
    fig=px.bar(
        df_select, #data frame to be used
        x='sub_category',
        y='Sales',
        color='sub_category', #which part of the bar chart should have different colours
        title='Total Sales by Sub-Category',
        labels={'Sales':'Total Sales', 'sub_category':'Sub-Category'},
        template='plotly_white',
    )
st.plotly_chart(fig,use_container_width=True)


with right_coulmn:
    fig_donut=px.pie(
        df_select,
        names='State',
        values='Sales',
        title='Sales based on State',
        hole=0.4,
    )
st.plotly_chart(fig_donut,use_container_width=True)

st.divider()


min_sales=df_select['Sales'].min()
max_sales=df_select['Sales'].max()
median_sales=int(df_select['Sales'].median())


c1,c2,c3 = st.columns(3)

with c1:
    st.header("Minimum Sales")
    st.subheader(f" $ {min_sales:,}")
    
with c2:
    st.header("Maximum Sales")
    st.subheader(f"$ {max_sales:,}")

with c3:
    st.header("Median Sales")
    st.subheader(f" $ {median_sales:,}")


st.dataframe(df_select)