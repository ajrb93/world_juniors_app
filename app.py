import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIG & COMPACT STYLING ---
st.set_page_config(layout="wide", page_title="WJC Fantasy")

# CUSTOM CSS: Shrinks headers, table padding, and overall container gaps
st.markdown("""
    <style>
    /* Reduce top/side margins */
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    
    /* Shrink Header sizes */
    h1 { font-size: 22px !important; margin-bottom: 0.2rem !important; }
    h3 { font-size: 16px !important; margin-top: 0.5rem !important; margin-bottom: 0.3rem !important; }
    
    /* Global font size for Dataframes */
    .stDataFrame div { font-size: 11px !important; }
    
    /* Condense Expander headers */
    div[data-testid="stExpander"] div[role="button"] p { font-size: 13px !important; font-weight: bold; }
    
    /* Reduce gap between elements */
    [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
    </style>
    """, unsafe_allow_html=True)

# COUNTRY HEX CODES
COUNTRY_COLORS = {
    'Canada': '#EF3340', 'Sweden': '#FFCD00', 'USA': '#002868', 
    'Finland': '#003580', 'Czechia': '#11457E', 'Slovakia': '#003399',
    'Switzerland': '#DA291C', 'Germany': '#000000', 'Latvia': '#9E3039', 'Kazakhstan': '#00B1D8'
}

@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("data/dynamic/Final_Master_Dataset.csv")
    df['fantasypoints'] = pd.to_numeric(df['FP'], errors='coerce').fillna(0)
    # Fill NA to show "Undrafted" in the pie chart
    df['draft_type'] = df['draft_type'].fillna('Undrafted').replace({'':'Undrafted'})
    # Use requested shorthand
    df = df.rename(columns={'fantasypoints': 'FPoints', 'fantasyplayer': 'Draftee'})
    return df

df = load_and_clean_data()
cy_val = df['year'].max()
cy_df = df[df['year'] == cy_val].copy()

# Formatting Helper: 1 decimal for FPoints, 0 for the rest
fmt_dict = {'FPoints': '{:.1f}', 'goals': '{:.0f}', 'assists': '{:.0f}', 'gwg': '{:.0f}'}

# --- MAIN DASHBOARD ---
tab_cy, tab_alltime = st.tabs(["📅 Current Year", "📜 All-Time"])

with tab_cy:
    col1, col2, col3 = st.columns([1, 1.4, 2.2])

    # --- COLUMN 1: LEFT ---
    with col1:
        st.markdown("### Standings")
        standings = cy_df.groupby('Draftee')['FPoints'].sum().reset_index().sort_values('FPoints', ascending=False)
        st.dataframe(standings.style.format({'FPoints': '{:.1f}'}).background_gradient(cmap='RdYlGn', subset=['FPoints']), 
                     hide_index=True, use_container_width=True, height=180)

        st.markdown("### Countries")
        country_pts = cy_df.groupby('team')['FPoints'].sum().reset_index().sort_values('FPoints')
        fig_bar = px.bar(country_pts, x='FPoints', y='team', orientation='h', color='team', color_discrete_map=COUNTRY_COLORS)
        fig_bar.update_layout(showlegend=False, margin=dict(l=0,r=0,t=0,b=0), height=230, xaxis_title=None, yaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### % Drafted")
        fig_pie = px.pie(cy_df, values='FPoints', names='draft_type', hole=0.4)
        fig_pie.update_layout(margin=dict(l=0,r=0,t=20,b=0), height=180, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5))
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- COLUMN 2: MIDDLE ---
    with col2:
        st.markdown("### Standings Over Time")
        timeline = cy_df.groupby(['game_id', 'Draftee'])['FPoints'].sum().reset_index()
        timeline = timeline.sort_values('game_id')
        timeline['cum_pts'] = timeline.groupby('Draftee')['FPoints'].cumsum()
        
        fig_line = px.line(timeline, x='game_id', y='cum_pts', color='Draftee', markers=True)
        fig_line.update_layout(height=320, margin=dict(l=0,r=0,t=20,b=0), xaxis_title="Game ID", yaxis_title="Points")
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("### Best Tournaments")
        best_tourney = cy_df.groupby(['name', 'team', 'Draftee']).agg({
            'FPoints': 'sum', 'goals': 'sum', 'assists': 'sum', 'gwg': 'sum'
        }).reset_index().sort_values('FPoints', ascending=False)
        
        st.dataframe(best_tourney.style.format(fmt_dict), height=420, use_container_width=True, hide_index=True)

    # --- COLUMN 3: RIGHT ---
    with col3:
        st.markdown("### Standings - Detail")
        ordered_managers = standings['Draftee'].tolist()
        
        for manager in ordered_managers:
            manager_data = cy_df[cy_df['Draftee'] == manager]
            player_detail = manager_data.groupby(['name', 'team', 'draft_type']).agg({
                'FPoints': 'sum', 'goals': 'sum', 'assists': 'sum', 'gwg': 'sum'
            }).reset_index().sort_values('FPoints', ascending=False)
            
            pts_val = standings.loc[standings['Draftee']==manager, 'FPoints'].values[0]
            with st.expander(f"👤 {manager} | {pts_val:.1f} pts", expanded=True):
                st.dataframe(player_detail.style.format(fmt_dict), use_container_width=True, hide_index=True)

with tab_alltime:
    st.info("Ready for your All-Time layout specs!")