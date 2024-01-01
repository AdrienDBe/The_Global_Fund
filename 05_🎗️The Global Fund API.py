import streamlit as st
import requests
import pandas as pd
import numpy as np
import wbgapi as wb
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
from datetime import date

# emojis list: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="GF API explorer", page_icon="🎗", layout="wide")

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style/style.css")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem
                }
        </style>
        """, unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="metric-container"] {
   background-color: #12151D;
   border: 1px solid #283648 ;
   border-radius: 5px;
   padding: 1% 1% 1% 5%;
   color: #04AA6D;
   overflow-wrap: break-word;
}
/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   overflow-wrap: break-word;
   white-space: break-spaces;
   color: white;
}
</style>
""", unsafe_allow_html=True)

# resize expanders
st.markdown("""
<style>
.streamlit-expanderHeader {
    font-size: medium;
    color:#ad8585;   
    }
.st-bd {border-style: none;}
</style>
""", unsafe_allow_html=True)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Landing page

if 'count' not in st.session_state:
	st.session_state.count = 0

if st.session_state.count == 0:
    arrival_message = st.empty()
    with arrival_message.container():
        st.title("Global Fund API explorer")
        st.subheader("Implementation periods, Grants, Disbursements")
        col1,col_mid, col2 = st.columns([4,0.1,1], gap='small')
        col1.write("<p style='text-align: justify;font-size: 18px;'>"
                   "This app imports data from the Global Fund API and displays it in a Streamlit web app."
                   "<br/>It allows the user to navigate between several information dimensions and represent it visually with "
                 "different level of granularity (region, country, disease, stakeholder etc.)"
                   " The data is also grouped by Region, Income level, or Country (using the World Bank API) depending "
                 "on the user's selection.",unsafe_allow_html=True)
        lottie_url = "https://lottie.host/285a7a0c-1d81-4a8f-9df5-c5bebaae5663/UDqNAwwYUo.json"
        lottie_json = load_lottieurl(lottie_url)
        with col2:
            st_lottie(lottie_json, height=150, key="loading_gif2")

        with st.expander("Read more about the Global Fund (TGF), what is an API and how to access TGF API"):
            col1, col2, col3 = st.columns([1, 1, 1], gap='small')
            with col1:
                # GF details
                st.subheader("The Global Fund")
                st.markdown("<p style='text-align: justify;font-size: 18px;'>"
                         "<a href='https://www.theglobalfund.org/en/'>The Global Fund </a> is a partnership designed to accelerate the end of AIDS, tuberculosis and "
                        "malaria as epidemics. <br> It prioritizes: results-based work, accountability, preparing countries"
                        " for graduation from aid, investing in people as assets for development and inclusive governance."
                        " To do so, the Global Fund mobilizes and invests more than US$4 billion a year to support programs "
                        "run by local experts in more than 100 countries in partnership with governments, civil society, "
                        "technical agencies, the private sector and people affected by the diseases. <br> You can visit <a href='https://www.theglobalfund.org/en/funding-model/'>this page</a> to"
                        " learn more about the organization Funding Model.</p>", unsafe_allow_html=True)
            with col2:
                st.subheader("API")
                st.markdown("<p style='text-align: justify;font-size: 18px;'>"
                            "An API, or Application Programming Interface, allows different applications to communicate and exchange data with one another. "
                            "In the case of the World Health Organization (WHO), The Global Fund, and the World Bank, these organizations have created APIs "
                            "to increase transparency and provide better access to information for stakeholders in their activities."
                            "<a href='https://en.wikipedia.org/wiki/API'> <br>Read more on Wikipedia</a></p>",
                            unsafe_allow_html=True)
            with col3:
                st.subheader("The Global Fund API")
                # GF details
                st.markdown("<p style='text-align: justify;font-size: 18px;'>"
                            "The Global Fund API <a href='https://data-service.theglobalfund.org/api'> (link to documentation)</a>"
                            " is providing access to different data including: <br>Lookup Lists, Funding Allocations, Donors & Implementation Partners,"
                            " various Grants information, information on Resource Mobilization and several de-normalized views of all eligibility records."
                            "<br>To offer more visualization options, we also imported the <a href='https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups'> World Bank regional groupings and Income group classifications </a> from the World Bank API and merged them with the country list from the WHO.",
                            unsafe_allow_html=True)

        col1, col2 = st.columns([10, 35], gap='small')
        col1.subheader("API status")

        url2 = "https://data-service.theglobalfund.org/v3.3/odata/VGrantAgreementImplementationPeriods"
        response1 = requests.get(url2)
        if response1.status_code != 200:
            col2.warning( "There seems to be an error with the Global Fund API (status code: {})".format(response1.status_code))
            col2.markdown("<p style='text-align: justify;font-size: 18px;'>"
                        "The API is currently unavailable (see <a href='https://data-service.theglobalfund.org/v3.3/odata/VGrantAgreementImplementationPeriods'> this link </a> )".format(response1.status_code)
                        ,unsafe_allow_html=True)
        else:
            col2.success("Connection to the Global Fund API established successfully")

        if response1.status_code != 200 :
            col2.info("This app will be accessible once the connection is back")

        col1, col2 = st.columns([10, 35], gap='small')
        col1.subheader("Disclaimer")
        col2.write("<p style='text-align: justify;font-size: 18px;'>"
            "Please note that the information provided in this page is created and shared by me as an individual and "
            "should not be taken as an official representation of the Global Fund."
            "<br>For accurate and up-to-date information, please consult the Global Fund official data explorer.",
            unsafe_allow_html=True)
        if response1.status_code == 200:
            disclaimer_confirmation = col2.button('I understand')
            if disclaimer_confirmation:
                st.session_state.count = 1
                st.experimental_rerun()

if st.session_state.count >= 1:

    # Use local CSS for background waves
    with open('./style/wave.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def Loading_country_list():

        service_url0 = "https://ghoapi.azureedge.net/api/DIMENSION/COUNTRY/DimensionValues"
        response0 = requests.get(service_url0)
        # make sure we got a valid response
        if (response0.ok):
            # get the full data from the response
            data0j = response0.json()
        else:
            st.caption("API data cannot be loaded")
        country_list = pd.DataFrame(data0j["value"])
        country_list.rename(columns={"Code": "SpatialDim", "Title": "Country"}, inplace=True)

        ## List of World Bank country with Region and Income Level
        WorldBank_countries = wb.economy.DataFrame().reset_index()[
            ['id', 'name', 'aggregate', 'region', 'incomeLevel']]
        WorldBank_countries = WorldBank_countries[WorldBank_countries['aggregate'] == False].drop('aggregate',
                                                                                                  axis=1)
        WorldBank_countries['incomeLevel'] = WorldBank_countries['incomeLevel'].map({
            'LIC': 'Low income country',
            'HIC': 'High income country',
            'LMC': 'Lower middle income country',
            'INX': 'Upper middle income country',
            'UMC': 'Upper middle income country'})
        WorldBank_countries['region'] = WorldBank_countries['region'].map({
            'LCN': 'Latin America & the Caribbean',
            'SAS': 'South Asia',
            'SSF': 'Sub-Saharan Africa',
            'ECS': 'Europe and Central Asia',
            'MEA': 'Middle East and North Africa',
            'EAS': 'East Asia and Pacific',
            'NAC': 'North America'})
        WorldBank_countries.rename(columns={"id": "SpatialDim", "incomeLevel": "Income level", "region": "Region"},
                                   inplace=True)
        country_list = country_list.merge(WorldBank_countries, how='left', on='SpatialDim')
        return country_list


    country_list = Loading_country_list()

    color_discrete_map_ip_status = {
        "Financially Closed": "grey",
        "Financial Closure": "#e63946",
        "Active": "#04AA6D"}

    color_discrete_map = {
        "HIV": "#fe9000",
        "Malaria": "#5b8e7d",
        "Tuberculosis": "#5adbff",
        "TB/HIV": "#3c6997",
        "RSSH": "#094074",
        "Multicomponent": "#ffdd4a"}

    color_discrete_map2 = {
        "Sub-Saharan Africa": "#0081a7",
        "East Asia and Pacific": "#b392ac",
        "Europe and Central Asia": "#02c39a",
        "Latin America & the Caribbean": "#fdfcdc",
        "Middle East and North Africa": "#736ced",
        "South Asia": "#f07167"}

    color_discrete_map3 = {
        "Ministry of Health": "#e6194B",
        "Ministry of Finance": "#3cb44b",
        "UN Agency": "#4363d8",
        "International NGO": "#ffe119",
        "Other Governmental": "#42d4f4",
        "International Faith Based Organization": "#f032e6",
        "Not indicated": "#ffffff",
        "Local Faith Based Organization": "#fabed4",
        "Private Sector Entity": "#a9a9a9",
        "Other Multilateral Organization": "#094074",
        "Other Community Sector Entity": "#3c6997",
        "Community Based Organization": "#5b8e7d"}

    color_discrete_map4 = {
        "Administratively Closed": "grey",
        "Terminated": "#fcd5ce",
        "In Closure": "#e63946",
        "Active": "#48cae4"}

    if st.session_state.count >= 1:
        # Enabling Plotly Scroll Zoom
        config = dict({'scrollZoom': True, 'displaylogo': False})

        header_space = st.container()

        with header_space:
            col1, col2 = st.columns([12, 35], gap='small')
            col1.markdown(
                "<span style='text-align: justify; font-size: 280% ; color:#ffffff'> **Global Fund <br>API explorer** </span> </p>",
                unsafe_allow_html=True)

        with st.sidebar:
            dataset = st.radio("Select Dataset", ('Implementation periods (IPs)', 'Disbursements', 'Reporting results'),
                               horizontal=True)

            # Loading API from WHO WB and GF ---------------------------------------------------

            count = 0
            gif_runner = st.empty()


        def Loading_API():
            # check if first load, if so it will take a few sec to load so we want to display a nice svg
            global count
            count += 1
            if count == 1:
                lottie_url = "https://assets1.lottiefiles.com/packages/lf20_18ple6ro.json"
                lottie_json = load_lottieurl(lottie_url)
                lottie_container = st.empty()
                with lottie_container:
                    st_lottie(lottie_json, height=350, key="loading_gif")

            # reading api
            service_url0 = 'https://data-service.theglobalfund.org/v3.3/odata/VGrantAgreementImplementationPeriods'
            response0 = requests.get(service_url0)
            # make sure we got a valid response
            if (response0.ok):
                # get the full data from the response
                data0j = response0.json()
            else:
                st.caption("Global Fund API cannot be loaded")
            df2 = pd.DataFrame(data0j["value"])
            if count == 1:
                lottie_container.empty()

            df2.principalRecipientSubClassificationName.fillna('Not indicated', inplace=True)

            # merge with country info
            df2.rename(columns={"geographicAreaCode_ISO3": "SpatialDim"}, inplace=True)
            df2 = pd.merge(df2,
                           country_list,
                           on='SpatialDim',
                           how='left')
            df2.Region.fillna('Non-regional IP', inplace=True)
            df2.principalRecipientName.fillna('Not indicated', inplace=True)
            df2.grantAgreementTitle.fillna('Not indicated', inplace=True)

            df2['implementationPeriodStartDate'] = pd.to_datetime(
                df2['implementationPeriodStartDate']).dt.tz_localize(None)
            df2['implementationPeriodEndDate'] = pd.to_datetime(df2['implementationPeriodEndDate']).dt.tz_localize(
                None)
            df2['programStartDate'] = pd.to_datetime(df2['programStartDate']).dt.tz_localize(None)
            df2['programEndDate'] = pd.to_datetime(df2['programEndDate']).dt.tz_localize(None)


            df2.sort_values('implementationPeriodStatusTypeName', inplace=True)
            # Conditionally replace 'geographicAreaName' with 'multiCountryName' when 'multiCountryName' is not None
            df2.loc[df2['multiCountryName'].notna(), 'geographicAreaName'] = df2.loc[
                df2['multiCountryName'].notna(), 'multiCountryName']

            # Keep only the desired columns in df2
            desired_columns = [
                'geographicAreaName',
                'SpatialDim',
                'componentName',
                'grantAgreementId',
                'grantAgreementNumber',
                'grantAgreementImplementationPeriodId',
                'grantAgreementStatusTypeName',
                'grantAgreementTitle',
                'programStartDate',
                'programEndDate',
                'principalRecipientName',
                'principalRecipientShortName',
                'principalRecipientClassificationName',
                'principalRecipientSubClassificationName',
                'leadImplementerName',
                'leadImplementerShortName',
                'isActive',
                'implementationPeriodStatusTypeName',
                'implementationPeriodNumber',
                'implementationPeriodStartDate',
                'implementationPeriodEndDate',
                'isCurrentImplementationPeriod',
                'currency',
                'totalSignedAmount',
                'totalCommittedAmount',
                'totalDisbursedAmount',
                'Country',
                'Dimension',
                'ParentDimension',
                'ParentTitle',
                'name',
                'Region',
                'Income level'
            ]
            df2 = df2[desired_columns]

            #df2 = df2[df2['programStartDate'].dt.year >= 2018]
            return country_list, df2


        country_list, df2 = Loading_API()

        gif_runner.empty()




        if dataset == "Reporting results":
            col2.markdown(
                "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **Reporting results <br >Section in development** </span> </p>",
                unsafe_allow_html=True)
            lottie_url = "https://assets5.lottiefiles.com/packages/lf20_s8nnfakd.json"
            lottie_json = load_lottieurl(lottie_url)
            st_lottie(lottie_json, height=500, key="loading_gif2")

        if dataset == "Implementation periods (IPs)":

            col2.markdown(
                "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **Implementation Periods** </span> <br>"
                "Implementation Period (or 'IP') refers to a predetermined timeframe of the Grant during which planned activities, initiatives, "
                "and projects are executed and monitored, often associated with the disbursement of funds in grant management, "
                "with the aim of achieving specific objectives and outcomes. </span> "
                "<span style='color:grey'>Loading takes a few seconds the first time.</span> </p>",
                unsafe_allow_html=True)

            # FILTERS ------------------------------------
            with st.sidebar:

                # Active Grant filter
                isActive = st.radio("Filter", ('All IPs', 'Active IPs'), horizontal=True)
                if isActive == "All IPs":
                    df2_group = df2
                if isActive == "Active IPs":
                    df2_group = df2[df2["implementationPeriodStatusTypeName"] == 'Active']

                # Component filter
                option_Component = st.multiselect(
                    'Filter component(s)',
                    options=list(df2_group.componentName.sort_values(ascending=True).unique()),
                    key="component_multiselect")
                if len(option_Component) == 0:
                    df_group_compo = df2_group
                else:
                    df_group_compo = df2_group[df2_group["componentName"].isin(option_Component)]

                # Country filter
                country_filter = st.multiselect(
                    'Select portfolio',
                    options=list(df_group_compo.geographicAreaName.sort_values(ascending=True).unique()),
                    key="Country_multiselect")
                if len(country_filter) == 0:
                    df2_group_country = df_group_compo
                else:
                    df2_group_country = df_group_compo[df_group_compo["geographicAreaName"].isin(country_filter)]

                # Region filter
                region_filter = st.multiselect(
                    'Select region',
                    options=list(df2_group_country.Region.sort_values(ascending=True).unique()),
                    key="Region_multiselect")
                if len(region_filter) == 0:
                    df2_group_region = df2_group_country
                else:
                    df2_group_region = df2_group_country[df2_group_country["Region"].isin(region_filter)]

                # Principal recipient filter
                option_map_pr = st.multiselect(
                    'Filter PR type',
                    options=list(
                        df2_group_region.principalRecipientSubClassificationName.sort_values(ascending=True).unique()),
                    key="pr_multiselect")
                if len(option_map_pr) == 0:
                    df_group_pr = df2_group_region
                else:
                    df_group_pr = df2_group_region[
                        df2_group_region["principalRecipientSubClassificationName"].isin(option_map_pr)]


            # TABS ------------------------------------
            tab1, tab2 = st.tabs(["View per category", "All"])



            with tab1:
                view = st.radio(
                    "Select category",
                    ('Component', 'Principal Recipient', 'Region'),
                    horizontal=True, key="scatter_view")

                if view == 'Component':
                    for i in ["HIV", "Tuberculosis", "Malaria", "TB/HIV", "RSSH", "Multicomponent"]:
                        df_temp = df2_group_region[df2_group_region['componentName'] == i]
                        if len(df_temp.index) != 0:
                            with st.container():
                                st.markdown(
                                    "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **{}** </span></p>".format(
                                        i),
                                    unsafe_allow_html=True)
                                col1, col2, col3, col4 = st.columns([30, 30, 30, 30])
                                if isActive == "Active IPs":
                                    col1.metric("Number of active IPs",
                                                "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                    col2.metric("Number of active Grants", "{:,}".format(
                                        len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                                else:
                                    col1.metric("Number of Grants",
                                                "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                    col2.metric("Number of Implementation Periods", "{:,}".format(
                                        len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                                Number_renewed = df_temp.grantAgreementId.value_counts()
                                Number_renewed = Number_renewed[Number_renewed > 1].count()
                                col3.metric("Principal Recipient(s)",
                                            "{:,}".format(len(df_temp["principalRecipientName"].unique())))
                                col4.metric("Total Disbursed Amount ($)",
                                            "{:,.2f}".format(df_temp["totalDisbursedAmount"].sum()))

                                col1, col2 = st.columns([15, 15], gap='large')

                                if len(df_temp.principalRecipientName.unique()) == 1:
                                    col1.write(df_temp.principalRecipientName.unique()[0])
                                else:
                                    PR = col1.multiselect(
                                        "{} Principal Recipient(s)".format(
                                            len(df_temp.principalRecipientName.unique())),
                                        (list(df_temp.principalRecipientName.unique())))
                                    if len(PR) != 0:
                                        df_temp = df_temp[df_temp['principalRecipientName'].isin(PR)]

                                if len(df_temp.grantAgreementNumber.unique()) == 1:
                                    col2.write(df_temp.grantAgreementNumber.unique()[0])
                                else:
                                    GN = col2.multiselect(
                                        "{} IP(s)".format(len(df_temp.grantAgreementNumber.unique())),
                                        (list(df_temp.grantAgreementNumber.unique())))
                                    if len(GN) != 0:
                                        df_temp = df_temp[df_temp['grantAgreementNumber'].isin(GN)]
                                #df_temp["implementationPeriodStartDate"] = pd.to_datetime(df_temp["implementationPeriodStartDate"])

                                df_temp['implementationPeriodStartDate'] = pd.to_datetime(
                                    df_temp['implementationPeriodStartDate'])
                                df_temp['implementationPeriodEndDate'] = pd.to_datetime(
                                    df_temp['implementationPeriodEndDate'])
                                df_temp['programStartDate'] = pd.to_datetime(
                                    df_temp['programStartDate'])
                                df_temp['programEndDate'] = pd.to_datetime(
                                    df_temp['programEndDate'])

                                fig = px.timeline(df_temp.sort_values('programStartDate'),
                                                  x_start="implementationPeriodStartDate",
                                                  x_end="implementationPeriodEndDate",
                                                  y="grantAgreementNumber",
                                                  color="implementationPeriodStatusTypeName",
                                                  color_discrete_map=color_discrete_map_ip_status,
                                                  hover_data={
                                                      "grantAgreementNumber": True,
                                                      "grantAgreementTitle": True,
                                                      "implementationPeriodStatusTypeName": True,
                                                      "geographicAreaName": True,
                                                      "principalRecipientName": True,
                                                      "programStartDate": True,
                                                      "implementationPeriodStartDate": True,
                                                      "implementationPeriodEndDate": True,
                                                  },
                                                  labels={
                                                      'grantAgreementNumber': 'Grant reference',
                                                      'grantAgreementTitle': 'Grant agreement title',
                                                      'implementationPeriodStatusTypeName': 'Implementation Period status',
                                                      'geographicAreaName': 'Portfolio',
                                                      'principalRecipientName': 'Principal Recipient',
                                                      'programStartDate': 'Grant start',
                                                      'implementationPeriodStartDate': 'Implementation Period start',
                                                      'implementationPeriodEndDate': 'Program end date'}
                                                  )


                                fig.add_vline(x=date.today(), line_width=2, line_color="white", line_dash="dot")
                                fig.add_annotation(x=date.today(), y=1, showarrow=False, text="{}".format(date.today()),
                                                   xshift=50)
                                fig.update_annotations(font_color="white", font_size=15)
                                fig.update_yaxes(showgrid=False, zeroline=True, title_text="", visible=False)
                                fig.update_layout(autosize=False,
                                                  margin=dict(
                                                      l=0,
                                                      r=0,
                                                      b=0,
                                                      t=50,
                                                      pad=4,
                                                      autoexpand=True),
                                                  height=300,
                                                  paper_bgcolor='rgba(0,0,0,0)',
                                                  plot_bgcolor='rgba(0,0,0,0)',
                                                  legend_title='',
                                                  font=dict(
                                                      size=15),

                                                  title="Grants Implementation Timeline")
                                col1.plotly_chart(fig, use_container_width=True, config=config)

                                df_temp2 = df_temp.sort_values('implementationPeriodStartDate')
                                df_temp2['disbursedtocommited'] = df_temp2['totalDisbursedAmount'] * 100 / df_temp2[
                                    'totalCommittedAmount']
                                df_temp2['disbursedtocommited'].fillna(0, inplace=True)
                                df_temp2['disbursedtocommited'] = round(df_temp2['disbursedtocommited']).astype(int)
                                df_temp2['disbursedtocommited'] = df_temp2['disbursedtocommited'].astype(str) + '%'

                                # Create a list of grant agreement numbers in the desired order
                                grant_order = df_temp2['grantAgreementNumber']

                                # Create the bar chart with the desired order of y-axis values
                                fig = {
                                    'data': [go.Bar(x=df_temp2["totalSignedAmount"],
                                                    y=grant_order,
                                                    width=0.7,
                                                    orientation='h',
                                                    marker=dict(color="#023824"),
                                                    name="Signed amount"
                                                    ),
                                             go.Bar(x=df_temp2["totalCommittedAmount"],
                                                    y=grant_order,
                                                    width=0.7,
                                                    orientation='h',
                                                    marker=dict(color="#046944"),
                                                    name="Committed amount"
                                                    ),
                                             go.Bar(x=df_temp2["totalDisbursedAmount"],
                                                    y=grant_order,
                                                    width=0.4,
                                                    orientation='h',
                                                    marker=dict(color="#C1EADB"),
                                                    name="Disbursed amount",
                                                    text=df_temp2['disbursedtocommited']
                                                    )
                                             ],
                                    'layout': go.Layout(barmode='overlay', autosize=False,
                                                        margin=dict(
                                                            l=0,
                                                            r=0,
                                                            b=0,
                                                            t=50,
                                                            pad=4,
                                                            autoexpand=True),
                                                        height=300,
                                                        paper_bgcolor='rgba(0,0,0,0)',
                                                        plot_bgcolor='rgba(0,0,0,0)',
                                                        legend_title='',
                                                        font=dict(
                                                            size=15),
                                                        title="Grants Disbursement Status")
                                }

                                col2.plotly_chart(fig, use_container_width=True, config=config)

                                with st.expander("See grant(s) detail"):
                                    df_temp1 = df_temp[['geographicAreaName',
                                                        'componentName',
                                                        'grantAgreementNumber',
                                                        'isActive',
                                                        'grantAgreementStatusTypeName',
                                                        'grantAgreementTitle',
                                                        'programStartDate',
                                                        'programEndDate',
                                                        'principalRecipientName',
                                                        'principalRecipientSubClassificationName',
                                                        'currency',
                                                        'totalSignedAmount',
                                                        'totalCommittedAmount',
                                                        'totalDisbursedAmount']]
                                    df_temp2 = df_temp1.reset_index(drop=True)
                                    df_temp2.columns = ['Portfolio',
                                                        'Component',
                                                        'Grant agreement number',
                                                        'Is the Grant Active',
                                                        'Grant agreement status type',
                                                        'Grant agreement title',
                                                        'Program start date',
                                                        'Program end date',
                                                        'Principal recipient name',
                                                        'Principal recipient sub-classification',
                                                        'Currency',
                                                        'Signed amount',
                                                        'Committed amount',
                                                        'Disbursed amount']
                                    st.dataframe(df_temp2)

                                    @st.cache_data
                                    def convert_df(df1_filtered_dates2):
                                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                                        return df_temp.to_csv().encode('utf-8')


                                    csv = convert_df(df_temp2)
                                    st.download_button(
                                        label="Download data as CSV",
                                        data=csv,
                                        file_name='GF_Grants_API.csv',
                                        key="dl_{}".format(i)
                                    )
                                st.write('---')

                if view == 'Principal Recipient':

                    for i in df2_group_region.principalRecipientClassificationName.unique():
                        if i is not None:
                            df_temp = df2_group_region[df2_group_region['principalRecipientClassificationName'] == i]

                            with st.container():

                                st.markdown(
                                    "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **{}** </span></p>".format(
                                        i),
                                    unsafe_allow_html=True)

                                col1, col2, col3, col4 = st.columns([30, 30, 30, 30])
                                if isActive == "Active IPs":
                                    col1.metric("Number of active IPs",
                                                "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                    col2.metric("Number of active Grants", "{:,}".format(
                                        len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                                else:
                                    col1.metric("Number of IPs",
                                                "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                    col2.metric("Number of Grants", "{:,}".format(
                                        len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                                Number_renewed = df_temp.grantAgreementId.value_counts()
                                Number_renewed = Number_renewed[Number_renewed > 1].count()
                                col3.metric("Principal Recipient(s)",
                                            "{:,}".format(len(df_temp["principalRecipientName"].unique())))
                                col4.metric("Total Disbursed Amount ($)",
                                            "{:,.2f}".format(df_temp["totalDisbursedAmount"].sum()))

                                col1, col2 = st.columns([15, 15], gap='large')

                                if len(df_temp.principalRecipientName.unique()) == 1:
                                    col1.write(df_temp.principalRecipientName.unique()[0])
                                else:
                                    PR = col1.multiselect(
                                        "{} Principal Recipient(s)".format(len(df_temp.principalRecipientName.unique())),
                                        (list(df_temp.principalRecipientName.unique())),key="{}".format(i))
                                    if len(PR) != 0:
                                        df_temp = df_temp[df_temp['principalRecipientName'].isin(PR)]

                                if len(df_temp.grantAgreementNumber.unique()) == 1:
                                    col2.write(df_temp.grantAgreementNumber.unique()[0])
                                else:
                                    GN = col2.multiselect(
                                        "{} IP(s)".format(len(df_temp.grantAgreementNumber.unique())),
                                        (list(df_temp.grantAgreementNumber.unique())),key="{}2".format(i))
                                    if len(GN) != 0:
                                        df_temp = df_temp[df_temp['grantAgreementNumber'].isin(GN)]

                                fig = px.timeline(df_temp.sort_values('programStartDate'),
                                                  x_start="implementationPeriodStartDate",
                                                  x_end="implementationPeriodEndDate",
                                                  y="grantAgreementNumber",
                                                  color="implementationPeriodStatusTypeName",
                                                  color_discrete_map=color_discrete_map_ip_status,
                                                  hover_data={
                                                      "grantAgreementNumber": True,
                                                      "grantAgreementTitle": True,
                                                      "implementationPeriodStatusTypeName": True,
                                                      "geographicAreaName": True,
                                                      "principalRecipientName": True,
                                                      "programStartDate": True,
                                                      "implementationPeriodStartDate": True,
                                                      "implementationPeriodEndDate": True,
                                                  },
                                                  labels={
                                                      'grantAgreementNumber': 'Grant reference',
                                                      'grantAgreementTitle': 'Grant agreement title',
                                                      'implementationPeriodStatusTypeName': 'Implementation Period status',
                                                      'geographicAreaName': 'Portfolio',
                                                      'principalRecipientName': 'Principal Recipient',
                                                      'programStartDate': 'Grant start',
                                                      'implementationPeriodStartDate': 'Implementation Period start',
                                                      'implementationPeriodEndDate': 'Program end date'}
                                                  )

                                fig.add_vline(x=date.today(), line_width=2, line_color="white", line_dash="dot")
                                fig.add_annotation(x=date.today(), y=1, showarrow=False, text="{}".format(date.today()),
                                                   xshift=50)
                                fig.update_annotations(font_color="white", font_size=15)
                                fig.update_layout(autosize=False,
                                                  margin=dict(
                                                      l=0,
                                                      r=0,
                                                      b=0,
                                                      t=50,
                                                      pad=4,
                                                      autoexpand=True),
                                                  height=300,
                                                  paper_bgcolor='rgba(0,0,0,0)',
                                                  plot_bgcolor='rgba(0,0,0,0)',
                                                  legend_title='',
                                                  font=dict(
                                                      size=15),
                                                  title = "Grants Implementation Timeline"
                                                  )
                                fig.update_yaxes(showgrid=False, zeroline=True, title_text="", visible=False)
                                col1.plotly_chart(fig, use_container_width=True, config=config)

                                df_temp2 = df_temp.sort_values('programStartDate')
                                df_temp2['disbursedtocommited'] = df_temp2['totalDisbursedAmount'] * 100 / df_temp2[
                                    'totalCommittedAmount']
                                df_temp2['disbursedtocommited'].fillna(0, inplace=True)
                                df_temp2['disbursedtocommited'] = round(df_temp2['disbursedtocommited']).astype(int)
                                df_temp2['disbursedtocommited'] = df_temp2['disbursedtocommited'].astype(str) + '%'
                                # Create a list of grant agreement numbers in the desired order
                                grant_order = df_temp2['grantAgreementNumber']

                                # Create the bar chart with the desired order of y-axis values
                                fig = {
                                    'data': [go.Bar(x=df_temp2["totalSignedAmount"],
                                                    y=grant_order,
                                                    width=0.7,
                                                    orientation='h',
                                                    marker=dict(color="#023824"),
                                                    name="Signed amount"
                                                    ),
                                             go.Bar(x=df_temp2["totalCommittedAmount"],
                                                    y=grant_order,
                                                    width=0.7,
                                                    orientation='h',
                                                    marker=dict(color="#046944"),
                                                    name="Committed amount"
                                                    ),
                                             go.Bar(x=df_temp2["totalDisbursedAmount"],
                                                    y=grant_order,
                                                    width=0.4,
                                                    orientation='h',
                                                    marker=dict(color="#C1EADB"),
                                                    name="Disbursed amount",
                                                    text=df_temp2['disbursedtocommited']
                                                    )
                                             ],
                                    'layout': go.Layout(barmode='overlay', autosize=False,
                                                        margin=dict(
                                                            l=0,
                                                            r=0,
                                                            b=0,
                                                            t=50,
                                                            pad=4,
                                                            autoexpand=True),
                                                        height=300,
                                                        paper_bgcolor='rgba(0,0,0,0)',
                                                        plot_bgcolor='rgba(0,0,0,0)',
                                                        legend_title='',
                                                        font=dict(
                                                            size=15),
                                                        title="Grants Disbursement Status")
                                }

                                col2.plotly_chart(fig, use_container_width=True, config=config)

                                with st.expander("See grant(s) detail"):
                                    col1, col2 = st.columns([90, 10])
                                    df_temp1 = df_temp[['geographicAreaName',
                                                        'componentName',
                                                        'grantAgreementNumber',
                                                        'isActive',
                                                        'grantAgreementStatusTypeName',
                                                        'grantAgreementTitle',
                                                        'programStartDate',
                                                        'programEndDate',
                                                        'principalRecipientName',
                                                        'principalRecipientSubClassificationName',
                                                        'currency',
                                                        'totalSignedAmount',
                                                        'totalCommittedAmount',
                                                        'totalDisbursedAmount']]
                                    df_temp2 = df_temp1.reset_index(drop=True)
                                    df_temp2.columns = ['Country',
                                                        'Component',
                                                        'Grant agreement number',
                                                        'Is the Grant Active',
                                                        'Grant agreement status type',
                                                        'Grant agreement title',
                                                        'Program start date',
                                                        'Program end date',
                                                        'Principal recipient name',
                                                        'Principal recipient sub-classification',
                                                        'Currency',
                                                        'Signed amount',
                                                        'Committed amount',
                                                        'Disbursed amount']
                                    col1.dataframe(df_temp2)

                                    @st.cache_data
                                    def convert_df(df2_group_region):
                                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                                        return df_temp.to_csv().encode('utf-8')


                                    csv = convert_df(df_temp2)
                                    col2.download_button(
                                        label="Download data as CSV",
                                        data=csv,
                                        file_name='GF_Grants_API.csv',
                                        key="download4{}".format(i)
                                    )
                                st.write('---')

                if view == 'Region':

                    for i in df2_group_region.Region.unique():
                        df_temp = df2_group_region[df2_group_region['Region'] == i]

                        with st.container():
                            st.markdown(
                                "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **{}** </span></p>".format(
                                    i),
                                unsafe_allow_html=True)

                            col1, col2, col3, col4 = st.columns([30, 30, 30, 30])
                            if isActive == "Active IPs":
                                col1.metric("Number of active IPs",
                                            "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                col2.metric("Number of active Grants", "{:,}".format(
                                    len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                            else:
                                col1.metric("Number of IPs",
                                            "{:,}".format(len(df_temp.groupby(['grantAgreementNumber']))))
                                col2.metric("Number of Grants", "{:,}".format(
                                    len(df_temp['grantAgreementImplementationPeriodId'].unique())))
                            col3.metric("Principal Recipient(s)",
                                        "{:,}".format(len(df_temp["principalRecipientName"].unique())))
                            col4.metric("Total Disbursed Amount ($)",
                                        "{:,.2f}".format(df_temp["totalDisbursedAmount"].sum()))

                            col1, col2 = st.columns([15, 15], gap='large')
                            if len(df_temp.Region.unique()) == 1:
                                geoAreaLevelName_option = col1.multiselect(
                                    'Select portfolio',
                                    (list(df_temp.Region.unique())))
                                if len(geoAreaLevelName_option) != 0:
                                    df_temp = df_temp[df_temp['geographicAreaName'].isin(geoAreaLevelName_option)]
                            elif len(df_temp.Region.unique()) != 1:
                                geoAreaLevelName_option = col1.multiselect(
                                    'Select scope',
                                    (list(df_temp.Region.unique())))
                                if len(geoAreaLevelName_option) != 0:
                                    df_temp = df_temp[df_temp['geographicAreaLevelName'].isin(geoAreaLevelName_option)]

                            if len(df_temp.grantAgreementNumber.unique()) == 1:
                                col2.write(df_temp.grantAgreementNumber.unique()[0])
                            else:
                                GN = col2.multiselect(
                                    "{} IP(s)".format(len(df_temp.grantAgreementNumber.unique())),
                                    (list(df_temp.grantAgreementNumber.unique())))
                                if len(GN) != 0:
                                    df_temp = df_temp[df_temp['grantAgreementNumber'].isin(GN)]

                            fig = px.timeline(df_temp.sort_values('programStartDate'),
                                              x_start="implementationPeriodStartDate",
                                              x_end="implementationPeriodEndDate",
                                              y="grantAgreementNumber",
                                              color="implementationPeriodStatusTypeName",
                                              color_discrete_map=color_discrete_map_ip_status,
                                              hover_data={
                                                          "grantAgreementNumber": True,
                                                          "grantAgreementTitle": True,
                                                          "implementationPeriodStatusTypeName": True,
                                                          "geographicAreaName": True,
                                                          "principalRecipientName": True,
                                                          "programStartDate": True,
                                                          "implementationPeriodStartDate": True,
                                                          "implementationPeriodEndDate": True,
                                              },
                                              labels={
                                                      'grantAgreementNumber': 'Grant reference',
                                                      'grantAgreementTitle': 'Grant agreement title',
                                                      'implementationPeriodStatusTypeName': 'Implementation Period status',
                                                      'geographicAreaName': 'Portfolio',
                                                      'principalRecipientName': 'Principal Recipient',
                                                      'programStartDate': 'Grant start',
                                                      'implementationPeriodStartDate': 'Implementation Period start',
                                                      'implementationPeriodEndDate': 'Program end date'}
                                              )
                            fig.update_traces(marker_line_color='white', line_width=10, opacity=1,
                                              selector=dict(fill='toself'))
                            fig.add_vline(x=date.today(), line_width=2, line_color="white", line_dash="dot")
                            fig.add_annotation(x=date.today(), y=1, showarrow=False, text="{}".format(date.today()),
                                               xshift=50)
                            fig.update_annotations(font_color="white", font_size=15)
                            fig.update_layout(
                                autosize=False,
                                margin=dict(
                                    l=0,
                                    r=0,
                                    b=0,
                                    t=50,
                                    pad=4,
                                    autoexpand=True),
                                height=300,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                legend_title='',
                                font=dict(
                                    size=15),
                                title="Grants Implementation Timeline"
                            )
                            fig.update_yaxes(showgrid=False, zeroline=True, title_text="", visible=False)
                            col1.plotly_chart(fig, use_container_width=True, config=config)

                            df_temp2 = df_temp.sort_values('programStartDate')
                            df_temp2['disbursedtocommited'] = df_temp2['totalDisbursedAmount'] * 100 / df_temp2[
                                'totalCommittedAmount']
                            df_temp2['disbursedtocommited'].fillna(0, inplace=True)
                            df_temp2['disbursedtocommited'] = round(df_temp2['disbursedtocommited']).astype(int)
                            df_temp2['disbursedtocommited'] = df_temp2['disbursedtocommited'].astype(str) + '%'

                            # Create a list of grant agreement numbers in the desired order
                            grant_order = df_temp2['grantAgreementNumber']

                            # Create the bar chart with the desired order of y-axis values
                            fig = {
                                'data': [go.Bar(x=df_temp2["totalSignedAmount"],
                                                y=grant_order,
                                                width=0.7,
                                                orientation='h',
                                                marker=dict(color="#023824"),
                                                name="Signed amount"
                                                ),
                                         go.Bar(x=df_temp2["totalCommittedAmount"],
                                                y=grant_order,
                                                width=0.7,
                                                orientation='h',
                                                marker=dict(color="#046944"),
                                                name="Committed amount"
                                                ),
                                         go.Bar(x=df_temp2["totalDisbursedAmount"],
                                                y=grant_order,
                                                width=0.4,
                                                orientation='h',
                                                marker=dict(color="#C1EADB"),
                                                name="Disbursed amount",
                                                text=df_temp2['disbursedtocommited']
                                                )
                                         ],
                                'layout': go.Layout(barmode='overlay', autosize=False,
                                                    margin=dict(
                                                        l=0,
                                                        r=0,
                                                        b=0,
                                                        t=50,
                                                        pad=4,
                                                        autoexpand=True),
                                                    height=300,
                                                    paper_bgcolor='rgba(0,0,0,0)',
                                                    plot_bgcolor='rgba(0,0,0,0)',
                                                    legend_title='',
                                                    font=dict(
                                                        size=15),
                                                    title="Grants Disbursement Status")
                            }

                            col2.plotly_chart(fig, use_container_width=True, config=config)

                            with st.expander("See grant(s) detail"):
                                col1, col2 = st.columns([90, 10])
                                df_temp1 = df_temp[['geographicAreaName',
                                                    'componentName',
                                                    'grantAgreementNumber',
                                                    'isActive',
                                                    'grantAgreementStatusTypeName',
                                                    'grantAgreementTitle',
                                                    'programStartDate',
                                                    'programEndDate',
                                                    'principalRecipientName',
                                                    'principalRecipientSubClassificationName',
                                                    'currency',
                                                    'totalSignedAmount',
                                                    'totalCommittedAmount',
                                                    'totalDisbursedAmount']]
                                df_temp2 = df_temp1.reset_index(drop=True)
                                df_temp2.columns = ['Country',
                                                    'Component',
                                                    'Grant agreement number',
                                                    'Is the Grant Active',
                                                    'Grant agreement status type',
                                                    'Grant agreement title',
                                                    'Program start date',
                                                    'Program end date',
                                                    'Principal recipient name',
                                                    'Principal recipient sub-classification',
                                                    'Currency',
                                                    'Signed amount',
                                                    'Committed amount',
                                                    'Disbursed amount']
                                col1.dataframe(df_temp2)


                                @st.cache_data
                                def convert_df(df1_filtered_dates2):
                                    # IMPORTANT: Cache the conversion to prevent computation on every rerun
                                    return df_temp.to_csv().encode('utf-8')


                                csv = convert_df(df_temp2)
                                col1.download_button(
                                    label="Download data as CSV",
                                    data=csv,
                                    file_name='GF_Grants_API.csv',
                                    key="download1{}".format(i)
                                )
                            st.write('---')

            with tab2:
                # METRICS ------------------------------------
                col1, col2, col3, col4 = st.columns([30, 30, 30, 30])
                if isActive == "Active Grants":
                    col1.metric("Number of active Grants",
                                "{:,}".format(len(df2_group_region.groupby(['grantAgreementNumber']))))
                    col2.metric("Number of active IPs",
                                "{:,}".format(len(df2_group_region['grantAgreementImplementationPeriodId'].unique())))
                else:
                    col1.metric("Number of Grants",
                                "{:,}".format(len(df2_group_region.groupby(['grantAgreementNumber']))))
                    col2.metric("Number of IPs",
                                "{:,}".format(len(df2_group_region['grantAgreementImplementationPeriodId'].unique())))
                col3.metric("Principal Recipient(s)",
                            "{:,}".format(len(df2_group_region["principalRecipientName"].unique())))
                col4.metric("Total Disbursed Amount ($)",
                            "{:,.2f}".format(df2_group_region["totalDisbursedAmount"].sum()))

                df_temp2 = df2_group_region
                df_temp2['disbursedtocommited'] = df_temp2['totalDisbursedAmount'] * 100 / df_temp2[
                    'totalCommittedAmount']
                df_temp2['disbursedtocommited'].fillna(0, inplace=True)
                df_temp2['disbursedtocommited'] = round(df_temp2['disbursedtocommited']).astype(int)
                df_temp2['disbursedtocommited'] = df_temp2['disbursedtocommited'].astype(str) + '%'

                col1, col2 = st.columns([15, 15], gap='large')

                fig = px.timeline(df2_group_region.sort_values(by='implementationPeriodStartDate', ascending=True),
                                  x_start="implementationPeriodStartDate",
                                  x_end="implementationPeriodEndDate",
                                  y="grantAgreementNumber",
                                  color="implementationPeriodStatusTypeName",
                                  color_discrete_map=color_discrete_map_ip_status,
                                  hover_data={"implementationPeriodStatusTypeName": True,
                                              "geographicAreaName": True,
                                              "principalRecipientName": True,
                                              "implementationPeriodStartDate": True,
                                              "implementationPeriodEndDate": True,
                                              "componentName": True},
                                  labels={'geographicAreaName': 'Country',
                                          'principalRecipientName': 'Principal Recipient',
                                          'implementationPeriodStartDate': 'IP start date',
                                          'implementationPeriodEndDate': 'IP end date',
                                          'grantAgreementNumber': 'Grant agreement number',
                                          'grantAgreementTitle': 'Grant agreement title'})

                fig.add_vline(x=date.today(), line_width=2, line_color="white", line_dash="dot")
                fig.add_annotation(x=date.today(), y=1, showarrow=False, text="{}".format(date.today()), xshift=50)
                fig.update_annotations(font_color="white", font_size=20)
                fig.update_layout(
                    autosize=False,
                    margin=dict(
                        l=0,
                        r=0,
                        b=0,
                        t=50,
                        pad=4,
                        autoexpand=True),
                    height=600,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    legend_title='Implementation Period Status',
                    title="Grants Implementation Timeline")
                fig.update_yaxes(showgrid=False, zeroline=True, title_text="", visible=False)
                col1.plotly_chart(fig, use_container_width=True, config=config)

                df_temp2 = df2_group_region.sort_values('programStartDate')
                df_temp2['disbursedtocommited'] = df_temp2['totalDisbursedAmount'] * 100 / df_temp2[
                    'totalCommittedAmount']
                df_temp2['disbursedtocommited'].fillna(0, inplace=True)
                df_temp2['disbursedtocommited'] = round(df_temp2['disbursedtocommited']).astype(int)
                df_temp2['disbursedtocommited'] = df_temp2['disbursedtocommited'].astype(str) + '%'

                # Create a list of grant agreement numbers in the desired order
                grant_order = df_temp2['grantAgreementNumber']

                # Create the bar chart with the desired order of y-axis values
                fig = {
                    'data': [go.Bar(x=df_temp2["totalSignedAmount"],
                                    y=grant_order,
                                    width=0.7,
                                    orientation='h',
                                    marker=dict(color="#023824"),
                                    name="Signed amount"
                                    ),
                             go.Bar(x=df_temp2["totalCommittedAmount"],
                                    y=grant_order,
                                    width=0.7,
                                    orientation='h',
                                    marker=dict(color="#046944"),
                                    name="Committed amount"
                                    ),
                             go.Bar(x=df_temp2["totalDisbursedAmount"],
                                    y=grant_order,
                                    width=0.4,
                                    orientation='h',
                                    marker=dict(color="#C1EADB"),
                                    name="Disbursed amount",
                                    text=df_temp2['disbursedtocommited']
                                    )
                             ],
                    'layout': go.Layout(barmode='overlay', autosize=False,
                                        margin=dict(
                                            l=0,
                                            r=0,
                                            b=0,
                                            t=50,
                                            pad=4,
                                            autoexpand=True),
                                        height=600,
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        legend_title='',
                                        font=dict(
                                            size=15),
                                        title="Grants Disbursement Status")
                }

                col2.plotly_chart(fig, use_container_width=True, config=config)

        if dataset == "Disbursements":
            col2.markdown(
                "<span style='text-align: justify; font-size: 280%; color:#04AA6D'> **Disbursements records** </span> "
                "<p style='text-align: justify'> A disbursement corresponds to a tranche transfer of the grant funds for the implementation"
                " of Programs.<br>"
                " In order to visualize disbursement information data we load and explore the API de-normalized view of all Grant Agreement "
                "Disbursements records. </span> "
                "<span style='color:grey'>Loading takes a few seconds the first time.</span> </p>",
                unsafe_allow_html=True)

            # Loading GF Disbursement API
            count = 0
            @st.cache_data(show_spinner=False)
            def Loading_API_disbursements():
                # reading api
                service_url0 = "https://data-service.theglobalfund.org/v3.3/odata/GrantAgreementDisbursements"
                response0 = requests.get(service_url0)
                # make sure we got a valid response
                if (response0.ok):
                    # get the full data from the response
                    data0j = response0.json()
                else:
                    st.caption("Global Fund API cannot be loaded")
                df1 = pd.DataFrame(data0j["value"])
                df1.drop(['dateTimeCreated', 'dateTimeUpdated'], axis=1, inplace=True)
                df1['disbursementDate'] = df1['disbursementDate'].str.slice(0, 10)
                df1['disbursementDate'] = pd.to_datetime(df1['disbursementDate'])
                return df1



            df1 = Loading_API_disbursements()
            df1 = pd.merge(df1,
                           df2,
                           on='grantAgreementImplementationPeriodId',
                           how='left')


            # FILTERS ------------------------------------

            with st.sidebar:

                # Component filter
                option_Component = st.multiselect(
                    'Filter grant component(s)',
                    options=list(df1.componentName.sort_values(ascending=True).unique()),
                    key="component_multiselect")
                if len(option_Component) == 0:
                    df1_df_group_compo = df1
                else:
                    df1_df_group_compo = df1[df1["componentName"].isin(option_Component)]

                # Principal recipient filter
                option_map_pr = st.multiselect(
                    'Filter PR type',
                    options=list(
                        df1_df_group_compo.principalRecipientSubClassificationName.sort_values(
                            ascending=True).unique()),
                    key="pr_multiselect2")
                if len(option_map_pr) == 0:
                    df_group_pr = df1_df_group_compo
                else:
                    df_group_pr = df1_df_group_compo[
                        df1_df_group_compo["principalRecipientSubClassificationName"].isin(option_map_pr)]

                # Region filter
                region_filter = st.multiselect(
                    'Select region',
                    options=list(df_group_pr.Region.sort_values(ascending=True).unique()),
                    key="pr_multiselect3")
                if len(region_filter) == 0:
                    df1_group_region = df_group_pr
                else:
                    df1_group_region = df_group_pr[df_group_pr["Region"].isin(region_filter)]

                # Country filter
                country_filter = st.multiselect(
                    'Select portfolio',
                    options=list(df1_group_region.geographicAreaName.sort_values(ascending=True).unique()),
                    key="pr_multiselect4")
                if len(country_filter) == 0:
                    df1_group_country = df1_group_region
                else:
                    df1_group_country = df1_group_region[df1_group_region["geographicAreaName"].isin(country_filter)]

                # Timeline filter
                if len(df1_group_country) != 0:
                    start_year, end_year = st.select_slider(
                        'Disbursement year range',
                        options=list(
                            df1_group_country.disbursementDate.astype('datetime64[ns]').dt.year.sort_values(
                                ascending=True).unique()),
                        value=(df1_group_country.disbursementDate.astype('datetime64[ns]').dt.year.sort_values(
                            ascending=True).min(),
                               df1_group_country.disbursementDate.astype('datetime64[ns]').dt.year.sort_values(
                                   ascending=True).max()))
                    # Filtered dataset:
                    df1_filtered_dates = df1_group_country[
                        (df1_group_country.disbursementDate.astype('datetime64[ns]').dt.year >= start_year) & (
                                df1_group_country.disbursementDate.astype('datetime64[ns]').dt.year <= end_year)]
                else:
                    df1_filtered_dates == df1_group_country


            # METRICS ------------------------------------
            col1, col2, col3, col4 = st.columns([30, 30, 30, 30])
            col1.metric("Number of disbursements", "{:,}".format(len(df1_filtered_dates.disbursementAmount)))
            col2.metric("Total amount ($)", "{:,}".format(round(df1_filtered_dates.disbursementAmount.sum())))
            col3.metric("First record", "{}".format(min(pd.to_datetime(df1_filtered_dates.disbursementDate).dt.date)))
            col4.metric("Last record", "{}".format(max(pd.to_datetime(df1_filtered_dates.disbursementDate).dt.date)))

            # TABS ------------------------------------
            tab1, tab2, tab3, tab4 = st.tabs(["Disbursements overview 📈", "Disbursements map 🗺️",
                                              "Components - Region - Country (Sankey Diagram) 📍", "Download Data 🔢"])

            df1_filtered_dates["Year"] = df1_filtered_dates.disbursementDate.astype('datetime64[ns]').dt.year
            df1_filtered_dates["Year"] = df1_filtered_dates["Year"].astype(int)

            with tab1:
                view = st.radio(
                    "Select view",
                    ('All disbursements', 'Component', 'Region', 'Principal Recipient'),
                    horizontal=True)
                if view == 'All disbursements':
                    fig = px.scatter(df1_filtered_dates, x="disbursementDate", y="disbursementAmount",
                                     color="componentName",
                                     log_y=True, hover_data=['disbursementAmount'],
                                     color_discrete_map=color_discrete_map,
                                     marginal_y="box", opacity=0.45)
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        height=600,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend_title='Component')
                    fig.update_traces(opacity=1, marker=dict(line=dict(width=0)))
                    fig.update_xaxes(showgrid=False, zeroline=True, title_text="")
                    fig.update_yaxes(showgrid=False, zeroline=True, title_text="Total disbursed amount ($)")
                    st.plotly_chart(fig, use_container_width=True, config=config)
                if view == 'Component':
                    col1, col2, col3 = st.columns([15, 15, 15])
                    df_line = df1_filtered_dates[["componentName", "disbursementAmount", "Year"]].groupby(
                        ["Year", "componentName"]).sum().reset_index()
                    fig = px.bar(df_line, x="Year", y="disbursementAmount", color="componentName",
                                 color_discrete_map=color_discrete_map)
                    fig.update_traces(hovertemplate='%{x} <br> %{y}')
                    fig.update_layout(
                        modebar_remove=['zoom'],
                        autosize=True,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=380,
                        title={
                            'text': 'Yearly disbursements ($)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            yanchor="top",
                            orientation="h",
                            title="Component")
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=True, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col1.plotly_chart(fig, use_container_width=True, config=config)

                    fig = px.area(df_line,
                                  y="disbursementAmount",
                                  x="Year",
                                  color="componentName",
                                  color_discrete_map=color_discrete_map,
                                  groupnorm='percent')
                    fig.update_traces(mode="lines",
                                      hovertemplate='%{x} <br> %{y:.2f}%')
                    fig.update_layout(
                        autosize=True,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Yearly disbursements normalized (%)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col2.plotly_chart(fig, use_container_width=True, config=config)

                    df_bar = df1_filtered_dates.groupby(['componentName'], as_index=False)[
                        'disbursementAmount'].sum().sort_values('disbursementAmount')
                    list_comp = list(df_bar.componentName.unique())
                    fig = px.bar(df_bar, y='componentName', x='disbursementAmount', color='componentName',
                                 text_auto=True, color_discrete_map=color_discrete_map)
                    y = list_comp
                    fig.update_layout(barmode='stack', yaxis={'categoryorder': 'array', 'categoryarray': y})
                    fig.update_traces(hovertemplate=None, hoverinfo='skip')
                    # paper_bgcolor="rgb(255,255,255)", plot_bgcolor="rgb(255,255,255)")
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    fig.update_layout(
                        autosize=True,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True
                        ),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Total per component ($)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=False)
                    col3.plotly_chart(fig, use_container_width=True, config=config)

                if view == 'Region':
                    col1, col2, col3 = st.columns([15, 15, 15], gap='medium')
                    df_line = df1_filtered_dates[["Region", "disbursementAmount", "Year"]].groupby(
                        ["Year", "Region"]).sum().reset_index()
                    fig = px.bar(df_line, x="Year", y="disbursementAmount", color="Region",
                                 color_discrete_map=color_discrete_map2)
                    fig.update_traces(hovertemplate='%{x} <br> %{y}')
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=380,
                        title={
                            'text': 'Yearly disbursements ($)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        legend=dict(
                            yanchor="top",
                            orientation="h")
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=True, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col1.plotly_chart(fig, use_container_width=True, config=config)

                    fig = px.area(df_line,
                                  y="disbursementAmount",
                                  x="Year",
                                  color="Region",
                                  color_discrete_map=color_discrete_map2,
                                  groupnorm='percent')
                    fig.update_traces(mode="lines",
                                      hovertemplate='%{x} <br> %{y:.2f}%')
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Yearly disbursements normalized (%)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col2.plotly_chart(fig, use_container_width=True, config=config)

                    df_bar2 = df1_filtered_dates.groupby(['Country'], as_index=False)[
                        'disbursementAmount'].sum().sort_values(
                        by='disbursementAmount', ascending=True).tail(10)
                    fig = px.bar(df_bar2, y='Country', x='disbursementAmount', text_auto=True)
                    fig.update_traces(hovertemplate=None, hoverinfo='skip')
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        width=800,
                        height=400,
                        title={
                            'text': 'Top 10 disbursement receivers',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=False)
                    fig.update_traces(marker_color='#003566', opacity=1)
                    col3.plotly_chart(fig, use_container_width=True, config=config)

                if view == "Principal Recipient":
                    col1, col2, col3 = st.columns([15, 15, 15], gap='medium')
                    df_line = df1_filtered_dates[
                        ["principalRecipientSubClassificationName", "disbursementAmount", "Year"]].groupby(
                        ["Year", "principalRecipientSubClassificationName"]).sum().reset_index()
                    fig = px.bar(df_line, x="Year", y="disbursementAmount",
                                 color="principalRecipientSubClassificationName",
                                 color_discrete_map=color_discrete_map3)
                    fig.update_traces(hovertemplate='%{x} <br> %{y}')
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Yearly disbursements ($)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=True, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col1.plotly_chart(fig, use_container_width=True, config=config)

                    fig = px.area(df_line,
                                  y="disbursementAmount",
                                  x="Year",
                                  color="principalRecipientSubClassificationName",
                                  color_discrete_map=color_discrete_map3,
                                  groupnorm='percent')
                    fig.update_traces(mode="lines",
                                      hovertemplate='%{x} <br> %{y:.2f}%')
                    fig.update_layout(
                        autosize=False,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Yearly disbursements normalized (%)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=True)
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    col2.plotly_chart(fig, use_container_width=True, config=config)

                    # Top disbursement receivers
                    df_pr = df1_filtered_dates.groupby(['principalRecipientSubClassificationName'], as_index=False)[
                        'disbursementAmount'].sum().sort_values('disbursementAmount')
                    list_pr = list(df_pr.principalRecipientSubClassificationName.unique())
                    fig = px.bar(df_pr, y='principalRecipientSubClassificationName', x='disbursementAmount',
                                 color='principalRecipientSubClassificationName',
                                 text_auto=True, color_discrete_map=color_discrete_map3)
                    y = list_pr
                    fig.update_layout(barmode='stack', yaxis={'categoryorder': 'array', 'categoryarray': y})
                    fig.update_traces(hovertemplate=None, hoverinfo='skip')
                    # paper_bgcolor="rgb(255,255,255)", plot_bgcolor="rgb(255,255,255)")
                    for axis in fig.layout:
                        if type(fig.layout[axis]) == go.layout.YAxis:
                            fig.layout[axis].title.text = ''
                        if type(fig.layout[axis]) == go.layout.XAxis:
                            fig.layout[axis].title.text = ''
                    fig.update_layout(
                        autosize=True,
                        margin=dict(
                            l=0,
                            r=0,
                            b=0,
                            t=50,
                            pad=4,
                            autoexpand=True
                        ),
                        # width=800,
                        height=400,
                        title={
                            'text': 'Total per component ($)',
                            'x': 0.5,
                            'xanchor': 'center'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        showlegend=False
                    )
                    fig.update_xaxes(showgrid=False, zeroline=True)
                    fig.update_yaxes(showgrid=False, zeroline=False)
                    col3.plotly_chart(fig, use_container_width=True, config=config)

                # Disbursement map
                with tab2:
                    view = st.radio(
                        "Select view",
                        ('All disbursements', 'Per components'),
                        horizontal=True)

                    df_geo = \
                    df1_filtered_dates.groupby(['componentName', 'geographicAreaName', 'SpatialDim'], as_index=False)[
                        'disbursementAmount'].sum().sort_values(by="disbursementAmount")

                    if view == 'All disbursements':
                        fig = go.Figure(
                            data=go.Choropleth(
                                locations=df_geo["SpatialDim"],
                                z=df_geo['disbursementAmount'],
                                colorscale="Blues",
                                showscale=True),
                            layout=go.Layout(height=500,
                                             margin=dict(
                                                 l=0,
                                                 r=10,
                                                 b=0,
                                                 t=0,
                                                 pad=4,
                                                 autoexpand=True),
                                             geo=dict(bgcolor='rgba(0,0,0,0)',
                                                      lakecolor='#4E5D6C',
                                                      visible=False,
                                                      landcolor='#3d3d3d',
                                                      showland=True,
                                                      showcountries=True,
                                                      countrycolor='#5c5c5c',
                                                      countrywidth=0.5,
                                                      projection=dict(type='natural earth'))))
                        st.plotly_chart(fig, use_container_width=True, config=config)

                    if view == 'Per components':
                        for i in df_geo["componentName"].unique():
                            df_geo2 = df_geo[df_geo["componentName"] == i]
                            fig = go.Figure(
                                data=go.Choropleth(
                                    locations=df_geo2["SpatialDim"],
                                    z=df_geo2['disbursementAmount'],
                                    colorscale="Blues",
                                    showscale=True),
                                layout=go.Layout(height=500,
                                                 margin=dict(
                                                     l=0,
                                                     r=10,
                                                     b=0,
                                                     t=10,
                                                     pad=4,
                                                     autoexpand=True),
                                                 geo=dict(bgcolor='rgba(0,0,0,0)',
                                                          lakecolor='#4E5D6C',
                                                          visible=False,
                                                          landcolor='#3d3d3d',
                                                          showland=True,
                                                          showcountries=True,
                                                          countrycolor='#5c5c5c',
                                                          countrywidth=0.5,
                                                          projection=dict(type='natural earth'))))
                            fig.update_layout(
                                title={
                                    'text': i,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'x': 0.5
                                },
                                title_font_color="white")
                            st.plotly_chart(fig, use_container_width=True, config=config)

                # Sankey diagriam
                with tab3:
                    # Data preparation for Sankey diagram
                    df1_sankey = df1_filtered_dates.copy()
                    df1_sankey["GF"] = "Global Fund"
                    df1_sankey = df1_sankey.groupby(['GF', 'componentName'], as_index=False)['disbursementAmount'].sum()
                    df2 = df1_filtered_dates.groupby(['componentName', 'Region'], as_index=False)[
                        'disbursementAmount'].sum()
                    df3 = df1_filtered_dates.groupby(['Region', 'geographicAreaName'], as_index=False)[
                        'disbursementAmount'].sum()

                    df1_sankey.columns = ['a', 'b', 'Quantity']
                    df2.columns = ['a', 'b', 'Quantity']
                    df3.columns = ['a', 'b', 'Quantity']

                    # Combine all DataFrames
                    df4 = pd.concat([df1_sankey, df2, df3])

                    # Generate the Sankey diagram
                    unique_labels = list(set(df4['a']).union(set(df4['b'])))
                    source_indices = [unique_labels.index(val) for val in df4['a']]
                    target_indices = [unique_labels.index(val) for val in df4['b']]

                    fig = go.Figure(data=[go.Sankey(
                        node=dict(
                            pad=15,
                            thickness=20,
                            line=dict(
                                color="black",
                                width=0.5
                            ),
                            label=unique_labels,
                        ),
                        link=dict(
                            source=source_indices,
                            target=target_indices,
                            value=df4['Quantity']
                        ),
                        textfont=dict(size=15)
                    )])

                    fig.update_layout(
                        title_text="Sankey Diagram of The Global Fund Disbursements",
                        font=dict(size=12),
                        height=825
                    )

                    # Show Sankey diagram in Streamlit
                    st.plotly_chart(fig, use_container_width=True)

                with tab4:
                    # Dataframe wrangler
                    groupby = st.radio(
                        "Which dataset do you want?",
                        ('Keep the same filters', 'All disbursements records'))

                    if groupby == 'All disbursements records':
                        dl_file = df1[
                            ["Country", "componentName", "principalRecipientSubClassificationName", "disbursementDate",
                             "disbursementAmount"]].sort_values(by="disbursementDate", ascending=True)
                    if groupby == 'Keep the same filters':
                        dl_file = df1_filtered_dates[
                            ["Country", "componentName", "principalRecipientSubClassificationName", "disbursementDate",
                             "disbursementAmount"]].sort_values(by="disbursementDate", ascending=True)

                    dl_file.columns = ["Country", "Component", "Principal Recipient", "Disbursement date",
                                       "Disbursement amount ($)"]
                    st.dataframe(dl_file.reset_index(drop=True))

                    @st.cache_data
                    def convert_df(dl_file):
                        # IMPORTANT: Cache the conversion to prevent computation on every rerun
                        return dl_file.to_csv().encode('utf-8')


                    csv = convert_df(dl_file)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name='GF_Disbursements_API.csv',
                        key="download2"
                    )

        # ---- SIDEBAR ----
        with st.sidebar:
            with st.expander("Read more about The Global Fund"):
                # Information on dataset chosen
                info_para = st.empty
                # The Global Fund details
                st.markdown("<p style='text-align: justify;'>"
                            "<a href='https://www.theglobalfund.org/en/'>The Global Fund </a> is a partnership designed to accelerate the end of AIDS, tuberculosis and "
                            "malaria as epidemics. <br> It prioritizes: results-based work, accountability, preparing countries"
                            " for graduation from aid, investing in people as assets for development and inclusive governance."
                            " To do so, the Global Fund mobilizes and invests more than US$4 billion a year to support programs "
                            "run by local experts in more than 100 countries in partnership with governments, civil society, "
                            "technical agencies, the private sector and people affected by the diseases. <br> You can visit <a href='https://www.theglobalfund.org/en/funding-model/'>this page</a> to"
                            " learn more about the organization Funding Model.<br><br>"
                            "The Global Fund API <a href='https://data-service.theglobalfund.org/api'> (link to documentation)</a>"
                            " is providing access to different data including: <br>Lookup Lists, Funding Allocations, Donors & Implementation Partners,"
                            " various Grants information, information on Resource Mobilization and several de-normalized views of all eligibility records.</p>",
                            unsafe_allow_html=True)
            with st.expander("What's an API?"):
                st.markdown("<p style='text-align: justify;'>"
                            "The term API stands for Application Programming Interface. "
                            "API enable applications, here our web app, to communicate with an external data source using simple commands. "
                            "<a href='https://en.wikipedia.org/wiki/API'> Wikipedia</a> defines it as a connection "
                            "between computers or between computer programs offering a service to other pieces of software."
                            "<br>In the case of the WHO, The Global Fund and the World Bank, all 3 APIs have been created by these organizations"
                            " with the purpose of ensuring transparency and a better access to information generated, "
                            "for the benefit of the stakeholders in their activities.<br>"
                            "In order to offer more filter options in this app I also imported the "
                            "<a href='https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups'> World Bank regional groupings and Income group classifications </a>"
                            " from the World Bank API through the Python wbgapi library and merged it with the country list from the WHO and Global Fund datasets."
                            "</p>", unsafe_allow_html=True)
