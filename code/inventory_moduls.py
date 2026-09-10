import numpy as np


def calculate_safety_stock(
    z_score,
    demand_std,
    lead_time_days
):
    """
    Calculate Safety Stock using demand variability
    and supplier lead time.
    """

    return (
        z_score
        * demand_std
        * np.sqrt(lead_time_days)
    )


def calculate_rop(
    avg_daily_demand,
    lead_time_days,
    safety_stock
):
    """
    Calculate Reorder Point (ROP).
    """

    return (
        avg_daily_demand * lead_time_days
        + safety_stock
    )


def calculate_eoq(
    annual_demand,
    ordering_cost,
    holding_cost
):
    """
    Calculate Economic Order Quantity (EOQ).
    """

    if holding_cost <= 0:
        return 0

    return np.sqrt(
        (2 * annual_demand * ordering_cost)
        / holding_cost
    )


def calculate_annual_ordering_cost(
    annual_demand,
    ordering_cost,
    order_quantity
):
    """
    Calculate annual ordering cost.
    """

    if order_quantity <= 0:
        return 0

    return (
        annual_demand / order_quantity
    ) * ordering_cost


def calculate_annual_holding_cost(
    order_quantity,
    holding_cost
):
    """
    Calculate annual holding cost.
    """

    if order_quantity <= 0:
        return 0

    return (
        order_quantity / 2
    ) * holding_cost


def calculate_inventory_cost(
    annual_demand,
    ordering_cost,
    holding_cost,
    order_quantity
):
    """
    Calculate relevant annual inventory cost.
    """

    if order_quantity <= 0:
        return 0

    ordering_cost_total = (
        annual_demand / order_quantity
    ) * ordering_cost

    holding_cost_total = (
        order_quantity / 2
    ) * holding_cost

    return (
        ordering_cost_total
        + holding_cost_total
    )
print("INVENTORY MODULE LOADED")
print(calculate_annual_ordering_cost)