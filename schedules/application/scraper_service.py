import time
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from lxml import etree

from schedules.domain.ports.schedule_scraper_port import ScheduleScraperPort


class SAESScraperService(ScheduleScraperPort):
    """Adaptador de scraping para SAES usando Selenium - Arquitectura Hexagonal
    
    Implementa ScheduleScraperPort para obtener horarios desde el sistema SAES de UPIICSA.
    Este es un adaptador externo (infrastructure) que conecta con un sistema legacy.
    """
    
    def __init__(self, session_id: str, token: str, domain: str = "www.saes.upiicsa.ipn.mx"):
        self.session_id = session_id
        self.token = token
        self.domain = domain
        self.driver = None
        
    def _init_driver(self):
        """Inicializa el driver de Firefox en modo headless"""
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        try:
            self.driver = webdriver.Firefox(service=FirefoxService(), options=firefox_options)
        except WebDriverException as e:
            raise RuntimeError(f"No se pudo iniciar Firefox/Geckodriver: {e}")
        
    def _setup_cookies(self):
        """Configura las cookies de autenticación en el navegador"""
        self.driver.get(f'https://{self.domain}/')
        
        cookies = [
            {'name': '.ASPXFORMSAUTH', 'value': self.token, 'domain': self.domain},
            {'name': 'ASP.NET_SessionId', 'value': self.session_id, 'domain': self.domain},
            {'name': 'AspxAutoDetectCookieSupport', 'value': '1', 'domain': self.domain},
        ]
        
        for cookie in cookies:
            self.driver.add_cookie(cookie)
            
        self.driver.refresh()
        
        
    def _navigate_to_schedules(self):
        """Navega a la página de horarios"""
        try:
            element_academica = self.driver.find_element(By.XPATH, '//a[@href="/Academica/default.aspx"]')
            element_academica.click()
            
            horarios_link = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Horarios de Clases')]")
            horarios_link.click()
            
        except NoSuchElementException as e:
            raise RuntimeError(f"No se encontró elemento de navegación a horarios: {e}")
        
    def _navigate_to_availability(self):
        """Navega a la página de ocupabilidad"""
        try:
            element_academica = self.driver.find_element(By.XPATH, '//a[@href="/Academica/default.aspx"]')
            element_academica.click()
            
            ocupabilidad_link = self.driver.find_element(By.XPATH, '//a[@href="/Academica/Ocupabilidad_grupos.aspx"]')
            ocupabilidad_link.click()
            
            radio_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'ctl00_mainCopy_rblEsquema_0'))
            )
            radio_button.click()
        except NoSuchElementException as e:
            raise RuntimeError(f"No se encontró elemento de navegación a ocupabilidad: {e}")
        except Exception as e:
            raise RuntimeError(f"Fallo al preparar página de ocupabilidad: {e}")
        
    def download_schedules(
        self,
        career: str,
        career_plan: str,
        plan_periods: List[int],
        shift: Optional[str] = None,
        sequence: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Descarga horarios del SAES
        
        Args:
            career: Código de carrera
            career_plan: Código del plan de estudios
            plan_periods: Lista de períodos (1-10)
            shift: Turno específico (opcional)
            sequence: Secuencia específica (opcional)
            
        Returns:
            Lista de cursos con su información de horario
        """
        courses = []
        
        try:
            self._init_driver()
            self._setup_cookies()
            self._navigate_to_schedules()
            
            # Seleccionar carrera
            
            carrera_select = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_Filtro_cboCarrera'))
            carrera_select.select_by_value(career)
            
            
            # Seleccionar plan
            plan_select = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_Filtro_cboPlanEstud'))
            plan_select.select_by_value(career_plan)
            
            
            # Iterar por cada período
            for periodo in plan_periods:
                periodo_str = str(periodo)
                
                periodo_select = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_Filtro_lsNoPeriodos'))
                periodo_select.select_by_value(periodo_str)
                
                
                # Obtener turnos disponibles
                turnos_disponibles = [
                    option.get_attribute("value") 
                    for option in Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_Filtro_cboTurno')).options
                ]
                
                if shift:
                    turnos_disponibles = [shift] if shift in turnos_disponibles else []
                    
                for turno in turnos_disponibles:
                    
                    turno_select = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_Filtro_cboTurno'))
                    turno_select.select_by_value(turno)
                    
                    
                    # Obtener secuencias disponibles
                    secuencias_disponibles = [
                        option.get_attribute("value")
                        for option in Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_lsSecuencias')).options
                    ]
                    
                    if sequence:
                        secuencias_disponibles = [sequence] if sequence in secuencias_disponibles else []
                        
                    for secuencia in secuencias_disponibles:
                        
                        if secuencia == 'Todo':
                            continue
                            
                        secuencia_select = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_lsSecuencias'))
                        secuencia_select.select_by_value(secuencia)
                        
                        
                        # Extraer datos de la página
                        page_html = self.driver.page_source
                        courses.extend(self._parse_schedules(
                            page_html, 
                            secuencia, 
                            career=career,
                            plan=career_plan,
                            shift=turno
                        ))
                        
        except Exception as e:
            print(f"Error en download_schedules: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                
        return courses
    
    def download_availability(
        self,
        career: str,
        career_plan: str
    ) -> List[Dict[str, Any]]:
        """
        Descarga la disponibilidad de cursos del SAES
        
        Args:
            career: Código de carrera
            career_plan: Código del plan de estudios
            
        Returns:
            Lista de disponibilidades por curso
        """
        availabilities = []
        
        try:
            self._init_driver()
            self._setup_cookies()
            self._navigate_to_availability()
            
            
            carrera_dropdown = Select(self.driver.find_element(By.ID, 'ctl00_mainCopy_dpdcarrera'))
            carrera_dropdown.select_by_value(career)
            
            
            plan_dropdown = Select(self.driver.find_element(By.ID, "ctl00_mainCopy_dpdplan"))
            plan_dropdown.select_by_value(career_plan)
            
            
            # Extraer datos de disponibilidad
            page_html = self.driver.page_source
            availabilities = self._parse_availability(page_html)
            
        except Exception as e:
            print(f"Error en download_availability: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                
        return availabilities
    
    def _parse_schedules(self, page_html: str, sequence: str, career: str, plan: str, shift: str) -> List[Dict[str, Any]]:
        """Parsea el HTML de horarios y extrae la información de los cursos"""
        courses = []
        
        dom = etree.HTML(str(BeautifulSoup(page_html, 'html.parser')))
        raw_courses = dom.xpath('//table[@id="ctl00_mainCopy_dbgHorarios"]//tr')[1:]
        
        for raw_course in raw_courses:
            try:
                sequence_text = raw_course.xpath('./td/text()')[0].strip().upper()
                
                if sequence_text != sequence:
                    continue
                    
                subject = raw_course.xpath('./td/text()')[1].strip()
                teacher = raw_course.xpath('./td/text()')[2].strip().upper()
                
                # Extraer horario
                schedule = self._extract_schedule(raw_course)
                
                # Extraer level y semester de la sequence (formato: 4CM40)
                # 4 = level, C = career, M = shift, 40 = semester
                level = sequence_text[0] if len(sequence_text) > 0 else ''
                semester = sequence_text[3:] if len(sequence_text) > 3 else ''
                
                course = {
                    'sequence': sequence_text,
                    'subject': subject,
                    'teacher': teacher,
                    'schedule': schedule,
                    'plan': plan,
                    'level': level,
                    'career': career,
                    'shift': shift,
                    'semester': semester,
                    'required_credits': 0.0,  # No disponible en el scraper
                    'teacher_positive_score': 0.0,  # No disponible en el scraper
                }
                
                courses.append(course)
                
            except Exception as e:
                print(f"Error parsing course: {e}")
                continue
                
        return courses
    
    def _extract_schedule(self, raw_course) -> List[Dict[str, str]]:
        """Extrae el horario de un curso"""
        sessions = []
        days = raw_course.xpath('./td/text()')[5:-1]
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        for session, day in zip(days, day_names):
            session = session.strip()
            if session:
                start_time, end_time = session.split('-')
                sessions.append({
                    'day': day,
                    'start_time': start_time,
                    'end_time': end_time,
                })
                
        return sessions
    
    def _parse_availability(self, page_html: str) -> List[Dict[str, Any]]:
        """Parsea el HTML de disponibilidad y extrae la información"""
        availabilities = []
        
        dom = etree.HTML(str(BeautifulSoup(page_html, 'html.parser')))
        raw_courses = dom.xpath('//table[@id="ctl00_mainCopy_GrvOcupabilidad"]//tr')[1:]
        
        for raw_course in raw_courses:
            try:
                sequence = raw_course.xpath('./td/text()')[0].strip().upper()
                subject = raw_course.xpath('./td/text()')[2].strip().upper()
                availability = int(raw_course.xpath('./td/text()')[6].strip())
                
                availabilities.append({
                    'sequence': sequence,
                    'subject': subject,
                    'availability': availability,
                })
                
            except Exception as e:
                print(f"Error parsing availability: {e}")
                continue
                
        return availabilities
