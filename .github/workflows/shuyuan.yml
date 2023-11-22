name: 书源
on:
  workflow_dispatch:
  schedule:
    - cron: "0 10 */3 * *"

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests bs4

      - name: Run Script
        run: python shuyuan.py

      - name: Commit files
        run: |
          git config --local user.email "${{ secrets.USER_EMAIL }}"
          git config --local user.name "${{ secrets.USER_NAME }}"
          echo "https://github.com/${{ github.repository }}:${{ secrets.REPO_TOKEN }}" > .git-credentials
          git add .
          git commit -m "Add new JSON files" || echo "No changes to commit"
          git push
          
      - name: Send Telegram notification
        run: |
          curl "https://api.telegram.org/bot${{ secrets.TELEGRAM_BOT_TOKEN }}/sendMessage" \
          -d "chat_id=${{ secrets.TELEGRAM_CHAT_ID }}" \
          -d "text=3.0阅读书源更新合并完成!分支：${{ github.ref }}"
