from pages import paginate

products = [f"p{i}" for i in range(1, 26)]
assert paginate(products, 1, 10)[0] == "p1", paginate(products, 1, 10)
print("ALL OK")
