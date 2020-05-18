# How to contribute

It makes me really glad you are reading this because volunteers like you are the backbone of this project. Thank you for all your contibutions.

If you haven't joined us already, come join us ([#the-help-project](https://join.slack.com/t/the-help-project/shared_invite/zt-ebvwz2np-SXVW6tJ20ayX4gQqRFQZRA) on slack). We want you working on things you're excited about.

Here are some important resources:

  * [H.E.L.P Project Details](https://quant-quest.com/landingPage/helpproject) has all the information required,
  * [Working Whitepaper](http://opengovernment.org/pages/wish-list) is the detailed outline of the project and approaches we are tackling.
  * [Project Overview Slides](https://links.quant-quest.com/HELPSlides) has high level information about the project.
  * [H.E.L.P. Project Slack](https://join.slack.com/t/the-help-project/shared_invite/zt-ebvwz2np-SXVW6tJ20ayX4gQqRFQZRA) for all the discussion around the project and collaboration.

# Contributing guidelines:

## Structure
  * There are different folders for economic_model, disease_model, policy_details. Each folder is used by respective teams for their work.
  * Each folder has its own set of requirements.txt for packages to avoid conflicts when merging.
  * Top level requirements.txt will install the latest version of a specific package so please use the latest stable versions where ever possible.
  * Test folder will mimic the structure of the src folder and tests go in their respective counterparts. Pytest conventions to be followed.
  * There are data folders for csv data < 1mb in respective modeling folders, if anything bigger goes into s3 bucket

## Branching:
  * Staging is the main branch used to do development with stable versions released to master.
  * Please take a branch off staging and name it meaningfully to indicate the work being done in the branch.
  * To merge code back in, create a pull request. It will have to be reviewed by a minimum of 2 reviewers and pass CI checks.

## Pull Request Guidelines:
  * Please name your pull request appropriately as it will become the commit message.
  * Please leave a meaningful description on the Pull Request so the reviewers have better context when reviewing.
  * Please assign reviewers once the CI checks have passed.
  * Please use github commenting for code review discussions and resolve the issues before approving the pull request and merging it.
  * All pull requests must include counterpart tests, as long as the folder structure above is honored CI will automatically run them. Test can also be run locally using pytest
  * Commits should be squashed when merging a PR and no merge commits should be created.

## Issue Creation:
  * Please use github issues to create an issue and discuss it.
  * Teams will triage their respective issue and provide resolution time frame or close the issue if the fix wont happen/is by design.

## Master Releases:
  * Release to master will be done through a way of PR from staging to master.
  * A reviewer from each team + repository owner will be required to sign off on the PR.
  * Everything else from PR guidelines above will apply.

## Testing
  * Any new code additions require counterpart tests to be added to the test folders
  * Use pytest conventions when testing and write unit tests for functions and classes.
  * Integration tests should be written with well defined fixtures.
  * Fixtures should be specified on a module level unless absolutely required on test case level.
  * All tests must pass for a PR to be merged.

## Coding conventions
 * We use pylint for linting and it is part of CI check and pre commit hook.
 * While pylimt may seem limiting/adding bloatware we are always open to suggestions of adding new rules/disabling some old ones.

Thanks,
H.E.L.P Project Team
