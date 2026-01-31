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

        # Retry logic for login page
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Navegando a Moodle login (Intento {attempt + 1}/{max_retries})...")
                # Increased timeout to 60 seconds
                page.goto("https://moodle.ccsancarlos.com/login/index.php", timeout=60000)
                break
            except Exception as e:
                print(f"Error cargando login: {e}")
                if attempt == max_retries - 1:
                    print("Se agotaron los intentos de conexión.")
                    browser.close()
                    sys.exit(1)
                time.sleep(5)

        print("Ingresando credenciales...")
        page.fill("input#username", USERNAME)
        page.fill("input#password", PASSWORD)

        print("Iniciando sesión...")
        page.click("button#loginbtn")

        try:
            page.wait_for_url("https://moodle.ccsancarlos.com/my/", timeout=30000)
            print("Sesión iniciada con éxito!")
        except Exception as e:
            print(f"Fallo al iniciar sesión: {e}")
            browser.close()
            sys.exit(1)

        # CICLO DE 20 REPETICIONES
        cycles = 20
        print(f"\nIniciando ciclo de {cycles} repeticiones para mantener actividad...")
        
        for cycle in range(cycles):
            print(f"\n--- CICLO {cycle + 1}/{cycles} ---")
            close_popups(page)
            
            try:
                # Navegar a "Mis cursos" para asegurar visibilidad y refrescar sesión
                print("Accediendo a la lista de cursos...")
                page.goto("https://moodle.ccsancarlos.com/my/courses.php", timeout=60000)
                page.wait_for_load_state("networkidle")

                # Intentar entrar al curso específico
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
                    try:
                        page.click('button[data-target="theme_boost-drawers-courseindex"]', timeout=5000)
                        page.wait_for_timeout(1000)
                    except:
                        print("No se pudo abrir sidebar (o ya estaba abierto).")

                # Iterar por las secciones
                print("Iterando por las secciones del sidebar...")
                links = page.query_selector_all('#course-index .courseindex-link')
                
                # Limitamos a visitar algunas secciones para no tardar demasiado por ciclo si hay muchas
                for i in range(len(links)):
                    try:
                        close_popups(page)
                        # Re-query elements to avoid stale handles
                        current_links = page.query_selector_all('#course-index .courseindex-link')
                        if i >= len(current_links): break
                            
                        section = current_links[i]
                        section_text = section.inner_text().strip()
                        if not section_text or "General" in section_text: continue
                            
                        # print(f"  - Click en sección {i+1}: {section_text}")
                        section.scroll_into_view_if_needed()
                        section.click()
                        # Breve espera entre clicks
                        page.wait_for_timeout(1000) 
                    except Exception as e:
                        pass # Ignorar errores en clicks individuales para no detener el ciclo

                print(f"Ciclo {cycle + 1} completado.")
                
                if cycle < cycles - 1:
                    wait_minutes = 3
                    print(f"Esperando {wait_minutes} minutos para el siguiente ciclo...")
                    time.sleep(wait_minutes * 60)
                
            except Exception as e:
                print(f"Error durante el ciclo {cycle + 1}: {e}")
                # No salimos, intentamos el siguiente ciclo tras una espera
                time.sleep(60)

        print("\nTodos los ciclos completados.")
        browser.close()

if __name__ == "__main__":
    run()
