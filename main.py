import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIGURATION
st.set_page_config(
    page_title="King County - pricing"  # , layout="wide"
)

# CSV FILE
houseData = pd.read_csv('kc_house_data.csv', parse_dates=["date"])

df = houseData.drop(
    columns=['bathrooms', 'sqft_lot', 'view', 'sqft_above',
             'sqft_basement', 'yr_renovated', 'zipcode', 'sqft_living15', 'sqft_lot15'])

tab1, tab2 = st.tabs([""
                      " **FILTERED DATA** "
                      "", ""
                          " **OVERALL DATA** "
                          ""])


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


# price per sqft living function
def divide_price_per_sqft_living(df_sub):
    if df_sub['sqft_living'].sum() > 0:
        return float(df_sub['price'].sum()) / float(df_sub['sqft_living'].sum())


# price per floor function
def divide_price_per_floor(df_sub):
    if df_sub['sqft_living'].sum() > 0:
        return float(df_sub['price'].sum()) / float(df_sub['floors'].sum())


# price per bedroom function
def divide_price_per_bedroom(df_sub):
    if df_sub['sqft_living'].sum() > 0:
        return float(df_sub['price'].sum()) / float(df_sub['bedrooms'].sum())


# average price per deal function
def average_price_per_deal(df_sub):
    if df_sub['sqft_living'].sum() > 0:
        return round(float(df_sub['price'].sum()) / float(df_sub['id'].count()))


def total_homes_sold(df_sub):
    if df_sub['id'].count() > 0:
        return float(df_sub['id'].count())


def total_price_sold(df_sub):
    if df_sub['price'].sum() > 0:
        return float(df_sub['price'].sum())


# homes sold, total price, avg price per sqft, average price function
def average_max_min_sqft_living(df_sub):
    d = {'homes sold': df_sub['id'].count(),
         'total price': '${:,.2f}'.format(df_sub['price'].sum()),
         'avg price per sqft': '${:,.2f}'.format(divide_price_per_sqft_living(df_sub)),
         'average price': '${:,.2f}'.format(average_price_per_deal(df_sub))
         }
    return pd.Series(d, index=['homes sold', 'total price', 'avg price per sqft',
                               'average price'])  # , #'max price', 'min price'])


# SIDEBAR
# SIDEBAR TITLE:
st.sidebar.header('Filter the parameters')

# BUILT YEAR :
subset_year_data = df
year_input = st.sidebar.multiselect(
    'Choose the year of built',
    df.sort_values('yr_built', ascending=False)['yr_built'].unique(),
    help='Select the year of build (possible multiple selection)')

if len(year_input) > 0:
    subset_year_data = df[df['yr_built'].isin(year_input)]

# NUMBER OF BEDROOMS:
subset_bedrooms_data = subset_year_data
bedrooms_input = st.sidebar.multiselect(
    'Number of bedrooms',
    subset_year_data.groupby('bedrooms').count().reset_index()['bedrooms'].tolist(),
    help='Select the number of bedrooms (possible multiple selection)')

if len(bedrooms_input) > 0:
    subset_bedrooms_data = subset_year_data[subset_year_data['bedrooms'].isin(bedrooms_input)]

# NUMBER OF FLOORS:
subset_floors_data = subset_bedrooms_data
floors_input = st.sidebar.multiselect(
    'Number of floors',
    subset_bedrooms_data.groupby('floors').count().reset_index()['floors'].tolist(),
    help='Select the number of floors (possible multiple selection)')

if len(floors_input) > 0:
    subset_floors_data = subset_bedrooms_data[subset_bedrooms_data['floors'].isin(floors_input)]

# SQFT SLIDER:
sqftSlider = subset_floors_data['sqft_living']
if int(sqftSlider.min()) == int(sqftSlider.max()):
    sqft_living_selected = sqftSlider.min()
    mask_sqft = subset_floors_data['sqft_living'].eq(sqft_living_selected)
    st.write("There is only size of house (*sqft living*) in this criteria:", sqft_living_selected)
else:
    sqft_living_selected = st.sidebar.slider(label="Select the range of sqft living :",
                                             min_value=int(sqftSlider.min()),
                                             max_value=int(sqftSlider.max()),
                                             value=(int(sqftSlider.min()), int(sqftSlider.max())),
                                             help='Choose the range of square feet of living ')
    mask_sqft = subset_floors_data['sqft_living'].between(*sqft_living_selected)

# FINAL FILTERED DATAFRAME:
df_filtered = subset_floors_data[mask_sqft]

st.sidebar.write("###### To remove the filters : clean the filters of the year of built")

# tab1 FILTERED DATA
with tab1:
    st.write("""
        # Houses sold in King County - filtered
        Analysis of the open [dataset](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) on House Sales in King County, USA
        """)

    st.write("Built year:", *year_input, ", Bedrooms:", *bedrooms_input, ", Floors:", *floors_input,
             ", Sqft living :",
             sqft_living_selected)

    if df_filtered.id.count() == 0:
        st.error("Zero records found. Please select some other criteria")

    else:
        if df_filtered.id.count() == 1:
            st.write("Found: ", df_filtered.id.count(), " record between ", df_filtered.date.min(),
                     " and ", df_filtered.date.max())
        else:
            st.write("Found: ", df_filtered.id.count(), " records between ", df_filtered.date.min(),
                     " and ", df_filtered.date.max())

        # DATAFRAMES FOR CHARTS : APPLIED FUNCTIONS
        df_filtered['month'] = pd.to_datetime(df_filtered['date']).dt.strftime('%Y-%m')

        df_average_price_sqft = df_filtered.groupby('month').apply(
            divide_price_per_sqft_living)

        df_average_price_floor = df_filtered.groupby('month').apply(
            divide_price_per_floor)

        df_average_price_deal = df_filtered.groupby('month').apply(
            average_price_per_deal)

        if df_average_price_sqft.size > 0:
            tabA, tabB, tabC, tabD = st.tabs(
                ["Average price per sqft living", "Average price per deal", "Average price per bedroom",
                 "Average price per floor"])
            # tabA Average price per sqft living
            with tabA:
                st.write("""
                            ##### Average price per sqft living:
                            """)

                df_average_price_sqft_filtered = df_filtered.groupby(['month']).apply(
                    divide_price_per_sqft_living)

                average_price_sqft_filtered = px.line(df_average_price_sqft_filtered, height=400,
                                                      labels={
                                                          "value": "Average price sqft/month (USD)",
                                                          "month": "Months"}
                                                      # ,  title='Average price per square feet per month'
                                                      )
                average_price_sqft_filtered.update_xaxes(tickangle=45, fixedrange=True)
                average_price_sqft_filtered.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                average_price_sqft_filtered.update_layout(showlegend=False)
                st.plotly_chart(average_price_sqft_filtered, use_container_width=True)

            # tabB Average price per deal
            with tabB:
                st.write("""
                                        ##### Average price per deal:
                                        """)
                df_average_price_per_sold_filtered = df_filtered.groupby(['month']).apply(
                    average_price_per_deal)

                average_price_sold_filtered = px.line(df_average_price_per_sold_filtered, height=400,
                                                      labels={
                                                          "value": "Average price per deal/month (USD)",
                                                          "month": "Months"}
                                                      # ,  title='Average price per square feet per month'
                                                      )
                average_price_sold_filtered.update_xaxes(tickangle=45, fixedrange=True)
                average_price_sold_filtered.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                average_price_sold_filtered.update_layout(showlegend=False)
                st.plotly_chart(average_price_sold_filtered, use_container_width=True)

            # tabC Average price per bedroom
            with tabC:
                st.write("""
                                        ##### Average price per bedroom:
                                        """)
                df_average_price_per_bedroom_filtered = df_filtered.groupby(['month']).apply(
                    divide_price_per_bedroom)

                average_price_bedroom_filtered = px.line(df_average_price_per_bedroom_filtered, height=400,
                                                         labels={
                                                             "value": "Average price per bedroom/month (USD)",
                                                             "month": "Months"}
                                                         # ,  title='Average price per square feet per month'
                                                         )
                average_price_bedroom_filtered.update_xaxes(tickangle=45, fixedrange=True)
                average_price_bedroom_filtered.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                average_price_bedroom_filtered.update_layout(showlegend=False)
                st.plotly_chart(average_price_bedroom_filtered, use_container_width=True)

            # tabD Average price per floor
            with tabD:
                st.write("""
                                        ##### Average price per floor:
                                        """)
                df_average_price_per_floor_filtered = df_filtered.groupby(['month']).apply(
                    divide_price_per_floor)

                average_price_floor_filtered = px.line(df_average_price_per_floor_filtered, height=400,
                                                       labels={
                                                           "value": "Average price per floor/month (USD)",
                                                           "month": "Months"}
                                                       # ,  title='Average price per square feet per month'
                                                       )
                average_price_floor_filtered.update_xaxes(tickangle=45, fixedrange=True)
                average_price_floor_filtered.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                average_price_floor_filtered.update_layout(showlegend=False)
                st.plotly_chart(average_price_floor_filtered, use_container_width=True)

        dataframe_average_filtered = df_filtered.groupby('month',
                                                         as_index=True).apply(average_max_min_sqft_living)

        # houses sold statistics:
        if df_average_price_floor.size > 0:
            dataframe_average_filtered = df_filtered.groupby('month',
                                                             as_index=True).apply(
                average_max_min_sqft_living)

            st.write("""
                    ##### Houses monthly statistics:
                    """)
            st.dataframe(dataframe_average_filtered, use_container_width=True)

            tabE, tabF = st.tabs(["Houses sold", "Total price of sold houses"])

            # tabE Houses sold
            with tabE:
                st.write("""
                                        ##### Houses sold:
                                        """)
                # BAR CHART TOTAL NUMBER OF SOLD HOMES
                df_total_homes_sold = df_filtered.groupby('month',
                                                          as_index=True).apply(total_homes_sold)

                bar_filtered_houses = px.bar(df_total_homes_sold, height=400,
                                             labels={
                                                 "value": "Sold homes",
                                                 "month": "Months"}  # , title='Total amount of sold houses'
                                             )
                bar_filtered_houses.update_xaxes(tickangle=45, fixedrange=True)
                bar_filtered_houses.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                bar_filtered_houses.update_layout(showlegend=False)
                st.plotly_chart(bar_filtered_houses, use_container_width=True)

            # tabF Total price of sold houses
            with tabF:
                st.write("""
                                                           ##### Total price of sold houses:
                                                           """)
                # BAR CHART TOTAL PRICE OF SOLD HOMES
                df_total_price_sold = df_filtered.groupby('month',
                                                          as_index=True).apply(total_price_sold)

                bar_filtered_total_price = px.bar(df_total_price_sold, height=400,
                                                  labels={
                                                      "value": "Total price",
                                                      "month": "Months"}  # , title='Total amount of sold houses'
                                                  )
                bar_filtered_total_price.update_xaxes(tickangle=45, fixedrange=True)
                bar_filtered_total_price.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
                bar_filtered_total_price.update_layout(showlegend=False)
                st.plotly_chart(bar_filtered_total_price, use_container_width=True)

            st.write("""
                    ##### Map of the filtered houses:
                    """)

            # MAP OF SOLD HOUSES
            df_filtered.rename(columns={"long": "lon"}, inplace=True)
            st.map(df_filtered)

            # Filtered houses list - to download
            st.write("""
                                          ##### List of filtered houses:
                                          """)
            df_to_display = df_filtered.drop(columns=['waterfront', 'lat', 'lon', 'month'])
            st.dataframe(df_to_display, use_container_width=True)

            csv = convert_df(df_filtered)

            st.download_button(
                "Download filtered houses data",
                csv,
                "filtered_king_county.csv",
                "text/csv",
                key='download-csv'
            )

        st.markdown("""---""")

# tab2 OVERALL DATA
with tab2:
    st.write("""
    # Overall data (non-filtered)
    Analysis of the open [dataset](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) on House Sales in King County, USA between 05-2014 and 05-2015
    """)

    # CSV FILE UPLOADER
    # uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])

    df_nonfiltered = df
    df_nonfiltered['month'] = pd.to_datetime(df_nonfiltered['date']).dt.strftime('%Y-%m')

    df_nonfiltered_grouped = df_nonfiltered.groupby(['month']).apply(divide_price_per_sqft_living)
    df_deals = df_nonfiltered.groupby(['month']).apply(average_price_per_deal)

    if df_nonfiltered_grouped.size > 0:
        st.subheader('How were the prices changing over the months?')

        dataframe_average = df_nonfiltered.groupby(['month'], as_index=True).apply(
            average_max_min_sqft_living)

        st.dataframe(dataframe_average, use_container_width=True)

        # TO BE ADDED LATER: functions (def)
        st.write("Total: ", round(df_nonfiltered['id'].count()), " homes sold in a total price of: ",
                 '${:,.2f}'.format(df_nonfiltered['price'].sum()), "")
        st.write("Average price per deal: ",
                 '${:,.2f}'.format(float(df_nonfiltered['price'].sum()) / float(df_nonfiltered['id'].count())))
        st.write("Average price per sqft living: ", '${:,.2f}'.format(
            float(df_nonfiltered['price'].sum()) / float(df_nonfiltered['sqft_living'].sum())))

        # DATAFRAMES FOR CHARTS : APPLIED FUNCTIONS
        df_average_price_sqft_non_filtered = df_nonfiltered.groupby(['month']).apply(
            divide_price_per_sqft_living)
        df_average_price_floor_non_filtered = df_nonfiltered.groupby(['month']).apply(
            divide_price_per_floor)
        df_average_price_bedroom_non_filtered = df_nonfiltered.groupby(['month']).apply(
            divide_price_per_bedroom)
        df_average_price_deal_non_filtered = df_nonfiltered.groupby(['month']).apply(
            average_price_per_deal)

        df_total_homes_sold_non_filtered = df_nonfiltered.groupby(['month']).apply(total_homes_sold)

        # BAR CHART : TOTAL HOMES SOLD
        bar_total = px.bar(df_total_homes_sold_non_filtered, height=400,
                           labels={
                               "value": "Sold homes",
                               "month": "Months"}, title='Total amount of sold houses'
                           )
        bar_total.update_xaxes(tickangle=45, fixedrange=True)
        bar_total.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
        bar_total.update_layout(showlegend=False)
        st.plotly_chart(bar_total, use_container_width=True)

        # Average price per sqft per month expander
        with st.expander(""
                         " **Average price per sqft per month** "
                         "", expanded=True):
            average_price_sqft_not_filtered = px.line(df_average_price_sqft_non_filtered, height=400,
                                                      labels={
                                                          "value": "Average price sqft/month (USD)",
                                                          "month": "Months"}
                                                      # ,  title='Average price per square feet per month'
                                                      )
            average_price_sqft_not_filtered.update_xaxes(tickangle=45, fixedrange=True)
            average_price_sqft_not_filtered.update_xaxes(dtick="M1", tickformat="%b %Y", tickangle=45)
            average_price_sqft_not_filtered.update_layout(showlegend=False)
            st.plotly_chart(average_price_sqft_not_filtered, use_container_width=True)

        # Average price per deal per month expander
        with st.expander(""
                         " **Average price per deal per month** "
                         ""):
            average_price_deal_filtered = px.line(df_average_price_deal_non_filtered, height=400,
                                                  labels={
                                                      "value": "Average price deal/month (USD)",
                                                      "date": "Months"}
                                                  # ,markers=True,title='Average price per deal per month'
                                                  )
            average_price_deal_filtered.update_layout(showlegend=False)
            st.plotly_chart(average_price_deal_filtered, use_container_width=True)

        # Average price per bedroom per month expander
        with st.expander(""
                         " **Average price per bedroom per month** "
                         ""):
            average_price_bedroom_not_filtered = px.line(df_average_price_bedroom_non_filtered, height=400,
                                                         labels={
                                                             "value": "Average price bedroom/month (USD)",
                                                             "date": "Months"}
                                                         # ,markers=True, title='Average price per bedroom per month'
                                                         )
            average_price_bedroom_not_filtered.update_layout(showlegend=False)
            st.plotly_chart(average_price_bedroom_not_filtered, use_container_width=True)

        # Average price per floor per month expander
        with st.expander(""
                         " **Average price per floor per month** "
                         ""):
            average_price_floor_not_filtered = px.line(df_average_price_floor_non_filtered, height=400,
                                                       labels={
                                                           "value": "Average price floor/month (USD)",
                                                           "date": "Months"}
                                                       # ,   markers=True, title='Average price per floor per month'
                                                       )
            average_price_floor_not_filtered.update_layout(showlegend=False)
            st.plotly_chart(average_price_floor_not_filtered, use_container_width=True)

# else:
#    st.error('There is no data to display - please select some other criteria')
