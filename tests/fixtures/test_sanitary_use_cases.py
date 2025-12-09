import unittest
from unittest.mock import AsyncMock, Mock, patch
from datetime import date, timedelta
from uuid import UUID, uuid4

from app.sanitary.domain.incident_type import IncidentType
from app.sanitary.domain.sanitary_company import SanitaryCompany
from app.sanitary.domain.sanitary_policy import SanitaryPolicy
from app.sanitary.domain.sanitary_review import SanitaryReview

from app.sanitary.application.use_cases.list_sanitary_policies import (
    ListSanitaryPoliciesUseCase, ListSanitaryPoliciesCommand
)
from app.sanitary.application.use_cases.get_sanitary_policy_history import (
    GetSanitaryPolicyHistoryUseCase, GetSanitaryPolicyHistoryCommand
)
from app.sanitary.application.use_cases.register_sanitary_review import (
    RegisterSanitaryReviewUseCase, RegisterSanitaryReviewCommand
)


# ==============================================================================
# SECCIÓN 1: CONFIGURACIÓN BASE Y FUNCIONES DE AYUDA
# ==============================================================================
# Esta sección contiene clases y funciones reutilizables que facilitan la
# creación de datos de prueba (mocks) sin necesidad de conectarse a una base
# de datos real.
# ==============================================================================

class TestSanitaryBase(unittest.TestCase):
    """
    Clase base que proporciona IDs únicos y fechas comunes para todas las pruebas.
    Cada prueba que herede de esta clase tendrá acceso a estos valores.
    """

    def setUp(self):
        # Generamos IDs únicos para usar en nuestras pruebas
        # uuid4() crea un identificador único universal aleatorio
        self.POLICY_ID = uuid4()
        self.USER_ID = uuid4()
        self.INCIDENT_ID = uuid4()
        self.COMPANY_ID = uuid4()
        self.TODAY = date.today()


class DomainMock(Mock):
    """
    Mock personalizado que simula objetos del dominio.
    Cada mock creado tendrá automáticamente un ID único.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si no se proporciona un ID, genera uno automáticamente
        self.id = kwargs.get('id', uuid4())


def create_policy_mock(is_active=True, name="Control de Plagas"):
    """
    Crea una política sanitaria falsa para pruebas.

    Parámetros:
        is_active: Si la política está activa (por defecto True)
        name: Nombre de la política (por defecto "Control de Plagas")

    Retorna: Un objeto mock que simula una SanitaryPolicy
    """
    return DomainMock(
        id=uuid4(), name=name, description="Desc.", is_active=is_active
    )


def create_review_mock(is_conform=True, policy_id=None, date_val=None, incident_type_id=None, company_id=None):
    """
    Crea una revisión sanitaria falsa para pruebas.

    Parámetros:
        is_conform: Si la revisión fue conforme (True) o no conforme (False)
        policy_id: ID de la política asociada
        date_val: Fecha de la revisión (por defecto hoy)
        incident_type_id: ID del tipo de incidencia (solo para revisiones no conformes)
        company_id: ID de la empresa sanitaria (solo para revisiones no conformes)

    Retorna: Un objeto mock que simula una SanitaryReview
    """
    return DomainMock(
        id=uuid4(),
        policy_id=policy_id or uuid4(),
        date=date_val or date.today(),
        is_conform=is_conform,
        observation="Obs",
        incident_type_id=incident_type_id,
        company_id=company_id
    )


def create_incident_type_mock(policy_id):
    """
    Crea un tipo de incidencia falso vinculado a una política específica.

    Parámetros:
        policy_id: ID de la política a la que pertenece este tipo de incidencia

    Retorna: Un objeto mock que simula un IncidentType
    """
    return DomainMock(id=uuid4(), policy_id=policy_id)


def create_company_mock():
    """
    Crea una empresa sanitaria falsa para pruebas.

    Retorna: Un objeto mock que simula una SanitaryCompany
    """
    return DomainMock(id=uuid4(), name="Empresa A")


# ==============================================================================
# SECCIÓN 2: PRUEBAS DE DOMINIO (REGLAS DE NEGOCIO)
# ==============================================================================
# Estas pruebas verifican que los objetos del dominio (entidades) se comporten
# correctamente según las reglas de negocio definidas. Son síncronas porque
# solo prueban lógica pura sin dependencias externas.
# ==============================================================================

class TestSanitaryPolicy(TestSanitaryBase):
    """
    Pruebas para la entidad SanitaryPolicy (Política Sanitaria).
    Verifica la creación, modificación y desactivación de políticas.
    """

    def test_policy_creation_defaults(self):
        """
        Verifica que al crear una política sin especificar todos los parámetros,
        se apliquen los valores por defecto correctos:
        - La política debe estar activa (is_active = True)
        - La descripción debe ser None si no se proporciona
        """
        policy = SanitaryPolicy.create(name="Control de Plagas")
        self.assertTrue(policy.is_active)
        self.assertIsNone(policy.description)

    def test_policy_mutation_methods(self):
        """
        Verifica que los métodos que modifican una política funcionen correctamente:
        - deactivate() debe cambiar is_active a False
        - rename() debe cambiar el nombre de la política
        """
        policy = SanitaryPolicy.create(name="Viejo Nombre")

        # Desactivamos la política
        policy.deactivate()
        self.assertFalse(policy.is_active)

        # Renombramos la política
        policy.rename("Nuevo Nombre")
        self.assertEqual(policy.name, "Nuevo Nombre")


class TestIncidentType(TestSanitaryBase):
    """
    Pruebas para la entidad IncidentType (Tipo de Incidencia).
    Verifica la creación y desactivación de tipos de incidencia.
    """

    def test_incident_type_creation(self):
        """
        Verifica que al crear un tipo de incidencia, quede correctamente
        vinculado a la política sanitaria especificada.
        """
        incident = IncidentType.create(
            policy_id=self.POLICY_ID, name="Contaminación cruzada"
        )
        self.assertEqual(incident.policy_id, self.POLICY_ID)

    def test_incident_type_deactivation(self):
        """
        Verifica que se pueda desactivar un tipo de incidencia cuando
        ya no se necesite (por ejemplo, si cambió el reglamento).
        """
        incident = IncidentType.create(policy_id=self.POLICY_ID, name="Prueba")
        incident.deactivate()
        self.assertFalse(incident.is_active)


class TestSanitaryCompany(TestSanitaryBase):
    """
    Pruebas para la entidad SanitaryCompany (Empresa Sanitaria).
    Verifica la creación y actualización de datos de empresas fumigadoras/sanitarias.
    """

    def test_company_creation_minimal(self):
        """
        Verifica que se pueda crear una empresa con solo los datos mínimos requeridos
        (nombre comercial y RUC). Los campos opcionales deben quedar como None.
        """
        company = SanitaryCompany.create(business_name="FumiSA", ruc="123")
        self.assertIsNone(company.phone)

    def test_company_update_partial(self):
        """
        Verifica que se puedan actualizar solo algunos campos de la empresa,
        manteniendo intactos los campos que no se especifiquen en la actualización.

        En este ejemplo:
        - Se actualiza business_name y phone
        - El RUC permanece sin cambios (OLD)
        """
        company = SanitaryCompany.create(
            business_name="Old Name", ruc="OLD", phone="111", email="old@corp.com"
        )

        # Actualizamos solo nombre y teléfono
        company.update_data(business_name="New Name", phone="222")

        # Verificamos que se actualizaron los campos especificados
        self.assertEqual(company.business_name, "New Name")
        # Verificamos que el RUC se mantuvo igual (no se tocó)
        self.assertEqual(company.ruc, "OLD")

    """
    NOTA: Existe una prueba comentada (test_company_update_to_none) que verifica
    si se pueden borrar campos estableciéndolos a None. Está deshabilitada porque
    esta funcionalidad aún no está implementada o en discusión.
    """


class TestSanitaryReview(TestSanitaryBase):
    """
    Pruebas para la entidad SanitaryReview (Revisión Sanitaria).
    Verifica la creación de revisiones conformes y no conformes.
    """

    def test_create_conform_review(self):
        """
        Verifica la creación de una revisión CONFORME (cuando todo está bien).

        Una revisión conforme:
        - Tiene is_conform = True
        - NO requiere tipo de incidencia (incident_type_id = None)
        - NO requiere empresa sanitaria (company_id = None)
        """
        review = SanitaryReview.create_conform(
            policy_id=self.POLICY_ID, user_id=self.USER_ID, date_value=self.TODAY
        )

        self.assertTrue(review.is_conform)
        self.assertIsNone(review.incident_type_id)
        self.assertIsNone(review.company_id)

    def test_create_non_conform_review(self):
        """
        Verifica la creación de una revisión NO CONFORME (cuando hay problemas).

        Una revisión no conforme:
        - Tiene is_conform = False
        - REQUIERE un tipo de incidencia (incident_type_id)
        - REQUIERE una empresa sanitaria para solucionar el problema (company_id)
        """
        review = SanitaryReview.create_non_conform(
            policy_id=self.POLICY_ID, user_id=self.USER_ID, date_value=self.TODAY,
            incident_type_id=self.INCIDENT_ID, company_id=self.COMPANY_ID
        )

        self.assertFalse(review.is_conform)
        self.assertEqual(review.incident_type_id, self.INCIDENT_ID)


# ==============================================================================
# SECCIÓN 3: PRUEBAS DE APLICACIÓN (CASOS DE USO)
# ==============================================================================
# Estas pruebas verifican que los casos de uso (la lógica de aplicación)
# funcionen correctamente. Son asíncronas porque simulan operaciones que
# normalmente consultarían bases de datos o servicios externos.
# ==============================================================================

class TestListSanitaryPoliciesUseCase(unittest.IsolatedAsyncioTestCase):
    """
    Pruebas para el caso de uso: Listar Políticas Sanitarias.
    Verifica que se puedan obtener listas filtradas de políticas.
    """

    def setUp(self):
        """
        Configuración inicial para cada prueba:
        - Creamos un repositorio mock (simulado)
        - Creamos el caso de uso con ese repositorio
        - Preparamos políticas de ejemplo (una activa y una inactiva)
        """
        self.mock_policy_repo = AsyncMock()
        self.use_case = ListSanitaryPoliciesUseCase(policy_repo=self.mock_policy_repo)
        self.P1 = create_policy_mock(is_active=True, name="P1")
        self.P2 = create_policy_mock(is_active=False, name="P2")

    async def test_list_active_policies_only(self):
        """
        Verifica que cuando se solicitan solo políticas activas:
        - Se llama al método list_active() del repositorio
        - Se retorna únicamente la cantidad correcta de políticas activas
        """
        # Configuramos el mock para que devuelva solo la política activa
        self.mock_policy_repo.list_active.return_value = [self.P1]

        # Ejecutamos el caso de uso pidiendo solo activas
        cmd = ListSanitaryPoliciesCommand(include_inactive=False)
        result = await self.use_case.execute(cmd)

        # Verificamos que se llamó al método correcto
        self.mock_policy_repo.list_active.assert_awaited_once()
        # Verificamos que recibimos 1 política
        self.assertEqual(len(result['policies']), 1)

    async def test_list_all_policies(self):
        """
        Verifica que cuando se solicitan todas las políticas (activas e inactivas):
        - Se llama al método list_all() del repositorio
        - Se retornan todas las políticas sin filtrar
        """
        # Configuramos el mock para que devuelva ambas políticas
        self.mock_policy_repo.list_all.return_value = [self.P1, self.P2]

        # Ejecutamos el caso de uso pidiendo todas las políticas
        cmd = ListSanitaryPoliciesCommand(include_inactive=True)
        result = await self.use_case.execute(cmd)

        # Verificamos que se llamó al método correcto
        self.mock_policy_repo.list_all.assert_awaited_once()
        # Verificamos que recibimos 2 políticas
        self.assertEqual(len(result['policies']), 2)


class TestGetSanitaryPolicyHistoryUseCase(unittest.IsolatedAsyncioTestCase):
    """
    Pruebas para el caso de uso: Obtener Historial de una Política Sanitaria.
    Verifica que se pueda consultar el historial de revisiones de una política
    y que se calcule correctamente la fecha de la próxima revisión.
    """

    def setUp(self):
        """
        Configuración inicial:
        - Creamos IDs y fecha para las pruebas
        - Creamos mocks de repositorios (políticas y revisiones)
        - Creamos el caso de uso con esos repositorios
        """
        self.POLICY_ID = uuid4()
        self.TODAY = date.today()
        self.mock_policy_repo = AsyncMock()
        self.mock_review_repo = AsyncMock()
        self.use_case = GetSanitaryPolicyHistoryUseCase(
            policy_repo=self.mock_policy_repo, review_repo=self.mock_review_repo
        )

    async def test_policy_not_found(self):
        """
        Verifica el comportamiento cuando se busca el historial de una política
        que no existe en el sistema. Debe retornar success=False.
        """
        # Simulamos que la política no existe (retorna None)
        self.mock_policy_repo.get_by_id.return_value = None

        cmd = GetSanitaryPolicyHistoryCommand(policy_id=self.POLICY_ID, months_back=6)
        result = await self.use_case.execute(cmd)

        # Verificamos que la operación falló
        self.assertFalse(result['success'])

    async def test_history_found_and_next_review_calculated(self):
        """
        Verifica que cuando existe historial de revisiones:
        - Se obtiene correctamente el historial
        - Se calcula la fecha de próxima revisión (30 días después de la última)

        Ejemplo: Si la última revisión fue hace 30 días, la próxima debe ser hoy.
        """
        policy_mock = create_policy_mock()

        # Simulamos que la última revisión fue hace 30 días
        last_review_date = self.TODAY - timedelta(days=30)
        review_last_mock = create_review_mock(date_val=last_review_date)

        # Configuramos los mocks
        self.mock_policy_repo.get_by_id.return_value = policy_mock
        self.mock_review_repo.get_last_by_policy.return_value = review_last_mock
        self.mock_review_repo.list_by_policy_and_period.return_value = [create_review_mock()]

        cmd = GetSanitaryPolicyHistoryCommand(policy_id=self.POLICY_ID, months_back=6)
        result = await self.use_case.execute(cmd)

        # La próxima revisión debe ser 30 días después de la última
        expected_next_review_date = (last_review_date + timedelta(days=30)).isoformat()

        # Verificamos que la operación fue exitosa
        self.assertTrue(result['success'])
        # Verificamos que el cálculo de la próxima revisión es correcto
        self.assertEqual(result['next_review_date'], expected_next_review_date)
        # Verificamos que hay 1 revisión en el historial
        self.assertEqual(len(result['history']), 1)

    async def test_no_history(self):
        """
        Verifica el comportamiento cuando la política existe pero aún no tiene
        revisiones registradas. En este caso, no se puede calcular una próxima
        revisión (next_review_date debe ser None).
        """
        # Configuramos los mocks para simular ausencia de revisiones
        self.mock_policy_repo.get_by_id.return_value = create_policy_mock()
        self.mock_review_repo.get_last_by_policy.return_value = None
        self.mock_review_repo.list_by_policy_and_period.return_value = []

        cmd = GetSanitaryPolicyHistoryCommand(policy_id=self.POLICY_ID, months_back=6)
        result = await self.use_case.execute(cmd)

        # La operación debe ser exitosa aunque no haya historial
        self.assertTrue(result['success'])
        # No debe haber fecha de próxima revisión
        self.assertIsNone(result['next_review_date'])


class TestRegisterSanitaryReviewUseCase(unittest.IsolatedAsyncioTestCase):
    """
    Pruebas para el caso de uso: Registrar Revisión Sanitaria.

    Este es el caso de uso más complejo porque valida múltiples reglas de negocio:
    - La política debe existir
    - Si es no conforme, DEBE tener tipo de incidencia
    - Si es no conforme, DEBE tener empresa sanitaria
    - El tipo de incidencia debe pertenecer a la política que se está revisando
    """

    def setUp(self):
        """
        Configuración inicial compleja porque este caso de uso necesita
        múltiples repositorios (políticas, tipos de incidencia, revisiones, empresas).
        """
        self.POLICY_ID = uuid4()
        self.USER_ID = uuid4()
        self.INCIDENT_ID = uuid4()
        self.COMPANY_ID = uuid4()
        self.TODAY = date.today()

        # Creamos todos los mocks de repositorios necesarios
        self.mock_policy_repo = AsyncMock()
        self.mock_incident_type_repo = AsyncMock()
        self.mock_review_repo = AsyncMock()
        self.mock_company_repo = AsyncMock()

        # Creamos el caso de uso con todos sus repositorios
        self.use_case = RegisterSanitaryReviewUseCase(
            policy_repo=self.mock_policy_repo,
            incident_type_repo=self.mock_incident_type_repo,
            review_repo=self.mock_review_repo,
            company_repo=self.mock_company_repo,
        )

        # Preparamos mocks de datos de ejemplo
        self.POLICY_MOCK = create_policy_mock()
        self.INCIDENT_MOCK = create_incident_type_mock(policy_id=self.POLICY_ID)
        self.SAVED_REVIEW_MOCK = create_review_mock(is_conform=True, policy_id=self.POLICY_ID)

        # Configuramos comportamientos por defecto de los mocks
        self.mock_policy_repo.get_by_id.return_value = self.POLICY_MOCK
        self.mock_incident_type_repo.get_by_id.return_value = self.INCIDENT_MOCK
        self.mock_company_repo.get_by_id.return_value = create_company_mock()
        self.mock_review_repo.save.return_value = self.SAVED_REVIEW_MOCK

        # Comando base para revisión no conforme (será modificado en cada prueba)
        self.VALID_CMD_BASE = RegisterSanitaryReviewCommand(
            policy_id=self.POLICY_ID, date=self.TODAY, user_id=self.USER_ID, is_conform=False
        )

    async def test_failure_policy_not_found(self):
        """
        REGLA DE NEGOCIO: No se puede registrar una revisión si la política no existe.

        Verifica que:
        - La operación falle (success=False)
        - NO se intente guardar la revisión (save no debe ser llamado)
        """
        # Simulamos que la política no existe
        self.mock_policy_repo.get_by_id.return_value = None

        result = await self.use_case.execute(self.VALID_CMD_BASE)

        # Verificamos que falló
        self.assertFalse(result['success'])
        # Verificamos que NO se intentó guardar nada
        self.mock_review_repo.save.assert_not_awaited()

    @patch('app.sanitary.domain.sanitary_review.SanitaryReview.create_conform', autospec=True)
    async def test_success_conform_review(self, mock_create_conform):
        """
        CASO EXITOSO: Registro de una revisión CONFORME.

        Cuando todo está bien (is_conform=True):
        - NO se requiere tipo de incidencia
        - NO se requiere empresa sanitaria
        - La revisión se guarda exitosamente
        """
        mock_create_conform.return_value = self.SAVED_REVIEW_MOCK

        # Creamos comando para revisión conforme
        cmd = RegisterSanitaryReviewCommand(
            policy_id=self.POLICY_ID, date=self.TODAY, user_id=self.USER_ID, is_conform=True
        )

        result = await self.use_case.execute(cmd)

        # Verificamos que fue exitoso
        self.assertTrue(result['success'])
        # Verificamos que NO se consultó el tipo de incidencia (no es necesario)
        self.mock_incident_type_repo.get_by_id.assert_not_awaited()

    async def test_failure_non_conform_missing_incident_type(self):
        """
        REGLA DE NEGOCIO: Si hay problemas (is_conform=False),
        ES OBLIGATORIO especificar qué tipo de problema ocurrió.

        Este test verifica que la operación falle si intentamos registrar
        una revisión no conforme sin especificar el tipo de incidencia.
        """
        cmd = RegisterSanitaryReviewCommand(
            policy_id=self.POLICY_ID, date=self.TODAY, user_id=self.USER_ID,
            is_conform=False,
            company_id=self.COMPANY_ID,  # Tenemos empresa
            incident_type_id=None  # PERO NO tenemos tipo de incidencia (ERROR)
        )

        result = await self.use_case.execute(cmd)

        # Verificamos que falló
        self.assertFalse(result['success'])
        # Verificamos que el mensaje de error menciona "tipo de incidencia"
        self.assertIn("tipo de incidencia", result['message'])

    async def test_failure_incident_type_wrong_policy(self):
        """
        REGLA DE NEGOCIO: El tipo de incidencia debe pertenecer a la misma
        política que se está revisando.

        No puedes usar un tipo de incidencia de "Control de Temperatura"
        cuando estás revisando "Control de Plagas".

        Este test simula ese error: el tipo de incidencia pertenece a OTRA política.
        """
        # Creamos un tipo de incidencia que pertenece a OTRA política (uuid4() aleatorio)
        incident_mock_wrong_policy = create_incident_type_mock(policy_id=uuid4())
        self.mock_incident_type_repo.get_by_id.return_value = incident_mock_wrong_policy

        # Intentamos usar ese tipo de incidencia incorrecto
        cmd = self.VALID_CMD_BASE
        cmd.incident_type_id = self.INCIDENT_ID
        cmd.company_id = self.COMPANY_ID

        result = await self.use_case.execute(cmd)

        # Verificamos que falló
        self.assertFalse(result['success'])
        # Verificamos que el mensaje indica que no pertenece a la política
        self.assertIn("no pertenece a la política", result['message'])

    @patch('app.sanitary.domain.sanitary_review.SanitaryReview.create_non_conform', autospec=True)
    async def test_success_non_conform_review(self, mock_create_non_conform):
        """
        CASO EXITOSO: Registro de una revisión NO CONFORME con todos los datos válidos.

        Cuando hay problemas (is_conform=False) y se proporcionan todos los datos
        requeridos correctamente:
        - Tipo de incidencia (que pertenece a la política correcta)
        - Empresa sanitaria para solucionar el problema

        La revisión se guarda exitosamente.
        """
        mock_create_non_conform.return_value = self.SAVED_REVIEW_MOCK

        # Configuramos todos los datos necesarios para una revisión no conforme
        cmd = self.VALID_CMD_BASE
        cmd.incident_type_id = self.INCIDENT_ID
        cmd.company_id = self.COMPANY_ID

        result = await self.use_case.execute(cmd)

        # Verificamos que fue exitoso
        self.assertTrue(result['success'])
        # Verificamos que se consultó el tipo de incidencia (es necesario validarlo)
        self.mock_incident_type_repo.get_by_id.assert_awaited_once()
        # Verificamos que se guardó la revisión
        self.mock_review_repo.save.assert_awaited_once()