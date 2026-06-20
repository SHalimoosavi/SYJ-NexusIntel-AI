from pydantic import BaseModel


class RevenueForecastRequest(BaseModel):
    pass


class RevenueForecastResponse(BaseModel):
    pipeline_value: int
    weighted_revenue: float
    won_revenue: int
    forecast_revenue: float
    close_rate: float
    annual_projection: float
