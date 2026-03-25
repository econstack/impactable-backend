# Impactable

Impactable is a library that implements an efficient data model and API using the Django Rest Framework for impact investors to collect, aggregate, and report on impact data

Written by Ron Leung and licensed under Creative Commons Non-Commercial (CC BY-NC) (note: maybe MIT license so that for-profit users can roll their own)

This software is intended for use by DFIs, other impact investors and their investees who have to report on their impact, typically on indicators on impact performance (e.g job creation). Collectively, these are referred to as Users. 

## Additionality Monitoring and Reporting

There is a standalone additionality module that is based on the [OECD-DAC](https://one.oecd.org/document/DCD/DAC/STAT(2024)15/en/pdf) guidance with 4 types of Financial Additionality and 3 types of Value Additionality. Indicators for monitoring and reporting can be attached to each type and can be configured for each User. 

Most additionality indicators are categorical and are typically classified as something like "achieved" or "not yet achieved" during monitoring with added categories of "not achieved" or "partly achieved" at termination. These can be remapped to the methodological language used by the User. 

## Impact Monitoring and Reporting

### Key Features
- Uses a tagging system so that almost all DFIs' impact methodologies and frameworks can be modeled for aggregration and reporting. The tagging system abstracts away from the internal complexities of any impact hierarchy. Aggregation is allowed by tag where tags can be a custom country group (e.g. BRIC), an organizational practice (e.g. clean transportation), a custom sector (e.g. energy and transport), an impact area (e.g. social inclusion) or instrument (e.g. blended finance), among others

  - Example 1. The African Development Bank's [ADOA Framework](https://www.afdb.org/en/documents/2022-adoa-general-framework) has frameworks that are sector specific with common impact categories (e.g. "households", "private sector development") but with different indicators for each category and by sector. Both the sectors and impact categories can be applied as tags for each project indicator so that we can aggregate up to each sector or impact category. 
  - Example 2. The International Finance Corporation's [AIMM Methodology](https://www.ifc.org/en/our-impact/measuring-and-monitoring/aimm-dimensions) has 28 sector frameworks. Each sector framework looks at "project outcomes" and "market outcomes", each with 3 top level categories called AIMM dimensions (e.g. "economy-wide effects"). Each top level category has additional impact areas (e.g. "job creation") for which there are associated indicators (e.g. "number of FTE jobs created"). Each project indicator can be tagged with the relevant sector framework, the top level categories and any of the additional impact areas so that we can aggregate up to each of them for monitoriong and reporting.  

- Delivery rate is the monitoring metric to which all indicators are converted for cross indicator comparison and aggregation. The delivery rate is top and bottom truncated. The main benefits are:
  - Enables aggregation across diverse project types, impact types and indicator types
  - Mitigates risk that large projects from dominating aggregated and monitoring metrics. For instance, if there is a single project with expected 5 million patients per year vs 10 other health projects ranging from 5,000 to 25,000 patients per year, straight aggregation means that none of the other projects will matter for measuring "overall" performance on "patients served". Nothing would be learned about smaller projects with such aggregation methods. 
  - Mitigates risk that over-delivery on a single indicator will end up dominating the "overall" performance for that project. For instance, consider a project with 5 indicators, of which one was job creation. If only 10 jobs were expected to be created at a 5000 person firm, creating 100 jobs would yeild a delivery rate of 1000% without top truncation and would lead to the project being rated as "overperform" even where all the other project indicators only achieved 20% delivery rate. Nothing would be learned about the other indicators without some top and bottom truncation. 

- Almost all of the [IRIS](https://iris.thegiin.org/catalog/download/) and [HIPSO](https://indicators.ifipartnership.org/dashboard/) indicators are available from the Impactable indicator catalog for selection into the User's indicator catalog. Also allows for user defined indicators. 

- API (and browser-based dashboard) to import User data and to export monitoring and reporting data. 
  - Users can update project monitoring data via the API 
  - Users can export aggregated monitoring data via the API for any of the available tags. The export will include the delivery rate statistics as well the underlying data project. 
  - Users can export the aggregate data for any indicator (e.g. number of jobs created) with a breakdown under each available tag (e.g. by User defined practice)
  - Users can export the underlying data for their own last-mile analysis and bespoke reporting (e.g. Tableau, PowerBI) 

### Setup
- User indicators are defined or selected from the Impactable indicator catalog to form the User indicator catalog (User catalog for short). User specific tags are applied to the indicators in the User catalog.  
- Project configuration data such as name, internal ID, country, etc  is loaded, along with the relevant tags (e.g. "blended finance", "IDA") and the list of monitoring indicators (from User catalog). These form a list of project indicators. 
- Each project indicator's actual value during monitoring is loaded using the project and indicator IDs as the key. 




## TODO

2026-03-12
- make repo for data projects - github  
- make repo for impactable - github
- setup indicator and project models
  - project 
  - indicator_definition  
  - pindicator_config - baseline and targets for project-indicator
    FK to project and indicator_definition 
  - pindicator_data - actuals and expected by year for project-indicator, FK to pindicator_config 
    - if categorical, then uses achieved/not achieved boolean
- have in_user_catalog flag to filter for user indicators, test pre-load hipso outcome indicators
- ~~use the dac additionality categories~~
  - ~~pull dac table for additionality~~
    - note need indicators for categories?
- use hipso and iris fields 
  - have is_iris flag 
  - have is_hipso flag
    - pull table and definitions for hipso indicators at the [hipso dashboard](https://indicators.ifipartnership.org/dashboard/#)
      - ~~issues - does not have table to download but have to scrape webpage. Use LLM~~ (scrapped into SDG and definitions csv files)
      - load indicators into indicator_definition model
  
- design afdb config as example
  - look at AAR 2025 database for indicators 
    - DO
    - Additionality
- design fictional DFI as example (factory)
  - GAIF - global agric industry fund
    - use hipso indicators overlay with practices (agric, manufacturing, infrastructure, ICT)
      - need to assign indicators to practices 
    - generate projects 
      - assign practice 
        - assign indicators
      - assign country or countries/region




2026-03-10
- ~~remove django-treebeard~~
- ~~add django-taggit~~
