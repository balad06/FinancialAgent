from bunq.sdk.context.api_context import ApiContext
from bunq.sdk.context.bunq_context import BunqContext
from bunq import ApiEnvironmentType, Pagination
from bunq.sdk.model.generated.endpoint import (
    MonetaryAccountBankApiObject,
    PaymentApiObject,
    BunqMeTabApiObject,
    BunqMeTabEntryApiObject
)
from bunq.sdk.model.generated.object_ import AmountObject, PointerObject, NotificationFilterObject


class BunqManager:
    def __init__(self, api_key: str, environment: ApiEnvironmentType = ApiEnvironmentType.SANDBOX):
        self.api_key = api_key
        self.environment = environment
        self.api_context = None
        self.user_context = None
        self.primary_account = None
        self._initialize_context()

    def _initialize_context(self):
        self.api_context = ApiContext.create(self.environment, self.api_key, "My Device")
        BunqContext.load_api_context(self.api_context)
        self.user_context = BunqContext.user_context()
        self.primary_account = self.user_context.primary_monetary_account

    def get_user_id(self):
        return self.user_context.user_id

    def get_all_accounts(self):
        accounts = MonetaryAccountBankApiObject.list().value
        return [{
            "id": acc.id_,
            "description": acc.description,
            "balance": f"{acc.balance.value} {acc.balance.currency}"
        } for acc in accounts]

    def get_account_by_id(self, account_id: int):
        account = MonetaryAccountBankApiObject.get(account_id).value
        return {
            "id": account.id_,
            "currency": account.currency,
            "balance": f"{account.balance.value} {account.balance.currency}",
            "daily_limit": account._daily_limit.value if account._daily_limit else None
        }

    def update_account_daily_limit(self, account_id: int, amount: str, currency: str = "EUR"):
        updated_account = MonetaryAccountBankApiObject.update(
            account_id,
            daily_limit=AmountObject(amount, currency)
        )
        return updated_account
    def list_all_payments(self,count: int =10):
        monetary_account = MonetaryAccountBankApiObject.list()
        accounts =monetary_account.value
        payments_total=[]
        for account in accounts:
            pagination = Pagination()
            pagination.count = count
            payments = PaymentApiObject.list(account.id_,params=pagination.url_params_count_only).value
            
            payments_total.extend([{
            "id": p.id_,
            "amount": f"{p.amount.value} {p.amount.currency}",
            "description": p.description
            }  for p in payments])
        return payments_total

    def list_payments(self,accountid: int ,count: int = 10):
        pagination = Pagination()
        pagination.count = count
        payments = PaymentApiObject.list(accountid,params=pagination.url_params_count_only).value
        return [{
            "id": p.id_,
            "amount": f"{p.amount.value} {p.amount.currency}",
            "description": p.description
        } for p in payments]

    def create_payment(self, amount: str, currency: str, email: str, description: str):
        payment = PaymentApiObject.create(
            amount=AmountObject(amount, currency),
            counterparty_alias=PointerObject("EMAIL", email),
            description=description
        ).value
        return payment

    def create_bunq_me_tab(self, amount: str, currency: str, description: str, redirect_url: str):
        bunq_me_tab_entry = BunqMeTabEntryApiObject(
            amount_inquired=AmountObject(amount, currency),
            description=description,
            redirect_url=redirect_url
        )
        bunq_me_tab = BunqMeTabApiObject(bunqme_tab_entry=bunq_me_tab_entry).create(
            bunqme_tab_entry=bunq_me_tab_entry
        ).value
        return bunq_me_tab.bunqme_tab_share_url

    def add_mutation_notification_filter(self, target_url: str):
        notification_filter = NotificationFilterObject(
            category="MUTATION",
            notification_target=target_url
        )
        return [notification_filter]


