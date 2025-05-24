import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import calendar
import datetime

def plot_birthday_calendar(df):
    """
    Create a calendar heatmap of birthdays by month and day
    
    Args:
        df (pandas.DataFrame): Passport data with DOB column
        
    Returns:
        plotly.graph_objects.Figure: Calendar heatmap
    """
    # Create a list to store birthday count data
    birthday_data = []
    
    # Get counts of birthdays for each day of the year
    for month in range(1, 13):
        days_in_month = calendar.monthrange(2023, month)[1]  # Use 2023 as a non-leap year
        for day in range(1, days_in_month + 1):
            count = len(df[(df['DOB'].dt.month == month) & (df['DOB'].dt.day == day)])
            birthday_data.append({
                'month': month,
                'day': day,
                'count': count
            })
    
    # Convert list to DataFrame
    birthday_counts = pd.DataFrame(birthday_data)
    
    # Convert month numbers to month names
    birthday_counts['month_name'] = birthday_counts['month'].apply(lambda x: calendar.month_name[x])
    
    # Create heatmap
    fig = px.density_heatmap(
        birthday_counts,
        x='day',
        y='month_name',
        z='count',
        title='Birthday Distribution Throughout the Year',
        labels={'day': 'Day of Month', 'month_name': 'Month', 'count': 'Number of Birthdays'},
        color_continuous_scale='YlOrRd'
    )
    
    # Update layout
    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=1,
            dtick=1,
            tickangle=0
        ),
        yaxis=dict(
            categoryorder='array',
            categoryarray=[calendar.month_name[i] for i in range(12, 0, -1)]
        )
    )
    
    return fig

def plot_expiration_distribution(df):
    """
    Create a bar chart of passport expirations by month
    
    Args:
        df (pandas.DataFrame): Passport data with Expiry column
        
    Returns:
        plotly.graph_objects.Figure: Bar chart of expirations
    """
    # Filter valid expiry dates
    valid_expiry = df[df['Expiry'].notna()].copy()
    
    if valid_expiry.empty:
        # Return empty figure if no valid data
        fig = go.Figure()
        fig.update_layout(
            title="No expiration data available",
            xaxis_title="Month",
            yaxis_title="Number of Expirations"
        )
        return fig
    
    # Get current year
    current_year = datetime.datetime.now().year
    
    # Filter to expirations in current and next year
    mask = (valid_expiry['Expiry'].dt.year.isin([current_year, current_year + 1]))
    upcoming_expiry = valid_expiry[mask].copy()
    
    if upcoming_expiry.empty:
        # Return empty figure if no upcoming expirations
        fig = go.Figure()
        fig.update_layout(
            title="No upcoming expirations found",
            xaxis_title="Month",
            yaxis_title="Number of Expirations"
        )
        return fig
    
    # Create a year-month field
    upcoming_expiry['year_month'] = upcoming_expiry['Expiry'].dt.strftime('%Y-%m')
    
    # Count expirations by year-month
    expiry_counts = upcoming_expiry.groupby('year_month').size().reset_index(name='count')
    expiry_counts['year_month_dt'] = pd.to_datetime(expiry_counts['year_month'] + '-01')
    expiry_counts = expiry_counts.sort_values('year_month_dt')
    
    # Create labels with month name and year
    expiry_counts['month_year_label'] = expiry_counts['year_month_dt'].dt.strftime('%b %Y')
    
    # Create bar chart
    fig = px.bar(
        expiry_counts,
        x='month_year_label',
        y='count',
        title='Passport Expirations by Month',
        labels={'month_year_label': 'Month', 'count': 'Number of Expirations'},
        color='count',
        color_continuous_scale='Viridis'
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Expirations",
        xaxis={'categoryorder': 'array', 'categoryarray': expiry_counts['month_year_label'].tolist()}
    )
    
    return fig

def plot_notification_history(history_df):
    """
    Create a stacked bar chart of notification history by date and status
    
    Args:
        history_df (pandas.DataFrame): Notification history data
        
    Returns:
        plotly.graph_objects.Figure: Stacked bar chart
    """
    if history_df.empty:
        # Return empty figure if no history data
        fig = go.Figure()
        fig.update_layout(
            title="No notification history available",
            xaxis_title="Date",
            yaxis_title="Count"
        )
        return fig
    
    # Convert date column to datetime if it's not already
    history_df['date'] = pd.to_datetime(history_df['date'])
    
    # Extract date part only
    history_df['date_only'] = history_df['date'].dt.date
    
    # Group by date and status
    notification_counts = history_df.groupby(['date_only', 'status']).size().reset_index(name='count')
    
    # Create stacked bar chart
    fig = px.bar(
        notification_counts,
        x='date_only',
        y='count',
        color='status',
        title='Notification History',
        labels={'date_only': 'Date', 'count': 'Number of Notifications', 'status': 'Status'},
        color_discrete_map={'Sent': 'green', 'Failed': 'red'}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Notifications",
        legend_title="Status"
    )
    
    return fig
