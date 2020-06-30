---
layout: article
categories: articles
Title: The HELP Story So Far
Excerpt: "A short summary of the teams achievements to date and current plan"
tags: []
image:
  feature:
  teaser: articles/whitepaper.png

---

The HELP project is a non-commercial, volunteer led project to model the combined health and economic impacts of COVID-19. Founded with the understanding that a successful approach to managing the crisis required analysis that combined the health and economic impacts from the bottom up. In other words we’re a team that’s aiming to help countries find lockdown strategies that save lives and the economy, not lives or the economy.

The team itself has an incredibly strong background in development and data science, with members working at firms including:

- Goldman Sachs
- Google
- Gusto
- Microsoft
- (plus throw in a couple founders too!)

The project had a strong start with our health model (the [Auquan-SEIR model](https://blog.auquan.com/page/cvdmdl2)) being used by the CDC as part of their ensemble models. This put the work alongside models from seasoned academics from Harvard, John Hopkins, MIT and Imperial in the UK. This provided a clear indication of the quality of work the team was able to produce and the real value that could be delivered by community efforts.

The next big step for the project was joining the [COMO consortium](https://www.tropicalmedicine.ox.ac.uk/news/como-consortium-the-covid-19-pandemic-modelling-in-context). The COMO consortium is a group of academics (e.g. [Oxford](https://www.tropicalmedicine.ox.ac.uk/team/lisa-white), [Cornell](https://weillcornell.org/nathanielhupert) and the [WHO](https://www.linkedin.com/in/keyrellous-adib/)) that are working to help policymakers in 47 different low and middle income countries to plan their exit strategies. Countries involved include, but are not limited to, Brazil, some US states and the [WHO-EMRO](http://www.emro.who.int/index.html) block of countries. Together HELP and COMO have set up an economic working group combining our expertise with their WHO, and country specific, economists to deliver actionable models for countries that need the support right now.

In an effort for transparency, the team has decided to open source all of the code produced and provide regular updates on the [website](https://www.help-corona.com). In the last couple of weeks we have released the V0 model, which uses simplified models to create a proof of concept of how the final model will work together. The overall process can be seen below:

![Model Flow Diagram](/images/model_example.png)

To view the V0 code, see the project's [Github repository](https://github.com/Auquan/help_project/).

The team is currently working towards the next iteration of the model that will be delivered in the coming two weeks. Improvements in this version will include:

- The ability to apply more historical lockdown strategies
- The ability to use the PyRoss health model as well as the AuquanSEIR model
- Development work on an Agent based and a SAM based economic model
- Improvement of the optimisation module and movement towards using WELBYs as an objective measure
