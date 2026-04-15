# ⚡ Energy Control System (ECS) Dashboard

**Distributed Energy Optimization Platform**  
Final project for the Distributed and Network Programming course.

Modern real-time dashboard for monitoring and managing a company's energy consumption using day-ahead optimization and intraday imbalance market corrections.

## ✨ Features

- Clean dark-themed responsive interface
- Interactive charts: electricity prices, demand forecast vs actual, energy source allocation
- Real-time battery State of Charge (SOC) visualization
- Intraday correction actions log
- Test scenarios results table (7 mandatory cases)
- Ready for integration with FastAPI backend + Kafka

## 📁 Project Structure

```bash
EnergyControlSystem/
├── frontend/                  # React + Vite + TypeScript + Tailwind + Recharts
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── data/
│   ├── public/
│   └── package.json
├── backend/                   # FastAPI services (in progress)
│   ├── ingestion/
│   ├── optimizer/
│   └── intraday/
├── docker-compose.yml
└── README.md
```
## 🚀 How to Run the Frontend

```bash 1. Go to frontend directory
# 1. Change the directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```
The dashboard will be available at: http://localhost:5173

## 🛠 Tech Stack (Frontend)

- React 18 + TypeScript
- Vite (fast build tool)
- Tailwind CSS
- Recharts – interactive charts
- Axios – API calls
- Lucide React – icons

## 👥 Team
e.neialov | RoleStudentFrontend & Visualization
--- | ---
ma.kalinin | Backend, DB & Kafka
p.troshkin | Optimization & Intraday Logic

## 📸 Screenshots
(Will be added after final integration)

- Daily Schedule with stacked bar chart
- Real-time Intraday Corrections
- Test Scenarios Results
- Input Data Panel

## 🔗 Links

Repository: https://github.com/Troshkins/EnergyControlSystem

Course: Distributed and Network Programming
