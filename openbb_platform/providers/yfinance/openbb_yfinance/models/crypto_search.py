"""Yahoo Finance Crypto Search Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.crypto_search import (
    CryptoSearchData,
    CryptoSearchQueryParams,
)
from pydantic import Field


class YFinanceCryptoSearchQueryParams(CryptoSearchQueryParams):
    """Yahoo Finance Crypto Search Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceCryptoSearchData(CryptoSearchData):
    """Yahoo Finance Crypto Search Data."""

    exchange: str | None = Field(
        default=None,
        description="The exchange the crypto trades on.",
    )
    quote_type: str | None = Field(
        default=None,
        description="The quote type of the asset.",
    )


class YFinanceCryptoSearchFetcher(
    Fetcher[
        YFinanceCryptoSearchQueryParams,
        list[YFinanceCryptoSearchData],
    ]
):
    """Yahoo Finance Crypto Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> YFinanceCryptoSearchQueryParams:
        """Transform the query."""
        return YFinanceCryptoSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceCryptoSearchQueryParams,
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
                "symbol": q.get("symbol", "").replace("-", ""),
                "name": q.get("longname") or q.get("shortname"),
                "exchange": q.get("exchDisp"),
                "quote_type": q.get("quoteType"),
            }
            for q in data.get("quotes", [])
            if q.get("quoteType") == "CRYPTOCURRENCY"
        ]

    @staticmethod
    def transform_data(
        query: YFinanceCryptoSearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceCryptoSearchData]:
        """Return the transformed data."""
        return [YFinanceCryptoSearchData.model_validate(d) for d in data]
