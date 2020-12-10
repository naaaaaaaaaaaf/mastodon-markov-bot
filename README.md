# mastodon-markov-bot
## 何これ
Mastodon上のアカウントの投稿を、マルコフ連鎖して投稿するBotアプリケーション

デフォルト設定では「非公開」・「DM」は学習せず、投稿を「公開」設定で投稿します。 
利用する際は各サーバーのBotガイドラインに従ってください。


例: https://ap.ketsuben.red/@mecha_naf/105073696514947785

## 必要なもの
Dockerが入ったマシン(入れ方は各自調べてください)

## 動かし方 
1. Mastodonのアクセストークンを取得(https://example.com/settings/applications/new から取得可能)
2. src/config.ini.sample を src/config.ini にコピー
3. src/config.ini の必要項目を入力(コメントに従って書いてください。)
4. docker-compose up -d でDockerコンテナがビルドされ起動します。

## おすすめ開発方法
VScodeのRemote containerから開発
