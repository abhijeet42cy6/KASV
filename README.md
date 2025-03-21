# Warewolf - Warehouse Broker Platform

Warewolf is a web application that connects warehouse owners with space seekers, similar to NoBroker but focused on warehouse properties. The platform serves as a broker-of-brokers, facilitating seamless connections between property owners, clients, and brokers.

## Features

- **For Warehouse Owners:**
  - List warehouse properties
  - Manage property details
  - Connect with potential clients

- **For Space Seekers:**
  - Search for available warehouses
  - Filter by location, size, and price
  - Contact warehouse owners directly

- **Web Scraping Integration:**
  - Scrape warehouse listings from external sources
  - Import scraped data into the platform
  - Enhance the property database

## Tech Stack

- **Backend:** FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Web Scraping:** BeautifulSoup, Requests
- **Templating:** Jinja2

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/warewolf.git
   cd warewolf
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

5. Access the application at `http://localhost:8000`

## Usage

### For Warehouse Owners

1. Register as a Warehouse Owner
2. Add your warehouse properties with details
3. Manage your listings and respond to inquiries

### For Space Seekers

1. Register as a Space Seeker
2. Search for warehouses based on your requirements
3. View property details and contact owners

### Web Scraping Dashboard

1. Configure scraping parameters (city, area type, etc.)
2. Run the scraper to fetch warehouse listings
3. Review and import scraped data into the platform

## Project Structure

```
app/
├── main.py            # FastAPI application
├── models/            # Data models
├── routers/           # API routes
│   ├── auth.py        # Authentication routes
│   ├── warehouse.py   # Warehouse listing routes
│   └── scraping.py    # Web scraping routes
├── scraper/           # Web scraping functionality
│   └── scraper.py     # NoBroker-inspired scraper
├── templates/         # HTML templates
└── static/            # Static assets (CSS, JS)
```

## Development

This project is built with FastAPI and includes web scraping capabilities inspired by the [NoBroker Web Scraping project](https://github.com/tusharkumawat/Web-Scraping-NoBroker-Website/).

## License

This project is licensed under the MIT License - see the LICENSE file for details. 