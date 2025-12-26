import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="WJC Fantasy Dashboard")

# 2. Data Loading (Points to your GitHub CSV)
@st.cache_data
def load_data():
    # Replace with your actual GitHub Raw URL
    url = "data/dynamic/Final_Master_Dataset.csv" 
    df = pd.read_csv(url)
    df['fantasypoints'] = pd.to_numeric(df['FP'], errors='coerce').fillna(0)
    return df

df = load_data()
# We'll pretend the current year is 2025 for your visuals
cy_val = 2025
cy_df = df[df['year'] == cy_val].copy()

# --- MAIN UI ---
tab_cy, tab_alltime = st.tabs(["📅 Current Year", "📜 All-Time"])

with tab_cy:
    # Set up our 3-column layout with specific ratios
    col1, col2, col3 = st.columns([1, 1.5, 2])

    # --- COLUMN 1: SUMMARIES ---
    with col1:
        st.markdown("### CY Standings")
        standings = cy_df.groupby('fantasyplayer')['fantasypoints'].sum().reset_index()
        standings = standings.sort_values('fantasypoints', ascending=False)
        st.dataframe(
            standings.style.background_gradient(cmap='RdYlGn', subset=['fantasypoints']),
            hide_index=True, use_container_width=True
        )

        st.markdown("### Best Countries")
        country_pts = cy_df.groupby('team')['fantasypoints'].sum().reset_index().sort_values('fantasypoints')
        fig_bar = px.bar(country_pts, x='fantasypoints', y='team', orientation='h', 
                         template="plotly_white", color_discrete_sequence=['#1f77b4'])
        fig_bar.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### % Points Drafted")
        draft_split = cy_df.groupby('draft_type')['fantasypoints'].sum().reset_index()
        fig_pie = px.pie(draft_split, values='fantasypoints', names='draft_type', hole=0.4)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- COLUMN 2: TRENDS & TOURNAMENTS ---
    with col2:
        st.markdown("### CY Standings Over Time")
        # Ensure data is sorted by game for the line chart
        line_data = cy_df.sort_values('game_id')
        line_data['cumulative_pts'] = line_data.groupby('fantasyplayer')['fantasypoints'].cumsum()
        fig_line = px.line(line_data, x='game_id', y='cumulative_pts', color='fantasyplayer', markers=True)
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("### CY Best Tournaments")
        # Summing points per player for the year
        best_tourney = cy_df.groupby(['name', 'team', 'fantasyplayer'])['fantasypoints'].sum().reset_index()
        best_tourney = best_tourney.sort_values('fantasypoints', ascending=False)
        st.dataframe(best_tourney, height=500, use_container_width=True, hide_index=True)

    # --- COLUMN 3: HIERARCHICAL DETAIL ---
    with col3:
        st.markdown("### CY Standings - Detail")
        # Grouping by Manager to create the "Hierarchical" look
        managers = standings['fantasyplayer'].tolist()
        
        for manager in managers:
            # Create an expander for each manager, set to True for "Expanded by default"
            with st.expander(f"👤 {manager}", expanded=True):
                manager_data = cy_df[cy_df['fantasyplayer'] == manager].copy()
                # Aggregate points per player within the manager's group
                player_detail = manager_data.groupby(['name', 'team', 'draft_type'])['fantasypoints'].sum().reset_index()
                player_detail = player_detail.sort_values('fantasypoints', ascending=False)
                
                st.dataframe(player_detail, use_container_width=True, hide_index=True)

with tab_alltime:
    st.info("The All-Time tab will go here once we map out the layout!")