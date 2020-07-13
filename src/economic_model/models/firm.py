from __future__ import division  # makes division work correctly
import random
import abcEconomics as abce
import copy
import numpy as np
import sys,os

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__
class Firm(abce.Agent, abce.Firm):
    def init(self, sector, output_input_ratio, num_sectors, ratio_dict ):
        """
        1. Gets an initial amount of money
        2. creates a production function that produces using fixed ratios, any extra input doesn't get used and is wasted.
        """
        self.create('money', 10)
        self.buy_ratio = 1
        self.ratio_dict = copy.deepcopy(ratio_dict)
        self.output_input_ratio = output_input_ratio
        self.last_output = 0
        for key in ratio_dict.keys():
            if key=="labor":
                continue
            self.create(key,ratio_dict[key])
        self.sector = sector
        self.expenses = 1
        self.num_sectors = num_sectors
        self.mygood = "GOOD_%s" % self.sector  # GOOD1 if self.id == 1
        self.target = 1
        self.target_input = copy.deepcopy(ratio_dict)
        self.labor_available = 1

        # Not using cobb douglas, fixed ratios for now
        # self.production_function = self.create_cobb_douglas(self.mygood, 1, {"labor": 1})

        self.production_function = self.create_production_function(ratio_dict)
        self.price = 1
        self.inventory = 0

    def create_production_function(self, ratio_dict):
        """
        creates production function
        :param ratio_dict: uses the ratio for each input good to define the production function
        :return: returns the production function
        """
        def production_function(**goods):
            """
            production function for this firm, takes input in fixed ratios, if anything extra is given over and above the ratio it's useless
            :param goods: dictionary with available input goods
            :return: final produce with remaining extra input goods
            """
            ratios = [goods[name] / ratio_dict[name]
                      for name in ratio_dict.keys()]
            output = (self.output_input_ratio*2)*min(ratios)
            self.last_output = output
            output_dict = {}
            for name in ratio_dict.keys():
                if name == "labor":
                    output_dict[name] = 0
                    continue
                output_dict[name] = goods[name] - (min(ratios)*ratio_dict[name])
            # enablePrint()
            # print({self.mygood:output})
            # blockPrint()
            # print("\n\n\n\n\n\n\n")
            output_dict[self.mygood]+= output

            return output_dict
        return production_function

    def buy_labor(self):
        """
        receives all labor offers and accepts them according the need and money
        :return:
        """
        # self.create('money',2)
        # print(self.id, self.possession('money'))
        oo = self.get_offers("labor")
        self.labor_available = 0
        for offer in oo:
            self.labor_available += offer.quantity
            self.accept(offer, min(offer.quantity,self.target_input['labor']*self.buy_ratio))

    def buy_goods(self):
        money = self.possession("money")
        ### try for slightly more production

        buying_list = {key:max(0,((2*self.target_input[key])-self.possession(key))) for key in self.target_input.keys()}

        quotes = self.get_messages('quote')
        buy_ratio = 0
        for key in self.ratio_dict.keys():
            if key==self.mygood:
                continue
            buy_ratio += self.ratio_dict[key]

        buy_ratio = 1
        self.buy_ratio = buy_ratio
        for quote in quotes:
            price = quote.content[1]
            if quote.content[0] in buying_list.keys():
                self.buy(quote.sender,
                        good=quote.content[0],
                        quantity=buying_list[quote.content[0]],
                        price=price)
        #handle keeping your good for next round

    def production(self):
        """ uses all labor that is available and produces
        according to the set cobb_douglas function """
        self.create('money',100)

        a = self.id
        availability = []
        for key in self.ratio_dict.keys():
            availability.append(self.possession(key)/self.ratio_dict[key])
        min_availability = min(availability)
        if min_availability < 1:
            ### try to find good with minimum availability and available resources after that try to maximize production
            key_min_availability = list(self.ratio_dict.keys())[np.argmin(availability)]
            # enablePrint()
            # print(key_min_availability)
            # print(min_availability)
            # blockPrint()
        # self.target_input[key_min_availability] = self.target_input[key_min_availability] * 1.05
        for key in self.ratio_dict.keys():
            if abs((self.target_input[key]/self.ratio_dict[key]) - min_availability)<0.0001 and self.target_input[key]>0:
                self.target_input[key] = self.target_input[key]
            else:
                self.target_input[key] = min_availability*self.ratio_dict[key]
        ## try to buy more for the bottleneck

        self.produce(self.production_function, list(self.ratio_dict.keys()))


    def quotes(self):
        for i in range(self.num_sectors):
            if i == self.id:
                continue
            self.send_envelope(('firm', i), 'quote', (self.mygood, self.price))

        self.send_envelope(('household', 0), 'quote',
                           (self.mygood, self.price))

    def sell_goods(self):
        """ sells goods """
        ### if available quantity less than total demand + need for own production then sell them in the same ratios
        # if self.id == 18:
        #     print(self.id)
        oo = self.get_offers(self.mygood)
        total_demand = 0
        for offer in oo:
            total_demand += offer.quantity
        if total_demand > (self.possession(self.mygood)-(self.target_input[self.mygood])):
            sale_ratio = (self.possession(self.mygood))/(total_demand +(2*self.target_input[self.mygood]))
        else:
            sale_ratio = 1
        for offer in oo:
            self.accept(offer, sale_ratio*offer.quantity)
        self.inventory = self.possession(self.mygood)

    def adjust_price(self):
        self.inventory = self.possession(self.mygood)
        if self.inventory < 0.1:
            self.price += (0.1 - self.inventory) * \
                0.01  # random number [0, 0.1]
        if self.inventory > 0.1:
            self.price = max(0.01, (self.price - 0.1) *
                             0.01)  # random number [0, 0.1]

    def adjust_target(self):
        self.inventory = self.possession(self.mygood)
        if self.inventory > 2*(self.target_input[self.mygood]):
            self.target =1
        else:
            self.target = 1
        # self.target_input ={}
        for key in self.ratio_dict.keys():
            self.target_input[key]=self.target*self.target_input[key]