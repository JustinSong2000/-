class SearchItem:
    def __init__(self, keyword, version, region, subject, min_price, start_page=1, end_page=10):
        self.keyword = keyword
        self.version = version
        self.region = region
        self.subject = subject
        self.min_price = min_price
        self.all_sku_min_price = min(self.min_price)
        self.start_page = start_page
        self.end_page = end_page


class ResultItem:
    def __init__(self, subject, price, sku_price):
        self.subject = subject
        self.price = price
        self.sku_price = sku_price
        self.diffs = float(sku_price) - float(price)
