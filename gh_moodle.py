from playwright.sync_api import sync_playwright
import os
import time
import sys

# Credenciales desde variables de entorno para seguridad en GH Actions
USERNAME = os.getenv("MOODLE_USER")
PASSWORD = os.getenv("MOODLE_PASSWORD")
# USERNAME = "fabricioarce"
# PASSWORD = "Arceroja.5"

if not USERNAME or not PASSWORD:
    print("Error: MOODLE_USER o MOODLE_PASSWORD no están configurados.")
    sys.exit(1)

def close_popups(page):
    """Sistema para cerrar pop-ups o modales comunes que podrían interferir."""
    try:
        popups = [
            'button[aria-label="Cerrar"]',
            '.modal-dialog .close',
            '.popover-region .close',
            '#action-menu-toggle-1'
        ]
        for selector in popups:
            if page.is_visible(selector):
                print(f"  [Anti-Noise] Cerrando pop-up: {selector}")
                page.click(selector)
                page.wait_for_timeout(500)
        page.keyboard.press("Escape")
    except:
        pass

def run():
    with sync_playwright() as p:
        print("Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("Navegando a Moodle login...")
        page.goto("https://moodle.ccsancarlos.com/login/index.php")

        print("Ingresando credenciales...")
        page.fill("input#username", USERNAME)
        page.fill("input#password", PASSWORD)

        print("Iniciando sesión...")
        page.click("button#loginbtn")

        try:
            page.wait_for_url("https://moodle.ccsancarlos.com/my/", timeout=15000)
            print("Sesión iniciada con éxito!")
        except Exception as e:
            print(f"Fallo al iniciar sesión: {e}")
            browser.close()
            sys.exit(1)

        # UNA SOLA PASADA (sin while True para GH Actions)
        print("\nIniciando ciclo de navegación única...")
        close_popups(page)
        
        try:
            # Navegar a "Mis cursos" para asegurar visibilidad
            print("Accediendo a la lista de cursos...")
            page.goto("https://moodle.ccsancarlos.com/my/courses.php", timeout=60000)
            page.wait_for_load_state("networkidle")

            if page.is_visible('div[data-course-id="77"] a'):
                print("Entrando al curso ID 77...")
                page.click('div[data-course-id="77"] a', timeout=10000)
                page.wait_for_load_state("networkidle")
            else:
                print("No se encontró el curso ID 77 en la página principal.")
                
            close_popups(page)

            # Asegurar que el sidebar esté abierto
            if not page.is_visible('#course-index'):
                print("Abriendo barra lateral...")
                page.click('button[data-target="theme_boost-drawers-courseindex"]', timeout=5000)
                page.wait_for_timeout(1000)

            # Iterar por las secciones una vez
            print("Iterando por las secciones del sidebar...")
            links = page.query_selector_all('#course-index .courseindex-link')
            
            for i in range(len(links)):
                try:
                    close_popups(page)
                    current_links = page.query_selector_all('#course-index .courseindex-link')
                    if i >= len(current_links): break
                        
                    section = current_links[i]
                    section_text = section.inner_text().strip()
                    if not section_text or "General" in section_text: continue
                        
                    print(f"  - Click en sección {i+1}: {section_text}")
                    section.scroll_into_view_if_needed()
                    section.click()
                    page.wait_for_timeout(2000) 
                except Exception as e:
                    print(f"  - Error en sección {i+1}: {e}")

            print("Ciclo completado con éxito.")
            
        except Exception as e:
            print(f"Error durante el ciclo: {e}")
            browser.close()
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    run()
