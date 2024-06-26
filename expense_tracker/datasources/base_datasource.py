from abc import ABC, abstractmethod

from pandera.typing import DataFrame
from expense_tracker.et_types import TransactionsSchema

class BaseDatasource(ABC):
    @abstractmethod
    def get_transactions(self) -> DataFrame[TransactionsSchema]:
        pass
