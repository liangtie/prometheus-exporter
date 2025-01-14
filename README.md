# Flask Project

This project is a Flask application designed to receive and process `DataBuriedPoint` data into a structured format called `data_buried_point`.

## Project Structure

```
flask-project
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── controllers
│   │   └── data_controller.py
│   ├── models
│   │   └── data_buried_point.py
│   └── services
│       └── data_service.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-project
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python app/main.py
```

The server will start, and you can send requests to the endpoints defined in the `data_controller.py` file to process `DataBuriedPoint` data.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.