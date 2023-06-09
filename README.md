# Setup Instructions

## Frontend

1. `cd nextjs`
1. Install node dependencies: `npm install`
1. Set up environment variables: `cp .env.local.example .env.local`
1. Run project: `npm run dev`


## Backend

### Initial setup

1. Set up environment variables (see below)
1. `cd backend`
1. Install python dependencies: `pip install -r requirements.txt`
1. Migrate database: `python manage.py migrate`
1. Create an admin user: `python manage.py createsuperuser`
1. Run server: `python manage.py runserver`

### Environment Variables

You need to export the following environment variables for the backend:

- `OPENSEA_API_KEY`

### Managing data

1. Visit /admin/ on the server to access admin panel
1. Collections of domains can be managed here
