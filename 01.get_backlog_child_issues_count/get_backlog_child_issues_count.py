import datetime
import logging
import json
import os
import requests
import sys
import traceback

"""共通設定"""
# 実行ファイルのカレントパス取得
current_path = os.path.dirname(os.path.abspath(__file__))
# セキュリティ対策でFalse
is_verify = False

"""ログ定義"""
# 基本設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d,%(levelname)s,%(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
log_path = "{current_path}/{log_filename}".format(
    current_path=current_path, log_filename="get_backlog_child_issues_count.log"
)
# 標準出力
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
# ファイル出力
file_handler = logging.FileHandler(filename=log_path, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

"""関数定義"""
# 親課題ID取得関数
def getParentIssueId(issue_key):
    # リクエストパラメータ定義
    api_url = "https://XXX.backlog.jp/api/v2/issues/{issue_id_or_key}".format(
        issue_id_or_key=issue_key
    )
    api_key = os.environ["BACKLOG_API_KEY"]
    # Backlog APIへのアクセス
    response = requests.get(
        url=api_url,
        params={
            "apiKey": api_key,
        },
        verify=is_verify,
    ).json()
    # Backlog APIからの返り値判定
    parent_Issue_Id=0
    if "errors" not in response:
        parent_Issue_Id=response["id"]
        logger.info(
            "親課題キー[{issue_key}]は親課題ID[{parent_Issue_Id}]を正常に取得できました。".format(
                issue_key=response["issueKey"],parent_Issue_Id=response["id"]
            )
        )
        return parent_Issue_Id
    else:
        logger.error(
            "Backlog APIエラーです。message[{message}]".format(
                message=response["errors"][0]["message"]
            )
        )
        raise Exception

# 子課題情報取得関数
def getChildIssues(issue_key: str, parent_Issue_Id: int):
    # リクエストパラメータ定義
    api_url = "https://XXX.backlog.jp/api/v2/issues"
    api_key = os.environ["BACKLOG_API_KEY"]
    # Backlog APIへのアクセス
    response = requests.get(
        url=api_url,
        params={
            "apiKey": api_key,
            "parentIssueId[]": parent_Issue_Id,
        },
        verify=is_verify,
    ).json()
    # Backlog APIからの返り値判定
    if "errors" not in response:
        logger.info('親課題ID[' + str(parent_Issue_Id) + ']から親課題キー[' + str(issue_key) + ']に紐づく子課題情報を正常に取得できました。次の通りです。')
    else:
        logger.error(
            "Backlog APIエラーです。message[{message}]".format(
                message=response["errors"][0]["message"]
            )
        )
        raise Exception

# 子課題数取得関数
def getChildIssuesCount(statusId: int, statusType: str, issue_key: str, parent_Issue_Id: int):
    # リクエストパラメータ定義
    api_url = "https://XXX.backlog.jp/api/v2/issues/count"
    api_key = os.environ["BACKLOG_API_KEY"]
    if statusId == 0:
        # Backlog APIへのアクセス
        response = requests.get(
            url=api_url,
            params={
                "apiKey": api_key,
                "parentIssueId[]": parent_Issue_Id,
            },
            verify=is_verify,
        ).json()
        # Backlog APIからの返り値判定
        if "errors" not in response:
            logger.info('課題キー[' + str(issue_key) + ']の子課題' + statusType + 'チケット数\t' + str(response["count"]))
        else:
            logger.error(
                "Backlog APIエラーです。message[{message}]".format(
                    message=response["errors"][0]["message"]
                )
            )
            raise Exception
    else:
        # Backlog APIへのアクセス
        response = requests.get(
            url=api_url,
            params={
                "apiKey": api_key,
                "parentIssueId[]": parent_Issue_Id,
                "statusId[]": statusId,
            },
            verify=is_verify,
        ).json()
        # Backlog APIからの返り値判定
        if "errors" not in response:
            logger.info('課題キー[' + str(issue_key) + ']の子課題' + statusType + 'チケット数\t' + str(response["count"]))
        else:
            logger.error(
                "Backlog APIエラーです。message[{message}]".format(
                    message=response["errors"][0]["message"]
                )
            )
            raise Exception

# メイン関数
def main(issue_key: str):
    logger.info("===== START SCRIPT =====")
    parent_Issue_Id = getParentIssueId(issue_key)
    getChildIssues(issue_key, parent_Issue_Id)
    getChildIssuesCount(0, "　全体", issue_key, parent_Issue_Id)
    getChildIssuesCount(1, " 未対応", issue_key, parent_Issue_Id)
    getChildIssuesCount(2, " 処理中", issue_key, parent_Issue_Id)
    getChildIssuesCount(3, " 処理済み", issue_key, parent_Issue_Id)
    getChildIssuesCount(4, "　完了", issue_key, parent_Issue_Id)
    logger.info("===== END SCRIPT =====")

"""エントリポイント"""
if __name__ == "__main__":
    try:
        args = sys.argv
        main(issue_key=args[1])
    except:
        logger.error("===== ABNORMAL END SCRIPT =====")
        logger.critical(traceback.format_exc())
        sys.exit(1)