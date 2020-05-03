class MarketTracker:

    def __init__(self):
        self.tracker = {}
        self.trackerSnapshot = {}
        self.trackerIndex = 0

    def Update(self, price_changes, lookBackLimit=10,  tickBounds=[0.33, 0.67]):
        stocksToBuy = {}
        stocksToKeep = {}
        stocksToSell = {}

        positive_changes = {k: v for k, v in price_changes.items() if v > 0}
        negative_changes = {k: v for k, v in price_changes.items() if v <= 0}

        for symbol in positive_changes:
            if symbol not in self.tracker:
                self.tracker[symbol] = {"positive": 0, "negative": 0}
                self.trackerSnapshot[symbol] = []
            self.tracker[symbol]['positive'] += 1
            self.trackerSnapshot[symbol].append(
                self.tracker[symbol].copy())  # Save to snapshot

        for symbol in negative_changes:
            if symbol not in self.tracker:
                self.tracker[symbol] = {"positive": 0, "negative": 0}
                self.trackerSnapshot[symbol] = []
            self.tracker[symbol]['negative'] += 1
            self.trackerSnapshot[symbol].append(
                self.tracker[symbol].copy())  # Save to snapshot

        self.trackerIndex += 1
        if self.trackerIndex < lookBackLimit:
            return stocksToSell, stocksToBuy, stocksToKeep
        # calculate
        for symbol in price_changes:
            history = self.trackerSnapshot[symbol][-lookBackLimit:]
            previous_history = history[0]

            # traverse from latest and check for number of upticks or downticks of the stock
            upticks = 0
            downticks = 0
            for item in history[1:]:
                upticks += 1 if (item['positive'] -
                                 previous_history['positive']) == 1 else 0
                downticks += 1 if (item['negative'] -
                                   previous_history['negative']) == 1 else 0
                previous_history = item

            uptickPercentage = (upticks * 1.0)/lookBackLimit
            #downtickPercentage = (downticks * 1.0)/lookBackLimit
            if uptickPercentage < tickBounds[0] and price_changes[symbol] > 0:
                stocksToBuy[symbol] = price_changes[symbol]
            elif uptickPercentage < tickBounds[0] and price_changes[symbol] <= 0:
                stocksToSell[symbol] = price_changes[symbol]
            elif uptickPercentage > tickBounds[0] and uptickPercentage < tickBounds[1]:
                stocksToKeep[symbol] = price_changes[symbol]
            elif uptickPercentage > tickBounds[1] and price_changes[symbol] > 0:
                stocksToKeep[symbol] = price_changes[symbol]
            elif uptickPercentage >tickBounds[1] and price_changes[symbol] <= 0:
                stocksToSell[symbol] = price_changes[symbol]

        return stocksToSell, stocksToBuy, stocksToKeep

    def Reset(self):
        self.tracker = {}
        self.trackerSnapshot = {}
        self.trackerIndex = 0
