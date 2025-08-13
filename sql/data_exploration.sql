-- ===============================================
-- Walmart Sales Data Exploration Queries
-- ===============================================

-- 1. Basic Data Overview
-- Check the structure and size of each table

-- Train dataset overview
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT Store) as unique_stores,
    COUNT(DISTINCT Dept) as unique_departments,
    MIN(Date) as earliest_date,
    MAX(Date) as latest_date
FROM train;

-- Features dataset overview  
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT Store) as unique_stores,
    MIN(Date) as earliest_date,
    MAX(Date) as latest_date
FROM features;

-- Stores dataset overview
SELECT 
    COUNT(*) as total_stores,
    COUNT(DISTINCT Type) as store_types,
    AVG(Size) as avg_store_size,
    MIN(Size) as min_store_size,
    MAX(Size) as max_store_size
FROM stores;

-- 2. Data Quality Checks
-- Check for missing values and data inconsistencies

-- Missing values in train dataset
SELECT 
    SUM(CASE WHEN Store IS NULL THEN 1 ELSE 0 END) as missing_store,
    SUM(CASE WHEN Dept IS NULL THEN 1 ELSE 0 END) as missing_dept,
    SUM(CASE WHEN Date IS NULL THEN 1 ELSE 0 END) as missing_date,
    SUM(CASE WHEN Weekly_Sales IS NULL THEN 1 ELSE 0 END) as missing_sales,
    SUM(CASE WHEN IsHoliday IS NULL THEN 1 ELSE 0 END) as missing_holiday
FROM train;

-- Check for negative sales values
SELECT 
    COUNT(*) as negative_sales_count,
    MIN(Weekly_Sales) as min_sales,
    MAX(Weekly_Sales) as max_sales
FROM train 
WHERE Weekly_Sales < 0;

-- 3. Store Analysis
-- Analyze store characteristics

-- Store types and their distribution
SELECT 
    Type,
    COUNT(*) as store_count,
    AVG(Size) as avg_size,
    MIN(Size) as min_size,
    MAX(Size) as max_size
FROM stores
GROUP BY Type
ORDER BY store_count DESC;

-- Store size distribution
SELECT 
    CASE 
        WHEN Size < 50000 THEN 'Small'
        WHEN Size < 100000 THEN 'Medium'
        WHEN Size < 150000 THEN 'Large'
        ELSE 'Extra Large'
    END as size_category,
    COUNT(*) as store_count,
    AVG(Size) as avg_size
FROM stores
GROUP BY 
    CASE 
        WHEN Size < 50000 THEN 'Small'
        WHEN Size < 100000 THEN 'Medium'
        WHEN Size < 150000 THEN 'Large'
        ELSE 'Extra Large'
    END
ORDER BY avg_size;

-- 4. Department Analysis
-- Analyze department performance

-- Department distribution
SELECT 
    Dept,
    COUNT(*) as record_count,
    COUNT(DISTINCT Store) as stores_with_dept,
    AVG(Weekly_Sales) as avg_weekly_sales,
    SUM(Weekly_Sales) as total_sales
FROM train
GROUP BY Dept
ORDER BY total_sales DESC
LIMIT 20;

-- Departments with highest average sales
SELECT 
    Dept,
    AVG(Weekly_Sales) as avg_weekly_sales,
    COUNT(*) as record_count
FROM train
GROUP BY Dept
HAVING COUNT(*) >= 100  -- Only departments with sufficient data
ORDER BY avg_weekly_sales DESC
LIMIT 15;

-- 5. Date Range Analysis
-- Understand the temporal coverage of data

-- Sales by year
SELECT 
    EXTRACT(YEAR FROM Date) as year,
    COUNT(*) as record_count,
    COUNT(DISTINCT Store) as active_stores,
    COUNT(DISTINCT Dept) as active_departments,
    SUM(Weekly_Sales) as total_sales,
    AVG(Weekly_Sales) as avg_weekly_sales
FROM train
GROUP BY EXTRACT(YEAR FROM Date)
ORDER BY year;

-- Sales by month
SELECT 
    EXTRACT(MONTH FROM Date) as month,
    COUNT(*) as record_count,
    AVG(Weekly_Sales) as avg_weekly_sales,
    SUM(Weekly_Sales) as total_sales
FROM train
GROUP BY EXTRACT(MONTH FROM Date)
ORDER BY month;

-- 6. Holiday Impact Analysis
-- Basic analysis of holiday vs non-holiday sales

-- Holiday vs Non-Holiday sales comparison
SELECT 
    IsHoliday,
    COUNT(*) as record_count,
    AVG(Weekly_Sales) as avg_weekly_sales,
    SUM(Weekly_Sales) as total_sales,
    MIN(Weekly_Sales) as min_sales,
    MAX(Weekly_Sales) as max_sales
FROM train
GROUP BY IsHoliday;

-- Holiday weeks identification
SELECT DISTINCT 
    Date,
    IsHoliday
FROM train
WHERE IsHoliday = TRUE
ORDER BY Date;

-- 7. Data Completeness Check
-- Verify data completeness across stores and time periods

-- Check if all stores have data for all time periods
SELECT 
    Store,
    COUNT(DISTINCT Date) as unique_dates,
    MIN(Date) as first_date,
    MAX(Date) as last_date
FROM train
GROUP BY Store
ORDER BY unique_dates DESC;

-- Check department coverage by store
SELECT 
    Store,
    COUNT(DISTINCT Dept) as unique_departments
FROM train
GROUP BY Store
ORDER BY unique_departments DESC;
