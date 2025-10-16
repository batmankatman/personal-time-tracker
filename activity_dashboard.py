#!/usr/bin/env python3
"""
Activity Dashboard - Personal Time Tracking Analysis
Based on diaw.txt data format analysis from activity_analysis.ipynb

A comprehensive dashboard for analyzing personal daily activity tracking data
with interactive visualizations, time allocation analysis, and pattern recognition.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime, timedelta
from collections import defaultdict
import os

# Configure Streamlit page
st.set_page_config(
    page_title="Personal Time Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to increase text size and reduce spacing
st.markdown("""
    <style>
    /* Increase base font size */
    html, body, [class*="css"] {
        font-size: 16px !important;
    }
    
    /* Reduce vertical spacing between elements */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Reduce spacing in columns */
    [data-testid="column"] {
        padding: 0.5rem 0.5rem !important;
    }
    
    /* Tighten up markdown spacing */
    .stMarkdown {
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce chart margins */
    .js-plotly-plot {
        margin-bottom: 0.5rem !important;
    }
    
    /* Tighten radio button spacing */
    .stRadio > div {
        gap: 0.3rem !important;
    }
    
    /* Reduce spacing in sidebar */
    .css-1d391kg, [data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Further reduce sidebar top padding */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        gap: 0.1rem !important;
    }
    
    /* Reduce sidebar header spacing */
    [data-testid="stSidebar"] h4 {
        margin-top: 0 !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Make headers more compact */
    h1, h2, h3, h4, h5 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Reduce gap between metric label and value */
    [data-testid="stMetric"] {
        gap: 0.2rem !important;
    }
    
    /* Make text inputs more compact */
    .stTextInput > div {
        margin-bottom: 0.3rem !important;
    }
    
    /* Reduce selectbox spacing */
    .stSelectbox > div {
        margin-bottom: 0.3rem !important;
    }
    
    /* Reduce multiselect spacing */
    .stMultiSelect > div {
        margin-bottom: 0.3rem !important;
    }
    
    /* Tighten checkbox spacing */
    .stCheckbox {
        margin-bottom: 0.1rem !important;
        margin-top: 0.1rem !important;
    }
    
    /* Make dividers thinner with less margin */
    hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Make select_slider track thicker */
    .stSlider > div > div > div {
        height: 8px !important;
    }
    
    /* Make select_slider thumb bigger */
    .stSlider > div > div > div > div {
        width: 20px !important;
        height: 20px !important;
    }
    
    /* Compact Statistical Summaries - ULTRA tight spacing */
    .compact-stats {
        max-height: 380px !important;
        overflow-y: auto !important;
    }
    
    .compact-stats * {
        font-size: 0.65rem !important;
        line-height: 1.1 !important;
    }
    
    .compact-stats [data-testid="stMetric"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 0 0.1rem 0 !important;
        gap: 0 !important;
        min-height: 0 !important;
    }
    
    .compact-stats [data-testid="stMetricLabel"] {
        font-size: 0.5rem !important;
        font-weight: 500 !important;
        color: #666 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .compact-stats [data-testid="stMetricValue"] {
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        line-height: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .compact-stats [data-testid="stMetricDelta"] {
        font-size: 0.45rem !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .compact-stats h4 {
        font-size: 0.65rem !important;
        margin: 0.15rem 0 0.05rem 0 !important;
        padding: 0 !important;
        font-weight: 700 !important;
        line-height: 1 !important;
    }
    
    .compact-stats h5 {
        font-size: 0.7rem !important;
        margin: 0 0 0.15rem 0 !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    
    .compact-stats hr {
        margin: 0.15rem 0 !important;
        padding: 0 !important;
        border-width: 0.5px !important;
        border-top: 0.5px solid #ddd !important;
    }
    
    .compact-stats [data-testid="column"] {
        padding: 0 0.15rem !important;
        gap: 0 !important;
    }
    
    .compact-stats .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Activity categories mapping (from analysis notebook)
ACTIVITY_CATEGORIES = {
    'P': 'Productive',
    'R': 'Routine', 
    'E': 'Eat',
    'S': 'Social',
    'W': 'Workout',
    'F': 'Fun',
    'GOD': 'God',
    'LO': 'Sleep'
}

# Diverse orange-to-purple palette (7 distinct colors)
FALL_COLORS = {
    'P': '#D84315',    # Productive - Deep Orange
    'R': '#FF9800',    # Routine - Orange  
    'E': '#FFC107',    # Eat - Amber
    'S': '#9C27B0',    # Social - Purple
    'W': '#673AB7',    # Workout - Deep Purple
    'F': '#FF6F00',    # Fun - Dark Orange
    'GOD': '#4A148C',  # God - Very Deep Purple
    'LO': '#7B1FA2'    # Sleep - Dark Purple
}

@st.cache_data
def load_and_parse_data(file_content):
    """
    Parse the diaw.txt data format into structured DataFrames.
    
    CORRECT INTERPRETATION:
    - Activities are listed in REVERSE chronological order (latest first, earliest last)
    - Duration = (next activity's timestamp) - (current activity's timestamp)
    - After reversing to chronological order, calculate duration to next activity
    - 'lo' (lights out) marks end of day and is excluded from duration calculations
    - Days are tracked by waking hours, not calendar days
    """
    
    def parse_day_header(line):
        """Parse day header: M/D/YY DayOfWeek StartTime-EndTime"""
        pattern = r'(\d{1,2}/\d{1,2}/\d{2})\s+(\w+)\s+(\d{4})-(\d{4})'
        match = re.match(pattern, line.strip())
        
        if match:
            date_str, day_of_week, start_time, end_time = match.groups()
            return {
                'date': date_str,
                'day_of_week': day_of_week,
                'start_time': start_time,
                'end_time': end_time
            }
        return None
    
    def parse_activity_record(line):
        """Parse activity record: HHMM Category Description"""
        parts = line.strip().split(' ', 2)
        if len(parts) >= 2:
            time_str = parts[0]
            category = parts[1]
            description = parts[2] if len(parts) > 2 else ''
            
            if len(time_str) == 4 and time_str.isdigit():
                return {
                    'time': time_str,
                    'category': category,
                    'description': description
                }
        return None
    
    def time_to_minutes(time_str):
        """Convert HHMM format to minutes since midnight"""
        if len(time_str) != 4 or not time_str.isdigit():
            return None
        hours = int(time_str[:2])
        minutes = int(time_str[2:])
        if hours >= 24 or minutes >= 60:
            return None
        return hours * 60 + minutes
    
    def parse_date(date_str):
        """Parse M/D/YY format to datetime"""
        try:
            month, day, year = date_str.split('/')
            year = int(year)
            if year < 50:
                year += 2000
            else:
                year += 1900
            return datetime(year, int(month), int(day))
        except:
            return None
    
    # Parse the data
    lines = file_content.strip().split('\n')
    days_data = []
    current_day = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        day_header = parse_day_header(line)
        if day_header:
            if current_day is not None:
                days_data.append(current_day)
            
            current_day = {
                'date': day_header['date'],
                'day_of_week': day_header['day_of_week'],
                'start_time': day_header['start_time'],
                'end_time': day_header['end_time'],
                'activities': []
            }
        elif current_day is not None:
            activity = parse_activity_record(line)
            if activity:
                current_day['activities'].append(activity)
    
    if current_day is not None:
        days_data.append(current_day)
    
    # CORRECT DURATION CALCULATION
    # Activities are listed in reverse chronological order, so we need to:
    # 1. Reverse them to get chronological order
    # 2. Calculate duration as (next_activity_time - current_activity_time)
    # 3. Exclude 'lo' (lights out) as it's just an end marker
    
    for day in days_data:
        day['parsed_date'] = parse_date(day['date'])
        activities = day['activities'].copy()
        
        # Reverse to get chronological order (earliest first)
        activities.reverse()
        
        # Calculate durations
        for i in range(len(activities) - 1):
            curr_activity = activities[i]
            next_activity = activities[i + 1]
            
            # Get time in minutes
            curr_minutes = time_to_minutes(curr_activity['time'])
            next_minutes = time_to_minutes(next_activity['time'])
            
            if curr_minutes is None or next_minutes is None:
                activities[i]['duration_minutes'] = None
                activities[i]['duration_hours'] = 0
                continue
            
            # Handle times that cross midnight
            if next_minutes < curr_minutes:
                next_minutes += 24 * 60
            
            duration = next_minutes - curr_minutes
            activities[i]['duration_minutes'] = duration
            activities[i]['duration_hours'] = duration / 60 if duration else 0
        
        # Last activity (should be 'lo' or similar end marker) gets no duration
        if activities:
            activities[-1]['duration_minutes'] = None
            activities[-1]['duration_hours'] = 0
        
        day['activities'] = activities
    
    # Create activities DataFrame
    # EXCLUDE 'lo' (lights out) activities as they are just end markers
    activities_data = []
    for day in days_data:
        for activity in day['activities']:
            # Skip 'lo' activities (lights out - end of day marker)
            if activity['description'].lower() == 'lo':
                continue
            
            # Skip activities with no duration (like the last activity of each day)
            if activity.get('duration_minutes') is None or activity.get('duration_minutes') == 0:
                continue
            
            activities_data.append({
                'date': day['date'],
                'parsed_date': day['parsed_date'],
                'day_of_week': day['day_of_week'],
                'start_time': day['start_time'],
                'end_time': day['end_time'],
                'activity_time': activity['time'],
                'category': activity['category'],
                'category_name': ACTIVITY_CATEGORIES.get(activity['category'], 'Unknown'),
                'description': activity['description'],
                'duration_minutes': activity.get('duration_minutes'),
                'duration_hours': activity.get('duration_hours', 0)
            })
    
    activities_df = pd.DataFrame(activities_data)
    
    # Calculate sleep data
    sleep_data = []
    days_sorted = sorted([d for d in days_data if d['parsed_date']], 
                        key=lambda x: x['parsed_date'])
    
    for i in range(len(days_sorted) - 1):
        current_day = days_sorted[i]
        next_day = days_sorted[i + 1]
        
        current_end = time_to_minutes(current_day['end_time'])
        next_start = time_to_minutes(next_day['start_time'])
        
        if current_end is not None and next_start is not None:
            if next_start < current_end:
                sleep_duration = (next_start + 1440) - current_end
            else:
                sleep_duration = next_start - current_end
            
            sleep_data.append({
                'current_date': current_day['date'],
                'next_date': next_day['date'],
                'sleep_duration_hours': sleep_duration / 60
            })
    
    sleep_df = pd.DataFrame(sleep_data)
    
    # Add parsed date column for filtering
    if not sleep_df.empty:
        sleep_df['sleep_start_date'] = pd.to_datetime(sleep_df['current_date'], format='%m/%d/%y')
    
    return activities_df, sleep_df, days_data

def create_category_summary(activities_df):
    """Create category summary statistics"""
    category_stats = {}
    
    for category in ACTIVITY_CATEGORIES.keys():
        category_data = activities_df[activities_df['category'] == category]
        if not category_data.empty:
            durations = category_data['duration_hours'].dropna()
            category_stats[category] = {
                'category_name': ACTIVITY_CATEGORIES[category],
                'total_hours': durations.sum(),
                'total_count': len(category_data),
                'avg_duration_hours': durations.mean() if len(durations) > 0 else 0,
                'median_duration_hours': durations.median() if len(durations) > 0 else 0
            }
        else:
            category_stats[category] = {
                'category_name': ACTIVITY_CATEGORIES[category],
                'total_hours': 0,
                'total_count': 0,
                'avg_duration_hours': 0,
                'median_duration_hours': 0
            }
    
    return pd.DataFrame(category_stats).T

def main():
    # Title with cool gradient effect - compact version
    st.markdown("""
        <h1 style='text-align: center;
                   font-size: 2.2em;
                   font-weight: bold;
                   margin-top: 0;
                   margin-bottom: 0.3em;'>
            <span style='background: linear-gradient(90deg, #D84315 0%, #FF9800 25%, #9C27B0 75%, #4A148C 100%);
                         -webkit-background-clip: text;
                         -webkit-text-fill-color: transparent;
                         background-clip: text;'>Personal Time Tracker</span>
            <span style='color: white; font-size: 0.5em; font-weight: normal; font-style: italic;'> for analytical and operational insights on behalf of Type A Personalities</span>
        </h1>
    """, unsafe_allow_html=True)
    
    # Automatically load diaw.txt
    default_file = "diaw.txt"
    if os.path.exists(default_file):
        with open(default_file, 'r') as f:
            file_content = f.read()
    else:
        file_content = None
    
    if file_content:
        # Load and parse data
        with st.spinner('🔄 Parsing activity data...'):
            activities_df, sleep_df, days_data = load_and_parse_data(file_content)
        
        # Use all data without filters, but exclude sleep (LO) category from main visualizations
        filtered_df = activities_df[activities_df['category'] != 'LO']
        
        # ========== SIDEBAR ==========
        with st.sidebar:
            # Week Pair Filter - Using select_slider with thicker styling
            st.markdown("#### Week Pair Selection")
            week_pair_options = ["All", "Weeks 1-2", "Weeks 3-4", "Weeks 5-6", "Weeks 7-8"]
            selected_week_pair = st.select_slider(
                "Select week pair to analyze",
                options=week_pair_options,
                value="All",
                key="week_pair_filter",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Category Filter with individual checkboxes
            st.markdown("#### Category Filter")
            
            category_options_list = [k for k in ACTIVITY_CATEGORIES.keys() if k != 'LO']
            
            # Individual checkboxes for each category
            selected_categories = []
            for cat in category_options_list:
                if st.checkbox(f"{ACTIVITY_CATEGORIES[cat]} ({cat})", value=True, key=f"cat_check_{cat}"):
                    selected_categories.append(cat)
            
            st.markdown("---")
            
            # Activity Browser
            st.markdown("#### Activity Browser")
            
            # Search box
            search_query = st.text_input(
                "🔍 Search activities",
                placeholder="Type to search...",
                key="activity_search"
            )
            
            # Category selector for activity browser
            browser_category = st.selectbox(
                "Select category to browse",
                options=category_options_list,
                format_func=lambda x: f"{ACTIVITY_CATEGORIES[x]} ({x})",
                key="browser_category"
            )
            
            # Filter and display activities
            if browser_category:
                category_activities = filtered_df[filtered_df['category'] == browser_category].copy()
                
                if not category_activities.empty:
                    # Group by description and count
                    activity_counts = category_activities.groupby('description').agg({
                        'duration_hours': ['sum', 'count']
                    }).reset_index()
                    activity_counts.columns = ['Activity', 'Total Hours', 'Count']
                    activity_counts = activity_counts.sort_values('Count', ascending=False)
                    
                    # Apply search filter
                    if search_query:
                        activity_counts = activity_counts[
                            activity_counts['Activity'].str.contains(search_query, case=False, na=False)
                        ]
                    
                    # Display in scrollable container
                    st.markdown(f"**{len(activity_counts)} activities found**")
                    
                    # Create a scrollable display
                    for idx, row in activity_counts.iterrows():
                        st.text(f"• {row['Activity'][:40]}{'...' if len(row['Activity']) > 40 else ''}")
                        st.caption(f"   Count: {int(row['Count'])} | Hours: {row['Total Hours']:.1f}h")
                else:
                    st.info(f"No activities in {ACTIVITY_CATEGORIES[browser_category]}")
        
        
        # Category distribution, Interesting Data, and Mini Weekly Distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### Time Distribution by Category")
            # Toggle for pie chart vs histogram
            view_type = st.radio(
                "",
                options=["Pie Chart", "Histogram"],
                horizontal=True,
                key="time_dist_toggle",
                label_visibility="collapsed"
            )
            
            if not filtered_df.empty:
                # Filter by selected week pair
                display_df = filtered_df.copy()
                if selected_week_pair != "All" and 'parsed_date' in display_df.columns:
                    sorted_dates = display_df[display_df['parsed_date'].notna()].sort_values('parsed_date')
                    unique_dates = sorted_dates['parsed_date'].dt.date.unique()
                    
                    # Create weeks
                    weeks = []
                    for i in range(0, len(unique_dates), 7):
                        week_dates = unique_dates[i:i+7]
                        if len(week_dates) > 0:
                            weeks.append(week_dates)
                    
                    # Get week pair indices
                    pair_map = {
                        "Weeks 1-2": [0, 1],
                        "Weeks 3-4": [2, 3],
                        "Weeks 5-6": [4, 5],
                        "Weeks 7-8": [6, 7]
                    }
                    week_indices = pair_map.get(selected_week_pair, [0, 1])
                    selected_dates = []
                    for idx in week_indices:
                        if idx < len(weeks):
                            selected_dates.extend(weeks[idx])
                    
                    if selected_dates:
                        display_df = display_df[display_df['parsed_date'].dt.date.isin(selected_dates)]
                
                category_totals = display_df.groupby('category')['duration_hours'].sum().reset_index()
                category_totals['category_name'] = category_totals['category'].map(ACTIVITY_CATEGORIES)
                
                if view_type == "Pie Chart":
                    fig = px.pie(
                        category_totals, 
                        values='duration_hours', 
                        names='category_name',
                        title="",
                        color='category',
                        color_discrete_map=FALL_COLORS
                    )
                    fig.update_layout(height=280, margin=dict(t=0, b=10, l=10, r=10))
                    fig.update_traces(
                        textposition='inside', 
                        textinfo='percent+label',
                        hovertemplate='<b>%{label}</b><br>%{value:.2f} hours<extra></extra>'
                    )
                else:  # Histogram
                    fig = px.bar(
                        category_totals,
                        x='category_name',
                        y='duration_hours',
                        title="",
                        color='category',
                        color_discrete_map=FALL_COLORS
                    )
                    fig.update_layout(height=280, xaxis_title="Category", yaxis_title="Hours", 
                                    margin=dict(t=0, b=10, l=10, r=10), showlegend=False)
                    fig.update_traces(
                        hovertemplate='<b>%{x}</b><br>%{y:.2f} hours<extra></extra>'
                    )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Weekly Trend")
            
            # Mini weekly activity distribution - line plot with bigger points and thicker lines
            if not filtered_df.empty and filtered_df['parsed_date'].notna().any():
                # Group data into 7-day periods
                sorted_dates = filtered_df[filtered_df['parsed_date'].notna()].sort_values('parsed_date')
                unique_dates = sorted_dates['parsed_date'].dt.date.unique()
                
                # Create weeks
                weeks = []
                for i in range(0, len(unique_dates), 7):
                    week_dates = unique_dates[i:i+7]
                    if len(week_dates) > 0:
                        weeks.append({
                            'week_num': len(weeks) + 1,
                            'start_date': week_dates[0],
                            'end_date': week_dates[-1],
                            'dates': week_dates
                        })
                
                if weeks and len(weeks) >= 2:
                    # Filter based on selected week pair
                    if selected_week_pair == "All":
                        analysis_weeks = weeks
                    else:
                        pair_map = {
                            "Weeks 1-2": [0, 1],
                            "Weeks 3-4": [2, 3],
                            "Weeks 5-6": [4, 5],
                            "Weeks 7-8": [6, 7]
                        }
                        week_indices = pair_map.get(selected_week_pair, [0, 1])
                        analysis_weeks = [weeks[i] for i in week_indices if i < len(weeks)]
                    
                    # Calculate 14-day averages
                    mini_weekday_data = []
                    weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    
                    for category in selected_categories:
                        cat_data = filtered_df[filtered_df['category'] == category]
                        
                        for day_idx in range(7):
                            day_hours = []
                            
                            for week in analysis_weeks:
                                if day_idx < len(week['dates']):
                                    day_date = week['dates'][day_idx]
                                    day_activities = cat_data[cat_data['parsed_date'].dt.date == day_date]
                                    day_total = day_activities['duration_hours'].sum()
                                    day_hours.append(day_total)
                            
                            avg_hours = np.mean(day_hours) if day_hours else 0
                            
                            mini_weekday_data.append({
                                'weekday': weekday_names[day_idx],
                                'day_idx': day_idx,
                                'category': category,
                                'category_name': ACTIVITY_CATEGORIES[category],
                                'avg_hours': avg_hours
                            })
                    
                    mini_weekday_df = pd.DataFrame(mini_weekday_data)
                    
                    # Create line plot with bigger markers and thicker lines
                    fig = px.line(
                        mini_weekday_df,
                        x='weekday',
                        y='avg_hours',
                        color='category_name',
                        title="",
                        markers=True,
                        color_discrete_map={ACTIVITY_CATEGORIES[k]: v for k, v in FALL_COLORS.items()}
                    )
                    
                    # Update traces with color squares in hover
                    for trace in fig.data:
                        trace_color = trace.line.color if hasattr(trace, 'line') else '#000000'
                        trace.update(
                            line=dict(width=4),
                            marker=dict(size=12),
                            hovertemplate=f'<span style="color:{trace_color};">■</span> <b>%{{fullData.name}}</b><br>%{{y:.2f}} hours<extra></extra>'
                        )
                    
                    fig.update_layout(
                        height=380,
                        xaxis_title="",
                        yaxis_title="Avg Hours",
                        margin=dict(t=0, b=10, l=10, r=10),
                        showlegend=False,
                        hovermode='x'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Need data")
            else:
                st.info("No data")
        
        with col3:
            week_indicator = f" ({selected_week_pair})" if selected_week_pair != "All" else ""
            
            # Build stats as pure HTML in a fixed-height container
            if not filtered_df.empty:
                # Helper function to filter data by week pair
                def filter_by_week_pair(df):
                    if selected_week_pair == "All":
                        return df
                    
                    if 'parsed_date' not in df.columns or not df['parsed_date'].notna().any():
                        return df
                    
                    sorted_dates = df[df['parsed_date'].notna()].sort_values('parsed_date')
                    unique_dates = sorted_dates['parsed_date'].dt.date.unique()
                    weeks = []
                    for i in range(0, len(unique_dates), 7):
                        week_dates = unique_dates[i:i+7]
                        if len(week_dates) > 0:
                            weeks.append(week_dates)
                    
                    pair_map = {"Weeks 1-2": [0, 1], "Weeks 3-4": [2, 3], "Weeks 5-6": [4, 5], "Weeks 7-8": [6, 7]}
                    week_indices = pair_map.get(selected_week_pair, [0, 1])
                    selected_dates = []
                    for idx in week_indices:
                        if idx < len(weeks):
                            selected_dates.extend(weeks[idx])
                    
                    if selected_dates:
                        return df[df['parsed_date'].dt.date.isin(selected_dates)]
                    return df
                
                # Filter main data by week pair for all statistics
                week_filtered_df = filter_by_week_pair(filtered_df)
                
                # Calculate all values with week filtering
                itsc_gen = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('itsc', na=False) & 
                                      ~week_filtered_df['description'].str.lower().str.contains('hw', na=False)]['duration_hours'].sum()
                itsc_hw = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('hw itsc', na=False)]['duration_hours'].sum()
                stat_gen = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('stat', na=False) & 
                                      ~week_filtered_df['description'].str.lower().str.contains('hw', na=False)]['duration_hours'].sum()
                stat_hw = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('hw stat', na=False)]['duration_hours'].sum()
                total_itsc = itsc_gen + itsc_hw
                total_stat = stat_gen + stat_hw
                
                # Notes analysis with proportion of Productivity
                notes_activities = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('notes', na=False)]
                total_notes_hours = notes_activities['duration_hours'].sum()
                productive_activities = week_filtered_df[week_filtered_df['category'] == 'P']
                total_productive_hours = productive_activities['duration_hours'].sum()
                notes_proportion = (total_notes_hours / total_productive_hours * 100) if total_productive_hours > 0 else 0
                
                # Communication analysis
                comm_activities = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('comm', na=False)]
                total_comm_hours = comm_activities['duration_hours'].sum()
                social_activities = week_filtered_df[week_filtered_df['category'] == 'S']
                total_social_hours = social_activities['duration_hours'].sum()
                comm_proportion = (total_comm_hours / total_social_hours * 100) if total_social_hours > 0 else 0
                
                # Walking activities - with week filtering
                walk_activities = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('walk', na=False)]
                total_walk_hours = walk_activities['duration_hours'].sum()
                
                # Multitasks calculation: 1/3 walking as communication, 1/4 as notes
                walk_as_comm = total_walk_hours / 3
                walk_as_notes = total_walk_hours / 4
                
                # Sleep - with week filtering
                filtered_sleep_df = None
                if not sleep_df.empty and filtered_df['parsed_date'].notna().any():
                    if 'sleep_start_date' not in sleep_df.columns:
                        sleep_df['sleep_start_date'] = pd.to_datetime(sleep_df['current_date'], format='%m/%d/%y', errors='coerce')
                    
                    if selected_week_pair != "All":
                        sorted_dates = filtered_df[filtered_df['parsed_date'].notna()].sort_values('parsed_date')
                        unique_dates = sorted_dates['parsed_date'].dt.date.unique()
                        weeks = []
                        for i in range(0, len(unique_dates), 7):
                            week_dates = unique_dates[i:i+7]
                            if len(week_dates) > 0:
                                weeks.append({'start_date': week_dates[0], 'end_date': week_dates[-1]})
                        
                        pair_map = {"Weeks 1-2": [0, 1], "Weeks 3-4": [2, 3], "Weeks 5-6": [4, 5], "Weeks 7-8": [6, 7]}
                        week_indices = pair_map.get(selected_week_pair, [0, 1])
                        selected_weeks = [weeks[i] for i in week_indices if i < len(weeks)]
                        
                        if selected_weeks and 'sleep_start_date' in sleep_df.columns:
                            start_date = min(w['start_date'] for w in selected_weeks)
                            end_date = max(w['end_date'] for w in selected_weeks)
                            filtered_sleep_df = sleep_df[
                                (sleep_df['sleep_start_date'].dt.date >= start_date) & 
                                (sleep_df['sleep_start_date'].dt.date <= end_date)
                            ]
                        else:
                            filtered_sleep_df = sleep_df
                    else:
                        filtered_sleep_df = sleep_df
                
                # Walking distance and calories - with week filtering
                tm_activities = week_filtered_df[week_filtered_df['description'].str.lower().str.contains('tm', na=False)]
                total_walk_hours_full = walk_activities['duration_hours'].sum() + tm_activities['duration_hours'].sum()
                total_distance_miles = total_walk_hours_full * 3
                total_calories = total_distance_miles * 130
                
                # Poop statistics - with week filtering
                poop_activities = week_filtered_df[
                    (week_filtered_df['category'] == 'R') & 
                    (week_filtered_df['description'].str.lower().str.contains('poop', na=False))
                ]
                avg_poop_minutes = poop_activities['duration_minutes'].mean() if not poop_activities.empty and 'duration_minutes' in poop_activities.columns else 0
                
                # Build ALL stats as pure HTML for complete control (increased font sizes further + extended height)
                html = '<div style="max-height: 450px; overflow-y: auto; font-size: 0.8rem; line-height: 1.35; padding: 0.3rem;">'
                html += f'<div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.4rem;">Quick Activity Stats{week_indicator}</div>'
                
                # Coursework
                html += '<div style="margin: 0.25rem 0;"><strong style="font-size: 0.88rem;">Coursework</strong></div>'
                if total_itsc > 0:
                    itsc_hw_ratio = (itsc_hw / total_itsc * 100)
                    html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>ITSC:</span><span><strong>{total_itsc:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">({itsc_hw_ratio:.0f}% is Homework)</span></span></div>'
                if total_stat > 0:
                    stat_hw_ratio = (stat_hw / total_stat * 100)
                    html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>STAT:</span><span><strong>{total_stat:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">({stat_hw_ratio:.0f}% is Homework)</span></span></div>'
                
                # Notes & Scheduling - week indicator on same line
                html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Notes & Scheduling</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>Total:</span><span><strong>{total_notes_hours:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">({notes_proportion:.0f}% of Productive)</span></span></div>'
                
                # Communication (Social) - week indicator on same line
                html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Communication (Social)</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>Texting:</span><span><strong>{total_comm_hours:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">({comm_proportion:.0f}% of Social)</span></span></div>'
                
                # Multitask Approximations - week indicator on same line
                html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Multitask Approximations</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span style="font-size: 0.75rem;">Walking + Texting:</span><span><strong>{walk_as_comm:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">(Approx 33% of all walking)</span></span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span style="font-size: 0.75rem;">Walking + Notes/Scheduling:</span><span><strong>{walk_as_notes:.1f}h</strong> <span style="color: #888; font-size: 0.72rem;">(Approx 25% of all walking)</span></span></div>'
                
                # Sleep - week indicator on same line
                if filtered_sleep_df is not None and not filtered_sleep_df.empty:
                    html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                    html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Sleep</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                    avg_sleep = filtered_sleep_df['sleep_duration_hours'].mean()
                    min_sleep = filtered_sleep_df['sleep_duration_hours'].min()
                    max_sleep = filtered_sleep_df['sleep_duration_hours'].max()
                    html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>Night Average:</span><strong>{avg_sleep:.1f}h</strong></div>'
                    html += f'<div style="margin: 0.15rem 0; font-size: 0.72rem; color: #888;">Range: {min_sleep:.1f}-{max_sleep:.1f}h</div>'
                
                # Walking Activity - week indicator on same line
                html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Walking</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>Distance:</span><strong>{total_distance_miles:.1f}mi</strong></div>'
                html += f'<div style="margin: 0.15rem 0; font-size: 0.72rem; color: #888;">{total_calories:.0f} cal burned</div>'
                
                # Fast Fecal Facts - week indicator on same line
                html += '<hr style="margin: 0.35rem 0; border: none; border-top: 1px solid #ddd;">'
                html += f'<div style="margin: 0.25rem 0; display: flex; justify-content: space-between; align-items: center;"><strong style="font-size: 0.88rem;">Fecal Facts</strong><span style="font-size: 0.88rem; color: #666;">{week_indicator}</span></div>'
                html += f'<div style="margin: 0.15rem 0; display: flex; justify-content: space-between;"><span>Average Duration:</span><strong>{avg_poop_minutes:.1f}min</strong></div>'
                
                html += '</div>'
                
                st.markdown(html, unsafe_allow_html=True)
        
        
        # Weekly Activity Distribution (Stacked Bar Chart)
        if not filtered_df.empty and filtered_df['parsed_date'].notna().any():
            # Get all unique dates and sort them chronologically
            sorted_dates = filtered_df[filtered_df['parsed_date'].notna()].sort_values('parsed_date')
            unique_dates = sorted(sorted_dates['parsed_date'].dt.date.unique())
            
            # Identify 14-day consecutive spans based on gaps
            # A new span starts when there's a gap of more than 30 days between dates
            spans_14day = []
            current_span = []
            
            for i, date in enumerate(unique_dates):
                if not current_span:
                    current_span.append(date)
                else:
                    # Check if this date is close to the last date (within 2 days for safety)
                    last_date = current_span[-1]
                    delta = (date - last_date).days
                    
                    if delta <= 2:  # Consecutive or very close
                        current_span.append(date)
                    else:  # Gap detected - start new span
                        if len(current_span) >= 14:
                            # Only keep the first 14 days of this span
                            spans_14day.append(current_span[:14])
                        current_span = [date]
            
            # Don't forget the last span
            if len(current_span) >= 14:
                spans_14day.append(current_span[:14])
            
            if spans_14day:
                # Map week pair selections to 14-day span indices
                if selected_week_pair == "All":
                    analysis_spans = spans_14day
                    date_range = "All Data"
                else:
                    pair_map = {
                        "Weeks 1-2": 0,
                        "Weeks 3-4": 1,
                        "Weeks 5-6": 2,
                        "Weeks 7-8": 3
                    }
                    span_idx = pair_map.get(selected_week_pair, 0)
                    if span_idx < len(spans_14day):
                        analysis_spans = [spans_14day[span_idx]]
                        # Get date range for title
                        start_date_str = analysis_spans[0][0].strftime('%m/%d/%y')
                        end_date_str = analysis_spans[0][-1].strftime('%m/%d/%y')
                        date_range = f"{start_date_str} - {end_date_str}"
                    else:
                        analysis_spans = []
                        date_range = "No Data"
                
                # Display title with date range
                st.markdown(f"##### Activity Distribution<span style='color: #555; font-size: 0.8em;'> {date_range}</span>", unsafe_allow_html=True)
                
                if analysis_spans:
                    # Calculate averages for each day of the week across the 14-day span(s)
                    # Group by day of week and average across all matching days
                    weekday_data = []
                    weekday_totals = {}  # To store total hours per day of week for hover
                    weekday_names_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
                    
                    for category in selected_categories:
                        cat_data = filtered_df[filtered_df['category'] == category]
                        
                        # For each day of week (0=Monday, 6=Sunday)
                        for dow in range(7):
                            day_hours_list = []
                            
                            # Collect all days matching this day of week from all analysis spans
                            for span in analysis_spans:
                                for date in span:
                                    if date.weekday() == dow:
                                        day_activities = cat_data[cat_data['parsed_date'].dt.date == date]
                                        day_total = day_activities['duration_hours'].sum()
                                        day_hours_list.append(day_total)
                            
                            # Calculate average for this day of week
                            avg_hours = np.mean(day_hours_list) if day_hours_list else 0
                            
                            # Track total for this day of week
                            weekday_name = weekday_names_map[dow]
                            if weekday_name not in weekday_totals:
                                weekday_totals[weekday_name] = 0
                            weekday_totals[weekday_name] += avg_hours
                            
                            weekday_data.append({
                                'weekday': weekday_name,
                                'day_of_week': dow,
                                'category': category,
                                'category_name': ACTIVITY_CATEGORIES[category],
                                'avg_hours': avg_hours
                            })
                    
                    # Create DataFrame
                    weekday_df = pd.DataFrame(weekday_data)
                    
                    # Sort by day of week to ensure proper order
                    weekday_df = weekday_df.sort_values('day_of_week')
                    
                    # Add total hours to each row for hover display
                    weekday_df['day_total'] = weekday_df['weekday'].map(weekday_totals)
                    
                    # Create stacked bar chart (no title in chart itself)
                    fig = px.bar(
                        weekday_df,
                        x='weekday',
                        y='avg_hours',
                        color='category_name',
                        title="",
                        color_discrete_map={ACTIVITY_CATEGORIES[k]: v for k, v in FALL_COLORS.items()},
                        barmode='stack',
                        custom_data=['day_total']
                    )
                    
                    fig.update_layout(
                        height=300,
                        xaxis_title="",  # Remove x-axis label
                        yaxis_title="Average Hours",
                        margin=dict(t=0, b=10, l=10, r=10),
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.25,
                            xanchor="center",
                            x=0.5,
                            title=""
                        ),
                        hovermode='x unified'
                    )
                    
                    # Add hover information - simplified
                    fig.update_traces(
                        hovertemplate='<b>%{fullData.name}</b><br>%{y:.2f} hours<extra></extra>'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for selected week pair.")
            else:
                st.info("Need at least 14 consecutive days of data for analysis.")
        
        # # Activity Detail Viewer by Category
        # if not filtered_df.empty:
        #     st.markdown("##### Activity Details by Category")
        #     # Exclude sleep (LO) from category selector
        #     category_options = [k for k in ACTIVITY_CATEGORIES.keys() if k != 'LO']
        #     selected_category = st.selectbox(
        #         "Select Category",
        #         options=category_options,
        #         format_func=lambda x: f"{ACTIVITY_CATEGORIES[x]} ({x})",
        #         key="category_selector"
        #     )
        #     
        #     # Get activities for selected category
        #     category_activities = filtered_df[filtered_df['category'] == selected_category].copy()
        #     
        #     if not category_activities.empty:
        #         # Group by description and sum hours
        #         activity_summary = category_activities.groupby('description')['duration_hours'].agg(['sum', 'count']).reset_index()
        #         activity_summary.columns = ['Activity', 'Total Hours', 'Count']
        #         activity_summary = activity_summary.sort_values('Total Hours', ascending=False)
        #         
        #         # Pagination for activities if too many
        #         items_per_page = 10
        #         total_items = len(activity_summary)
        #         total_pages = (total_items + items_per_page - 1) // items_per_page
        #         
        #         if total_pages > 1:
        #             col1, col2, col3 = st.columns([1, 3, 1])
        #             with col2:
        #                 page = st.select_slider(
        #                     "Page",
        #                     options=list(range(1, total_pages + 1)),
        #                     key="activity_page"
        #                 )
        #                 # Pagination dots
        #                 dots = "".join(["🔵" if i == page else "⚪" for i in range(1, min(total_pages + 1, 11))])
        #                 st.markdown(f"<div style='text-align: center'>{dots}</div>", unsafe_allow_html=True)
        #         else:
        #             page = 1
        #         
        #         # Display paginated activities
        #         start_idx = (page - 1) * items_per_page
        #         end_idx = start_idx + items_per_page
        #         page_activities = activity_summary.iloc[start_idx:end_idx]
        #         
        #         # Display as a bar chart
        #         fig = px.bar(
        #             page_activities,
        #             x='Total Hours',
        #             y='Activity',
        #             orientation='h',
        #             title=f"{ACTIVITY_CATEGORIES[selected_category]} Activities (Page {page}/{total_pages})",
        #             color='Total Hours',
        #             color_continuous_scale='Viridis'
        #         )
        #         fig.update_layout(
        #             height=min(350, len(page_activities) * 40 + 100),
        #             margin=dict(t=40, b=20, l=20, r=20),
        #             yaxis={'categoryorder': 'total ascending'}
        #         )
        #         st.plotly_chart(fig, use_container_width=True)
        #         
        #         # Show summary stats
        #         col1, col2, col3 = st.columns(3)
        #         with col1:
        #             st.metric("Total Hours", f"{activity_summary['Total Hours'].sum():.1f}h")
        #         with col2:
        #             st.metric("Total Activities", len(activity_summary))
        #         with col3:
        #             st.metric("Avg Hours/Activity", f"{activity_summary['Total Hours'].mean():.1f}h")
        #     else:
        #         st.info(f"No activities found for {ACTIVITY_CATEGORIES[selected_category]}")
    
    else:
        st.error("⚠️ diaw.txt file not found. Please ensure the file exists in the current directory.")

if __name__ == "__main__":
    main()
