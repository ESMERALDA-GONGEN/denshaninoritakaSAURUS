# 電車に乗りたかザウルス

東海道新幹線の旅の思い出アプリ（Streamlit）。

## ローカルで動かす

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## デプロイ（おすすめ: Streamlit Community Cloud）

無料で公開でき、GitHub と連携します。

1. このフォルダを **Git リポジトリ**にして GitHub に push する  
   - 例: GitHub で空リポジトリを作り、以下を実行

   ```powershell
   cd denshaninoritaka
   git init
   git add app.py album_generator.py tokaido_stations.py requirements.txt packages.txt README.md .gitignore .streamlit Dockerfile
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<あなたのユーザー名>/<リポジトリ名>.git
   git push -u origin main
   ```

2. [Streamlit Community Cloud](https://share.streamlit.io/) にサインイン（GitHub アカウント）

3. **New app** → リポジトリ・ブランチを選ぶ

4. **Main file path** に `app.py` を指定して Deploy

5. 完了すると URL が発行される（`*.streamlit.app`）

### メモ

- 秘密情報（API キーなど）は使っていません。将来使う場合は Cloud の **Secrets** に設定します。
- `requirements.txt` があれば依存関係は自動インストールされます。
- リポジトリ直下の **`packages.txt`** で Linux に **Noto CJK フォント**を入れています。アルバム PNG の日本語が極小になる問題の対策です（Streamlit Community Cloud が `packages.txt` に対応している前提）。

## 別の方法（Docker）

コンテナ対応ホスト（Railway、Render、自前サーバーなど）向け。

```powershell
docker build -t densha-zaurus .
docker run -p 8501:8501 densha-zaurus
```

ブラウザで `http://localhost:8501` を開きます。
