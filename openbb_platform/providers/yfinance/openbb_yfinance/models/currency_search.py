"""Yahoo Finance Currency Search Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.currency_pairs import (
    CurrencyPairsData,
    CurrencyPairsQueryParams,
)
from pydantic import Field


class YFinanceCurrencySearchQueryParams(CurrencyPairsQueryParams):
    """Yahoo Finance Currency Search Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceCurrencySearchData(CurrencyPairsData):
    """Yahoo Finance Currency Search Data."""

    exchange: str | None = Field(
        default=None,
        description="The exchange the currency pair trades on.",
    )
    quote_type: str | None = Field(
        default=None,
        description="The quote type of the asset.",
    )


class YFinanceCurrencySearchFetcher(
    Fetcher[
        YFinanceCurrencySearchQueryParams,
        list[YFinanceCurrencySearchData],
    ]
):
    """Yahoo Finance Currency Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceCurrencySearchQueryParams:
        """Transform the query."""
        return YFinanceCurrencySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceCurrencySearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Yahoo Finance endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import amake_request

        if not query.query:
            return []

        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = f"q={query.query}&quotesCount=50&newsCount=0&enableFuzzyQuery=true"

        async def callback(response, _):
            """Parse the response."""
            return await response.json()

        data = await amake_request(
            f"{url}?{params}",
            response_callback=callback,
            headers={"User-Agent": "Mozilla/5.0"},
            **kwargs,
        )

        return [
            {
                "symbol": q.get("symbol", "").replace("=X", ""),
                "name": q.get("longname") or q.get("shortname"),
                "exchange": q.get("exchDisp"),
                "quote_type": q.get("quoteType"),
            }
            for q in data.get("quotes", [])
            if q.get("quoteType") == "CURRENCY"
        ]

    @staticmethod
    def transform_data(
        query: YFinanceCurrencySearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceCurrencySearchData]:
        """Return the transformed data."""
        return [YFinanceCurrencySearchData.model_validate(d) for d in data]
