---
layout: article
categories: articles
Title: Sprint 1 Update
Excerpt: "A short update from our teams on the progress that has been made during the proof of concept sprint"
tags: []
image:
  feature:
  teaser: articles/update_1.png

---

The two week point we've just hit marks the end of the first planned sprint. We are expecting to have the proof of concept model finalised in the coming week, but we reached out to each of the teams for an update of how their work is going. You can read summaries below:

## Disease team

The disease team is lucky as we're starting from a much more advanced place than the other teams. There are many open source models out there and we've just had to do minimal work to adapt them to take inputs from the lockdown team's output. For the POC sprint we're going with the [Auquan SEIR model](https://blog.auquan.com/page/cvdmdl2) and our PR is up in staging!



## Lockdown team

We've achieved more than we originally set out to, but have traded that off by limiting our research to fewer countries. We've started to build up a repository of different lockdown strategies and have produced daily resolution data for India from March 1st to May 18th. Now we have the approach locked down, we can scale this up and quickly add new countries.



## Economic Modelling team

The economic modelling team had probably the hardest initial task and you can see their road map in the [econ_model_1 spec](#). Apart from doing the research to decide on this short term approach, we are working towards a POC model that creates simple GVA estimates by applying a hair cut based on sector productivities given by the Lockdown team.



## Loss team

We've got a clear roadmap for v0 and v1. Initially we will use a Pereito method for estimation, before switching over to a WELLBY approach suggested in the [whitepaper](articles/overview-slides/). Waiting for the final work from teams 1-3 before we commit our code for the first sprint.



## Data and Maintainer teams

Not much to say here, we've set up the repository and a process for data requests. Enjoying the slow start whilst it lasts!
