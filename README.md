# steamscope

What this application must do?
1. Scrape Steam's deals/specials page and extract game data
2. Store each scrape run in MongoDB with a timestamp
3. Avoid duplicate entries for the same game in the same run
4. Run automatically on a schedule (every 6–12h)
5. Allow querying the database for analysis
6. Produce at least 4 visualizations from the collected data
7. Train a simple ML model to classify "great deals"
