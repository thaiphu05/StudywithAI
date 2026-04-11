from src.services.account_service import AccountService
from src.services.auth_service import AuthService
from src.services.orchestration_service import EvaluationOrchestrator

account_service = AccountService()
auth_service = AuthService()
orchestrator = EvaluationOrchestrator(account_service=account_service)


def get_account_service() -> AccountService:
    return account_service


def get_orchestrator() -> EvaluationOrchestrator:
    return orchestrator

def get_auth_service() -> AuthService:
    return auth_service