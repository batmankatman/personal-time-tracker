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
    initial_sidebar_state="collapsed"
)

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
    Based on parsing logic from activity_analysis.ipynb
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
    
    def calculate_duration_minutes(start_time, end_time):
        """Calculate duration handling day crossover"""
        start_mins = time_to_minutes(start_time)
        end_mins = time_to_minutes(end_time)
        
        if start_mins is None or end_mins is None:
            return None
        
        if end_mins < start_mins:
            duration = (end_mins + 1440) - start_mins
        else:
            duration = end_mins - start_mins
        
        return duration if duration >= 0 else None
    
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
    
    # Calculate durations and add parsed dates
    for day in days_data:
        day['parsed_date'] = parse_date(day['date'])
        activities = day['activities'].copy()
        
        for i in range(len(activities)):
            if i == len(activities) - 1:
                start_time = day['start_time']
                end_time = activities[i]['time']
                duration = calculate_duration_minutes(start_time, end_time)
            else:
                start_time = activities[i + 1]['time']
                end_time = activities[i]['time']
                duration = calculate_duration_minutes(start_time, end_time)
            
            activities[i]['duration_minutes'] = duration
            activities[i]['duration_hours'] = duration / 60 if duration else 0
        
        day['activities'] = activities
    
    # Create activities DataFrame
    activities_data = []
    for day in days_data:
        for activity in day['activities']:
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
    # Title with cool gradient effect
    st.markdown("""
        <h1 style='text-align: center; 
                   background: linear-gradient(90deg, #D84315 0%, #FF9800 25%, #9C27B0 75%, #4A148C 100%);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   font-size: 3em;
                   font-weight: bold;
                   margin-bottom: 0.5em;'>
            Personal Time Tracker
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
        
        # Category distribution with toggle and Interesting Data side-by-side
        col1, col2 = st.columns(2)
        
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
                category_totals = filtered_df.groupby('category')['duration_hours'].sum().reset_index()
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
                    fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                else:  # Histogram
                    fig = px.bar(
                        category_totals,
                        x='category_name',
                        y='duration_hours',
                        title="",
                        color='category',
                        color_discrete_map=FALL_COLORS
                    )
                    fig.update_layout(height=350, xaxis_title="Category", yaxis_title="Hours", 
                                    margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("##### Interesting Data")
            # Page selector for interesting data
            interesting_pages = ["Course Time", "Sleep Duration", "Poop Time"]
            interesting_page = st.radio(
                "",
                options=interesting_pages,
                horizontal=True,
                key="interesting_data_selector",
                label_visibility="collapsed"
            )
            
            if interesting_page == "Course Time":
                # Simplified course time distribution - just the pie chart
                course_patterns = {
                    'ITSC (General)': 'ITSC',
                    'ITSC Homework': 'hw ITSC',
                    'STAT (General)': 'STAT', 
                    'STAT Homework': 'hw STAT'
                }
                
                course_data = {}
                for pattern_name, pattern in course_patterns.items():
                    pattern_lower = pattern.lower()
                    matching_activities = filtered_df[
                        filtered_df['description'].str.lower().str.contains(pattern_lower, na=False)
                    ]
                    course_data[pattern_name] = matching_activities['duration_hours'].sum()
                
                course_df = pd.DataFrame(list(course_data.items()), columns=['Course', 'Hours'])
                course_df = course_df[course_df['Hours'] > 0]
                
                if not course_df.empty:
                    fig = px.pie(
                        course_df,
                        values='Hours',
                        names='Course',
                        title=""
                    )
                    fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No course data found.")
            
            elif interesting_page == "Sleep Duration":
                if not sleep_df.empty:
                    fig = px.histogram(
                        sleep_df,
                        x='sleep_duration_hours',
                        nbins=20,
                        title="",
                        color_discrete_sequence=['#7B1FA2']
                    )
                    fig.update_layout(xaxis_title="Sleep Hours", yaxis_title="Frequency", 
                                    height=350, margin=dict(t=20, b=20, l=20, r=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No sleep data.")
            
            elif interesting_page == "Poop Time":
                # Filter for poop activities (R category with "poop" in description)
                poop_activities = activities_df[
                    (activities_df['category'] == 'R') & 
                    (activities_df['description'].str.lower().str.contains('poop', na=False))
                ]
                
                if not poop_activities.empty and 'duration_minutes' in poop_activities.columns:
                    # Group by day of week and calculate average time
                    weekday_order = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'Su']
                    poop_by_weekday = poop_activities.groupby('day_of_week')['duration_minutes'].mean().reset_index()
                    poop_by_weekday.columns = ['weekday', 'avg_minutes']
                    
                    # Reorder by weekday
                    poop_by_weekday['weekday_cat'] = pd.Categorical(
                        poop_by_weekday['weekday'],
                        categories=weekday_order,
                        ordered=True
                    )
                    poop_by_weekday = poop_by_weekday.sort_values('weekday_cat')
                    
                    fig = px.bar(
                        poop_by_weekday,
                        x='weekday',
                        y='avg_minutes',
                        title="",
                        color='avg_minutes',
                        color_continuous_scale='Browns'
                    )
                    fig.update_layout(
                        height=350,
                        xaxis_title="Day of Week",
                        yaxis_title="Avg Minutes",
                        margin=dict(t=20, b=20, l=20, r=20),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No poop data found.")
        
        # Week-by-Week Carousel Viewer
        if not filtered_df.empty and filtered_df['parsed_date'].notna().any():
            # Group data into 7-day periods
            sorted_dates = filtered_df[filtered_df['parsed_date'].notna()].sort_values('parsed_date')
            unique_dates = sorted_dates['parsed_date'].dt.date.unique()
            
            # Create weeks (7-day periods)
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
            
            if weeks:
                # Week selector
                week_options = [f"Week {w['week_num']}: {w['start_date']} to {w['end_date']}" for w in weeks]
                selected_week_idx = st.select_slider(
                    "Select Week",
                    options=list(range(len(weeks))),
                    format_func=lambda x: week_options[x],
                    key="week_selector"
                )
                
                selected_week = weeks[selected_week_idx]
                
                # Filter data for selected week
                week_mask = filtered_df['parsed_date'].dt.date.isin(selected_week['dates'])
                week_data = filtered_df[week_mask]
                
                # Create stacked bar chart for the week
                week_daily = week_data.groupby(['parsed_date', 'category'])['duration_hours'].sum().reset_index()
                week_daily['category_name'] = week_daily['category'].map(ACTIVITY_CATEGORIES)
                week_daily['date_label'] = week_daily['parsed_date'].dt.strftime('%m/%d (%a)')
                
                fig = px.bar(
                    week_daily,
                    x='date_label',
                    y='duration_hours',
                    color='category_name',
                    title=f"Week {selected_week['week_num']} Activity Distribution",
                    color_discrete_map={ACTIVITY_CATEGORIES[k]: v for k, v in FALL_COLORS.items()},
                    text='duration_hours'
                )
                fig.update_traces(texttemplate='%{text:.1f}h', textposition='inside')
                fig.update_layout(
                    height=350, 
                    xaxis_title="Date", 
                    yaxis_title="Hours",
                    margin=dict(t=40, b=20, l=20, r=20),
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Activity Detail Viewer by Category
        if not filtered_df.empty:
            st.markdown("##### Activity Details by Category")
            # Exclude sleep (LO) from category selector
            category_options = [k for k in ACTIVITY_CATEGORIES.keys() if k != 'LO']
            selected_category = st.selectbox(
                "Select Category",
                options=category_options,
                format_func=lambda x: f"{ACTIVITY_CATEGORIES[x]} ({x})",
                key="category_selector"
            )
            
            # Get activities for selected category
            category_activities = filtered_df[filtered_df['category'] == selected_category].copy()
            
            if not category_activities.empty:
                # Group by description and sum hours
                activity_summary = category_activities.groupby('description')['duration_hours'].agg(['sum', 'count']).reset_index()
                activity_summary.columns = ['Activity', 'Total Hours', 'Count']
                activity_summary = activity_summary.sort_values('Total Hours', ascending=False)
                
                # Pagination for activities if too many
                items_per_page = 10
                total_items = len(activity_summary)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                
                if total_pages > 1:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        page = st.select_slider(
                            "Page",
                            options=list(range(1, total_pages + 1)),
                            key="activity_page"
                        )
                        # Pagination dots
                        dots = "".join(["🔵" if i == page else "⚪" for i in range(1, min(total_pages + 1, 11))])
                        st.markdown(f"<div style='text-align: center'>{dots}</div>", unsafe_allow_html=True)
                else:
                    page = 1
                
                # Display paginated activities
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                page_activities = activity_summary.iloc[start_idx:end_idx]
                
                # Display as a bar chart
                fig = px.bar(
                    page_activities,
                    x='Total Hours',
                    y='Activity',
                    orientation='h',
                    title=f"{ACTIVITY_CATEGORIES[selected_category]} Activities (Page {page}/{total_pages})",
                    color='Total Hours',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    height=min(350, len(page_activities) * 40 + 100),
                    margin=dict(t=40, b=20, l=20, r=20),
                    yaxis={'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Hours", f"{activity_summary['Total Hours'].sum():.1f}h")
                with col2:
                    st.metric("Total Activities", len(activity_summary))
                with col3:
                    st.metric("Avg Hours/Activity", f"{activity_summary['Total Hours'].mean():.1f}h")
            else:
                st.info(f"No activities found for {ACTIVITY_CATEGORIES[selected_category]}")
    
    else:
        st.error("⚠️ diaw.txt file not found. Please ensure the file exists in the current directory.")

if __name__ == "__main__":
    main()
