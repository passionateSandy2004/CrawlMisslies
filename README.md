# E-Commerce Product Extraction Pipeline

Production-ready system for discovering e-commerce sites and extracting product data.

## Overview

This system consists of two main pipelines that run concurrently:

1. **Category Search Pipeline** - Discovers e-commerce sites and saves search URL templates
2. **Product Extraction Pipeline** - Extracts products using saved templates

## Architecture

```
finalDeploy/
├── main.py                          # Main entry point - runs both pipelines
├── LaunchPad/
│   ├── categorySearchPipeline.py    # Discovers e-commerce sites & templates
│   ├── productExtractionPipeline.py # Extracts products from URLs
│   ├── inputDataHandler.py          # Handles category/product input
│   ├── ecomFinding.py               # Google Custom Search API wrapper
│   └── universalSearch.py           # Discovers search URL patterns
├── Missile/
│   └── universalProductExtractor.py # Extracts product data from pages
└── requirements.txt                 # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file (or set environment variables):

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

Or copy `.env.example` and fill in your values:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Set Up Database

Run these SQL commands in Supabase SQL Editor:

```sql
-- Add last_extracted column to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS last_extracted TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS idx_products_last_extracted ON products(last_extracted);

-- Create extracted_urls table to track processed URLs
CREATE TABLE IF NOT EXISTS extracted_urls (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    constructed_url TEXT NOT NULL,
    products_found INTEGER DEFAULT 0,
    products_saved INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT FALSE,
    extracted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (template_id) REFERENCES search_url_templates(id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_extracted_urls_unique 
ON extracted_urls(product_id, template_id);

CREATE INDEX IF NOT EXISTS idx_extracted_urls_product_id ON extracted_urls(product_id);
CREATE INDEX IF NOT EXISTS idx_extracted_urls_template_id ON extracted_urls(template_id);
```

### 4. Add Initial Data

Use `inputDataHandler.py` to add categories and products:

```python
from LaunchPad.inputDataHandler import InputDataHandler

handler = InputDataHandler()
data = {
    "Electronics": ["laptop", "smartphone", "headphones"],
    "Fashion": ["shirt", "jeans", "shoes"]
}
handler.process_input_data(data)
```

Or from command line:
```bash
python LaunchPad/inputDataHandler.py
```

### 5. Run Production Pipeline

```bash
python main.py
```

## How It Works

### Category Search Pipeline

1. Gets oldest category (least recently updated)
2. Gets Nth product from category (cycles through 1st, 2nd, 3rd...)
3. Searches Google: "{category_name} {product_name}"
4. Discovers ~10 e-commerce sites
5. Converts sites to search URL templates
6. Saves templates to `search_url_templates` table
7. Updates category timestamp
8. Moves to next category (endless loop)

### Product Extraction Pipeline

1. Gets oldest product (least recently extracted)
2. Gets all search URL templates for product's category
3. Checks if URL already extracted (from `extracted_urls` table)
4. Replaces placeholder with product name (e.g., `{query}` → "laptop")
5. Extracts products from constructed URL
6. Saves products to `product_data` table
7. Saves URL to `extracted_urls` table
8. Updates product timestamp
9. Moves to next product (endless loop)

## Database Tables

### `categories`
- `category_id` (PK)
- `name`
- `latest_input` (timestamp)
- `latest_updated` (timestamp)

### `products`
- `product_id` (PK)
- `name`
- `category_id` (FK)
- `last_extracted` (timestamp) - **Needs to be added**

### `search_url_templates`
- `id` (PK)
- `search_url` (template with {query} placeholder)
- `category_id` (FK)

### `product_data`
- `id` (PK)
- `platform_url`
- `product_name`
- `original_price`
- `current_price`
- `product_url`
- `product_image_url`
- `description`
- `rating`
- `reviews`
- `in_stock`
- `brand`

### `extracted_urls`
- `id` (PK)
- `product_id` (FK)
- `template_id` (FK)
- `constructed_url`
- `products_found`
- `products_saved`
- `success`
- `extracted_at`

## Configuration

### Environment Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key

### API Keys

Google Custom Search API keys are set in `LaunchPad/ecomFinding.py`:
- `API_KEY` - Google API key
- `SEARCH_ENGINE_ID` - Google Search Engine ID

## Features

✅ **Continuous Operation** - Runs endlessly, processing all data
✅ **Resume Capability** - Resumes from where it left off after interruption
✅ **Duplicate Prevention** - Tracks extracted URLs to avoid re-extraction
✅ **Parallel Processing** - Both pipelines run concurrently
✅ **Auto-Recovery** - Restarts crashed threads automatically
✅ **Graceful Shutdown** - Handles Ctrl+C cleanly

## Troubleshooting

### "No products found"
- Add products using `inputDataHandler.py`

### "No templates found"
- Wait for Category Search Pipeline to discover templates
- Or add templates manually to `search_url_templates` table

### "Supabase connection failed"
- Check `SUPABASE_URL` and `SUPABASE_KEY` environment variables
- Verify your Supabase project is active

### "ChromeDriver not found"
- Install Chrome browser
- Selenium will automatically use installed Chrome

## Monitoring

The pipeline provides detailed logging:
- `[✓]` - Success
- `[✗]` - Error
- `[!]` - Warning
- `[*]` - Info
- `[⊘]` - Skipped (already processed)

## Production Deployment

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run database migrations (SQL above)
4. Add initial data (categories/products)
5. Run: `python main.py`

The system will run continuously, discovering new sites and extracting products automatically.

