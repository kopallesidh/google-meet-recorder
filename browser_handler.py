from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def initialize_driver():
    """
    Launches Chrome using the dedicated 'BotChromeProfile'.
    This is the final, correct autonomous method.
    """
    print("🚀 Launching Chrome with the dedicated 'BotChromeProfile'...")
    chrome_options = Options()
    chrome_options.add_argument(r'--user-data-dir=C:\BotChromeProfile')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        if not os.path.exists(driver_path):
            print(f"❌ FATAL ERROR: 'chromedriver.exe' not found.")
            return None
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ WebDriver initialized successfully using the persistent bot profile.")
        return driver
    except Exception as e:
        print(f"❌ WebDriver initialization failed. Error: {e}")
        return None

def join_meet(driver, meet_link):
    """
    Navigates to the meet, handles pop-ups, and clicks the join button
    using the most modern and robust selectors.
    """
    print(f"🌐 Navigating to Google Meet: {meet_link}")
    driver.get(meet_link)
    
    print("... Allowing 10 seconds for the page to load all elements...")
    time.sleep(10)

    try:
        # Step 1: Handle any notification pop-ups first.
        try:
            not_now_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Not now')]"))
            )
            print("🔔 Dismissing 'desktop notifications' pop-up...")
            not_now_button.click()
            time.sleep(2)
        except Exception:
            print("✅ No 'desktop notifications' pop-up found.")

        # Step 2: Mute mic and camera using more robust selectors that check for multiple text variations.
        print("... Searching for Mute and Camera buttons...")
        all_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
        mic_muted = False
        cam_off = False
        for button in all_buttons:
            label = button.get_attribute("aria-label")
            if label:
                if "microphone" in label.lower() and not mic_muted:
                    try:
                        button.click()
                        print("🎤 Microphone muted.")
                        mic_muted = True
                    except:
                        pass
                if "camera" in label.lower() and not cam_off:
                    try:
                        button.click()
                        print("📷 Camera turned off.")
                        cam_off = True
                    except:
                        pass
        
        time.sleep(2)

        # Step 3: Find and click the final join button.
        join_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Join now') or contains(., 'Ask to join')]"))
        )
        print(f"✅ Found join button: '{join_button.text}'. Clicking it...")
        join_button.click()
        
        return True
    except Exception as e:
        print(f"⚠️ Could not complete the joining process. The UI might have changed.")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# --- THIS IS THE FINAL get_participant_names FUNCTION ---
def get_participant_names(driver):
    """
    Scrapes the list of participants using a multi-fallback selector strategy
    to be as resilient as possible to UI changes.
    Returns a list of dictionaries with 'name' and 'id' for each participant.
    """
    print("🕵️‍♂️ Scraping participant names with the final robust method...")
    try:
        # Step 1: Find and click the "Participants" button.
        print("   - Step 1: Looking for the 'Participants' button...")
        
        # Try multiple selectors for the participants button
        participants_button = None
        button_selectors = [
            (By.XPATH, "//button[.//i[contains(text(), 'people')]]"),
            (By.XPATH, "//button[@aria-label[contains(., 'participant')]]"),
            (By.XPATH, "//button[@aria-label[contains(., 'People')]]"),
            (By.XPATH, "//button[contains(@aria-label, 'Show everyone')]"),
            (By.CSS_SELECTOR, "button[jsname='A5il2e']"),
        ]
        
        for selector_type, selector_value in button_selectors:
            try:
                participants_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                print(f"   - Found participants button using selector: {selector_value}")
                break
            except Exception as e:
                print(f"   - Selector failed: {selector_value}")
                continue
        
        if not participants_button:
            print("   - ❌ FATAL: Could not find the Participants button with any selector.")
            return [{"name": "participants_button_not_found", "id": "error"}]
        
        participants_button.click()
        print("   - Successfully clicked the 'Participants' button.")

        # Step 2: Wait for the participant list panel to become visible.
        print("   - Step 2: Waiting for the participant panel to appear...")
        
        # Try multiple panel selectors
        panel_visible = False
        panel_selectors = ["div.R3Gmyc", "div[role='list']", "div.Sfe7Qb", "div.CKKJIf"]
        
        for panel_selector in panel_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, panel_selector))
                )
                print(f"   - Participant panel found with selector: {panel_selector}")
                panel_visible = True
                break
            except:
                continue
        
        if not panel_visible:
            print("   - ⚠️ Warning: Could not confirm panel visibility, continuing anyway...")
        
        time.sleep(3) # Extra pause for all names to render inside the panel.

        # Step 3: Try to find participant names and IDs using multiple modern selectors.
        print("   - Step 3: Searching for participant names and IDs...")
        
        participants = []
        
        # Strategy 1: Try to find elements with data-participant-id (most reliable for IDs)
        print("   - Trying Strategy 1: Elements with data-participant-id...")
        participant_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-participant-id]")
        
        if participant_elements:
            print(f"   - Strategy 1 found {len(participant_elements)} elements with data-participant-id.")
            for elem in participant_elements:
                participant_id = elem.get_attribute("data-participant-id")
                # Try to extract name from within this element
                name = ""
                try:
                    # Try the most common modern selector
                    name_elem = elem.find_element(By.CSS_SELECTOR, "div.zWGUib")
                    name = name_elem.text.split('\n')[0] if name_elem.text else ""
                except:
                    try:
                        # Try fallback selector
                        name_elem = elem.find_element(By.CSS_SELECTOR, "div.Yx52jb")
                        name = name_elem.text.split('\n')[0] if name_elem.text else ""
                    except:
                        try:
                            # Try another fallback
                            name_elem = elem.find_element(By.CSS_SELECTOR, "span[data-self-name]")
                            name = name_elem.text.split('\n')[0] if name_elem.text else ""
                        except:
                            # Use the entire element's text as fallback
                            name = elem.text.split('\n')[0] if elem.text else ""
                
                if name and participant_id:
                    participants.append({'name': name, 'id': participant_id})
                    print(f"   - Found: {name} (ID: {participant_id})")
        
        # Strategy 2: If Strategy 1 failed, try finding name elements first
        if not participants:
            print("   - Strategy 1 yielded no results. Trying Strategy 2...")
            
            name_selectors = [
                "div.zWGUib",
                "div.Yx52jb",
                "span[data-self-name]",
                "div.GvcuGe",
                "div.wnPUne"
            ]
            
            name_elements = []
            for name_selector in name_selectors:
                name_elements = driver.find_elements(By.CSS_SELECTOR, name_selector)
                if name_elements:
                    print(f"   - Found {len(name_elements)} elements using selector: {name_selector}")
                    break

            if name_elements:
                for idx, elem in enumerate(name_elements):
                    name = elem.text.split('\n')[0] if elem.text else ""
                    if name:
                        # Try to find parent with data-participant-id
                        participant_id = f"unknown_{idx}"
                        try:
                            parent = elem.find_element(By.XPATH, "./ancestor::div[@data-participant-id]")
                            participant_id = parent.get_attribute("data-participant-id")
                        except:
                            pass
                        
                        participants.append({'name': name, 'id': participant_id})
                        print(f"   - Found: {name} (ID: {participant_id})")

        # Strategy 3: Last resort - get all text from the panel
        if not participants:
            print("   - Strategy 2 failed. Trying Strategy 3 (text extraction)...")
            try:
                panel = driver.find_element(By.CSS_SELECTOR, "div.R3Gmyc, div[role='list']")
                all_text = panel.text.split('\n')
                for idx, line in enumerate(all_text):
                    if line.strip() and len(line.strip()) > 1:
                        # Filter out common UI elements
                        if line.strip() not in ['In this call', 'Mute', 'Pin', 'More options']:
                            participants.append({'name': line.strip(), 'id': f'extracted_{idx}'})
                            print(f"   - Extracted: {line.strip()}")
            except Exception as e:
                print(f"   - Strategy 3 failed: {e}")

        if not participants:
            print("   - FATAL: All strategies failed. Could not find any participant name elements.")
            try:
                participants_button.click() # Attempt to close the panel before failing.
            except:
                pass
            return [{"name": "scraping_failed_no_elements", "id": "error"}]

        print(f"   - Success! Found {len(participants)} participant elements.")
        
        # Step 4: Click the button again to close the panel.
        print("   - Step 4: Closing the participant panel...")
        try:
            participants_button.click()
        except:
            print("   - Could not close panel, continuing anyway...")
        
        print(f"✅ Successfully scraped {len(participants)} participants:")
        for p in participants:
            print(f"   📋 Name: {p['name']}, ID: {p['id']}")
        
        return participants if participants else [{"name": "no_participants_found", "id": "error"}]
        
    except Exception as e:
        print(f"❌ A critical error occurred during the scraping process.")
        print(f"   This usually means a button or panel was not found.")
        print(f"   Error details: {e}")
        import traceback
        traceback.print_exc()
        return [{"name": "scraping_failed", "id": "error"}]

# --- HELPER FUNCTION FOR BACKWARD COMPATIBILITY ---
def get_participant_names_only(driver):
    """
    Helper function for backward compatibility.
    Returns only participant names as a list of strings.
    Deduplicates participants by their ID to avoid counting the same person multiple times.
    
    Returns:
        list of str: List of unique participant names
    """
    participants = get_participant_names(driver)
    
    # Extract just the names from the dictionaries
    if participants and isinstance(participants[0], dict):
        # Deduplicate by ID to avoid counting same person multiple times
        seen_ids = set()
        unique_names = []
        
        for p in participants:
            if 'name' in p and 'id' in p:
                participant_id = p['id']
                # Only add if we haven't seen this ID before
                if participant_id not in seen_ids:
                    seen_ids.add(participant_id)
                    unique_names.append(p['name'])
        
        print(f"🔍 Deduplication: Found {len(participants)} total, {len(unique_names)} unique participants")
        return unique_names
    
    # Fallback for error cases
    return participants