import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Data Quality Impact Calculator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1E3A8A;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #F9FAFB;
        margin-bottom: 1rem;
    }
    .warning {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEF3C7;
        color: #92400E;
        margin-bottom: 1rem;
    }
    .success {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D1FAE5;
        color: #065F46;
        margin-bottom: 1rem;
    }
    .danger {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FEE2E2;
        color: #B91C1C;
        margin-bottom: 1rem;
    }
    .info {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E0F2FE;
        color: #0369A1;
        margin-bottom: 1rem;
    }
    .metric-label {
        font-weight: 600;
        color: #4B5563;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
    }
    .progress-container {
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>Data Quality Impact Calculator</h1>", unsafe_allow_html=True)
st.markdown("""
This interactive tool demonstrates how data quality issues affect experimental results and decision-making.
Adjust the parameters to see how different types of errors impact your experiment outcomes.
""")

# Create sidebar for inputs
st.sidebar.markdown("<h2 class='sub-header'>Experiment Parameters</h2>", unsafe_allow_html=True)

# Basic experiment parameters
sample_size = st.sidebar.number_input("Sample Size (users)", min_value=100, max_value=1000000, value=10000, step=1000)
baseline_conversion = st.sidebar.number_input("Baseline Conversion Rate (%)", min_value=0.1, max_value=99.9, value=10.0, step=0.1)
expected_lift = st.sidebar.number_input("Expected Lift (%)", min_value=-50.0, max_value=100.0, value=5.0, step=0.5)
confidence = st.sidebar.selectbox("Confidence Level", [90, 95, 99], index=1)

# Create two columns for control and variation inputs
st.sidebar.markdown("<h2 class='sub-header'>Data Quality Parameters</h2>", unsafe_allow_html=True)
control_col, variation_col = st.sidebar.columns(2)

# Control group parameters
with control_col:
    st.markdown("<h3>Control Group</h3>", unsafe_allow_html=True)
    control_event_loss = st.number_input("Event Loss (%)", min_value=0.0, max_value=50.0, value=2.0, step=0.5, key="control_event_loss")
    control_user_id_error = st.number_input("User ID Errors (%)", min_value=0.0, max_value=50.0, value=1.0, step=0.5, key="control_user_id_error")
    control_partial_data = st.number_input("Partial Data (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5, key="control_partial_data")

# Variation group parameters
with variation_col:
    st.markdown("<h3>Variation Group</h3>", unsafe_allow_html=True)
    variation_event_loss = st.number_input("Event Loss (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5, key="variation_event_loss")
    variation_user_id_error = st.number_input("User ID Errors (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.5, key="variation_user_id_error")
    variation_partial_data = st.number_input("Partial Data (%)", min_value=0.0, max_value=50.0, value=7.0, step=0.5, key="variation_partial_data")

# Additional factors
st.sidebar.markdown("<h3>Additional Factors</h3>", unsafe_allow_html=True)
segmentation_errors = st.sidebar.number_input("Segmentation Errors (%)", min_value=0.0, max_value=50.0, value=4.0, step=0.5)
timeframe_bias = st.sidebar.number_input("Timeframe Bias (%)", min_value=0.0, max_value=50.0, value=2.0, step=0.5)

# Add information button
with st.sidebar.expander("About this tool"):
    st.markdown("""
    This calculator models the impact of data quality issues on A/B test results. 
    
    Key concepts:
    - **Event Loss**: Complete failure to track events
    - **User ID Errors**: Incorrect user identification
    - **Partial Data**: Missing properties in tracked events
    - **Segmentation Errors**: Users in wrong segments
    - **Timeframe Bias**: Inconsistent measurement windows
    
    For more information, visit the [GitHub repository](https://github.com/yourusername/data-quality-calculator).
    """)

# Calculations
def calculate_metrics():
    # Calculate effective sample size
    control_effective_sample = sample_size / 2 * (1 - control_user_id_error / 100) * (1 - control_event_loss / 100)
    variation_effective_sample = sample_size / 2 * (1 - variation_user_id_error / 100) * (1 - variation_event_loss / 100)
    total_effective_sample = control_effective_sample + variation_effective_sample
    
    # Calculate observed conversion
    control_observed_conversion = baseline_conversion * (1 - control_partial_data / 100)
    variation_expected_conversion = baseline_conversion * (1 + expected_lift / 100)
    variation_observed_conversion = variation_expected_conversion * (1 - variation_partial_data / 100)
    
    # Calculate actual lift
    reported_lift = ((variation_observed_conversion / control_observed_conversion) - 1) * 100
    
    # Calculate bias risk score
    control_quality_score = 100 - (control_event_loss + control_user_id_error + control_partial_data) / 3
    variation_quality_score = 100 - (variation_event_loss + variation_user_id_error + variation_partial_data) / 3
    quality_difference = abs(control_quality_score - variation_quality_score)
    
    # Calculate statistical power (simplified)
    alpha = (100 - confidence) / 100
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    
    # Standard error calculation
    se_control = np.sqrt((control_observed_conversion * (100 - control_observed_conversion)) / control_effective_sample)
    se_variation = np.sqrt((variation_observed_conversion * (100 - variation_observed_conversion)) / variation_effective_sample)
    pooled_se = np.sqrt(se_control**2 + se_variation**2)
    
    # Z-score for power calculation
    expected_effect = expected_lift / 100 * baseline_conversion
    z_score = expected_effect / pooled_se
    power = stats.norm.cdf(z_score - z_alpha)
    
    # Minimum detectable effect
    mde = z_alpha * pooled_se * 2
    
    # Calculate false positive and negative risks
    data_quality_impact = (variation_event_loss + variation_user_id_error + variation_partial_data) - \
                          (control_event_loss + control_user_id_error + control_partial_data)
    false_positive_risk = abs(data_quality_impact / 5) if data_quality_impact < 0 else 0
    false_negative_risk = (data_quality_impact / 5) if data_quality_impact > 0 else 0
    
    # Determine conclusion
    if reported_lift > 0 and reported_lift < expected_lift and data_quality_impact > 5:
        conclusion = "Likely false negative (true effect is being diluted by data quality issues)"
        conclusion_class = "warning"
    elif reported_lift > expected_lift and data_quality_impact < -5:
        conclusion = "Potential false positive (observed lift is artificially inflated)"
        conclusion_class = "danger"
    elif abs(reported_lift) < mde:
        conclusion = "Inconclusive (effect size is below detection threshold)"
        conclusion_class = "info"
    elif abs(reported_lift - expected_lift) < mde / 2:
        conclusion = "Likely valid result (observed lift matches expected)"
        conclusion_class = "success"
    else:
        conclusion = "Requires investigation (unexpected results)"
        conclusion_class = "warning"
    
    # Generate chart data
    error_rates = list(range(0, 21, 2))
    true_lifts = [expected_lift] * len(error_rates)
    observed_lifts = []
    significance_flags = []
    
    for error in error_rates:
        # Calculate lift at this error level with asymmetric impact
        control_error_impact = control_event_loss / 100 + control_user_id_error / 100 + (error / 100) * (control_partial_data / 100)
        variation_error_impact = variation_event_loss / 100 + variation_user_id_error / 100 + (error / 100) * (variation_partial_data / 100)
        
        control_observed_rate = baseline_conversion * (1 - control_error_impact)
        variation_true_rate = baseline_conversion * (1 + expected_lift / 100)
        variation_observed_rate = variation_true_rate * (1 - variation_error_impact)
        
        observed_lift = ((variation_observed_rate / control_observed_rate) - 1) * 100
        observed_lifts.append(observed_lift)
        
        # Check if significant
        significance_flags.append(abs(observed_lift) > mde)
    
    chart_data = pd.DataFrame({
        'Error Rate': error_rates,
        'True Lift': true_lifts,
        'Observed Lift': observed_lifts,
        'Significant': significance_flags
    })
    
    return {
        'effective_sample_size': total_effective_sample,
        'control_observed_conversion': control_observed_conversion,
        'variation_observed_conversion': variation_observed_conversion,
        'actual_lift': reported_lift,
        'bias_risk_score': quality_difference,
        'stat_power': power * 100,
        'false_positive_risk': false_positive_risk,
        'false_negative_risk': false_negative_risk,
        'detection_threshold': mde,
        'conclusion': conclusion,
        'conclusion_class': conclusion_class,
        'chart_data': chart_data,
        'control_quality_score': control_quality_score,
        'variation_quality_score': variation_quality_score
    }

results = calculate_metrics()

# Create three columns for metrics display
col1, col2, col3 = st.columns(3)

# Column 1 - Basic Metrics
with col1:
    st.markdown("<h2 class='sub-header'>Key Metrics</h2>", unsafe_allow_html=True)
    
    # Effective Sample Size
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Effective Sample Size:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value'>{int(results['effective_sample_size']):,} users</span>", unsafe_allow_html=True)
    
    # Progress bar
    sample_ratio = results['effective_sample_size'] / sample_size
    st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
    st.progress(sample_ratio)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<span>{int(sample_ratio * 100)}% of original sample</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Observed Conversion
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Observed Conversion:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value'>{results['control_observed_conversion']:.2f}% vs {results['variation_observed_conversion']:.2f}%</span>", unsafe_allow_html=True)
    
    conversion_ratio = results['control_observed_conversion'] / baseline_conversion
    st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
    st.progress(min(1.0, conversion_ratio))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<span>{int(conversion_ratio * 100)}% of true conversion captured</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Actual Lift
    lift_color = "green" if results['actual_lift'] > 0 else "red"
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Actual Lift:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value' style='color: {lift_color};'>{'+' if results['actual_lift'] > 0 else ''}{results['actual_lift']:.2f}%</span>", unsafe_allow_html=True)
    
    if expected_lift != 0:
        lift_ratio = min(1.0, max(0.0, results['actual_lift'] / expected_lift if expected_lift > 0 else results['actual_lift'] / expected_lift))
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        st.progress(lift_ratio)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if expected_lift > 0:
            ratio_text = f"{int(results['actual_lift'] / expected_lift * 100)}% of expected lift" if results['actual_lift'] > 0 else "Negative lift (expected positive)"
        else:
            ratio_text = f"{int(results['actual_lift'] / expected_lift * 100)}% of expected lift" if results['actual_lift'] < 0 else "Positive lift (expected negative)"
        
        st.markdown(f"<span>{ratio_text}</span>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Column 2 - Statistical Metrics
with col2:
    st.markdown("<h2 class='sub-header'>Statistical Measures</h2>", unsafe_allow_html=True)
    
    # Statistical Power
    power_color = "green" if results['stat_power'] >= 80 else ("orange" if results['stat_power'] >= 50 else "red")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Statistical Power:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value' style='color: {power_color};'>{results['stat_power']:.1f}%</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
    st.progress(min(1.0, results['stat_power'] / 100))
    st.markdown("</div>", unsafe_allow_html=True)
    
    power_text = "Sufficient power" if results['stat_power'] >= 80 else ("Borderline power" if results['stat_power'] >= 50 else "Insufficient power")
    st.markdown(f"<span>{power_text}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bias Risk Score
    bias_color = "green" if results['bias_risk_score'] < 5 else ("orange" if results['bias_risk_score'] < 10 else "red")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Bias Risk Score:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value' style='color: {bias_color};'>{results['bias_risk_score']:.1f}</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
    st.progress(min(1.0, results['bias_risk_score'] / 20))
    st.markdown("</div>", unsafe_allow_html=True)
    
    bias_text = "Low risk of bias" if results['bias_risk_score'] < 5 else ("Moderate risk of bias" if results['bias_risk_score'] < 10 else "High risk of bias")
    st.markdown(f"<span>{bias_text}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Detection Threshold
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Detection Threshold:</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='metric-value'>{results['detection_threshold']:.2f}%</span>", unsafe_allow_html=True)
    st.markdown("<span>Minimum detectable effect at chosen confidence</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Column 3 - Risk Analysis
with col3:
    st.markdown("<h2 class='sub-header'>Risk Analysis</h2>", unsafe_allow_html=True)
    
    # Data Quality Scores
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Data Quality Scores:</span>", unsafe_allow_html=True)
    
    # Compare Control vs Variation quality scores
    quality_df = pd.DataFrame({
        'Group': ['Control', 'Variation'],
        'Score': [results['control_quality_score'], results['variation_quality_score']]
    })
    
    quality_chart = alt.Chart(quality_df).mark_bar().encode(
        x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 100])),
        y=alt.Y('Group:N'),
        color=alt.condition(
            alt.datum.Score > 90,
            alt.value('green'),
            alt.condition(
                alt.datum.Score > 80,
                alt.value('lightgreen'),
                alt.condition(
                    alt.datum.Score > 70,
                    alt.value('orange'),
                    alt.value('red')
                )
            )
        )
    ).properties(height=100)
    
    st.altair_chart(quality_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # False Positive/Negative Risk
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Decision Risk:</span>", unsafe_allow_html=True)
    
    risk_df = pd.DataFrame({
        'Risk Type': ['False Positive', 'False Negative'],
        'Score': [results['false_positive_risk'], results['false_negative_risk']]
    })
    
    risk_chart = alt.Chart(risk_df).mark_bar().encode(
        x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 20])),
        y=alt.Y('Risk Type:N'),
        color=alt.condition(
            alt.datum.Score < 5,
            alt.value('green'),
            alt.condition(
                alt.datum.Score < 15,
                alt.value('orange'),
                alt.value('red')
            )
        )
    ).properties(height=100)
    
    st.altair_chart(risk_chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Conclusion
    st.markdown(f"<div class='{results['conclusion_class']}'>", unsafe_allow_html=True)
    st.markdown("<span class='metric-label'>Analysis Conclusion:</span>", unsafe_allow_html=True)
    st.markdown(f"<p>{results['conclusion']}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Visualization section
st.markdown("<h2 class='sub-header'>Data Quality Impact Visualization</h2>", unsafe_allow_html=True)

# Create a line chart
chart_data = results['chart_data']

# Define the base charts
base = alt.Chart(chart_data).encode(
    x=alt.X('Error Rate:Q', title='Error Rate (%)'),
    y=alt.Y('Observed Lift:Q', title='Lift (%)', scale=alt.Scale(
        domain=[min(min(chart_data['Observed Lift']), min(chart_data['True Lift'])) - 1,
                max(max(chart_data['Observed Lift']), max(chart_data['True Lift'])) + 1]
    ))
)

# Add true lift reference line
true_lift_line = base.mark_line(strokeDash=[5, 5], color='blue', strokeWidth=2).encode(
    y='True Lift:Q'
)

# Add observed lift line with color based on significance
observed_lift_line = base.mark_line(color='red', strokeWidth=2).encode(
    y='Observed Lift:Q'
)

# Add points with color based on significance
observed_lift_points = base.mark_circle(size=80).encode(
    y='Observed Lift:Q',
    color=alt.condition(
        'datum.Significant',
        alt.value('green'),
        alt.value('red')
    ),
    tooltip=['Error Rate:Q', 'Observed Lift:Q', 'Significant:N']
)

# Add a zero reference line
zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(strokeDash=[2, 2], color='gray').encode(
    y='y:Q'
)

# Combine the charts
final_chart = (true_lift_line + observed_lift_line + observed_lift_points + zero_line).properties(
    height=400
).interactive()

st.altair_chart(final_chart, use_container_width=True)

st.markdown("""
<div style='font-size: 0.9rem; color: #4B5563;'>
This chart shows how increasing error rates affect the observed lift compared to the true lift.
Green points indicate error levels where the observed effect would still be statistically significant, 
while red points indicate where significance would be lost, potentially leading to false negative results.
</div>
""", unsafe_allow_html=True)

# Recommendations section
st.markdown("<h2 class='sub-header'>Recommendations</h2>", unsafe_allow_html=True)

# Generate recommendations based on results
if results['bias_risk_score'] >= 5:
    st.markdown("""
    <div class='warning'>
      <strong>⚠️ Data quality asymmetry detected between control and variation groups.</strong><br>
      Consider investigating tracking implementation differences. Asymmetric data quality is a common
      source of systematic experiment bias.
    </div>
    """, unsafe_allow_html=True)

if results['effective_sample_size'] / sample_size < 0.8:
    st.markdown("""
    <div class='warning'>
      <strong>⚠️ Significant sample size reduction due to data quality issues.</strong><br>
      Consider increasing initial sample size or improving data collection methods to compensate
      for lost data points.
    </div>
    """, unsafe_allow_html=True)

if results['stat_power'] < 80:
    st.markdown("""
    <div class='warning'>
      <strong>⚠️ Statistical power is below the recommended threshold (80%).</strong><br>
      Results may be unreliable and could miss true effects. Consider increasing sample size
      or improving data quality to enhance power.
    </div>
    """, unsafe_allow_html=True)

if abs(results['actual_lift'] - expected_lift) > results['detection_threshold']:
    st.markdown("""
    <div class='warning'>
      <strong>⚠️ Observed lift differs significantly from expected lift.</strong><br>
      Investigate potential implementation or tracking issues that could be causing this discrepancy.
    </div>
    """, unsafe_allow_html=True)

# Best practices section
st.markdown("<h3>Best Practices</h3>", unsafe_allow_html=True)
st.markdown("""
- **Run A/A tests** before important experiments to validate tracking consistency
- **Monitor data quality metrics** in real-time throughout experiment runtime
- **Segment analysis by platform/browser** to identify platform-specific tracking issues
- **Implement dedicated QA processes** for new tracking code in experimental variants
- **Create data quality dashboards** to monitor trends over time
- **Document known data limitations** when sharing experiment results
- **Apply correction factors** when asymmetric data quality is unavoidable
""")

# Footer with GitHub link
st.markdown("""
---
<div style="text-align: center; color: #6B7280; font-size: 0.8rem;">
Developed with ❤️ for data quality | <a href="https://github.com/yourusername/data-quality-calculator">GitHub Repository</a>
</div>
""", unsafe_allow_html=True)
