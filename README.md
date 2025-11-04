# google-meet-recorder
An automated Google Meet recorder using FFmpeg, VB-Cable, and Python
# 🤖 Google Meet Recorder Bot

This project automates joining Google Meet sessions and records both **audio** and **video** using Selenium and FFmpeg.  
It stores meeting details (metadata) in **MongoDB Atlas** for later access.

---

## 🧠 Features

- Automatically joins Google Meet links
- Records both **screen and system audio**
- Supports **microphone input + system output** (via VB-Audio Virtual Cable)
- Saves recordings as `.mp4` files
- Logs metadata in **MongoDB Atlas**
- Uses a **dedicated Chrome profile** for persistent login
- Environment variables are safely managed with `.env`

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Selenium** (browser automation)
- **FFmpeg** (audio/video recording)
- **MongoDB Atlas** (metadata storage)
- **dotenv** (for environment configuration)

---

## ⚙️ Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
2. Install Chrome
Ensure that Google Chrome is installed in the default path:

C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
3. Install ChromeDriver

If you already have chromedriver.exe, place it in the project root.

Or let Selenium automatically install it via webdriver_manager.

4. Install VB-Audio Virtual Cable (for system audio)

Download from VB Audio

Set both Input and Output to the virtual cable in Windows Sound Settings.

🔐 Environment Setup

Create a .env file in the project root:

# .env
MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/
DATABASE_NAME=meet_recordings
COLLECTION_NAME=metadata

🧭 Chrome Profile Setup

Use a dedicated Chrome profile so the bot can stay logged in to Google Meet without relogging.

Create a profile directory:

C:\BotChromeProfile

Then open Chrome manually using this command once:

"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\BotChromeProfile"

▶️ Running the Bot

Once everything is configured, simply run:

python main.py

📂 Project Structure
google-meet-recorder/
│
├── main.py                # Main entry point
├── browser_handler.py     # Selenium browser automation
├── recorder.py            # Handles FFmpeg recording
├── db_handler.py          # MongoDB metadata logging
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (not committed)
├── .gitignore             # Files to ignore
└── chromedriver.exe       # Optional: local ChromeDriver
🧰 Example MongoDB Metadata
{
  "meeting_id": "tph-pstn-nxj",
  "recording_path": "recordings/meet_2025_11_04.mp4",
  "timestamp": "2025-11-04T12:15:00Z",
  "duration_minutes": 30
}
