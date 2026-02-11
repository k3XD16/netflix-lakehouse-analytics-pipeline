# 🚀 AWS Glue Workflow – CLI Implementation (PowerShell)

**Workflow:** Netflix Medallion Pipeline (Bronze → Silver → Gold)

**Execution:** AWS CLI (PowerShell)


## ✅ Execution Flow
```
Start Trigger
   ↓
Raw Crawler
   ↓
Raw → Silver ETL
   ↓
Silver Crawler
   ↓
Silver → Gold ETL
   ↓
Gold Crawler
```
## Step-by-Step CLI Commands 

### 1️⃣ Create Glue Workflow

```powershell
aws glue create-workflow `
  --name netflix-data-pipeline-workflow `
  --description "Netflix end-to-end data pipeline orchestration" `
  --region ap-south-1
```

### 2️⃣ Create On-Demand Start Trigger (Raw Crawler)

```powershell
aws glue create-trigger `
  --name start-trigger-ondemand `
  --type ON_DEMAND `
  --workflow-name netflix-data-pipeline-workflow `
  --actions "[{""CrawlerName"":""crawler-raw-netflix""}]"
  --start-on-creation
```

### ▶ Start the workflow
```powershell
aws glue start-workflow-run `
    --name netflix-data-pipeline-workflow
```

### 3️⃣ Raw → Silver ETL Trigger
```powershell
aws glue create-trigger `
  --name trigger-etl-raw-to-silver `
  --type CONDITIONAL `
  --workflow-name netflix-data-pipeline-workflow `
  --predicate "{""Conditions"":[{""CrawlerName"":""crawler-raw-netflix"",""CrawlState"":""SUCCEEDED""}]}" `
  --actions "[{""JobName"":""etl-raw-to-silver""}]"
```

### 4️⃣ Silver Crawler Trigger
```powershell
aws glue create-trigger `
  --name trigger-crawler-silver `
  --type CONDITIONAL `
  --workflow-name netflix-data-pipeline-workflow `
  --predicate "{""Conditions"":[{""JobName"":""etl-raw-to-silver"",""State"":""SUCCEEDED""}]}" `
  --actions "[{""CrawlerName"":""crawler-silver-netflix""}]"
```

### 5️⃣ Silver → Gold ETL Trigger
```powershell
aws glue create-trigger `
  --name trigger-etl-silver-to-gold `
  --type CONDITIONAL `
  --workflow-name netflix-data-pipeline-workflow `
  --predicate "{""Conditions"":[{""CrawlerName"":""crawler-silver-netflix"",""CrawlState"":""SUCCEEDED""}]}" `
  --actions "[{""JobName"":""etl-silver-to-gold""}]"
```

### 6️⃣ Gold Crawler Trigger
```powershell
aws glue create-trigger `
  --name trigger-crawler-gold `
  --type CONDITIONAL `
  --workflow-name netflix-data-pipeline-workflow `
  --predicate "{""Conditions"":[{""JobName"":""etl-silver-to-gold"",""State"":""SUCCEEDED""}]}" `
  --actions "[{""CrawlerName"":""crawler-gold-netflix""}]"
```

### 7️⃣ (Optional) Daily Schedule Trigger – 2:00 AM IST
```powershell
aws glue create-trigger `
  --name schedule-trigger-daily `
  --type SCHEDULED `
  --schedule "cron(30 20 * * ? *)" `
  --workflow-name netflix-data-pipeline-workflow `
  --actions "[{""CrawlerName"":""crawler-raw-netflix""}]"
```

***But in our case, we didn't add this schedule trigger since we are running the workflow on-demand.***


---
