from __future__ import division  # makes division work correctly
from builtins import range
import abcEconomics as abce
import copy

class Household(abce.Agent, abce.Household):
    def init(self, firms_info, labor_alphas, needed_labor):
        """ 1. labor_endowment, which produces, because of w.declare_resource(...)
        in start.py one unit of labor per month
        2. Sets the utility function to utility = consumption of good "GOOD"
        """
        self.create('adult', 1)
        self.num_firms = len(firms_info)
        self.firms_info = copy.deepcopy(firms_info)
        self.alphas = {key:(labor_alphas[key]/sum(labor_alphas.values())) for key in labor_alphas.keys()}
        cd = self.alphas
        # creates {GOOD1: 1/3, GOOD2: 1/3, GOOD3: 1/3}
        self.consumption_function = self.create_cobb_douglas_utility_function(cd)
        self.current_utility = 0
        self.needed_labor = needed_labor
        self.shocks = [1]*self.num_firms

    def create_labor(self):
        self._inventory.haves['labor']=self.needed_labor

    def sell_labor(self):
        """ offers one unit of labor to firm 0, for the price of 1 "money" """
        sum_labor = 0
        for i in range(self.num_firms):
            sum_labor += self.firms_info[i]['ratio_dict']['labor']

        for i in range(self.num_firms):
            self.sell(('firm', i),
                      good="labor",
                      quantity=self.possession('labor')*((self.firms_info[i]['ratio_dict']['labor']*self.shocks[i]) / sum_labor),
                      price=1)

    def buy_goods(self):
        """ receives the offers and accepts them one by one """
        money = self.possession("money")
        self.create('money',20)
        quotes = self.get_messages('quote')
        for quote in quotes:
            price = quote.content[1]
            self.buy(quote.sender,
                     good=quote.content[0],
                     quantity=self.alphas[quote.content[0]],
                     price=price)

    def consumption(self):
        """ consumes_everything and logs the aggregate utility. current_utiliy
        """
        self.current_utility = self.consume(self.consumption_function, ["GOOD_sector%i" % (i) for i in range(self.num_firms)])
        # self.log('HH', self.current_utiliy)

    def apply_shocks(self, shocks):
        self.shocks = copy.deepcopy(shocks)