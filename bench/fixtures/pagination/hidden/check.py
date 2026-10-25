from pages import page_count, paginate

products = [f"p{i}" for i in range(1, 26)]
assert paginate(products, 1, 10) == [f"p{i}" for i in range(1, 11)]
assert paginate(products, 3, 10) == ["p21", "p22", "p23", "p24", "p25"]
assert paginate(products, 4, 10) == []
assert page_count(products, 10) == 3, f"page_count = {page_count(products, 10)}, expected 3"
assert page_count([], 10) == 0
assert page_count(products[:20], 10) == 2
print("OK")
