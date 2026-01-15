-- Seed data for StockPulse

-- Default factor weights (20% each)
INSERT INTO factor_weights (factor_name, weight, description) VALUES
    ('value', 0.200, 'Measures how cheap the stock is relative to fundamentals (P/E, P/B, P/S)'),
    ('growth', 0.200, 'Measures revenue and earnings growth rates'),
    ('profitability', 0.200, 'Measures profit margins, ROE, and ROIC'),
    ('momentum', 0.200, 'Measures recent price performance (3m, 6m returns)'),
    ('quality', 0.200, 'Measures financial health (debt levels, current ratio, FCF)')
ON CONFLICT (factor_name) DO NOTHING;
