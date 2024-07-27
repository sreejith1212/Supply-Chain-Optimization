import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

if __name__ == "__main__":

    # #Initializing the session state
    # if 'airbnb_data' not in st.session_state:
    #     st.session_state.airbnb_data = None
    # if 'processed_airbnb_df' not in st.session_state:
    #     st.session_state['processed_airbnb_df'] = None

    # set app page layout type
    st.set_page_config(layout="wide")

    # create sidebar
    with st.sidebar:        
        page = option_menu(
                            menu_title='Supply Chain',
                            options=['Exploratory Data Analysis (EDA)', 'Advanced Analysis'],
                            icons=['gear', 'bar-chart-line'],#, 'info-circle', 'map'],
                            menu_icon="pin-map-fill",
                            default_index=0 ,
                            styles={"container": {"padding": "5!important"},
                                    "icon": {"color": "brown", "font-size": "23px"}, 
                                    "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "lightblue", "display": "flex", 
                                                 "align-items": "center"},
                                    "nav-link-selected": {"background-color": "grey"},}  
        )

    warehouse_costs = pd.read_csv("warehouse_costs.csv")
    warehouse_capacity = pd.read_csv("warehouse_capacity.csv")
    vmi_customer = pd.read_csv("vmi_customer.csv")
    product_per_plant = pd.read_csv("product_per_plant.csv")
    plant_ports = pd.read_csv("plant_ports.csv")
    freight = pd.read_csv("freight_info.csv")
    total_order_cost = pd.read_csv("total_order_cost.csv")
    order = pd.read_csv("supply_chain_cleaned_1.csv")
    order_new = pd.read_csv("supply_chain_cleaned_2.csv")

    if page == "Exploratory Data Analysis (EDA)":

        col001, col002 = st.columns([10,2])
        col002.write(":orange[Note: All cost is in dollars($)]")

        st.header("Exploratory Data Analysis (EDA) on Preprocessed Supply Chain Data", divider = "rainbow")
        st.write("")
        st.write("")
        st.write("")
        
        container_5 = st.container(border=True)
        col1, col2, col3 = container_5.columns([1,20,1])
        try:

            categorical_features = ['Origin Port', 'Destination Port', 'Plant Code', 'Service Level', 'Carrier']
            fig, axes = plt.subplots(len(categorical_features), 1, figsize=(10, 15))

            for i, feature in enumerate(categorical_features):
                sns.countplot(data=order, y=feature, ax=axes[i], order=order[feature].value_counts().index, palette="Dark2")
                axes[i].set_title(f'Distribution of Orders by {feature}')
                axes[i].set_xlabel('Count')
                axes[i].set_ylabel(feature)

            plt.tight_layout()
            col2.pyplot(fig)

            # Warehouse Analysis: Capacity constraints and product distribution
            warehouse_capacity.rename(columns={'Daily Capacity ': 'Daily Capacity'}, inplace=True)

            # Plotting the capacities of each warehouse
            fig, ax = plt.subplots(figsize=(10,3))
            sns.barplot(data=warehouse_capacity, x='Plant ID', y='Daily Capacity', palette="Paired")
            plt.title('Daily Capacities of Warehouses')
            plt.xlabel('Warehouse (Plant ID)')
            plt.ylabel('Daily Capacity')
            plt.xticks(rotation=45)
            col2.pyplot(fig)


            # Analyzing the distribution of products per plant
            fig, ax = plt.subplots(figsize=(10,3))
            products_count_per_plant = product_per_plant.groupby('Plant Code').count()
            sns.barplot(x=products_count_per_plant.index, y=products_count_per_plant['Product ID'], palette="Set2")
            plt.title('Number of Products per Plant')
            plt.xlabel('Plant Code')
            plt.ylabel('Number of Products')
            plt.xticks(rotation=45)
            col2.pyplot(fig)

        except:
            st.warning("Processed Data Not Available!")

    if page == "Advanced Analysis":

        col001, col002 = st.columns([10,2])
        col002.write(":orange[Note: All cost is in dollars($)]")

        st.header("Advanced Analysis And Optimization", divider = "rainbow")
        st.write("")
        st.write("")
        st.write("")
        
        container_6 = st.container(border=True)
        col9, col10 = container_6.columns([1,1])

        col10.dataframe(total_order_cost,hide_index =True, column_order= ["Order ID", "Product ID", "Shipment Cost", "Total Order Cost"],  use_container_width=True, height=255)
        # Plot histogram with KDE of Order Cost'
        fig, ax = plt.subplots(figsize=(10,3))
        sns.histplot(total_order_cost["Total Order Cost"], kde=True, log_scale=True)
        plt.xlabel('Order Cost')
        plt.ylabel('Density')
        plt.title('Histogram with KDE of Total Order Cost')
        plt.grid(True)
        col9.pyplot(fig, use_container_width=True)

        # Count orders per plant code
        order_counts = order.groupby(by=['Plant Code'])["Product ID"].nunique().reset_index(name='Order Count')
        order_counts.columns = ['Plant Code', 'Order Count']

        # Aggregate daily capacity per plant
        capacity_per_plant = warehouse_capacity.groupby(by=["Plant ID"]).sum().reset_index()
        capacity_per_plant.drop(columns=["Unnamed: 0"], inplace=True)
        capacity_per_plant.columns = ['Plant Code', 'Daily Capacity']

        # Merge order counts and capacity dataframes
        warehouse_cap_utilise = pd.merge(order_counts, capacity_per_plant, on='Plant Code', how='right')
        warehouse_cap_utilise.fillna(value=0, inplace=True)
        warehouse_cap_utilise["Capacity Utilized"] = (warehouse_cap_utilise["Order Count"]/warehouse_cap_utilise["Daily Capacity"]) * 100

        fig = px.bar(warehouse_cap_utilise, 
            x="Plant Code", 
            y="Capacity Utilized", 
            color="Capacity Utilized",
            height=400, 
            width=800,
            title = "Capacity Utilized by Each Warehouse")
        col9.plotly_chart(fig)

        avg_freight_cost = freight.groupby(by=["orig_port_cd", "dest_port_cd"]).agg({"rate" : "mean"}).reset_index()
        avg_freight_cost["Route"] = avg_freight_cost["orig_port_cd"] + " TO " + avg_freight_cost["dest_port_cd"]
        
        fig = px.bar(avg_freight_cost, 
            x="Route", 
            y="rate",
            color="Route",
            height=400, 
            width=800,
            title = "Average Rate For Each Route")
        col10.plotly_chart(fig)
        
        merged_df = pd.merge(total_order_cost, order_new, on=["Order ID", "Product ID", "Origin Port", "Plant Code"], how="left")
        merged_df.dropna(inplace=True)
        merged_df["Cost Difference"] = merged_df["Total Order Cost"] - merged_df["Efficient Total Cost"]
        col9.dataframe(merged_df,hide_index =True, column_order= ["Order ID", "Product ID", "Shipment Cost", "Efficient Freight Cost", "Total Order Cost", "Efficient Total Cost",
                                                                    "Cost Difference", "Efficient WareHouse",  "Efficient Port"],  use_container_width=True)

        total_order_cost["storage cost"] = total_order_cost["Total Order Cost"] - total_order_cost["Shipment Cost"]
        fig = px.scatter(total_order_cost, 
            y="storage cost", 
            x="Shipment Cost",
            height=400, 
            width=800,
            title = "Cost Distribution (Storage V/s Freight)")
        col10.plotly_chart(fig)

        efficient_data = order_new.groupby(by=["Efficient WareHouse", "Efficient Port"]).size().reset_index(name='count')
        fig = px.bar(efficient_data, 
            x="Efficient WareHouse", 
            y="count",
            color="Efficient Port",
            height=400, 
            width=800,
            title = "Optimal Warehouse To Port")
        col9.plotly_chart(fig)