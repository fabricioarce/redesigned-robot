from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser (set headless=False to see the actions)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to the Moodle login page
        print("Navigating to Moodle login page...")
        page.goto("https://moodle.ccsancarlos.com/login/index.php")

        # Fill in the login form
        print("Filling in credentials...")
        page.fill("input#username", "fabricioarce")
        page.fill("input#password", "Arceroja.5")

        # Click the login button
        print("Logging in...")
        page.click("button#loginbtn")

        # Wait for navigation to the personal area
        try:
            page.wait_for_url("https://moodle.ccsancarlos.com/my/", timeout=15000)
            print("Successfully logged in!")
        except Exception as e:
            print(f"Login failed: {e}")
            browser.close()
            return

        def close_popups():
            """System to close common pop-ups or modals that might interfere."""
            try:
                # Generic selectors for 'Close' buttons in Moodle
                popups = [
                    'button[aria-label="Cerrar"]',
                    '.modal-dialog .close',
                    '.popover-region .close',
                    '#action-menu-toggle-1' # Sometimes menus stay open
                ]
                for selector in popups:
                    if page.is_visible(selector):
                        print(f"  [Anti-Noise] Closing pop-up: {selector}")
                        page.click(selector)
                        page.wait_for_timeout(500)
                # Also try pressing Escape to clear some overlays
                page.keyboard.press("Escape")
            except:
                pass

        # Start the "closed circle" loop
        while True:
            print("\nEntering the course loop...")
            close_popups()
            
            # 1. Click on the course (ID 77)
            try:
                # Ensure the course is visible; if not, force navigation to dashboard
                if not page.is_visible('div[data-course-id="77"] a'):
                    print("Dashboard not visible or course not found. Navigating to 'Mis cursos'...")
                    page.goto("https://moodle.ccsancarlos.com/my/courses.php", timeout=60000)
                    page.wait_for_load_state("networkidle")

                print("Accessing course ID 77...")
                page.click('div[data-course-id="77"] a', timeout=10000)
                page.wait_for_load_state("networkidle")
            except Exception as e:
                print(f"Error accessing course: {e}. Restarting loop...")
                continue
            close_popups()

            # Ensure sidebar is open
            try:
                # We check for visibility and also wait a bit for any dynamic loading
                if not page.is_visible('#course-index'):
                    print("Sidebar is hidden. Clicking toggler...")
                    page.click('button[data-target="theme_boost-drawers-courseindex"]')
                    # Wait for the animation to finish (drawer transition usually ~300-500ms)
                    page.wait_for_timeout(1000)
                    
                # Robustness check: if it's still not open, try a fallback selector
                if not page.is_visible('#course-index'):
                     page.click('.drawer-toggler button')
                     page.wait_for_timeout(1000)
            except Exception as e:
                print(f"Could not handle sidebar: {e}")

            # 2. Touch each object in the sidebar list (nav#courseindex)
            print("Iterating through sidebar sections...")
            
            # Re-fetch links to ensure they are available
            links = page.query_selector_all('#course-index .courseindex-link')
            
            for i in range(len(links)):
                try:
                    close_popups()
                    # Re-fetch elements in each step to avoid staleness
                    current_links = page.query_selector_all('#course-index .courseindex-link')
                    if i >= len(current_links):
                        break
                        
                    section = current_links[i]
                    section_text = section.inner_text().strip()
                    if not section_text or "General" in section_text: # Skip empty or headers if needed
                        continue
                        
                    print(f"  - Clicking section {i+1}: {section_text}")
                    
                    section.scroll_into_view_if_needed()
                    section.click()
                    
                    # Wait for navigation or update
                    page.wait_for_timeout(3000) 
                    
                except Exception as e:
                    print(f"  - Could not click section {i+1}: {e}")

            # 3. Go to "Mis cursos"
            print("Navigating back to 'Mis cursos'...")
            try:
                page.click('a[href="https://moodle.ccsancarlos.com/my/courses.php"]')
                page.wait_for_url("https://moodle.ccsancarlos.com/my/courses.php", timeout=5000)
            except:
                try:
                    # Fallback to direct navigation if clicking fails
                    # Increased timeout to 60s and added error handling
                    page.goto("https://moodle.ccsancarlos.com/my/courses.php", timeout=60000)
                except Exception as e:
                    print(f"Error navigating back to courses: {e}")
            
            print("Loop cycle complete. Restarting...")
            page.wait_for_timeout(3000)

if __name__ == "__main__":
    run()
