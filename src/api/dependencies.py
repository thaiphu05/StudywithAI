from src.services.account_service import AccountService
from src.services.orchestration_service import EvaluationOrchestrator

account_service = AccountService()
orchestrator = EvaluationOrchestrator(account_service=account_service)


def get_account_service() -> AccountService:
    return account_service


def get_orchestrator() -> EvaluationOrchestrator:
    return orchestrator
