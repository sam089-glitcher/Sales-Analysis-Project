# Sales Data Analysis Project - Walmart Dataset

## Project Overview
This project analyzes Walmart sales data to identify trends, seasonality, and product performance patterns using SQL queries and data analysis techniques.

## Dataset
- **Source**: Walmart Sales Dataset from Kaggle
- **URL**: https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/data
- **Description**: Historical sales data from 45 Walmart stores located in different regions

## Project Structure
```
sales-analysis-project/
├── data/                   # Raw and processed datasets
├── sql/                    # SQL queries for analysis
├── notebooks/              # Jupyter notebooks for analysis
├── visualizations/         # Charts and graphs
├── reports/               # Analysis reports and insights
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Key Analysis Areas
1. **Sales Trends Analysis**
   - Monthly, quarterly, and yearly sales patterns
   - Store performance comparison
   - Department-wise sales analysis

2. **Seasonality Analysis**
   - Holiday impact on sales
   - Seasonal patterns identification
   - Week-over-week variations

3. **Product Performance**
   - Top-performing departments
   - Underperforming categories
   - Sales correlation analysis

## Setup Instructions
1. Clone/download the project
2. Install required dependencies: `pip install -r requirements.txt`
3. Download the dataset from Kaggle (requires Kaggle account)
4. Place CSV files in the `data/` directory
5. Run the analysis notebooks

## Key Files
- `sql/data_exploration.sql` - Initial data exploration queries
- `sql/sales_analysis.sql` - Core sales analysis queries
- `notebooks/walmart_analysis.ipynb` - Main analysis notebook
- `reports/sales_insights.md` - Summary of key findings

## Technologies Used
- **Database**: SQLite/PostgreSQL
- **Languages**: SQL, Python
- **Libraries**: pandas, numpy, matplotlib, seaborn, plotly
- **Tools**: Jupyter Notebook, DBeaver (optional)
