# Warewolf - Warehouse Broker Platform

Warewolf is a web application that connects warehouse owners with space seekers, similar to NoBroker but focused on warehouse properties. The platform serves as a broker-of-brokers, facilitating seamless connections between property owners, clients, and brokers.

## Known Issues and Fixes

### Python 3.12 Compatibility with python-jose

When running on Python 3.12, you might encounter a SyntaxError in the jose.py file:

```
SyntaxError: Missing parentheses in call to 'print'. Did you mean print(...)?
```

This is due to Python 2 style print statements in the jose.py file. To fix this issue:

1. Run the included `fix_jose.py` script after installing dependencies:
   ```
   python fix_jose.py
   ```

2. Alternatively, you can manually edit the jose.py file in your virtual environment's site-packages and add parentheses to all print statements.

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

4. Fix python-jose for Python 3.12 compatibility (if needed):
   ```
   python fix_jose.py
   ```

5. Run the application:
   ```
   uvicorn app.main:app --reload
   ```
   Or use the provided run.py script:
   ```
   python run.py
   ```

6. Access the application at `http://localhost:8000`

## Dependencies

The application uses the following key dependencies:

- **FastAPI (0.110.0)**: Modern, high-performance web framework
- **SQLAlchemy (2.0.27)**: SQL toolkit and ORM
- **Pydantic (2.5.2)**: Data validation and settings management
- **Jinja2 (3.1.3)**: Template engine
- **Python-Jose (3.3.0)**: JSON Web Token implementation
- **BeautifulSoup4 (4.12.2)**: Web scraping library

See requirements.txt for the full list of dependencies.

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