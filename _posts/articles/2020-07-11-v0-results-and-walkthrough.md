---
layout: article
categories: articles
Title: V0 Release Walkthrough
Excerpt: "This is a code and text walkthrough of the V0 HELP model, containing working health, economic, lockdown and optimization modules"
tags: []
image:
  feature:
  teaser: articles/whitepaper.png

---

On the 29th June, the HELP project released the V0 of our lockdown impact model. This fully functional release contains 4 modules that are interconnected and work together to produce the estimated impact for a specific country and intervention pair. Users can select a country to investigate and will automatically be shown the best lockdown policy(ies) for that country over the time period.

The model is capable of automatically identifying possible policies to apply to the country of interest. It will then manipulate them to be applicable to the target country, before calculating an estimate for the country’s economic trajectory with and without that intervention. This process is repeated for each potential policy before the model returns the best policies and key statistics.

The final model design is as follows:

![model overview](/images/v0/1)


The aim of this article is to give you a run down of how the model generates its outputs. The diagram above should hopefully serve as a mental map of how the different modules interact.. As there isn’t currently a UI, we will look through the main notebook to understand how all the parts come together. [The main notebook can be found here for reference.](https://github.com/Auquan/help_project/blob/staging/src/main.ipynb)

As you will see, the notebook follows the following flow (excluding setup), so we will follow the same path in this article.

![model walkthrough](/images/v0/2)


### Step One: Selecting a country and gathering data

The first step we need to do is to pick a country to work with and a time range we’re interested in. In this example we have used India asthe V0 version of the lockdown strategies contains the most time series information about the Indian lockdown. In V1 this will be expanded to include most of the OECD countries, as well as any specific countries that users request.

It should be quickly noted that in this example we’ve set the time frame we’re interested in as being in the past. The reason we’ve done this is to allow us to compare the outputs of the model with what actually happened - thus giving us better feedback about the model’s efficacy. If you wanted to compare the effects of possible interventions, the process would be the same to investigate and apply policies into the future. Here’s the code to this:

![setup code](/images/v0/3)


The most interesting part is in the last cell above. Here, we are looking through the lockdown policy timeframe and returning all the policies that can be applied. In this case we get 4 returned as the indian time series data contains 4 different policies (unique combinations of interventions). This can be explained in the diagram below:

![policy explaination](/images/v0/4)


This data would contain 3 policies, with each orange box identifying one distinct policy. On the left the policy would be made of three interventions (social distancing, closing hospitality industry and closing schools). The middle contains the same plus a strict lockdown, and the right hand policy would just be distancing and a closed hospitality industry.

*Within the HELP project we refer to a policy as a unique combination of interventions implemented at the same time. An intervention (sometimes NPI), is a single rule - e.g. making face masks mandatory.*


### Step Two: Train and run the different modules

The next couple of cells contain configuration, so we’re going to skip them. Sufficient to say that they are setting up the lockdown policy and health modules.

Now everything is just about set up, we need to retrain our models for the specific countries that we’re looking at. In the initial V0, the focus of the work was to integrate all the different modules and work out how they would interact. To help this process we’re using a single health and economic model. In later versions we will implement the Auquan_Seir, Pyross and other health models. On the economic side, we will create comprehensive agent based and SAM models.

![health model code](/images/v0/5)

There are two steps in using the health model. First, the model trains on data from the target country. This creates a baseline of the disease dynamics for that county, as derived from their actual data. After this, the health_model.parameter_mapper iterates through the list of policies selected earlier and calculates how those policies will modify the health model parameters. These will then be applied by the optimisation module to calculate the health impact of the policies.

Next the economic module is called to generate the economic impact of the chosen policies. In V0 this module is simplified, simply taking how open each sector is and reducing the previous GVA by that amount. (i.e. if the chemical sector is 20% open, the econ model will reduce the most recent sector GVA by 80%). Accordingly, this module can be called in one line:

![economic model code](/images/v0/6)

### Step Four: Run the Optimisation Module:

![optimisation code](/images/v0/7)

The final step is to run the optimisation module. This will then iterate through the policies to calculate the impact of each and suggest the best approach. In the V0 module, the optimizer uses a Pareto optimization to find a frontier of best policies for the user to investigate further. This will identify policies that have lowest health impacts and lowest economic impacts. Where there is a trade-off, the model will return all possibilities. In V1 we will be adding an implementation of WELLBYs to further help compare the impacts of these policies.

The module will then print the policies that are identified by the optimization, including a plot of how the best ones compare. In this example, there is only one policy in the pareto frontier, so it is just returned alone.

The final portion of the code deals with visualisation of the health model and optimisation module. It gives the user a detailed breakdown of the models projections for the top policy when compared to the baseline (if available). As we have been looking to apply a policy in the past, we can compare the model’s predictions to what actually happened. Below we can see that our model's forecast was reasonably close to what happened, though it does seem to overestimate the impact of COVID-19. This could be due to an uncaptured exogenous difference between the two countries, or could be a calibration error that will be addressed in V1.

![printout](/images/v0/8)
