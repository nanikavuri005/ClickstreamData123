import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def load_and_validate_data(file):
    """Load and validate uploaded clickstream data"""
    try:
        df = pd.read_csv(file)
        required_columns = ['User_ID', 'Session_ID', 'Timestamp', 'Page_Type', 'Product_ID', 'Category', 'Action', 'Device_Type', 'Platform']

        if not all(col in df.columns for col in required_columns):
            return None, "Missing required columns in the clickstream data"

        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df, None
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

def calculate_key_metrics(df):
    """Calculate key e-commerce metrics"""
    metrics = {
        'total_users': df['User_ID'].nunique(),
        'total_sessions': df['Session_ID'].nunique(),
        'conversion_rate': (df[df['Action'] == 'Purchase'].User_ID.nunique() / df['User_ID'].nunique() * 100),
        'avg_pages_per_session': df.groupby('Session_ID').size().mean(),
        'bounce_rate': (df.groupby('Session_ID').size().value_counts()[1] / len(df['Session_ID'].unique()) * 100)
    }
    return metrics

def analyze_user_behavior(df):
    """Analyze user shopping behavior patterns"""
    # User engagement by device
    device_usage = df['Device_Type'].value_counts().to_dict()

    # Popular categories
    category_popularity = df['Category'].value_counts().head(5).to_dict()

    # User actions distribution
    action_dist = df['Action'].value_counts().to_dict()

    # Platform preference
    platform_dist = df['Platform'].value_counts().to_dict()

    # Time analysis
    df['Hour'] = df['Timestamp'].dt.hour
    hourly_activity = df.groupby('Hour').size().to_dict()

    return {
        'device_usage': device_usage,
        'category_popularity': category_popularity,
        'action_dist': action_dist,
        'platform_dist': platform_dist,
        'hourly_activity': hourly_activity
    }

def analyze_product_sales(df):
    """Analyze product sales and trends"""
    # Filter purchases
    purchases = df[df['Action'] == 'Purchase']

    # Get top selling products
    top_products = purchases.groupby('Product_ID').size().sort_values(ascending=False)

    # Get sales by category
    category_sales = purchases['Category'].value_counts()

    # Monthly sales trend
    purchases['Month'] = purchases['Timestamp'].dt.strftime('%Y-%m')
    monthly_sales = purchases.groupby('Month').size().sort_index()

    # Sales by platform
    platform_sales = purchases['Platform'].value_counts()

    return {
        'top_products': top_products.head(10).to_dict(),
        'category_sales': category_sales.to_dict(),
        'monthly_sales': monthly_sales.to_dict(),
        'platform_sales': platform_sales.to_dict()
    }

def segment_users(df):
    """Segment users based on their behavior"""
    # Create user-level features
    user_features = df.groupby('User_ID').agg({
        'Session_ID': 'nunique',  # Number of sessions
        'Action': lambda x: (x == 'Purchase').sum(),  # Number of purchases
        'Category': 'nunique',  # Category diversity
        'Platform': 'nunique'  # Platform diversity
    })

    # Standardize features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(user_features)

    # Perform clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    user_features['Segment'] = kmeans.fit_predict(features_scaled)

    # Calculate segment characteristics
    segment_profile = user_features.groupby('Segment').mean().round(2)

    return user_features, segment_profile


def analyze_clickstream(df):
    """Analyze clickstream patterns"""
    # Session analysis remains unchanged
    session_stats = df.groupby('Session_ID').agg({
        'Timestamp': lambda x: (x.max() - x.min()).total_seconds(),
        'Page_Type': 'count',
        'Action': 'nunique'
    }).rename(columns={
        'Timestamp': 'duration_seconds',
        'Page_Type': 'page_views',
        'Action': 'unique_actions'
    })

    # Navigation paths
    path_analysis = df.groupby('Session_ID')['Page_Type'].agg(lambda x: '->'.join(x)).value_counts().head(10)

    # Action sequences
    action_sequences = df.groupby('Session_ID')['Action'].agg(lambda x: '->'.join(x)).value_counts().head(10)

    # Page type transitions
    df['next_page'] = df.groupby('Session_ID')['Page_Type'].shift(-1)
    transitions = df[df['next_page'].notna()].groupby(['Page_Type', 'next_page']).size()

    # Enhanced click patterns focusing on electronics
    clicks_df = df[df['Action'] == 'Click'].copy()
    click_counts = clicks_df.groupby(['Category', 'Page_Type']).size().reset_index(name='clicks')

    # Sort to prioritize electronics
    click_counts['is_electronics'] = click_counts['Category'] == 'Electronics'
    click_counts = click_counts.sort_values(['is_electronics', 'clicks'], ascending=[False, False])

    # Create formatted labels and dictionary
    click_patterns = {
        f"{row['Category']} - {row['Page_Type']}": row['clicks']
        for _, row in click_counts.head(10).iterrows()
    }

    return {
        'avg_session_duration': session_stats['duration_seconds'].mean(),
        'avg_page_views': session_stats['page_views'].mean(),
        'common_paths': path_analysis.to_dict(),
        'action_sequences': action_sequences.to_dict(),
        'top_transitions': transitions.head(10).to_dict(),
        'click_patterns': click_patterns
    }

def analyze_conversion_funnel(df):
    """Analyze the conversion funnel from view to purchase"""
    total_sessions = df['Session_ID'].nunique()

    funnel_stages = {
        'View': df[df['Action'] == 'View']['Session_ID'].nunique(),
        'Click': df[df['Action'] == 'Click']['Session_ID'].nunique(),
        'Add to Cart': df[df['Action'] == 'Add to Cart']['Session_ID'].nunique(),
        'Purchase': df[df['Action'] == 'Purchase']['Session_ID'].nunique()
    }

    # Calculate conversion rates
    funnel_rates = {
        stage: (count / total_sessions * 100) 
        for stage, count in funnel_stages.items()
    }

    return funnel_stages, funnel_rates

def analyze_session_metrics(df):
    """Calculate detailed session metrics"""
    session_metrics = {}

    # Time on page by page type
    time_on_page = df.groupby('Page_Type').agg({
        'Timestamp': lambda x: (x.max() - x.min()).total_seconds()
    }).mean()

    # Entry and exit pages
    entry_pages = df.groupby('Session_ID')['Page_Type'].first().value_counts()
    exit_pages = df.groupby('Session_ID')['Page_Type'].last().value_counts()

    # Session depth distribution
    session_depth = df.groupby('Session_ID').size().value_counts()

    session_metrics['avg_time_by_page'] = time_on_page.to_dict()
    session_metrics['top_entry_pages'] = entry_pages.head(5).to_dict()
    session_metrics['top_exit_pages'] = exit_pages.head(5).to_dict()
    session_metrics['depth_distribution'] = session_depth.head(10).to_dict()

    return session_metrics