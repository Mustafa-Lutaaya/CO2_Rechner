# CO₂ Spar Rechner – Frontend Interface
This is the frontend interface for the CO₂ Spar Rechner system.

It serves as the public-facing component of the project, developed to visualize, track, and promote CO₂ savings through user interactions.

Built using FastAPI, MongoDB, and Jinja2, this interface shares the PostgreSQL database (used by the backend) to fetch and display clothing item data

It then uses MongoDB to store session interactions and logs.

## It depends on the backend for:

- Authentication

- Clothing item data (from PostgreSQL)

## Then Handles:

- User sessions

- CO₂ tracking

- Session persistence (via MongoDB)
independently.


## Tech Stack

| Component       | Purpose                                  |
| --------------- | ---------------------------------------- |
| **FastAPI**     | Web routing & form handling              |
| **MongoDB**     | NoSQL database for session and item data |
| **Jinja2**      | HTML templating engine for dynamic UI    |
| **HTML/CSS/JS** | Frontend design & user interaction       |
| **dotenv**      | Environment variable management          |
| **Python**      | Core programming language                |
| **Docker**      | Containerization   

## Authentication & User Flow
- Login: Handled by the backend, which sets a secure cookie (user_name) that the frontend reads for personalization.

- Logout: /main/logout route clears the session cookie and resets MongoDB session data.

- User Session Logs: MongoDB stores session-based item selections, totals, and equivalencies.

## Routes Overview
| Route             | Purpose                                        |
| ----------------- | ---------------------------------------------- |
| `/`               | Demo page for anonymous interaction            |
| `/main`           | Main session interface (requires login cookie) |
| `/main/reset`     | Saves session, resets local counters           |
| `/main/logout`    | Logs session to MongoDB, clears user           |

## Admin Routes
| `/main/reset_DBS` | Admin: Resets all item counts in DB            |
| `/main/clear_SOS` | Admin: Clears all MongoDB sessions             |


## Maintainer : Mustafa Lutaaya