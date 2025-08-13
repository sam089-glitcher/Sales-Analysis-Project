-- ===============================================
-- Walmart Sales Analysis Queries
-- Advanced analysis for trends, seasonality, and performance
-- ===============================================

-- 1. SALES TRENDS ANALYSIS
-- ===============================================

-- Monthly sales trends over time
SELECT 
    DATE_TRUNC('month', Date) as month_year,
    SUM(Weekly_Sales) as total_monthly_sales,
    AVG(Weekly_Sales) as avg_weekly_sales,
    COUNT(DISTINCT Store) as active_stores,
    COUNT(DISTINCT Dept) as active_departments
FROM train
GROUP BY DATE_TRUNC('month', Date)
ORDER BY month_year;

-- Year-over-year growth analysis
WITH yearly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM Date) as year,
        SUM(Weekly_Sales) as total_sales
    FROM train
    GROUP BY EXTRACT(YEAR FROM Date)
)
SELECT 
    year,
    total_sales,
    LAG(total_sales) OVER (ORDER BY year) as prev_year_sales,
    CASE 
        WHEN LAG(total_sales) OVER (ORDER BY year) IS NOT NULL 
        THEN ROUND(((total_sales - LAG(total_sales) OVER (ORDER BY year)) / 
                    LAG(total_sales) OVER (ORDER BY year) * 100), 2)
        ELSE NULL 
    END as yoy_growth_percent
FROM yearly_sales
ORDER BY year;

-- Quarterly performance analysis
SELECT 
    EXTRACT(YEAR FROM Date) as year,
    EXTRACT(QUARTER FROM Date) as quarter,
    SUM(Weekly_Sales) as quarterly_sales,
    AVG(Weekly_Sales) as avg_weekly_sales,
    COUNT(*) as total_records
FROM train
GROUP BY EXTRACT(YEAR FROM Date), EXTRACT(QUARTER FROM Date)
ORDER BY year, quarter;

-- 2. STORE PERFORMANCE ANALYSIS
-- ===============================================

-- Top performing stores by total sales
SELECT 
    t.Store,
    s.Type as store_type,
    s.Size as store_size,
    SUM(t.Weekly_Sales) as total_sales,
    AVG(t.Weekly_Sales) as avg_weekly_sales,
    COUNT(DISTINCT t.Dept) as departments_count,
    COUNT(*) as total_records
FROM train t
JOIN stores s ON t.Store = s.Store
GROUP BY t.Store, s.Type, s.Size
ORDER BY total_sales DESC
LIMIT 15;

-- Store performance by type
SELECT 
    s.Type,
    COUNT(DISTINCT t.Store) as store_count,
    SUM(t.Weekly_Sales) as total_sales,
    AVG(t.Weekly_Sales) as avg_weekly_sales,
    AVG(s.Size) as avg_store_size
FROM train t
JOIN stores s ON t.Store = s.Store
GROUP BY s.Type
ORDER BY total_sales DESC;

-- Store size vs performance correlation
SELECT 
    CASE 
        WHEN s.Size < 50000 THEN 'Small (< 50K)'
        WHEN s.Size < 100000 THEN 'Medium (50K-100K)'
        WHEN s.Size < 150000 THEN 'Large (100K-150K)'
        ELSE 'Extra Large (150K+)'
    END as size_category,
    COUNT(DISTINCT t.Store) as store_count,
    AVG(s.Size) as avg_size,
    SUM(t.Weekly_Sales) as total_sales,
    AVG(t.Weekly_Sales) as avg_weekly_sales,
    SUM(t.Weekly_Sales) / COUNT(DISTINCT t.Store) as sales_per_store
FROM train t
JOIN stores s ON t.Store = s.Store
GROUP BY 
    CASE 
        WHEN s.Size < 50000 THEN 'Small (< 50K)'
        WHEN s.Size < 100000 THEN 'Medium (50K-100K)'
        WHEN s.Size < 150000 THEN 'Large (100K-150K)'
        ELSE 'Extra Large (150K+)'
    END
ORDER BY avg_size;

-- 3. DEPARTMENT PERFORMANCE ANALYSIS
-- ===============================================

-- Top performing departments
SELECT 
    Dept,
    SUM(Weekly_Sales) as total_sales,
    AVG(Weekly_Sales) as avg_weekly_sales,
    COUNT(DISTINCT Store) as stores_present,
    COUNT(*) as total_records,
    STDDEV(Weekly_Sales) as sales_volatility
FROM train
GROUP BY Dept
ORDER BY total_sales DESC
LIMIT 20;

-- Department performance by store type
SELECT 
    t.Dept,
    s.Type as store_type,
    SUM(t.Weekly_Sales) as total_sales,
    AVG(t.Weekly_Sales) as avg_weekly_sales,
    COUNT(*) as record_count
FROM train t
JOIN stores s ON t.Store = s.Store
GROUP BY t.Dept, s.Type
HAVING COUNT(*) >= 50  -- Filter for departments with sufficient data
ORDER BY t.Dept, total_sales DESC;

-- Most consistent departments (lowest variability)
SELECT 
    Dept,
    AVG(Weekly_Sales) as avg_sales,
    STDDEV(Weekly_Sales) as std_dev,
    CASE 
        WHEN AVG(Weekly_Sales) > 0 
        THEN ROUND((STDDEV(Weekly_Sales) / AVG(Weekly_Sales)) * 100, 2) 
        ELSE NULL 
    END as coefficient_of_variation,
    COUNT(*) as record_count
FROM train
GROUP BY Dept
HAVING COUNT(*) >= 100
ORDER BY coefficient_of_variation ASC
LIMIT 15;

-- 4. SEASONALITY ANALYSIS
-- ===============================================

-- Sales by day of week
SELECT 
    EXTRACT(DOW FROM Date) as day_of_week,
    CASE EXTRACT(DOW FROM Date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    SUM(Weekly_Sales) as total_sales,
    AVG(Weekly_Sales) as avg_sales,
    COUNT(*) as record_count
FROM train
GROUP BY EXTRACT(DOW FROM Date)
ORDER BY day_of_week;

-- Monthly seasonal patterns
SELECT 
    EXTRACT(MONTH FROM Date) as month,
    CASE EXTRACT(MONTH FROM Date)
        WHEN 1 THEN 'January' WHEN 2 THEN 'February' WHEN 3 THEN 'March'
        WHEN 4 THEN 'April' WHEN 5 THEN 'May' WHEN 6 THEN 'June'
        WHEN 7 THEN 'July' WHEN 8 THEN 'August' WHEN 9 THEN 'September'
        WHEN 10 THEN 'October' WHEN 11 THEN 'November' WHEN 12 THEN 'December'
    END as month_name,
    AVG(Weekly_Sales) as avg_monthly_sales,
    SUM(Weekly_Sales) as total_monthly_sales,
    COUNT(*) as record_count
FROM train
GROUP BY EXTRACT(MONTH FROM Date)
ORDER BY month;

-- Holiday impact analysis (detailed)
WITH holiday_analysis AS (
    SELECT 
        Date,
        IsHoliday,
        SUM(Weekly_Sales) as daily_total_sales,
        AVG(Weekly_Sales) as daily_avg_sales,
        COUNT(*) as transactions
    FROM train
    GROUP BY Date, IsHoliday
)
SELECT 
    IsHoliday,
    COUNT(*) as days_count,
    AVG(daily_total_sales) as avg_daily_total,
    AVG(daily_avg_sales) as avg_daily_avg,
    MIN(daily_total_sales) as min_daily_total,
    MAX(daily_total_sales) as max_daily_total
FROM holiday_analysis
GROUP BY IsHoliday;

-- 5. ADVANCED ANALYTICS
-- ===============================================

-- Sales trend with moving averages (4-week)
WITH weekly_sales AS (
    SELECT 
        Date,
        SUM(Weekly_Sales) as total_weekly_sales
    FROM train
    GROUP BY Date
),
moving_avg AS (
    SELECT 
        Date,
        total_weekly_sales,
        AVG(total_weekly_sales) OVER (
            ORDER BY Date 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) as four_week_avg
    FROM weekly_sales
)
SELECT 
    Date,
    total_weekly_sales,
    ROUND(four_week_avg, 2) as moving_average_4_weeks,
    ROUND(((total_weekly_sales - four_week_avg) / four_week_avg * 100), 2) as variance_from_avg_percent
FROM moving_avg
ORDER BY Date;

-- Store ranking by consistent performance
WITH store_consistency AS (
    SELECT 
        Store,
        AVG(Weekly_Sales) as avg_sales,
        STDDEV(Weekly_Sales) as std_dev,
        COUNT(*) as record_count,
        MIN(Weekly_Sales) as min_sales,
        MAX(Weekly_Sales) as max_sales
    FROM train
    GROUP BY Store
)
SELECT 
    Store,
    ROUND(avg_sales, 2) as avg_weekly_sales,
    ROUND(std_dev, 2) as sales_std_dev,
    ROUND((std_dev / avg_sales * 100), 2) as coefficient_of_variation,
    record_count,
    min_sales,
    max_sales,
    RANK() OVER (ORDER BY (std_dev / avg_sales)) as consistency_rank
FROM store_consistency
WHERE record_count >= 100  -- Only stores with sufficient data
ORDER BY consistency_rank;

-- 6. COMPARATIVE ANALYSIS
-- ===============================================

-- Department comparison across different store types
SELECT 
    t.Dept,
    s.Type as store_type,
    COUNT(DISTINCT t.Store) as stores_count,
    SUM(t.Weekly_Sales) as total_sales,
    AVG(t.Weekly_Sales) as avg_weekly_sales,
    RANK() OVER (PARTITION BY t.Dept ORDER BY SUM(t.Weekly_Sales) DESC) as rank_within_dept
FROM train t
JOIN stores s ON t.Store = s.Store
GROUP BY t.Dept, s.Type
HAVING COUNT(*) >= 20  -- Filter for sufficient data
ORDER BY t.Dept, total_sales DESC;

-- Time-based performance comparison (pre vs post specific date)
WITH date_split AS (
    SELECT 
        Store,
        Dept,
        CASE 
            WHEN Date < '2011-07-01' THEN 'First_Half_2011'
            ELSE 'Post_July_2011'
        END as time_period,
        AVG(Weekly_Sales) as avg_sales,
        COUNT(*) as record_count
    FROM train
    GROUP BY Store, Dept, 
        CASE 
            WHEN Date < '2011-07-01' THEN 'First_Half_2011'
            ELSE 'Post_July_2011'
        END
)
SELECT 
    Store,
    Dept,
    MAX(CASE WHEN time_period = 'First_Half_2011' THEN avg_sales END) as first_half_avg,
    MAX(CASE WHEN time_period = 'Post_July_2011' THEN avg_sales END) as post_july_avg,
    CASE 
        WHEN MAX(CASE WHEN time_period = 'First_Half_2011' THEN avg_sales END) IS NOT NULL
             AND MAX(CASE WHEN time_period = 'Post_July_2011' THEN avg_sales END) IS NOT NULL
        THEN ROUND(((MAX(CASE WHEN time_period = 'Post_July_2011' THEN avg_sales END) - 
                     MAX(CASE WHEN time_period = 'First_Half_2011' THEN avg_sales END)) / 
                     MAX(CASE WHEN time_period = 'First_Half_2011' THEN avg_sales END) * 100), 2)
        ELSE NULL
    END as growth_percentage
FROM date_split
GROUP BY Store, Dept
HAVING MAX(CASE WHEN time_period = 'First_Half_2011' THEN avg_sales END) IS NOT NULL
   AND MAX(CASE WHEN time_period = 'Post_July_2011' THEN avg_sales END) IS NOT NULL
ORDER BY growth_percentage DESC NULLS LAST;
