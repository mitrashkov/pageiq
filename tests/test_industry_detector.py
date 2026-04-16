from app.services.industry_detector import guess_industry


def test_guess_industry_ecommerce():
    guess = guess_industry(
        title="My Shop",
        description="Buy products, checkout fast, shipping worldwide",
        keywords=["cart", "checkout", "product"],
        tech_stack=["Shopify"],
    )
    assert guess is not None
    assert guess.label == "ecommerce"
    assert 0.0 < guess.confidence <= 1.0


def test_guess_industry_none_when_no_signals():
    guess = guess_industry(title=None, description=None, keywords=[], tech_stack=[])
    assert guess is None

