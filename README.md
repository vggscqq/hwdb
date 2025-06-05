# hwinfo-db

A hardware information database and dashboard for tracking PC hardware configurations.

## Description

hwinfo-db is a web application that allows you to:
- Store hardware information about multiple PCs in a database
- View all PCs in a dashboard with collapsible tiles
- See detailed hardware information for each PC

The application consists of:
- A Flask web application with both frontend and API functionality
- A SQLite database for data storage

## Features

- **Dashboard with PC Tiles**: All PCs are displayed as tiles on the main screen
- **Collapsible Tiles**: Each PC tile can be expanded/collapsed to show more/less information
- **Short Info Display**: When collapsed, tiles show basic information (hostname, CPU, RAM)
- **Extended Info Display**: When expanded, tiles show detailed hardware information including:
  - Mainboard details
  - RAM configuration
  - GPU information
  - Disk information
  - Screen resolution
  - Serial numbers

## Installation

1. Clone this repository:
```
git clone https://git.vgscq.cc/vgscq/hwinfo-db.git
cd hwinfo-db
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

### Using Devfile

This project includes a devfile.yaml that can be used with compatible development environments:

```
# Install dependencies
devfile install

# Run tests
devfile test
```

## Usage

1. Start the application server:
```
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. The dashboard will load and display all PCs in the database as tiles.

## API Endpoints

The application provides the following API endpoints:

- `POST /submit`: Submit hardware information for a PC
- `GET /pcs`: Get a list of all PCs in the database
- `GET /pc/<pc_id>`: Get detailed information for a specific PC

## Testing

Run the application tests:
```
python test_app.py
```

## Project Structure

- `app.py`: Flask application with frontend and API functionality
- `schema.sql`: SQL schema for the database
- `pcs.db`: SQLite database file (created automatically)
- `test_app.py`: Unit tests for the application

## License

This project is open source and available under the MIT License.
