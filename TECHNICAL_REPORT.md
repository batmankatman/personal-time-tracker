# Personal Time Tracker Dashboard - Technical Report

## 1. Audience and Context
This dashboard was designed for individuals interested in understanding their personal time allocation patterns (like Type A personalities, lol), or anyone seeking to optimize their daily routines through data-driven insights. The primary goal was to create an interactive tool that allows users to explore activity distribution, productivity trends, and behavioral patterns across multiple weeks. Instead of presenting a static summary, the dashboard encourages exploration through filters and visual interactivity, making it easier to identify habits, time allocation inefficiencies, and opportunities for schedule optimization.

## 2. Key Performance Indicators (KPIs)
The dashboard focuses on several main Key Performance Indicators (KPIs) that summarize personal activity patterns and time management:

- **Coursework Hours** - Tracks total hours spent on academic work (ITSC and STAT courses), breaking down homework versus other coursework activities.
- **Sleep Patterns** - Shows average, minimum, and maximum sleep duration, reflecting sleep consistency and health metrics across time periods.
- **Walking Activity** - Measures total distance walked and calories burned, providing insights into physical activity levels.
- **Productive vs. Non-Productive Time** - Categorizes activities into Productive (P), Routine (R), Social (S), Workout (W), Fun (F), Eat (E), and God (GOD) categories to understand time distribution (I like the Pie chart display for this KPI)
- **Notes & Scheduling, Communication (Social), and Multitask Approximations** - Additional metrics that capture planning activities, social communication time, and estimated multitasking overlaps.

## 3. Dashboard Structure and Interactivity
The dashboard is structured to present information in a clear left-to-right and top-down hierarchy:

1. **Sidebar Filters** - Week pair selection (Weeks 1-2, 3-4, 5-6, 7-8, or All) and category filters with color-coded checkboxes allow users to isolate specific time periods or activity types. An activity browser provides searchable access to detailed activity logs.

2. **Top Row Visualizations** - Three side-by-side panels display:
   - Time Distribution by Category (pie chart or histogram toggle)
   - Weekly Trend (line chart showing average hours per weekday)
   - Quick Activity Stats (compact HTML-rendered statistics panel)

3. **Bottom Section** - Activity Distribution chart shows stacked bar visualization of average hours per weekday across 14-day consecutive spans, with date ranges.

## 4. Data Preparation and Cleaning
The dataset used is the proprietary text file (2024-2025 academic year) containing reverse-chronological daily activity logs. The data includes date headers, activity codes (P, R, E, S, W, F, GOD, LO), timestamps (HHMM format), durations, and activity descriptions.

Preprocessing steps in Python include:

- **Parsing date headers** with day-of-week indicators and converting to datetime objects
- **Extracting activity codes** and mapping them to full category names (Productive, Routine, Eat, Social, Workout, Fun, God, Sleep)
- **Converting time durations** from various formats (HHMM notation, decimal hours) to standardized hours
- **Calculating derived metrics** such as walking distance, calories burned, and sleep durations
- **Detecting consecutive 14-day spans** with gap detection (>30 days) to properly group week pairs for accurate averaging
- **Category filtering** to exclude sleep (LO) from main visualizations while preserving it for sleep-specific metrics

*Custom calculations were implemented for multitasking approximations (e.g., 33% of walking time counted toward communication, 25% toward notes/scheduling).

## 5. Design Choices
I liked the dark theme :))) but otherwise wanted to choose useful diagrams and graphs that would best represent the data. So histograms, pie charts, and line charts, though simple, clearly show the distribution and trends in time allocation.

Each activity category color ("Fall grdaient" theme):
- Productive (Deep Orange #D84315)
- Routine (Orange #FF9800)
- Eat (Amber #FFC107)
- Social (Purple #9C27B0)
- Workout (Deep Purple #673AB7)
- Fun (Dark Orange #FF6F00)
- God (Very Deep Purple #4A148C)
- Sleep (Dark Purple #7B1FA2)

Visuals were sized appropriately for three-column layouts, and margins were minimized (t=0) to bring content closer to section titles. The Quick Activity Stats panel uses custom HTML with precise font sizing and spacing control for a polished, compact appearance.

## 6. Reflection and Evaluation
Overall, the dashboard effectively communicates personal time allocation patterns and provides an accessible way to explore behavioral data across multiple weeks. The combination of interactivity, clean design, and focused KPIs helps users quickly identify time management patterns and draw meaningful conclusions about their daily habits.

The process of building this dashboard reinforced the importance of accurate date range calculations and visual consistency; each element serves a specific purpose in understanding personal productivity. One significant challenge involved implementing proper 14-day consecutive span detection with gap handling, which required rewriting the week grouping logic to avoid incorrect averaging. Another challenge was balancing hover detail with visual clarity—ensuring that color-coded information was present without overwhelming the user.

Future improvements could include:
- Goal-setting features with visual indicators for target hours
- Correlation analysis between sleep quality and productive hours
- Qualitative indicators (like productive activity time spans and standard deviations for duration)

The dashboard successfully transforms raw time-tracking data into actionable insights for Type A personalities seeking analytical and operational clarity in their daily routines.

## 7. Data and Publication Details
- **Dataset**: Proprietary daily activity log (diaw.txt, 2024-2025)
- **Tool**: Streamlit with Plotly visualizations
- **Audience**: for analytical and operational insights on behalf of Type A Personalities
- **Purpose**: To visualize and analyze personal time allocation, activity patterns, and productivity trends across multiple weeks, enabling data-driven optimization of daily routines and lifestyle balance.
- **Publication**: Hosted on Streamlit Cloud (https://personal-time-tracker-jk5m8slvssdp748bny2wbr.streamlit.app)
- **Credit**: Cluade Sonnet 4.5 Undergirded the technical code development.