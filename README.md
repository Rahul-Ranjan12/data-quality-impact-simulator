# Data Quality Impact Calculator

An interactive Streamlit application that demonstrates how data quality issues affect experiment results and decision making.

![App Screenshot](screenshot.png)

## Live Demo

Access the live application at: [https://data-quality-calculator.streamlit.app/](https://data-quality-calculator.streamlit.app/)

## Features

- Model the impact of different data quality issues on A/B test results
- Visualize how error rates affect observed metrics
- Calculate statistical power and detection thresholds
- Analyze asymmetric quality impacts between control and variation groups
- Receive automatic recommendations based on data quality patterns

## Types of Data Quality Issues Modeled

- **Event Loss Rate**: Complete failure to track events
- **User ID Error Rate**: Incorrect user identification
- **Partial Data Rate**: Missing properties in tracked events
- **Segmentation Errors**: Incorrect user categorization
- **Timeframe Bias**: Inconsistent measurement windows

## Running Locally

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/data-quality-calculator.git
   cd data-quality-calculator
   ```

2. Create a virtual environment and install dependencies
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the Streamlit app
   ```bash
   streamlit run data_quality_calculator.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Deployment

This application is deployed using [Streamlit Community Cloud](https://streamlit.io/cloud).

To deploy your own version:

1. Fork this repository
2. Sign up for Streamlit Community Cloud
3. Create a new app pointing to your forked repository
4. Deploy and share!

## How to Contribute

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Make your changes
4. Submit a pull request

Looking for ways to contribute? Check out our [issues](https://github.com/yourusername/data-quality-calculator/issues) page.

## Educational Resources

For more information on data quality in experimentation:

- Read our [Data Quality Impact Guide](docs/data_quality_guide.md)
- Check out the [Common Error Patterns](docs/error_patterns.md) documentation
- Follow our [Best Practices](docs/best_practices.md) for experimentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by real-world experimentation challenges in product analytics
- Built with [Streamlit](https://streamlit.io/)
- Data visualization powered by [Altair](https://altair-viz.github.io/)
