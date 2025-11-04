import time
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from browser_handler import initialize_driver, join_meet, get_participant_names_only

from browser_handler import initialize_driver, join_meet, get_participant_names
from recorder import Recorder
from gcp_handler import upload_to_gcs
from db_handler import store_metadata

# --- YOUR NAME AS IT APPEARS IN GOOGLE MEET ---
# This is crucial for the bot to identify the other participant.
# Please check how your name appears in the participant list and enter it here.
YOUR_NAME_IN_MEET = "Kopalle Sidhartha" 

def main():
    """
    Autonomous bot that:
    1. Deduces the partner_id by finding the other person in the meeting.
    2. Records the start and end time of the session.
    3. Saves the meeting URL as the meeting_id.
    """
    
    print("🧹 Closing any existing Chrome processes...")
    os.system("taskkill /F /IM chrome.exe >nul 2>&1")
    time.sleep(2)
    
    load_dotenv()
    
    meet_link = "https://meet.google.com/tdd-mikb-rko"
    local_filename = None
    start_time = None
    end_time = None

    driver = initialize_driver()
    if not driver:
        return

    try:
        if not join_meet(driver, meet_link):
            return

        print("⏳ Waiting to be admitted to the meeting room...")
        leave_button_selector = "button[aria-label='Leave call']"
        
        try:
            WebDriverWait(driver, 300).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, leave_button_selector))
            )
            print("✅ Successfully entered the meeting room.")
            # --- CAPTURE START TIME ---
            start_time = datetime.utcnow()
            print(f"   Start time captured: {start_time.isoformat()}Z")

        except TimeoutException:
            print("❌ Was not admitted after 5 minutes. Halting.")
            return

        # --- DEDUCE THE PARTNER_ID ---
        print("🕵️‍♂️ Determining the partner_id...")
        all_participants = get_participant_names_only(driver)  # Changed here
        
        # Filter out your own name from the list
        other_participants = [name for name in all_participants if name != YOUR_NAME_IN_MEET]
        
        partner_id = None
        if len(other_participants) == 1:
            # If there's exactly one other person, we've found our partner.
            partner_id = other_participants[0]
            print(f"   Partner ID identified as: {partner_id}")
        elif len(other_participants) > 1:
            # If there's more than one, we save them all as a comma-separated string.
            partner_id = ", ".join(other_participants)
            print(f"   Multiple participants found: {partner_id}")
        else:
            # If no one else is there, we note it.
            partner_id = "No other participants found"
            print("   Warning: Could not identify any other participants.")

        # --- START RECORDING ---
        meeting_id_uuid = str(uuid.uuid4()) # We still need a unique ID for the filename
        local_filename = f"recording_{meeting_id_uuid}.mp4"
        recorder = Recorder(local_filename)
        recorder.start_recording()

        print(f"🟢 Recording started. Monitoring meeting...")
        while True:
            try:
                driver.find_element(By.CSS_SELECTOR, leave_button_selector)
                time.sleep(10)
            except NoSuchElementException:
                print("✅ Meeting has ended.")
                # --- CAPTURE END TIME ---
                end_time = datetime.utcnow()
                print(f"   End time captured: {end_time.isoformat()}Z")
                break

        recorder.stop_recording()

        gcs_destination_path = f"recordings/{local_filename}"
        gcs_uri = upload_to_gcs(local_filename, gcs_destination_path)
        if gcs_uri:
            # Pass all the new data points to the metadata storage function
            store_metadata(
                partner_id=partner_id,
                meeting_id=meet_link, # Using the URL as the meeting ID
                start_time=start_time,
                end_time=end_time,
                gcs_url=gcs_uri
            )
        else:
            print("❌ Skipping metadata storage.")

    finally:
        if 'driver' in locals() and driver:
            driver.quit()
            print("✅ Browser closed.")
        
        if local_filename and os.path.exists(local_filename):
            full_path = os.path.join(os.getcwd(), local_filename)
            print(f"✅ Recording saved successfully to: {full_path}")
        else:
            print("⚠️ No recording file was found or created.")

    print("\n🎉 Process finished.")

if __name__ == "__main__":
    main()