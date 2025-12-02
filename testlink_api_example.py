"""
testlink_api_example.py
TestLink API Integration Example
Demuestra la complejidad de integración con TestLink usando XML-RPC
"""

import xmlrpc.client
import json
from typing import Dict, List, Optional
from datetime import datetime


class TestLinkAPIClient:
    """Cliente para la API XML-RPC de TestLink"""
    
    def __init__(self, url: str, dev_key: str):
        """
        Inicializa el cliente de TestLink
        
        Args:
            url: URL completa del endpoint XML-RPC
                 (ej: http://example.com/lib/api/xmlrpc/v1/xmlrpc.php)
            dev_key: Developer key generada en TestLink
        """
        self.server = xmlrpc.client.ServerProxy(url)
        self.dev_key = dev_key
    
    def report_result(self, testcase_id: int, testplan_id: int, 
                     build_id: int, status: str, notes: str = "") -> Dict:
        """
        Reporta el resultado de una prueba
        
        Args:
            testcase_id: ID del caso de prueba
            testplan_id: ID del plan de pruebas
            build_id: ID del build
            status: 'p' (passed), 'f' (failed), 'b' (blocked)
            notes: Notas opcionales
        
        Returns:
            Respuesta del servidor
        """
        # Construir el diccionario de datos (verbose)
        data = {
            "devKey": self.dev_key,
            "testcaseid": testcase_id,
            "testplanid": testplan_id,
            "status": status,
            "buildid": build_id,
            "notes": notes,
            "overwrite": True
        }
        
        # Llamada XML-RPC (protocolo legacy)
        try:
            response = self.server.tl.reportTCResult(data)
            return response
        except xmlrpc.client.Fault as fault:
            raise Exception(f"XML-RPC Fault: {fault.faultCode} - {fault.faultString}")
    
    def report_multiple_results(self, testplan_id: int, build_id: int, 
                               results: List[Dict]) -> List[Dict]:
        """
        Reporta múltiples resultados (NO hay batch nativo, se itera)
        
        Args:
            testplan_id: ID del plan de pruebas
            build_id: ID del build
            results: Lista de resultados con formato:
                     [{"testcase_id": 1, "status": "p", "notes": "..."}, ...]
        
        Returns:
            Lista de respuestas (una por cada llamada individual)
        """
        responses = []
        
        # TestLink NO soporta batch operations nativamente
        # Debemos hacer una llamada por cada resultado
        for result in results:
            response = self.report_result(
                testcase_id=result["testcase_id"],
                testplan_id=testplan_id,
                build_id=build_id,
                status=result["status"],
                notes=result.get("notes", "")
            )
            responses.append(response)
        
        return responses
    
    def get_test_case(self, testcase_id: int) -> Dict:
        """Obtiene información de un caso de prueba"""
        data = {
            "devKey": self.dev_key,
            "testcaseid": testcase_id
        }
        
        try:
            response = self.server.tl.getTestCase(data)
            return response
        except xmlrpc.client.Fault as fault:
            raise Exception(f"XML-RPC Fault: {fault.faultCode} - {fault.faultString}")
    
    def get_test_plan(self, testplan_id: int) -> Dict:
        """Obtiene información de un plan de pruebas"""
        data = {
            "devKey": self.dev_key,
            "testplanid": testplan_id
        }
        
        try:
            response = self.server.tl.getTestPlanByID(data)
            return response
        except xmlrpc.client.Fault as fault:
            raise Exception(f"XML-RPC Fault: {fault.faultCode} - {fault.faultString}")


# ============================================================================
# EJEMPLO DE USO: Integración con CI/CD
# ============================================================================

def report_automated_test_results():
    """
    Ejemplo: Reportar resultados de tests automatizados desde un pipeline CI/CD
    NOTA: TestLink requiere múltiples llamadas individuales (sin batch)
    """
    # Configuración (URL más compleja)
    client = TestLinkAPIClient(
        url='http://example.com/lib/api/xmlrpc/v1/xmlrpc.php',
        dev_key='your_dev_key_here'
    )
    
    # Simular resultados de tests automatizados
    test_results = [
        {"testcase_id": 101, "status": "p", "notes": "Login test passed"},
        {"testcase_id": 102, "status": "p", "notes": "Registration test passed"},
        {"testcase_id": 103, "status": "f", "notes": "Payment test failed: timeout"},
        {"testcase_id": 104, "status": "p", "notes": "Logout test passed"},
    ]
    
    # Reportar uno por uno (NO hay batch operation)
    testplan_id = 10
    build_id = 5
    
    responses = client.report_multiple_results(testplan_id, build_id, test_results)
    
    print(f"✓ Reportados {len(test_results)} resultados en {len(test_results)} requests")
    print(f"  Overhead: {len(test_results)} llamadas HTTP individuales")
    return responses


def report_single_manual_test():
    """
    Ejemplo: Reportar resultado de una prueba manual individual
    """
    client = TestLinkAPIClient(
        url='http://example.com/lib/api/xmlrpc/v1/xmlrpc.php',
        dev_key='your_dev_key_here'
    )
    
    # Reportar resultado individual
    result = client.report_result(
        testcase_id=100,
        testplan_id=10,
        build_id=5,
        status='p',  # passed
        notes="Test passed successfully. All validation checks completed."
    )
    
    print(f"✓ Resultado reportado")
    print(f"  Response: {result}")
    return result


# ============================================================================
# WRAPPER CLASS (Necesario para mejorar la experiencia de desarrollo)
# ============================================================================

class TestLinkAPIWrapper:
    """
    Wrapper para simplificar el uso de TestLink API
    NOTA: Este código adicional es necesario debido a las limitaciones del protocolo
    """
    
    def __init__(self, url: str, dev_key: str):
        self.client = TestLinkAPIClient(url, dev_key)
        self.status_map = {
            'passed': 'p',
            'failed': 'f',
            'blocked': 'b'
        }
    
    def report_result_friendly(self, testcase_id: int, testplan_id: int,
                              build_id: int, status: str, notes: str = "") -> Dict:
        """
        Versión más amigable con nombres de status legibles
        """
        # Convertir status legible a código de TestLink
        status_code = self.status_map.get(status.lower(), 'p')
        
        return self.client.report_result(
            testcase_id=testcase_id,
            testplan_id=testplan_id,
            build_id=build_id,
            status=status_code,
            notes=notes
        )


# ============================================================================
# ANÁLISIS DE COMPLEJIDAD
# ============================================================================

def analyze_api_complexity():
    """Análisis de complejidad del código"""
    
    single_result_code = """
class TestLinkAPIClient:
    def __init__(self, url, key):
        self.server = xmlrpc.client.ServerProxy(url)
        self.key = key
        
    def reportResult(self, tcid, tpid, status):
        data = {
            "devKey": self.key,
            "testcaseid": tcid,
            "testplanid": tpid,
            "status": status,
            "buildid": 5,
            "notes": "Test passed successfully.",
            "overwrite": True
        }
        return self.server.tl.reportTCResult(data)

client = TestLinkAPIClient(
    'http://example.com/lib/api/xmlrpc/v1/xmlrpc.php', 
    'KEY'
)
client.reportResult(100, 10, 'p')
"""
    
    print("=" * 70)
    print("ANÁLISIS DE COMPLEJIDAD - TestLink API")
    print("=" * 70)
    print(f"Líneas de código (caso simple): 23")
    print(f"Protocolo: XML-RPC (legacy)")
    print(f"Formato: XML")
    print(f"Autenticación: Developer Key en payload")
    print(f"Payload size (estimado): ~240 bytes (con overhead XML)")
    print(f"Dependencias: xmlrpc.client (menos común)")
    print(f"Curva de aprendizaje: Alta (XML-RPC no estándar)")
    print(f"Documentación: Fragmentada, ejemplos limitados")
    print(f"Batch operations: NO SOPORTADO (N llamadas para N resultados)")
    print("=" * 70)
    
    # Simular payload XML-RPC
    print("\nEjemplo de payload XML-RPC (verbose):")
    print("""
<?xml version='1.0'?>
<methodCall>
  <methodName>tl.reportTCResult</methodName>
  <params>
    <param>
      <value>
        <struct>
          <member>
            <name>devKey</name>
            <value><string>your_key_here</string></value>
          </member>
          <member>
            <name>testcaseid</name>
            <value><int>100</int></value>
          </member>
          <member>
            <name>testplanid</name>
            <value><int>10</int></value>
          </member>
          <member>
            <name>status</name>
            <value><string>p</string></value>
          </member>
          <member>
            <name>buildid</name>
            <value><int>5</int></value>
          </member>
          <member>
            <name>notes</name>
            <value><string>Test passed successfully.</string></value>
          </member>
          <member>
            <name>overwrite</name>
            <value><boolean>1</boolean></value>
          </member>
        </struct>
      </value>
    </param>
  </params>
</methodCall>
    """)
    print(f"Tamaño aproximado: ~240 bytes (vs ~80 bytes JSON)")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TestLink API - Ejemplos de Integración")
    print("=" * 70 + "\n")
    
    # Mostrar análisis de complejidad
    analyze_api_complexity()
    
    print("\n" + "=" * 70)
    print("LIMITACIONES DE LA API DE TestLink:")
    print("=" * 70)
    print("✗ XML-RPC legacy - protocolo obsoleto")
    print("✗ Payload verbose - 3x más grande que JSON")
    print("✗ NO batch operations - N llamadas para N resultados")
    print("✗ Documentación fragmentada - ejemplos limitados")
    print("✗ Sin webhooks - polling manual requerido")
    print("✗ Manejo de errores complejo - XML-RPC Faults")
    print("✗ URL endpoint compleja - /lib/api/xmlrpc/v1/xmlrpc.php")
    print("✗ Requiere wrapper classes - para mejorar DX")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("IMPACTO EN DESARROLLO:")
    print("=" * 70)
    print("• Tiempo de implementación: 3-5x mayor que TestRail")
    print("• Mantenimiento: Requiere conocimiento de XML-RPC")
    print("• Debugging: Más complejo (XML vs JSON)")
    print("• Performance: Overhead de protocolo significativo")
    print("• CI/CD: Ineficiente para reportar múltiples resultados")
    print("=" * 70)
