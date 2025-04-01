# main.py
from app.portfolio.portfolio import create_and_optimize_portfolio, print_purchases_result
from app.data.data_collector import collect_stock_data
def main():
    """
    MAX_ASSET_SHARE = 0.1
    exchange_rate = get_usd_rub_cbr()
    print(exchange_rate)
    sectors_updated = update_sector_data()
    # Формирование портфеля по секторам из конфигурационного файла
    result = form_portfolio(sectors_updated, ["Finance", "IT", "Raw"], max_asset_share=MAX_ASSET_SHARE, total_budget=1000000, target_beta=1, include_crypto=True, exchange_rate=exchange_rate)
    companies, weights, weight_dict = extract_companies_and_weights(result)
    print("Компании:", companies)
    print("Веса:", weights)
    print("Словарь весов:", weight_dict)
    collect_stock_data(companies, days=365)
    # Загрузка чистых данных и аналитических прогнозов
    df_clean = load_clean_data()
    mu_anal = load_analyst_returns(companies)
    print(mu_anal)
    # Оптимизация портфеля
    optimized_weights = optimize_portfolio(df_clean, mu_anal, weights, MAX_ASSET_SHARE)
    print("Оптимизированные веса:", optimized_weights)

    print(calculate_purchases(optimized_weights,1000000, exchange_rate=exchange_rate))
    """
    selected_sectors = ["Finance", "IT", "Raw"]
    max_asset_share = 0.1
    total_budget = 1000000



    result = create_and_optimize_portfolio(
        selected_sectors,
        max_asset_share,
        total_budget,
        target_beta=1.0,
        include_crypto=True,
    )
    print_purchases_result(result)
if __name__ == "__main__":
    main()
