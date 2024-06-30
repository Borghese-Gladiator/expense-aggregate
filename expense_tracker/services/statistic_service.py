import pandas as pd
import arrow
from arrow import Arrow
from pandera.typing import DataFrame

from expense_tracker.datasources import BaseDatasource
from expense_tracker.et_types import (
    TransactionsSchema,
    StatisticServiceFilter,
    StatisticServiceGroup, 
    StatisticServiceAggregationInterval
)

class StatisticService:
    datasource: BaseDatasource
    interval_format_mapping = {
        StatisticServiceAggregationInterval.MONTHLY: "YYYY-MM",
        StatisticServiceAggregationInterval.YEARLY: "YYYY"
    }

    def __init__(self, datasource):
        self.datasource = datasource

    def calculate(
        self,
        timeframe_start: Arrow,
        timeframe_end: Arrow,
        filter_by: StatisticServiceFilter = None,
        group_by_list: list[StatisticServiceGroup] = None,
        interval: StatisticServiceAggregationInterval = None,
    ) -> list[dict]:
        if group_by_list is None:
            group_by_list = []
        if interval is None:
            interval = StatisticServiceAggregationInterval.MONTHLY
        
        df: DataFrame[TransactionsSchema] = self.datasource.get_transactions()
        
        # Add date column for comparison
        df['date'] = df['date_str'].apply(lambda date_str: arrow.get(date_str, 'YYYY-MM-DD'))
        df = df.drop('date_str', axis=1)
        
        # Filter by time
        df = df[(df['date'] >= timeframe_start) & (df['date'] <= timeframe_end)]
        
        # Filter by tags
        df = df if filter_by is None else df[df['tags'].apply(lambda tags: filter_by.value in tags)]
        
        # Aggregate by interval and group_by (eg: monthly, yearly)
        # NOTE: grouping by columns means other columns will be lost in final output
        df['date'] = df['date'].apply(lambda date: date.format(self.interval_format_mapping[interval]))
        df = df.groupby(['date'] + [group_by.value for group_by in group_by_list])[['amount']].mean().reset_index()
        
        return df.to_dict(orient='records')

    def get(
        self,
        timeframe_start: Arrow,
        timeframe_end: Arrow,
        filter_by: StatisticServiceFilter,
    ) -> list[dict]:
        df: DataFrame[TransactionsSchema] = self.datasource.get_transactions()
        # Apply the time filter
        df = df[(df['date'] >= timeframe_start) & (df['date'] <= timeframe_end)]
        # Apply the filter by 'tags'
        df = df[df['tags'].apply(lambda tags: filter_by in tags)]
        return df.to_dict(orient='records')
        