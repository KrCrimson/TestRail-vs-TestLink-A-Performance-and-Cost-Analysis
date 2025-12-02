"""
testrail_api_example.py
TestRail API Integration Example
Demuestra la simplicidad de integración con TestRail usando REST/JSON
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional


class TestRailClient:
    """Cliente simple para la API REST de TestRail"""
    
    def __init__(self, base_url: str, email: str, api_key: str):
        """
        Inicializa el cliente de TestRail
        
        Args:
            base_url: URL base de TestRail (ej: https://example.testrail.io)
            email: Email del usuario
            api_key: API key generada en TestRail
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (email, api_key)
        self.headers = {'Content-Type': 'application/json'}
    
    def add_result(self, test_id: int, status_id: int, 
                   comment: str = "", elapsed: str = "") -> Dict:
        """
        Reporta el resultado de una prueba
        
        Args:
            test_id: ID del test
            status_id: 1=Passed, 2=Blocked, 3=Untested, 4=Retest, 5=Failed
            comment: Comentario opcional
            elapsed: Tiempo transcurrido (ej: "1m 30s")
        
        Returns:
            Respuesta JSON con el resultado creado
        """
        endpoint = f'{self.base_url}/index.php?/api/v2/add_result/{test_id}'
        
        payload = {
            "status_id": status_id,
            "comment": comment,
            "elapsed": elapsed
        }
        
        response = requests.post(
            endpoint,
            auth=self.auth,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def add_results_batch(self, run_id: int, results: List[Dict]) -> Dict:
        """
        Reporta múltiples resultados en un solo request (batch)
        
        Args:
            run_id: ID del test run
            results: Lista de resultados con formato:
                     [{"test_id": 1, "status_id": 1, "comment": "..."}, ...]
        
        Returns:
            Respuesta JSON con los resultados creados
        """
        endpoint = f'{self.base_url}/index.php?/api/v2/add_results/{run_id}'
        
        payload = {"results": results}
        
        response = requests.post(
            endpoint,
            auth=self.auth,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_test(self, test_id: int) -> Dict:
        """Obtiene información de un test"""
        endpoint = f'{self.base_url}/index.php?/api/v2/get_test/{test_id}'
        
        response = requests.get(
            endpoint,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_run(self, run_id: int) -> Dict:
        """Obtiene información de un test run"""
        endpoint = f'{self.base_url}/index.php?/api/v2/get_run/{run_id}'
        
        response = requests.get(
            endpoint,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# EJEMPLO DE USO: Integración con CI/CD
# ============================================================================

def report_automated_test_results():
    """
    Ejemplo: Reportar resultados de tests automatizados desde un pipeline CI/CD
    """
    # Configuración
    client = TestRailClient(
        base_url='https://example.testrail.io',
        email='automation@example.com',
        api_key='your_api_key_here'
    )
    
    # Simular resultados de tests automatizados
    test_results = [
        {"test_id": 101, "status_id": 1, "comment": "Login test passed", "elapsed": "2s"},
        {"test_id": 102, "status_id": 1, "comment": "Registration test passed", "elapsed": "3s"},
        {"test_id": 103, "status_id": 5, "comment": "Payment test failed: timeout", "elapsed": "30s"},
        {"test_id": 104, "status_id": 1, "comment": "Logout test passed", "elapsed": "1s"},
    ]
    
    # Reportar en batch (eficiente)
    run_id = 42  # ID del test run
    response = client.add_results_batch(run_id, test_results)
    
    print(f"✓ Reportados {len(test_results)} resultados en un solo request")
    print(f"  Payload size: ~{len(json.dumps(test_results))} bytes")
    return response


def report_single_manual_test():
    """
    Ejemplo: Reportar resultado de una prueba manual individual
    """
    client = TestRailClient(
        base_url='https://example.testrail.io',
        email='tester@example.com',
        api_key='your_api_key_here'
    )
    
    # Reportar resultado individual
    result = client.add_result(
        test_id=1,
        status_id=1,  # Passed
        comment="Test passed successfully. All validation checks completed.",
        elapsed="1m 30s"
    )
    
    print(f"✓ Resultado reportado: Test #{result.get('test_id')}")
    print(f"  Status: {result.get('status_id')}")
    print(f"  Created: {result.get('created_on')}")
    return result


# ============================================================================
# ANÁLISIS DE COMPLEJIDAD
# ============================================================================

def analyze_api_complexity():
    """Análisis de complejidad del código"""
    
    single_result_code = """
response = requests.post(
    'https://example.testrail.io/index.php?/api/v2/add_result/1',
    auth=('user@example.com', 'password'),
    json={
        "status_id": 1,
        "comment": "Test passed successfully.",
        "elapsed": "1m 30s"
    }
)
"""
    
    print("=" * 70)
    print("ANÁLISIS DE COMPLEJIDAD - TestRail API")
    print("=" * 70)
    print(f"Líneas de código (caso simple): 9")
    print(f"Protocolo: REST/HTTP")
    print(f"Formato: JSON")
    print(f"Autenticación: HTTP Basic Auth")
    print(f"Payload size (estimado): ~80 bytes")
    print(f"Dependencias: requests (estándar)")
    print(f"Curva de aprendizaje: Baja (REST estándar)")
    print(f"Documentación: Completa con ejemplos interactivos")
    print("=" * 70)
    
    # Calcular payload real
    payload = {
        "status_id": 1,
        "comment": "Test passed successfully.",
        "elapsed": "1m 30s"
    }
    payload_size = len(json.dumps(payload))
    print(f"\nPayload real: {payload_size} bytes")
    print(f"Payload JSON:\n{json.dumps(payload, indent=2)}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("TestRail API - Ejemplos de Integración")
    print("=" * 70 + "\n")
    
    # Mostrar análisis de complejidad
    analyze_api_complexity()
    
    print("\n" + "=" * 70)
    print("VENTAJAS DE LA API DE TestRail:")
    print("=" * 70)
    print("✓ REST estándar - familiar para cualquier desarrollador")
    print("✓ JSON nativo - fácil de serializar/deserializar")
    print("✓ Batch operations - eficiente para CI/CD")
    print("✓ Documentación interactiva con ejemplos")
    print("✓ Webhooks para eventos en tiempo real")
    print("✓ Rate limiting claro y predecible")
    print("✓ Versionado de API (v2) con retrocompatibilidad")
    print("=" * 70)
