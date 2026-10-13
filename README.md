# AI Healthcare Assistant

The **AI Healthcare Assistant** is a simple web application that provides general health information based on symptoms entered by the user. It uses Google's Gemini API to generate responses and stores previous interactions in a MySQL database.

The project was built using Python and Streamlit, with basic NLP techniques to process user input. It is intended for educational purposes only and is not a medical diagnosis tool.

**Technologies Used:** Python, Streamlit, Google Gemini API, MySQL, basic NLP.

## 1. What Does the Application Do?

The application allows users to describe their symptoms and receive general health information through a simple web interface.

Here's how it works:

1. The user enters a symptom description, such as "I have a mild headache and a runny nose."
2. The application checks the input and performs basic text preprocessing, including cleaning and keyword extraction.
3. A safety module checks for certain emergency-related phrases. If a matching phrase is found, the application displays urgent-care guidance without calling Gemini.
4. If no emergency phrase is detected, the symptom description is sent to the Gemini API to generate general health information.
5. The response is displayed on the screen, and the interaction is saved to MySQL when the database is available.
6. Users can open the History page to view previously saved interactions.

The application is designed to provide general information, not to diagnose conditions or recommend prescription treatments.

## 2. Project Architecture

The application is divided into small modules so that each part has a specific responsibility.

```text
AIHealthcareAssistant/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
│
├── database/
│   └── schema.sql
│
├── modules/
│   ├── __init__.py
│   ├── database.py
│   ├── gemini_service.py
│   ├── nlp_processor.py
│   └── safety.py
│
├── tests/
│   ├── test_nlp_processor.py
│   ├── test_safety.py
│   ├── test_gemini_service.py
│   └── test_database.py
│
└── interview-preparation/
    ├── project-explanation.md
    └── interview-questions.md
```

*This structure shows the intended organization. Keep only the files that have actually been created in the repository.*

### Role of Each File

- **`app.py`** — Provides the Streamlit interface and connects the different modules.
- **`nlp_processor.py`** — Validates the input, cleans the text, and identifies relevant keywords.
- **`safety.py`** — Contains the disclaimer, emergency phrase checks, and safety messages.
- **`gemini_service.py`** — Handles requests to the Gemini API and manages API errors.
- **`database.py`** — Connects to MySQL and saves or retrieves interaction history.
- **`schema.sql`** — Creates the database and the table used to store interactions.
- **`tests/`** — Contains tests for the application's main components.
- **`interview-preparation/`** — Contains notes for explaining the project and preparing for technical questions.

### Application Workflow

```text
User enters symptoms
        |
        v
Input validation and text preprocessing
        |
        v
Emergency phrase check
        |
        +---- Matching phrase found
        |          |
        |          v
        |    Display safety guidance
        |          |
        |          v
        |    Save interaction if possible
        |
        +---- No matching phrase
                   |
                   v
             Call Gemini API
                   |
                   v
             Display response
                   |
                   v
             Save to MySQL
                   |
                   v
             View in History
```

## 3. Technologies Used

| Technology | How it is used |
|---|---|
| Python | Handles the application's logic and connects the different modules. |
| Streamlit | Creates the web interface, input form, sidebar, and history page. |
| Google Gemini API | Generates general health information from the user's input. |
| MySQL | Stores symptom descriptions, AI responses, and timestamps. |
| Basic NLP | Performs text cleaning, input validation, and keyword extraction. |
| Pytest | Tests application components and error-handling behaviour. |

The NLP component uses basic text-processing techniques. It does not contain a trained medical model, and keyword matching should not be treated as a reliable method of identifying medical conditions.

## 4. Requirements

Before running the application, make sure the following are available:

- Python 3.10 or newer
- MySQL Server 8.x
- A Google Gemini API key
- VS Code or another code editor
- A terminal such as Windows PowerShell

MySQL Workbench can also be used to create the database and inspect stored records.

## 5. Set Up the Project

Open PowerShell and navigate to the project folder.

```powershell
cd path\to\AIHealthcareAssistant
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation, review the execution policy for your account before changing it.

## 6. Configure MySQL

Start the MySQL service and make sure you can connect to the server.

You can use an existing MySQL account or create a separate account for this application. A dedicated account with only the required database permissions is preferable to using the root account.

The application uses the following database configuration:

- **Database name:** `healthcare_assistant_db`
- **Table name:** `interactions`

## 7. Create the Database and Table

The SQL script is available at `database/schema.sql`.

Run it using the MySQL command-line client:

```powershell
Get-Content database\schema.sql |
    mysql -u YOUR_MYSQL_USERNAME -p
```

Replace `YOUR_MYSQL_USERNAME` with the MySQL account you use. Enter the password when prompted.

To check whether the database and table were created, run these SQL commands in MySQL Workbench or the MySQL client:

```sql
USE healthcare_assistant_db;

SHOW TABLES;

DESCRIBE interactions;
```

The `interactions` table stores:

- `id` — A unique ID for each interaction.
- `user_input` — The symptom description entered by the user.
- `ai_response` — The response generated by the AI.
- `created_at` — The date and time the interaction was saved.

## 8. Configure the Gemini API

The application uses Google's Gemini API to generate responses.

1. Visit [Google AI Studio](https://aistudio.google.com).
2. Sign in and create an API key.
3. Keep the key private and do not add it directly to your Python source code.

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add your own configuration:

```dotenv
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash

DB_HOST=localhost
DB_PORT=3306
DB_USER=YOUR_MYSQL_USERNAME
DB_PASSWORD=YOUR_MYSQL_PASSWORD
DB_NAME=healthcare_assistant_db
```

The model name is configurable, so it can be changed to another model available to your API key.

The `.env` file contains private credentials and should be excluded from Git using `.gitignore`. Only the placeholder configuration in `.env.example` should be uploaded to GitHub.

## 9. Run the Application

Once the dependencies, database, and environment variables are configured, start the application:

```powershell
streamlit run app.py
```

Streamlit normally opens the application in your browser at:

[http://localhost:8501](http://localhost:8501)

If the browser does not open automatically, enter the address manually.

You can then enter a sample symptom description, view the generated response, and check the History page to see whether the interaction was saved.

## 10. Run the Tests

The project uses Pytest to check individual components.

Run:

```powershell
python -m pytest
```

The tests can cover input validation, emergency phrase matching, Gemini error handling, and database query behaviour.

Where the tests use mocked API clients and database connections, they do not require a live Gemini API key or a running MySQL server. Actual integration tests may require additional configuration.

## 11. Common Problems

| Problem | What to check |
|---|---|
| Gemini API key is missing | Check the `.env` file and confirm that the application loads it. |
| API key is rejected | Verify the key in Google AI Studio and replace it if necessary. |
| Model not found | Choose a model currently available to your API key. |
| API quota exceeded | Check your usage limits and retry when appropriate. |
| MySQL connection failed | Check the MySQL service, hostname, port, and credentials. |
| Database or table not found | Run `database/schema.sql` and verify the table names. |
| Streamlit command not recognized | Activate the virtual environment and install the dependencies. |
| Response generated but not saved | Check the MySQL connection and the database error message. |

## 12. Safety and Privacy

This project is intended for learning and demonstration purposes.

- The application provides general health information and does not diagnose medical conditions.
- AI responses may contain errors or incomplete information and have not been medically verified.
- Emergency detection relies on simple phrase matching. It can miss serious situations or flag harmless text incorrectly.
- The absence of an emergency warning does not mean that symptoms are safe.
- For a medical emergency in India, call **112** or seek immediate medical care. Do not wait for an AI response.
- Do not enter names, phone numbers, addresses, or other identifying information.
- Symptom descriptions may contain sensitive health information and are sent to a third-party AI service when Gemini is called.
- The application may store symptom descriptions and generated responses in MySQL. Use fictional test data and avoid storing real patient records.
- The current version does not include user authentication or individual access controls for interaction history.

## 13. Future Improvements

Possible improvements include:

- Adding conversation sessions and better history management.
- Improving input validation and error messages.
- Adding user feedback for generated responses.
- Improving the interface and making it more accessible.
- Expanding automated tests for different inputs and failure scenarios.

These improvements can be added gradually as the project develops.

## Conclusion

The AI Healthcare Assistant demonstrates how a Python web application can combine a language model API, basic NLP, and a relational database in one workflow. It also provides practical experience with API integration, input validation, database operations, error handling, and automated testing.

The project is an educational demonstration of AI-assisted health information, not a replacement for qualified medical advice.