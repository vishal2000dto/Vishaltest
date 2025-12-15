# aiops

Top Level will be all the Modules/Services

Current State
- ai (service_desk, noc_desk) (fastapi)
- copilot-infra (fastapi)
- backend (backend of frontend (user logins, organizations, saving of chats) ) (fastapi)
- infra (terraform)
- frontend (react)

Future State
- channels (monolithic) - Email, SMS, WhatsApp, Voice
- integrations (monolithic) - ITOM, ITSM, INTUNES, PBX


### Gitflow

We have two environments production and staging

#### Production Branch: main
#### Staging Branch: staging

Gitflow:
1. Dev creates a feature branch
2. Dev creates a PR from feature branch to staging
3. PR gets approved by another dev
4. PR gets merged into staging
5. CI/CD kicks in and deploys the code to staging environment
6. Dev/QA tests in staging environment
7. Dev creates a PR to main
8. PR is merged
9. CI/CD deploys the PR to production environment
10. Dev/QA validates the feature in production env

#### Setup Branch Protection Rules



# AIPOS Project Setup Guide

This guide outlines the steps required to run the AIPOS project locally, which includes components such as AI, frontend, backend, and copilot.

## Prerequisites

- **pnpm**: Needed for package management.
- **ngrok**: Used for exposing local servers to the internet.
- **Twilio**: Required for phone call setup.
- Database access for configuration settings.

## Repository Structure

- `ai`: Contains AI backend code.
- `frontend`: Houses frontend code.
- `backend`: Includes product backend code.
- `copilot`: Comprises Copilot platform backend (not AI).
- `cli`: Comprises of Admin UI & CLI for Onboarding

## Setup Instructions

### **Admin UI for onboarding local setup**
1. **Navigate** to the `cli` directory.
2. **Install** Create a new python venv and run `poetry install`, then do a `prisma generate` 
3. **Start** the development server with `poetry run python gradio_app.py`.

### **Frontend Setup**
1. **Navigate** to the `frontend` directory.
2. **Install** dependencies with `pnpm install`.
3. **Start** the development server with `pnpm dev`.

### **Online Meeting Integration**
1. **Start ngrok** at port 8003 using `ngrok http 8003`.
2. **Update** the `env.local.servicedesk` file, replacing `COPILOT_PUBLIC_URL` with the new ngrok link and the WebSocket URL as `wss://{ngrok without http}`.

### **Copilot Backend Setup**
1. **Navigate** to the `copilot` directory.
2. **Run** the setup script with `./run setup`.
3. **Start** the Copilot service desk development server with `./run dev_service_desk`.

### **Phone Call Setup**
1. **Access** Twilio's "Active Numbers" section.
2. **Assign** an active number to the "Saurab Dev" TwiML application.
3. **Verify** the user you log in with has the phone number assigned to "Saurab Dev". Check this in the `config org` in the database.

### **Backend Setup**
1. **Navigate** to the `backend` directory.
2. **Run** the setup script with `./run setup`.
3. **Start** the backend development server with `./run dev`.

### **Accessing the Application**
1. **Open** a web browser and go to `http://localhost:8003`.
2. **Wait** for the UI to load; refresh if necessary.
